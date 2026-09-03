import pandas as pd
from splink import Linker, SettingsCreator, block_on
import splink.comparison_library as cl
from splink.duckdb.database_api import DuckDBAPI

df = pd.DataFrame([
    {"unique_id": "1", "name": "Rahul Sharma"},
    {"unique_id": "2", "name": "R Sharma"},
    {"unique_id": "3", "name": "Rocky"},
    {"unique_id": "4", "name": "Rahul S."},
    {"unique_id": "5", "name": "Amit Kumar"}
])

settings = SettingsCreator(
    link_type="dedupe_only",
    blocking_rules_to_generate_predictions=[
        "1=1"
    ],
    comparisons=[
        cl.JaroWinklerAtThresholds("name", [0.8, 0.9])
    ],
    retain_matching_columns=True
)

db_api = DuckDBAPI()
linker = Linker(df, settings, database_api=db_api)
df_predict = linker.inference.predict(threshold_match_probability=0.0)
print(df_predict.as_pandas_dataframe())
