import pandas as pd
from scraper import Scraper

# Sesuai dengan library scraper
cpu_scraper = Scraper("www.cpubenchmark.net")
gpu_scraper = Scraper("www.videocardbenchmark.net")

# Load dataset yang sudah dibersihkan
df = pd.read_csv("../1_Features or Specs Parsing/clean_parsed.csv")

# Caching biar lebih efisien eak
cpu_score_cache = {}
gpu_score_cache = {}

def get_cpu_score(cpu_name):
    if pd.isna(cpu_name):
        return 0
    if cpu_name in cpu_score_cache:
        return cpu_score_cache[cpu_name]

    results = cpu_scraper.search(cpu_name, limit=5)
    if results:
        score = int(results[0][0]["cpumark"].replace(",", ""))
        cpu_score_cache[cpu_name] = score
        return score
    else:
        cpu_score_cache[cpu_name] = 0
        return 0

def get_gpu_score(gpu_name):
    if pd.isna(gpu_name):
        return 0
    if gpu_name in gpu_score_cache:
        return gpu_score_cache[gpu_name]

    results = gpu_scraper.search(gpu_name, limit=5)
    if results:
        score = int(results[0][0]["g3d"].replace(",", ""))
        gpu_score_cache[gpu_name] = score
        return score
    else:
        gpu_score_cache[gpu_name] = 0
        return 0

df["CPU"] = df["CPU"].apply(get_cpu_score)
df["GPU"] = df["GPU"].apply(get_gpu_score)

df.to_csv("scored.csv", index=False)
print("Done scored")
