import pandas as pd
from splink import Linker, SettingsCreator, DuckDBAPI
import splink.comparison_library as cl

df = pd.DataFrame([
    {"unique_id": "1", "name": "Rahul Sharma"},
    {"unique_id": "2", "name": "R Sharma"},
])

settings = SettingsCreator(
    link_type="dedupe_only",
    comparisons=[cl.JaroWinklerAtThresholds("name", [0.9])]
)

db_api = DuckDBAPI()
linker = Linker(df, settings, database_api=db_api)
try:
    df_predict = linker.inference.predict(threshold_match_probability=0.0)
    print(df_predict.as_pandas_dataframe())
except Exception as e:
    print(e)
