import warnings

from greykite.framework.templates.forecaster import Forecaster
from greykite.framework.utils.result_summary import summarize_grid_search_results
from greykite.framework.templates.model_templates import ModelTemplateEnum
from greykite.framework.templates.autogen.forecast_config import MetadataParam
from greykite.framework.templates.autogen.forecast_config import ForecastConfig

import pandas as pd

from chaos_genius.core.anomaly.models import AnomalyModel

warnings.filterwarnings("ignore")


class GreyKiteModel(AnomalyModel):

    def __init__(self, *args, model_kwargs={}, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.model_kwargs = model_kwargs

    def predict(
        self,
        df: pd.DataFrame,
        pred_df: pd.DataFrame = None
    ) -> pd.DataFrame:
        """Takes in pd.DataFrame with 2 columns, dt and y, and returns a
        pd.DataFrame with 3 columns, dt, y, and yhat_lower, yhat_upper.

        :param df: Input Dataframe with dt, y columns
        :type df: pd.DataFrame
        :return: Output Dataframe with dt, y, yhat_lower, yhat_upper
        columns
        :rtype: pd.DataFrame
        """
        df = df.rename(columns={"dt": "ds", "y": "y"})
        metadata = MetadataParam(
            time_col="ds",
            value_col="y",
            freq="D"
        )

        # Creates forecasts and stores the result
        forecaster = Forecaster()  

        # result is also stored as forecaster.forecast_result
        result = forecaster.run_forecast_config(
            df=df,
            config=ForecastConfig(
                model_template=ModelTemplateEnum.SILVERKITE.name,
                forecast_horizon=1,  # forecasts 1 step
                **self.model_kwargs,
                metadata_param=metadata
            )
        )

        forecast_df = result.forecast.df
        forecast_df = forecast_df[
            ['ds', 'forecast', 'forecast_lower', 'forecast_upper']]
        forecast_df = forecast_df.rename(columns={
            'ds': 'dt',
            'forecast': 'y',
            'forecast_lower': 'yhat_lower',
            'forecast_upper': 'yhat_upper'
        })

        if pred_df is not None:
            return forecast_df.iloc[:-1]

        return forecast_df
