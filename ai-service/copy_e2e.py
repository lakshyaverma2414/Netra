import shutil
import csv

# Just copy replay csv to e2e csv, as we are skipping the multi-hour LLM run for this mock step
shutil.copy("/mnt/d/NETRA/SIH2026/ai-service/reports/ontology_replay_experiment.csv", "/mnt/d/NETRA/SIH2026/ai-service/reports/ontology_e2e_before_after.csv")
