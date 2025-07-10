import json
import time
import urllib.parse
import requests
import pandas as pd

# const buat file json dan url
BASE_URL = "https://gql.tokopedia.com/graphql/SearchProductV5Query"
COOKIE_PATH = './JSON/cookies.json'
HEADER_PATH = './JSON/headers.json'
PAYLOAD_TEMPLATE_PATH = './JSON/search.json'

def load_json_file(path):
    with open(path, 'r') as file:
        return json.load(file)

def build_param_string(keyword, page, rows, pmin, pmax, original_param_str):
    # Ambil params
    param_dict = dict(urllib.parse.parse_qsl(original_param_str))

    # Ganti params sesuai kebutuhan
    param_dict.update({
        'q': keyword,
        'page': str(page),
        'rows': str(rows),
        'start': str((page - 1) * rows),
        'pmin': str(pmin),
        'pmax': str(pmax),
        'ob': '23',
        'next_offset_organic': str((page - 1) * rows)
    })

    param_dict.pop('minus_ids', None)

    # Encode lagi
    return urllib.parse.urlencode(param_dict)

def scrape_tokopedia_search_v5(keyword, page, rows, pmin, pmax):
    # load file json
    cookies = load_json_file(COOKIE_PATH)
    headers = load_json_file(HEADER_PATH)
    payload = load_json_file(PAYLOAD_TEMPLATE_PATH)

    # rebuild params buat payload
    original_param_str = payload['variables']['params']
    updated_param_str = build_param_string(keyword, page, rows, pmin, pmax, original_param_str)
    payload['variables']['params'] = updated_param_str

    # 🚀 meluncur cihuy 🚀
    response = requests.post(BASE_URL, cookies=cookies, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"[ERROR] HTTP {response.status_code}")
        print(response.text)
        return []

    try:
        products = response.json()['data']['searchProductV5']['data']['products']
    except (KeyError, TypeError) as e:
        print(f"[ERROR] Failed to parse product data: {e}")
        return []

    # Format result
    results = []
    for item in products:
        results.append({
            'id': item['id'],
            'name': item['name'],
            'price': item.get('price', {}).get('number'),
            'price_text': item.get('price', {}).get('text'),
            'product_url': item['url'],
            'shop_name': item.get('shop', {}).get('name')
        })

    return results

def main():
    keyword = "laptop"
    rows = 50
    max_pages = 1

    # sesuaikan aja buat range & step
    range_start = 5_000_000
    range_end = 25_000_000
    step = 1_000_000

    for pmin in range(range_start, range_end, step):
        pmax = pmin + step
        all_data = []

        print(f"Scraping price range {pmin} - {pmax}...")

        for page in range(1, max_pages + 1):
            print(f"Scraping page {page}...")
            results = scrape_tokopedia_search_v5(keyword, page, rows, pmin, pmax)
            all_data.extend(results)
            time.sleep(3)

        if all_data:
            filename = f"{str(pmin//1_000_000)}{str(pmax//1_000_000)}.csv"
            df = pd.DataFrame(all_data)
            df.to_csv(filename, index=False)
            print(f"Saved {len(df)} ke {filename}")
        else:
            print(f"Data tidak ditemukan pada range {pmin} - {pmax}")

if __name__ == "__main__":
    main()
