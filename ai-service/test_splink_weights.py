import pandas as pd
from splink import Linker, SettingsCreator, DuckDBAPI
import splink.comparison_library as cl
from splink import block_on

df = pd.DataFrame([
    {"unique_id": "1", "name": "Rahul Sharma", "first": "rahul", "last": "sharma", "first_init": "r"},
    {"unique_id": "2", "name": "R Sharma", "first": "r", "last": "sharma", "first_init": "r"},
    {"unique_id": "3", "name": "Rahul Verma", "first": "rahul", "last": "verma", "first_init": "r"},
    {"unique_id": "4", "name": "Rocky", "first": "rocky", "last": "", "first_init": "r"}
])

settings = SettingsCreator(
    link_type="dedupe_only",
    probability_two_random_records_match=0.1,
    blocking_rules_to_generate_predictions=[
        "l.first = r.first",
        "l.last = r.last",
        "l.first_init = r.first_init and l.last = r.last"
    ],
    comparisons=[
        cl.JaroWinklerAtThresholds("name", [0.9, 0.7])
    ]
)

db_api = DuckDBAPI()
linker = Linker(df, settings, db_api=db_api)
df_predict = linker.inference.predict(threshold_match_probability=0.0).as_pandas_dataframe()
print(df_predict[['unique_id_l', 'unique_id_r', 'match_probability']])
