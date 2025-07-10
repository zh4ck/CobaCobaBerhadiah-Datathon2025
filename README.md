
# 🎁 Coba Coba Berhadiah — Datathon 2025
**Integrasi SGD Regression dan Random Forest Classification untuk Penetapan Harga  Kompetitif dan Analisis Daya Beli Laptop di Indonesia**<br>
Sistem analitik terintegrasi yang mengombinasikan model regression dan classification untuk analisis produk laptop di pasar Indonesia. Sistem ini menentukan harga optimal berdasarkan spesifikasi teknis dan memprediksi potensi daya beli melalui analisis specification-to-price ratio. Dataset mencakup 1.126 produk laptop dari marketplace dengan fitur utama spesifikasi teknis dan harga produk. Implementasi model regresi (SGD Regression) mencapai MAE 889.73, RMSE 1167.156, dan R2 0,99, sementara model klasifikasi (Random Forest) memperoleh akurasi 90%. Hasil eksperimen menunjukkan kemampuan sistem dalam mengidentifikasi produk overpriced/underpriced serta memberikan rekomendasi strategis. Sistem ini berpotensi meningkatkan efisiensi pasar dan mendukung pengambilan keputusan bagi produsen dan konsumen.

**Anggota Tim :**
1. Glenn Josia Devano (glenn.josia.devano@ui.ac.id)
2. Nadhim Muzhaffar Hakim (nadhim.muzhaffar@ui.ac.id)
3. Zayyan Ramadzaki Firdaus (zayyan.ramadzaki@ui.ac.id)

**🤗 HuggingFace Links :**
* [Models](https://huggingface.co/clowndhim/Model_Coba-Coba-Berhadiah)
* [Datasets](https://huggingface.co/datasets/clowndhim/Dataset_Model_CobaCobaBerhadiah)

## 📖 Dependencies & Library

Semua library yang dibutuhkan tercantum dalam file `requirements.txt` lengkap dengan versinya.



## 🚀 Cara Penggunaan

### 1. Ambil Cookie, Headers, dan Payload

Masuk ke folder `1_Tokopedia Web Scraping` dan ikuti langkah berikut:

1. Buka [tokopedia.com](https://tokopedia.com) dan aktifkan developer tools > tab **Network**.
2. Filter `Fetch/XHR`, lalu:

   * Cari `SearchProductV5Query` saat mencari produk → klik kanan → salin sebagai `cURL (bash)`
   * Buka halaman produk, cari `PDPGetLayoutQuery` → salin juga sebagai `cURL (bash)`
3. Disini kami menggunakan [https://curlconverter.com/json/](https://curlconverter.com/json/) untuk mengubah cURL menjadi JSON.
4. Simpan hasil konversi:

   * Headers → `headers.json`
   * Cookies → `cookies.json`
   * Payload `SearchProductV5Query` → `search.json`
   * Payload `PDPGetLayoutQuery` → `description.json`

> **⚠️ Dimohon untuk membaca `notes.txt` terlebih dahulu pada folder `1_Tokopedia Web Scraping`.**

### 2. Scraping Produk

Jalankan:

```bash
python 1_Items Scraping.py
```

Output akan disimpan dalam bentuk `.csv` di folder `Items`.


### 3. Scraping Deskripsi

Jalankan:

```bash
python 2_Description Scraping.py
```

Deskripsi setiap produk akan diambil berdasarkan kelas harga dan disimpan ke dalam folder `2_Features or Specs Parsing/sources`.

⚠️ *Dilakukan bertahap untuk menghindari deteksi bot oleh pihak Tokopedia.*


### 4. Parsing Spesifikasi

Masuk ke folder `2_Features or Specs Parsing`, lalu:

```bash
python 1_Regex Parsing.py
```

File output `.csv` akan berisi hasil parsing dari judul & deskripsi, disimpan di folder `parsed`.


### 5. Menggabungkan Hasil Parsing

```bash
python 2_Merge Parsed.py
```

Output: `main_parsed.csv`
> Pada tahap ini, dilakukan juga normalisasi satuan (GB/Hz/Rp).


### 6. Cleaning & Generalization

```bash
python 3_Clean Parsed.py
```

* Menghapus dan memperbaiki data kosong
* Menyamakan format
* Generalisasi data
* Melakukan fuzzy matching untuk CPU & GPU berdasarkan `cpu.txt` dan `gpu.txt`

Output: `clean_parsed.csv`

### 7. Menambahkan Skor CPU & GPU

Masuk ke folder `3_Passmark Fetch & Parse` dan jalankan:

```bash
python parse-score.py
```

> Menggunakan `scraper.py` dari: [passmark-scraper](https://github.com/ading2210/passmark-scraper)

Output: `scored.csv`

### 8. Labelling Manual (Points & Worth)

Masuk ke folder `4_Points & Classification`, lalu:

1. Hitung skor poin berdasarkan spesifikasi:

   ```bash
   python 1_Points Labelling.py
   ```

2. Tentukan kelas harga berdasarkan skor poin & harga:

   ```bash
   python 2_Worth Labelling.py
   ```

Output akhir: `dataset_ready.csv`

### 9. Model Pelatihan

Dataset final dapat digunakan untuk keperluan pelatihan, validasi, dan evaluasi model. Lihat folder `5_Models` untuk list model yang digunakan baik untuk pengujian maupun deployment final.

## 📝 Notes

* **Headers dan cookies harus sesuai dengan payload**, jika tidak, scraping akan gagal.
* Akun Tokopedia **yang belum diverifikasi** (atau akun baru) cenderung gagal melakukan scraping (hasil percobaan kami).
* Proses scraping deskripsi mungkin akan memakan waktu yang cukup lama tergantung jumlah data.
* Parsing CPU/GPU dilakukan dengan bantuan RegEx dan files `cpu.txt` & `gpu.txt` yang dimana masih bersifat *hardcoded*. Solusi alternatif bisa digunakan seperti NLP dengan pertimbangan penggunaan resources yang lumayan besar.
* Perhitungan points dan penentuan worth saat ini masih *hardcoded* dan belum dinamis, namun sudah cukup akurat untuk sekarang.

## 📂 Dictionaries

```bash
.
├── 1_Tokopedia Web Scraping/
├── 2_Features or Specs Parsing/
├── 3_Passmark Fetch & Parse/
├── 4_Points & Classification/
├── 5_Models/
└── requirements.txt
```

## 💖 Special Thanks

* Tuhan Yang Maha Esa
* Doa Orang Tua
* RISTEK Universitas Indonesia
* [Stackoverflow](stackoverflow.com)

## 📄 License
[MIT License](LICENSE)

