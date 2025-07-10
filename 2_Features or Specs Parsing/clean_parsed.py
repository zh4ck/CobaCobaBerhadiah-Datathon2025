import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
import re
import ast

df = pd.read_csv("main_parsed.csv")

# Hapus row tanpa CPU dan row dengan nama CPU yang kurang jelas (tidak ada angka)
df = df.dropna(subset=["CPU"])
df = df[df["CPU"].str.strip().astype(bool)]
df = df[df["CPU"].str.contains(r"\d", regex=True)]

# Ubah GPU kosong dari yang '-' menjadi NaN (avoid confusion)
df["GPU"] = df["GPU"].replace("-", np.nan)

# Ubah nilai uniqueness jadi integer
def convert_uniqueness(row):
    try:
        items = ast.literal_eval(row) if isinstance(row, str) else row
        if not items:
            return 0
        elif items == ['fingerprint']:
            return 1
        else:
            return 2
    except Exception:
        return 0 

# Clean RAM Size & Storage
def strip_gb(row):
    if pd.isna(row):
        return None
    return int(str(row).replace("GB", "").strip())

# Default jika kosong
df["RAM Size (GB)"] = df["RAM Size (GB)"].fillna(8)

# Generalisir storage
def generalize_storage(row):
    price = row["Price (Rupiah)"]
    brand = str(row["Brand"]).strip().upper()
    storage = row["Storage (GB)"]
    if pd.notna(storage): # kalau data ga kosong
        # Kasus aneh nan ajaib
        if storage == 128: # maaf hardcoded banget, ini kyknya gara gara RegEx 😔
            return 512

        # Generalisir data
        if price <= 6_500_000 and brand != "AXIOO": # biasanya dibawah harga segini storagenya 256gb
            return 256
        elif price < 13_500_000 and storage > 512: # Mencegah RegEx salah parse 1024GB (max storage) sebagai storage
            return 512
        elif storage > 1024: # Entah kenapa ada laptop 2TB saya juga bingung
            return 1024
        return row["Storage (GB)"]

    # Jika kosong
    if price <= 7_000_000:
        return 256 
    else:
        return 512

# Generalisir ukuran RAM kecuali AXIOO
def generalize_ram(row):
    if row["Price (Rupiah)"] < 8_000_000 and str(row["Brand"]).strip().upper() != "AXIOO":
        return 8
    elif row["Price (Rupiah)"] < 14_500_000 and row["RAM Size (GB)"] > 16: # RegEx kadang salah parse 32 GB sebagai ukuran RAM (biasanya 32 GB itu max expand RAM)
        return 16
    return row["RAM Size (GB)"]

# Generalisir tipe layar menjadi LED & OLED saja
def generalize_screen_type(row):
    row = str(row).strip().upper()
    if row == "OLED":
        return "OLED"
    elif row:  # selain OLED = LED
        return "LED"
    return "LED"

# Cleaning CPU & GPU dimulai disini
# Import list CPU & GPU
with open("./cpu.txt", "r", encoding="utf-8") as file:
    cpu_list = [line.strip() for line in file if line.strip()]
with open("./gpu.txt", "r", encoding="utf-8") as file:
    gpu_list = [line.strip() for line in file if line.strip()]

# Normalisasi & Match Fuzz CPU
def normalize_cpu(text):
    text = str(text).lower()
    text = text.replace("intel", "").replace("core", "")
    text = text.replace("ryzen", "").replace("amd", "")
    text = text.replace("celeron", "").replace("pentium", "").replace("athlon", "")
    text = text.replace("ultra", "")
    text = text.replace("-", " ").replace("_", " ")
    text = text.replace("  ", " ")
    return text.strip()

cpu_list_clean = [normalize_cpu(cpu) for cpu in cpu_list]

def match_cpu(raw_cpu, gpu_value=None):
    if pd.isna(raw_cpu) or not str(raw_cpu).strip():
        return None
    
    raw_norm = normalize_cpu(raw_cpu)

    matches = process.extract(raw_norm, cpu_list_clean, scorer=fuzz.token_sort_ratio, limit=5)
    filtered_matches = [m for m in matches if m[1] >= 70]

    if not filtered_matches:
        return None

    # Gunakan processor dengan suffix 'X' kalau ada GPUnya
    prefer_suffix = "x" if pd.notna(gpu_value) and str(gpu_value).strip() else None

    candidates = []
    # JANGAN HAPUS MATCH_TEXT NANTI ERROR
    for match_text, score, idx in filtered_matches:
        original_cpu = cpu_list[idx]
        candidates.append((original_cpu, score))

    if prefer_suffix:
        with_x = [cpu for cpu, _ in candidates if "x" in cpu.lower()]
        if with_x:
            return with_x[0]
    else:
        without_x = [cpu for cpu, _ in candidates if "x" not in cpu.lower()]
        if without_x:
            return without_x[0]

    return candidates[0][0]

# Normalisasi & Match Fuzz GPU
def normalize_gpu(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"(nvidia|amd|intel|geforce|radeon|graphics|laptop|mobile)", "", text)
    text = text.replace("-", " ").replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(mx|gtx|rtx)\s*", r"\1 ", text)
    text = text.strip()
    return text

gpu_list_clean = [normalize_gpu(gpu) for gpu in gpu_list]

def match_gpu(raw_gpu):
    if pd.isna(raw_gpu) or not str(raw_gpu).strip():
        return None

    raw_norm = normalize_gpu(raw_gpu)

    for clean, original in zip(gpu_list_clean, gpu_list):
        if raw_norm == clean:
            return original

    match = process.extractOne(raw_norm, gpu_list_clean, scorer=fuzz.token_sort_ratio, score_cutoff=85)
    if match:
        index = gpu_list_clean.index(match[0])
        return gpu_list[index]
    return None

df["Uniqueness"] = df["Uniqueness"].apply(convert_uniqueness)
df["RAM Size (GB)"] = df["RAM Size (GB)"].apply(strip_gb)
df["Storage (GB)"] = df["Storage (GB)"].apply(strip_gb)
df["RAM Size (GB)"] = df.apply(generalize_ram, axis=1)
df["Storage (GB)"] = df.apply(generalize_storage, axis=1)
df["Screen Type"] = df["Screen Type"].apply(generalize_screen_type)
df["GPU"] = df["GPU"].apply(match_gpu)
df["CPU"] = df.apply(lambda row: match_cpu(row["CPU"], row["GPU"]), axis=1)

# hapus row dengan CPU kosong lagi
df = df.dropna(subset=["CPU"])
df = df[df["CPU"].str.strip().astype(bool)]
df = df[df["CPU"].str.contains(r"\d", regex=True)]

# Tambahin nomor biar cakep
df.insert(0, 'No', range(1, len(df) + 1))
f = df.drop(columns=["RAM Size (GB)", "Storage (GB)"], errors='ignore')

df.to_csv("clean_parsed.csv", index=False)
print("Done cleaning")
