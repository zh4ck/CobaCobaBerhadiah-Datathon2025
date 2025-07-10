import pandas as pd

df = pd.read_csv('points.csv')

# hardcoded, really sorry king
kelas_mapping = [
    ("5 - 6jt", 0, 13795, 5000000, 6000000),
    ("6 - 7jt", 13796, 16537, 6000001, 7000000),
    ("7 - 8jt", 16538, 18049, 7000001, 8000000),
    ("8 - 9jt", 18050, 21279, 8000001, 9000000),
    ("9 - 10jt", 21280, 28431, 9000001, 10000000),
    ("10 - 11jt", 28432, 31507, 10000001, 11000000),
    ("11 - 12jt", 31508, 33314, 11000001, 12000000),
    ("12 - 13jt", 33315, 36566, 12000001, 13000000),
    ("13 - 14jt", 36567, 38288, 13000001, 14000000),
    ("14 - 15jt", 38289, 42088, 14000001, 15000000),
    ("15 - 16jt", 42089, 45070, 15000001, 16000000),
    ("16 - 17jt", 45071, 51353, 16000001, 17000000),
    ("17 - 18jt", 51354, 54009, 17000001, 18000000),
    ("18 - 19jt", 54010, 59522, 18000001, 19000000),
    ("19 - 20jt", 59523, 59722, 19000001, 20000000),
    ("20 - 21jt", 59723, 61261, 20000001, 21000000),
    ("21 - 22jt", 61262, 64163, 21000001, 22000000),
    ("22 - 23jt", 64164, 71699, 22000001, 23000000),
    ("23 - 24jt", 72000, 74981, 23000001, 24000000),
]

# ambil harga ideal
def get_price_range_from_points(points):
    for label, min_point, max_point, min_price, max_price in kelas_mapping:
        if min_point <= points <= max_point:
            return min_price, max_price
    return None, None

# if and if and more if's
def calculate_worth(row):
    price = row['Price (Rupiah)']
    min_val, max_val = get_price_range_from_points(row['points'])

    if min_val is None or max_val is None or pd.isna(price):
        return "Unknown"

    if min_val <= price <= max_val:
        return "well-priced"
    elif (min_val - 1000000) <= price < min_val:
        return "good"
    elif price < (min_val - 1000000):
        return "excellent"
    elif max_val < price <= (max_val + 1000000):
        return "slight overprice"
    elif price > (max_val + 1000000):
        return "overpriced"
    else:
        return "Unknown"

df['worth'] = df.apply(calculate_worth, axis=1)

df.to_csv('dataset_ready.csv', index=False)
print(df[['points', 'Price (Rupiah)', 'worth']].head())
