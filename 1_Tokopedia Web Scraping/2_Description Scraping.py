import os
import re
import time
import json
import requests
import pandas as pd
from tqdm import tqdm

# const buat json, input/output dir
INPUT_DIR = './Items/'
OUTPUT_DIR = '../2_Features or Specs Parsing/sources'
COOKIE_PATH = './JSON/cookies.json'
HEADER_PATH = './JSON/headers.json'
PAYLOAD_TEMPLATE_PATH = './JSON/description.json'
SLEEP_DURATION = 3 # biar ga di ban (mamah aku takut)


def list_input_files(input_dir):
    return [os.path.join(input_dir, f) for f in os.listdir(input_dir)
            if f.endswith('.csv') and os.path.isfile(os.path.join(input_dir, f))]

def extract_shop_and_productkey(url):
    match = re.match(r'https://www\.tokopedia\.com/([^/]+)/([^?]+)', url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def load_static_json(path):
    with open(path, 'r') as file:
        return json.load(file)

def get_description(shop_domain, product_key, payload_template, cookies, headers):
    payload = payload_template.copy()
    payload['variables']['shopDomain'] = shop_domain
    payload['variables']['productKey'] = product_key

    try:
        response = requests.post(
            'https://gql.tokopedia.com/graphql/PDPGetLayoutQuery',
            headers=headers,
            cookies=cookies,
            json=[payload], # HARUS DIUBAH KE LIST
            timeout=20
        )

        result = response.json()
        root = result[0] if isinstance(result, list) else result
        components = root.get("data", {}).get("pdpGetLayout", {}).get("components", [])

        for comp in components:
            if comp.get("name") == "product_detail":
                data = comp.get("data")
                all_contents = []

                if isinstance(data, dict) and "content" in data:
                    for item in data["content"]:
                        title = item.get("title", "").strip()
                        subtitle = item.get("subtitle", "").strip()
                        all_contents.append(f"{title}: {subtitle}".strip(": "))
                elif isinstance(data, list):
                    for block in data:
                        if isinstance(block, dict) and "content" in block:
                            for item in block["content"]:
                                title = item.get("title", "").strip()
                                subtitle = item.get("subtitle", "").strip()
                                all_contents.append(f"{title}: {subtitle}".strip(": "))

                return "\n".join(all_contents).strip()

        return "Desc kosong"

    except Exception as e:
        return f"Gagal fetch: {e}"


def process_files():
    # load dulu masseh
    input_files = list_input_files(INPUT_DIR)
    cookies = load_static_json(COOKIE_PATH)
    headers = load_static_json(HEADER_PATH)
    payload_template = load_static_json(PAYLOAD_TEMPLATE_PATH)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for input_path in input_files:
        filename = os.path.basename(input_path)
        output_path = os.path.join(OUTPUT_DIR, filename)

        print(f"Processing: {filename}")
        df = pd.read_csv(input_path)

        if 'product_url' not in df.columns:
            print(f"{filename} tidak ada 'product_url'")
            continue

        if 'deskripsi' not in df.columns:
            df['deskripsi'] = ''

        for idx, row in tqdm(df.iterrows(), total=len(df)):
            url = row['product_url']
            shop_domain, product_key = extract_shop_and_productkey(url)

            if shop_domain and product_key:
                deskripsi = get_description(shop_domain, product_key, payload_template, cookies, headers)
                df.at[idx, 'deskripsi'] = deskripsi
            else:
                df.at[idx, 'deskripsi'] = 'gagal ambil domain/product_key'

            time.sleep(SLEEP_DURATION)

        df.to_csv(output_path, index=False)
        print(f"Output: {output_path}\n")


if __name__ == "__main__":
    process_files()
