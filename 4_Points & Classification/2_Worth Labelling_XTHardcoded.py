#     _              _       _   _               _               _ _             
#    / \    ______ _| |__   | | | | __ _ _ __ __| | ___ ___   __| (_)_ __   __ _ 
#   / _ \  |_  / _` | '_ \  | |_| |/ _` | '__/ _` |/ __/ _ \ / _` | | '_ \ / _` |
#  / ___ \  / / (_| | |_) | |  _  | (_| | | | (_| | (_| (_) | (_| | | | | | (_| |
# /_/   \_\/___\__,_|_.__/  |_| |_|\__,_|_|  \__,_|\___\___/ \__,_|_|_| |_|\__, |
#                                                                          |___/ 
# maaf :(
import pandas as pd

df = pd.read_csv('points.csv')

# hardcoded, really sorry king
kelas_mapping = [
    ("5 - 6jt", 0, 12274, 5000000, 6000000),
    ("6 - 7jt", 12275, 16207, 6000001, 7000000),
    ("7 - 8jt", 16208, 18304, 7000001, 8000000),
    ("8 - 9jt", 18305, 22447, 8000001, 9000000),
    ("9 - 10jt", 22448, 27761, 9000001, 10000000),
    ("10 - 11jt", 27762, 31000, 10000001, 11000000),
    ("11 - 12jt", 31001, 33002, 11000001, 12000000),
    ("12 - 13jt", 0, 1, 12000001, 13000000), # makanya jangan hardcoded
    ("13 - 14jt", 0, 1, 13000001, 14000000), # susah bang
    ("14 - 15jt", 0, 1, 14000001, 15000000), # ya belajar
    ("15 - 16jt", 0, 1, 15000001, 16000000), # ok maaf
    ("16 - 17jt", 0, 1, 16000001, 17000000), # itu siapa ngomong sendiri
    ("17 - 18jt", 0, 1, 17000001, 18000000), # barangnya bagus
    ("18 - 19jt", 0, 1, 18000001, 19000000), # barangnya bagus
    ("19 - 20jt", 36134, 39258, 19000001, 20000000), # zayyan ada disini
    ("20 - 21jt", 39259, 42137, 20000001, 21000000), # berisik zayyan
    ("21 - 22jt", 42138, 51567, 21000001, 22000000), # ok
    ("22 - 23jt", 51568, 64450, 22000001, 23000000),
    ("23 - 24jt", 64451, 71692, 23000001, 24000000),
    ("24 - 25jt", 71693, 76813, 24000001, 25000000),
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
        return "well-priced"

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
        return "well-priced"

df['worth'] = df.apply(calculate_worth, axis=1)

df.to_csv('dataset_ready.csv', index=False)
print(df[['points', 'Price (Rupiah)', 'worth']].head())
