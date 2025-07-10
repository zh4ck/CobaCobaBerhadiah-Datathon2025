import pandas as pd
import re
import os

# Folder untuk input & output
input_folder = './sources'
output_folder = './parsed'

# Mencari file dengan tipe data .csv
csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

# Menambahkan beberpa keywords yang umum untuk menentukan 'keunikan' dari sebuah produk
# Juga keywords yang bisa menjadi indikator bahwa sebuah produk tidak bisa di upgrade (dari segi RAM)
uniqueness_keywords = ['fingerprint', 'yoga', 'flex']
non_upgradeable_keywords = ['soldered', 'non-upgradeable', 'not upgradeable', 'nonupgradeable', 'non upgradeable']

main_results = []

for csv_file in csv_files:
    df = pd.read_csv(os.path.join(input_folder, csv_file))

    # Membersihkan text dari beberapa simbol khusus, spaces, dan lain sebaginya
    def clean_text(text):
        text = re.sub(r'[\u00A0\u200b]', ' ', text) 
        text = re.sub(r'[®™]', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'–|—|-', '-', text)
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'\bprossesor\b', 'processor', text, flags=re.IGNORECASE)
        return text.strip()

    # Beberapa produk mencantumkan max RAM / Storage, guna menghindari salah intepretasi, ambil angka terkecil
    def extract_lowest(text, pattern):
        matches = re.findall(pattern, text, re.IGNORECASE)
        numbers = []
        for match in matches:
            try:
                num = int(match[0])
                unit = match[1].upper()
                if unit == 'TB':
                    num *= 1024
                numbers.append(num)
            except:
                continue
        return min(numbers) if numbers else None

    # Membuat list brand yang biasa muncul di eCommerce Tokopedia
    def parse_brand(name, description):
        brands = ['Axioo', 'Asus', 'Acer', 'HP', 'Advan', 'Tecno', 'Dell', 'MSI', 'Lenovo', 'Infinix']
        for brand in brands:
            if re.search(r'\b' + re.escape(brand) + r'\b', name, re.IGNORECASE):
                return brand.upper()
        for brand in brands:
            if re.search(r'\b' + re.escape(brand) + r'\b', description, re.IGNORECASE):
                return brand.upper()
        return ''

    # Parsing kode CPU
    def parse_cpu(text):
        # Bersihin teks
        text = clean_text(text)

        # Pola umum
        pattern = r'''
            \b(?:Intel\s*)?
            (?:Core\s*(?:Ultra\s*)?)?
            (i[3579]|i3|i5|i7|i9)
            [\s\-:]*
            ([A-Za-z]?\d{3,5}[A-Za-z]{0,2})
            |
            \b(?:AMD\s*)?
            Ryzen\s*
            ([3579])[\s\-:]*
            (\d{3,5}[A-Za-z]{0,2})
            |
            \b(?:Intel\s*)?
            (Celeron|Pentium)\s*(?:Silver|Gold)?[\s\-:]*
            (\w{3,5})
            |
            \b(?:AMD\s*)?
            (Athlon)[\s\-:]*
            (\w{3,5})
            |
            \b(?:Intel\s*)?
            (N\d{3,4})
        '''

        matches = re.findall(pattern, text, re.IGNORECASE | re.VERBOSE)

        # Append jenis model
        cpus = []
        for intel_i, intel_model, amd_gen, amd_model, cel_pent_type, cel_pent_model, athlon, athlon_model, intel_n in matches:
            if intel_i and intel_model:
                cpus.append(f"{intel_i.upper()}-{intel_model.upper()}")
            elif amd_gen and amd_model:
                cpus.append(f"RYZEN {amd_gen}-{amd_model.upper()}")
            elif cel_pent_type and cel_pent_model:
                cpus.append(f"{cel_pent_type.upper()} {cel_pent_model.upper()}")
            elif athlon and athlon_model:
                cpus.append(f"ATHLON {athlon_model.upper()}")
            elif intel_n:
                cpus.append(f"{intel_n.upper()}")

        # Fallback untuk beberapa kasus spesifik
        ultra_match = re.search(
            r'(?:Intel\s*)?(?:Core\s*)(Ultra\s*)?([3579])\s*(?:Processor\s*)?([A-Za-z]?\d{3,5}[A-Za-z]{0,2})',
            text, re.IGNORECASE
        )
        if ultra_match:
            gen = ultra_match.group(2)
            model = ultra_match.group(3)
            return f"I{gen}-{model.upper()}"

        intel_bare_match = re.search(
            r'(?:Intel\s*)(3|5|7)[\s\-:]*(\d{3,5}[A-Za-z]{0,2})',
            text, re.IGNORECASE
        )
        if intel_bare_match:
            gen = intel_bare_match.group(1)
            model = intel_bare_match.group(2)
            return f"I{gen}-{model.upper()}"

        ryzen_ai = re.search(r'RYZEN\s+AI\s+(3|5|7|9)[\s\-:]*(\d{3,5}[A-Za-z]{0,2})', text, re.IGNORECASE)
        if ryzen_ai:
            return f"RYZEN {ryzen_ai.group(1)}-{ryzen_ai.group(2).upper()}"

        intel_ultra_loose = re.search(r'\bULTRA\s+(3|5|7|9)[\s\-:]*(\d{3,5}[A-Za-z]{0,2})', text, re.IGNORECASE)
        if intel_ultra_loose:
            return f"I{intel_ultra_loose.group(1)}-{intel_ultra_loose.group(2).upper()}"

        intel_ultra_dash = re.search(r'Intel\s+Core\s+Ultra\s+(3|5|7|9)[\s\-:]*(\d{3,5}[A-Za-z]{0,2})', text, re.IGNORECASE)
        if intel_ultra_dash:
            return f"I{intel_ultra_dash.group(1)}-{intel_ultra_dash.group(2).upper()}"
        
        return cpus[-1] if cpus else ''

    def parse_gpu(text):
        matches = re.findall(
            r'\b((RTX|GTX|GeForce|NVIDIA)\s*[A-Za-z]*\d{3,4})\b',
            text, re.IGNORECASE
        )
        if matches:
            return matches[-1][0].upper()
        return '-'

    def parse_ram_type(text):
        ram_section = re.search(r'(?:memory|ram|memori)[:\s-]*([^.;\n]+)', text, re.IGNORECASE)
        if ram_section:
            section_text = ram_section.group(1)
            match = re.search(r'(DDR[45])', section_text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        # Fallback kalau gak ada
        match = re.search(r'(DDR[45])', text, re.IGNORECASE)
        return match.group(1).upper() if match else 'DDR4'

    def parse_ram_size(text):
        # Terkadang VRAM GPU disalahartikan sebagai RAM, jadi kita hindarin hal itu
        if re.search(r'\b(?:GTX|RTX|NVIDIA|VGA|Graphics)[^\n]{0,30}?(4|6|8)\s*GB\b', text, re.IGNORECASE):
            pass

        match = re.search(r'(\d{1,3})\s*GB\s*(?:LP)?DDR\d', text, re.IGNORECASE)
        if match:
            size = int(match.group(1))
            if 8 <= size <= 32:
                return f"{size}GB"

        # fallback untuk beberapa ukran ram yang umum ditemukan
        fallback_match = re.findall(r'\b(8|12|16|24|32)\s*GB\b', text, re.IGNORECASE)
        for val in fallback_match:
            size = int(val)
            if 8 <= size <= 32:
                return f"{size}GB"

        size = extract_lowest(
            text,
            r'(\d+)\s*(GB|TB)(?=\s*(?:DDR|RAM|SO-DIMM|memory|LPDDR|LP|MHz|\)|,|$))'
        )
        return f"{size}GB" if size and 8 <= size <= 32 else ''

    def parse_storage(text):
        matches = re.findall(r'(?:SSD|HDD|NVMe|M\.2|storage|Storage)[^\n]{0,30}?(\d+)\s*(GB|TB)', text, re.IGNORECASE)
        sizes = []
        for val, unit in matches:
            val = int(val)
            if unit.upper() == 'TB':
                val *= 1024
            sizes.append(val)
        if sizes:
            sizes = [s for s in sizes if s >= 128]
            return f"{min(sizes)}GB" if sizes else ''

        # Fallback ukuran storage yang umum ditemukan
        fallback_match = re.findall(r'\b(256|512|1024)\s*GB\b', text, re.IGNORECASE)
        if fallback_match:
            return f"{int(fallback_match[0])}GB"

        size = extract_lowest(
            text,
            r'(\d+)\s*(GB|TB)(?=\s*(?:SSD|HDD|NVMe|PCIe|storage|M\.2|\)|,|$))'
        )
        return f"{size}GB" if size and size >= 128 else ''

    def parse_screen(text):
        # Jenis panel yang biasa ditemukan
        match = re.search(
            r'\b(?:IPS|OLED|TN|VA|PLS|Mini-LED|LCD|LED)\b',
            text,
            re.IGNORECASE
        )
        # fallback utama jika tidak ditemkan -> LED
        return match.group(0).upper() if match else 'LED'

    def parse_refresh(text):
        text = text.lower()

        # ini sebenernya bruteforce untuk beberapa kemungkinan kasus, very hardcoded sorry 🙏
        match1 = re.search(
            r'(refresh rate|refresh|screen|layar|display|panel)[^\n]{0,25}?\b(60|75|90|120|144|165|180|240)\s*hz\b',
            text, re.IGNORECASE
        )
        if match1:
            return int(match1.group(2))

        match2 = re.search(
            r'\b(60|75|90|120|144|165|180|240)\s*hz\b[^\n]{0,25}?(refresh rate|refresh|screen|layar|display|panel)',
            text, re.IGNORECASE
        )
        if match2:
            return int(match2.group(1))

        context_around_screen = re.findall(
            r'(?:\b(?:oled|ips|lcd|2\.8k|3k|4k|qhd|fhd|uhd|hd|[\d\.]{2,3}\s*(?:inch|in|\"))[^.\n]{0,20}?)?\b(60|75|90|120|144|165|180|240)\s*hz\b',
            text, re.IGNORECASE
        )
        if context_around_screen:
            return int(context_around_screen[-1])

        all_matches = re.findall(r'\b(60|75|90|120|144|165|180|240)\s*hz\b', text, re.IGNORECASE)
        if all_matches:
            for hz in all_matches:
                idx = text.find(hz + 'hz')
                surrounding = text[max(0, idx - 30):idx + 10]
                # biar ga salah nangkep 50Hz/60Hz sebagai refresh rate
                if not re.search(r'(ac|volt|power|listrik)', surrounding):
                    return int(hz)
        return 60

    def parse_uniqueness(text):
        text_lower = text.lower()
        matched_keywords = [kw for kw in uniqueness_keywords if kw.lower() in text_lower]
        return matched_keywords

    def parse_upgradeable(text):
        return 0 if any(kw in text.lower() for kw in non_upgradeable_keywords) else 1

    results = []
    for _, row in df.iterrows():
        combined = clean_text(f"{row.get('name','')} {row.get('deskripsi','')}")
        name = row.get('name', '')
        results.append({
            'Brand': parse_brand(name, combined),
            'CPU': parse_cpu(combined),
            'GPU': parse_gpu(combined),
            'RAM Type': parse_ram_type(combined),
            'RAM Size': parse_ram_size(combined),
            'Storage': parse_storage(combined),
            'Screen Type': parse_screen(combined),
            'Refresh Rate': parse_refresh(combined),
            'Uniqueness': parse_uniqueness(combined),
            'Upgradeable': parse_upgradeable(combined),
            'price': row.get('price', '')
        })

    parsed_df = pd.DataFrame(results)
    output_path = os.path.join(output_folder, csv_file.replace('.csv', '_parsed.csv'))
    parsed_df.to_csv(output_path, index=False)
    print(f"Parsed {csv_file}, dir: {output_path}")