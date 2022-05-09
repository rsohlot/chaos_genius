from . import webapp_url_prefix
"""
A util function to get the url for the anomaly dashboard.
"""


def anomaly_dashboard_url(kpi_id: int, dashboard_id: int = 0):
    """
    A util function to get the url for the anomaly dashboard.
    """
    return f"{webapp_url_prefix()}#/dashboard/{dashboard_id}/anomaly/{kpi_id}"


def deepdrills_dashboard_url(kpi_id: int, dashboard_id: int = 0):
    """
    A util function to get the url for the anomaly dashboard.
    """
    return f"{webapp_url_prefix()}#/dashboard/{dashboard_id}/deepdrills/{kpi_id}"


def dashboard_url(dashboard_id: int = 0):
    """
    A util function to get the url for the anomaly dashboard.
    """
    return f"{webapp_url_prefix()}#/dashboard/{dashboard_id}"


def anomaly_edit_url(kpi_id: int, dashboard_id: int = 0):
    """
    A util function to get the url for the anomaly dashboard.
    """
    return f"{webapp_url_prefix()}#/dashboard/{dashboard_id}/settings/{kpi_id}"
