import pandas as pd
import glob
import os

input_path = './parsed'
csv_files = sorted(glob.glob(os.path.join(input_path, '*.csv')))

df_all = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)
df_all = df_all.sort_values(by='price', ascending=True).reset_index(drop=True)
df_all.rename(columns={'RAM Size': 'RAM Size (GB)', 'Storage': 'Storage (GB)', 'Refresh Rate': 'Refresh Rate (Hz)', 'price': 'Price (Rupiah)'}, inplace=True)
df_all.to_csv('main_parsed.csv', index=False)

print("Done merged")
