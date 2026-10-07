"""
Script buat EXPORT SEMUA data WildChat-4.8M (3,2 juta percakapan, SEMUA
bahasa) jadi SATU file CSV, lengkap dengan isi pesannya (baik pesan dari
pengguna maupun balasan AI), dipecah satu baris per pesan.

PENTING SEBELUM MULAI:
- Proses ini BISA MAKAN WAKTU BERJAM-JAM tergantung spek laptopmu.
- Hasil akhirnya BISA BERUKURAN BESAR (potensial belasan-puluhan GB).
  Pastikan E:\ masih ada ruang kosong minimal 30-50 GB biar aman.
- File CSV sebesar ini TIDAK BISA dibuka penuh di Excel (limit Excel
  cuma ~1.048.576 baris), jadi nanti buat lihat-lihat isinya lebih
  enak pakai pandas/DuckDB lagi, atau buka sebagian pakai text editor
  yang mendukung file besar (misalnya VS Code / Notepad++).
- Script ini AMAN buat ditutup paksa (Ctrl+C / tutup terminal) dan
  DILANJUTKAN lagi kapan saja, tinggal jalankan ulang. Progressnya
  dicatat di file progress_file_selesai.txt, file yang sudah selesai
  diproses otomatis dilewati.

Cara pakai:
1. Taruh file ini di folder E:\dataset.
2. pip install -U pandas pyarrow  (kalau belum)
3. python export_semua_data_wildchat.py
4. Kalau keputus di tengah jalan, tinggal jalankan lagi command yang sama,
   otomatis lanjut dari file terakhir yang belum selesai.
"""

import os
import glob
import pandas as pd

FOLDER_DATASET = r"E:\dataset\wildchat_4_8m"
SUMBER = f"{FOLDER_DATASET}/data"
OUTPUT = "wildchat_semua_pesan.csv"
PROGRESS = "progress_file_selesai.txt"

file_list = sorted(glob.glob(f"{SUMBER}/*.parquet"))
if not file_list:
    print(f"PERINGATAN: Tidak ada file .parquet ditemukan di {SUMBER}")
    print("Cek ulang lokasi foldernya, lalu sesuaikan FOLDER_DATASET di script ini.")
    raise SystemExit(1)

print(f"Ditemukan {len(file_list)} file parquet total.")

# ============================================================
# Cek progress sebelumnya (kalau ada), biar bisa lanjut bukan ulang
# ============================================================
selesai = set()
if os.path.exists(PROGRESS):
    with open(PROGRESS, "r", encoding="utf-8") as f:
        selesai = set(line.strip() for line in f if line.strip())
    print(f"Melanjutkan proses sebelumnya: {len(selesai)} file sudah pernah selesai diproses, akan dilewati.")

file_belum = [f for f in file_list if os.path.basename(f) not in selesai]
print(f"Sisa {len(file_belum)} file yang perlu diproses sekarang.\n")

# Kalau file output belum ada sama sekali, berarti ini proses baru -> tulis header.
# Kalau file output sudah ada (lanjutan proses sebelumnya) -> jangan tulis header lagi.
tulis_header = not os.path.exists(OUTPUT)

total_pesan_sesi_ini = 0
total_percakapan_sesi_ini = 0

for idx, file_path in enumerate(file_belum, start=1):
    nama_file = os.path.basename(file_path)
    print(f"[{idx}/{len(file_belum)}] Memproses {nama_file} ...")

    df = pd.read_parquet(file_path)
    total_percakapan_sesi_ini += len(df)

    baris_pesan = []
    for _, percakapan in df.iterrows():
        for urutan, pesan in enumerate(percakapan["conversation"], start=1):
            baris_pesan.append({
                "conversation_hash": percakapan["conversation_hash"],
                "urutan_pesan": urutan,
                "peran": pesan.get("role"),
                "teks_pesan": pesan.get("content"),
                "model_ai": percakapan["model"],
                "waktu_percakapan": percakapan["timestamp"],
                "jumlah_giliran": percakapan["turn"],
                "bahasa": percakapan["language"],
                "negara": percakapan["country"],
                "flag_redaksi": percakapan["redacted"],
                "flag_toxic": percakapan["toxic"],
            })

    pesan_df = pd.DataFrame(baris_pesan)

    # Ditambahkan (append) ke CSV yang sama, bukan bikin file baru tiap kali,
    # biar hasil akhirnya tetap satu file CSV besar.
    pesan_df.to_csv(OUTPUT, mode="a", index=False, header=tulis_header, encoding="utf-8")
    tulis_header = False  # header cuma ditulis sekali di paling atas file

    total_pesan_sesi_ini += len(pesan_df)

    # Catat file ini sudah kelar, biar kalau macet di tengah bisa lanjut dari sini
    with open(PROGRESS, "a", encoding="utf-8") as f:
        f.write(nama_file + "\n")

    print(f"    -> {len(df)} percakapan menghasilkan {len(pesan_df)} baris pesan. "
          f"Total baris ditambahkan sesi ini: {total_pesan_sesi_ini}")

print(f"\nSELESAI untuk sesi ini.")
print(f"Percakapan diproses sesi ini : {total_percakapan_sesi_ini}")
print(f"Baris pesan ditambahkan sesi ini : {total_pesan_sesi_ini}")
print(f"Semua hasil tersimpan di : {OUTPUT}")
print(f"Kalau jumlah baris di {PROGRESS} sudah = {len(file_list)}, berarti export sudah 100% lengkap untuk semua file.")