from datetime import datetime
from typing import cast

from celery import chain, group
from celery.app.base import Celery
from sqlalchemy.orm.attributes import flag_modified

from chaos_genius.controllers.kpi_controller import run_anomaly_for_kpi, run_rca_for_kpi
from chaos_genius.databases.models.kpi_model import Kpi
from chaos_genius.extensions import celery as celery_ext

celery = cast(Celery, celery_ext.celery)


# @celery.task
# def add_together(a, b):
#     print(a + b)
#     print("It works...xD")
#     # return a + b


@celery.task
def anomaly_single_kpi(kpi_id, end_date=None):
    """Run anomaly detection for the given KPI ID.

    Must be run as a celery task.
    """
    print(f"Running anomaly for KPI ID: {kpi_id}")

    status = run_anomaly_for_kpi(kpi_id, end_date)

    kpi = cast(Kpi, Kpi.get_by_id(kpi_id))
    anomaly_params = kpi.anomaly_params

    if status:
        print(f"Completed the anomaly for KPI ID: {kpi_id}.")
        anomaly_params["scheduler_params"]["anomaly_status"] = "completed"
    else:
        print(f"Anomaly failed for the for KPI ID: {kpi_id}.")
        anomaly_params["scheduler_params"]["anomaly_status"] = "failed"

    flag_modified(kpi, "anomaly_params")
    kpi.update(commit=True, anomaly_params=anomaly_params)

    return status


@celery.task
def rca_single_kpi(kpi_id: int):
    """Run RCA for the given KPI ID.

    Must be run as a celery task.
    """
    print(f"Running RCA for KPI ID: {kpi_id}")

    status = run_rca_for_kpi(kpi_id)

    kpi = cast(Kpi, Kpi.get_by_id(kpi_id))
    anomaly_params = kpi.anomaly_params

    if status:
        print(f"Completed RCA for KPI ID: {kpi_id}")
        anomaly_params["scheduler_params"]["rca_status"] = "completed"
    else:
        print(f"RCA FAILED for KPI ID: {kpi_id}")
        anomaly_params["scheduler_params"]["rca_status"] = "failed"

    flag_modified(kpi, "anomaly_params")
    kpi.update(commit=True, anomaly_params=anomaly_params)

    return status


@celery.task
def anomaly_kpi():
    kpis = Kpi.query.distinct("kpi_id").filter(
        (Kpi.run_anomaly == True) & (Kpi.active == True)
    )
    task_group = []
    for kpi in kpis:
        print(f"Starting anomaly task for KPI: {kpi.id}")
        task_group.append(anomaly_single_kpi.s(kpi.id))
    g = group(task_group)
    res = g.apply_async()
    return res


# runs every N time (set in celery_config)
# if time > scheduled time today, run task
# last_scheduled_time -> if it's < specified time of today's date, run task
@celery.task
def anomaly_scheduler():
    # find KPIs
    kpis: Kpi = Kpi.query.distinct("kpi_id").filter(
        (Kpi.run_anomaly == True) & (Kpi.active == True) & (Kpi.is_static == False)
    )

    task_group = []

    for kpi in kpis:
        kpi: Kpi

        # if anomaly isn't setup yet, we still run RCA at     tR + 24 hours
        # if anomaly is setup, we run both anomaly and RCA at tA + 24 hours

        # get scheduler_params, will be None if it's not set
        scheduler_params = (
            kpi.anomaly_params.get("scheduler_params")
            if kpi.anomaly_params is not None
            else None
        )

        scheduled_time = datetime.now()
        scheduled_time = scheduled_time.replace(hour=11, minute=0, second=0)
        if scheduler_params is not None and "time" in scheduler_params:
            # HH:MM:SS
            # this is tA
            hour, minute, second = map(int, scheduler_params["time"].split(":"))

            scheduled_time = datetime.now()
            # today's date, but at HH:MM:SS
            scheduled_time = scheduled_time.replace(
                hour=hour, minute=minute, second=second
            )
        elif scheduler_params is not None:
            # today's date, but at rca time (tR) or at kpi creation time
            scheduled_time = datetime.now()
            # this is tR
            if "rca_time" in scheduler_params:
                hour, minute, second = map(int, scheduler_params["rca_time"].split(":"))
                scheduled_time = scheduled_time.replace(
                    hour=hour, minute=minute, second=second
                )
            else:
                # this is kpi creation time
                canon_time = kpi.created_at
                scheduled_time = scheduled_time.replace(
                    hour=canon_time.hour, minute=canon_time.minute, second=canon_time.second
                )

        current_time = datetime.now()

        # check if we have to run anomaly:
        # 1. not already scheduled today
        # 2. anomaly is set up
        #
        # anomaly is setup if model_name is set in anomaly_params
        anomaly_is_setup = kpi.anomaly_params is not None and "model_name" in kpi.anomaly_params
        anomaly_already_run = (
            scheduler_params is not None
            and "last_scheduled_time" in scheduler_params
            and datetime.fromisoformat(scheduler_params["last_scheduled_time"])
            > scheduled_time
        )
        to_run_anomaly = (not anomaly_already_run) and anomaly_is_setup

        # check if we have to run RCA
        # 1. if not already scheduled today
        # 2. if anomaly is scheduled, run RCA too
        rca_already_run = (
            scheduler_params is not None
            and "last_scheduled_time" in scheduler_params
            and datetime.fromisoformat(scheduler_params["last_scheduled_time"])
            > scheduled_time
        )
        to_run_rca = to_run_anomaly or (not rca_already_run)

        if current_time > scheduled_time and (to_run_rca or to_run_anomaly):

            if to_run_anomaly:
                print(f"Scheduling anomaly for KPI: {kpi.id}")
                task_group.append(anomaly_single_kpi.s(kpi.id))
            if to_run_rca:
                print(f"Scheduling RCA for KPI: {kpi.id}")
                task_group.append(rca_single_kpi.s(kpi.id))

            new_scheduler_params = (
                scheduler_params if scheduler_params is not None else {}
            )
            if to_run_anomaly:
                new_scheduler_params["last_scheduled_time"] = current_time.isoformat()
                new_scheduler_params["anomaly_status"] = "in-progress"
            if to_run_rca:
                new_scheduler_params["last_scheduled_time"] = current_time.isoformat()
                new_scheduler_params["rca_status"] = "in-progress"

            anomaly_params = kpi.anomaly_params or {}
            anomaly_params["scheduler_params"] = new_scheduler_params

            flag_modified(kpi, "anomaly_params")
            kpi.update(commit=True, anomaly_params=anomaly_params)

    if not task_group:
        print("Found no pending KPI tasks.")
        return []

    g = group(task_group)
    res = g.apply_async()
    return res
