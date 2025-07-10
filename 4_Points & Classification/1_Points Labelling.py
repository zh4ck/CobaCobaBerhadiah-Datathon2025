import pandas as pd

csv_file = "../3_Passmark Fetch & Parse/scored.csv"

df = pd.read_csv(csv_file)
df["GPU"] = df["GPU"].fillna(0)
df["Brand"] = df["Brand"].fillna(0)

def calculate_points(row):
    try:
        cpu = float(row["CPU"]) if pd.notna(row["CPU"]) else 0
        ram_type = str(row["RAM Type"]).strip().upper() if pd.notna(row["RAM Type"]) else ""
        ram_size = float(row["RAM Size (GB)"]) if pd.notna(row["RAM Size (GB)"]) else 0
        storage = float(row["Storage (GB)"]) if pd.notna(row["Storage (GB)"]) else 0
        screen_type = str(row["Screen Type"]).strip().upper() if pd.notna(row["Screen Type"]) else ""
        refresh_rate = float(row["Refresh Rate (Hz)"]) if pd.notna(row["Refresh Rate (Hz)"]) else 0
        upgradeable = int(row["Upgradeable"]) if pd.notna(row["Upgradeable"]) else 0
        uniqueness = int(row["Uniqueness"]) if pd.notna(row["Uniqueness"]) else 0
        gpu = float(row["GPU"]) if pd.notna(row["GPU"]) else 0
        brand = str(row["Brand"]).strip().upper() if pd.notna(row["Brand"]) else ""
    except (ValueError, TypeError):
        return None

    ram_score = (cpu * 5 * ram_size if ram_type == "DDR5" else cpu * ram_size) / 500

    storage_score = storage * 3

    oled_bonus = 10000 if screen_type == "OLED" else 0

    refresh_score = refresh_rate * 30

    upgrade_score = cpu * 1.2 if upgradeable == 1 else cpu

    unique_score = cpu * 1.28 if uniqueness == 1 else cpu

    base = (cpu + ram_score)
    mid = storage_score + oled_bonus + refresh_score + upgrade_score + unique_score
    result = ((base + mid) - (cpu * 2.5)) + gpu

    # maf ya kalau ada fans brand ini, biar ga imba 💔
    if brand in ["AXIOO", "INFINIX", "TECNO", "ADVAN"]:
        result *= 0.9

    return int(result)

df["points"] = df.apply(calculate_points, axis=1)
df.to_csv("points.csv", index=False)

print("Done extracting points")
