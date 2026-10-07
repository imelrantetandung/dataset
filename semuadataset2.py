"""
Versi 2: sama kayak export_semua_data_wildchat.py, tapi lebih TAHAN BANTING.
Kalau ada satu file parquet yang gagal dibaca (karena ada data "kotor"/rusak
di dalamnya, ini wajar terjadi di dataset besar), script ini akan:
  - Mencatat file itu ke file_gagal.txt (beserta pesan errornya)
  - MELEWATI file itu (tidak berhenti total)
  - Lanjut memproses file-file berikutnya

Cara pakai sama seperti sebelumnya:
1. Taruh file ini di folder E:\dataset.
2. python export_semua_data_wildchat_v2.py
3. Kalau keputus/error di tengah jalan, tinggal jalankan lagi command yang sama,
   otomatis lanjut dari file yang belum selesai maupun belum dicoba.

Kalau kamu sebelumnya sudah pakai script versi lama (semuadataset.py) dan
progress_file_selesai.txt sudah ada isinya, script ini tetap akan
melanjutkan dari situ (file yang sama isi/formatnya).
"""

import os
import glob
import traceback
import pandas as pd

FOLDER_DATASET = r"E:\dataset\wildchat_4_8m"
SUMBER = f"{FOLDER_DATASET}/data"
OUTPUT = "wildchat_semua_pesan.csv"
PROGRESS = "progress_file_selesai.txt"
GAGAL = "file_gagal.txt"

file_list = sorted(glob.glob(f"{SUMBER}/*.parquet"))
if not file_list:
    print(f"PERINGATAN: Tidak ada file .parquet ditemukan di {SUMBER}")
    raise SystemExit(1)

print(f"Ditemukan {len(file_list)} file parquet total.")

# File yang sudah SELESAI diproses sebelumnya
selesai = set()
if os.path.exists(PROGRESS):
    with open(PROGRESS, "r", encoding="utf-8") as f:
        selesai = set(line.strip() for line in f if line.strip())
    print(f"{len(selesai)} file sudah pernah selesai diproses, akan dilewati.")

# File yang sudah dicoba tapi GAGAL sebelumnya (biar nggak nyoba lagi percuma)
gagal_sebelumnya = set()
if os.path.exists(GAGAL):
    with open(GAGAL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                gagal_sebelumnya.add(line.split("\t")[0])
    if gagal_sebelumnya:
        print(f"{len(gagal_sebelumnya)} file sebelumnya gagal diproses, akan dilewati juga "
              f"(lihat detail di {GAGAL}). Hapus namanya dari file itu kalau mau dicoba ulang.")

file_belum = [f for f in file_list if os.path.basename(f) not in selesai
              and os.path.basename(f) not in gagal_sebelumnya]
print(f"Sisa {len(file_belum)} file yang akan diproses sekarang.\n")

tulis_header = not os.path.exists(OUTPUT)

total_pesan_sesi_ini = 0
total_percakapan_sesi_ini = 0
jumlah_gagal_sesi_ini = 0

for idx, file_path in enumerate(file_belum, start=1):
    nama_file = os.path.basename(file_path)
    print(f"[{idx}/{len(file_belum)}] Memproses {nama_file} ...")

    try:
        df = pd.read_parquet(file_path)

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
        pesan_df.to_csv(OUTPUT, mode="a", index=False, header=tulis_header, encoding="utf-8")
        tulis_header = False

        total_percakapan_sesi_ini += len(df)
        total_pesan_sesi_ini += len(pesan_df)

        with open(PROGRESS, "a", encoding="utf-8") as f:
            f.write(nama_file + "\n")

        print(f"    -> {len(df)} percakapan -> {len(pesan_df)} baris pesan ditambahkan. "
              f"Total baris sesi ini: {total_pesan_sesi_ini}")

    except Exception as e:
        # Jangan berhenti total. Catat file ini gagal, lanjut ke file berikutnya.
        jumlah_gagal_sesi_ini += 1
        pesan_error = str(e).replace("\n", " ")[:200]  # potong biar nggak kepanjangan
        print(f"    !! GAGAL memproses {nama_file}: {pesan_error}")
        print(f"    !! File ini DILEWATI, lanjut ke file berikutnya.")
        with open(GAGAL, "a", encoding="utf-8") as f:
            f.write(f"{nama_file}\t{pesan_error}\n")
        # (opsional) simpan traceback lengkap untuk debugging manual kalau perlu
        # traceback.print_exc()
        continue

print(f"\n=== SELESAI untuk sesi ini ===")
print(f"Percakapan diproses  : {total_percakapan_sesi_ini}")
print(f"Baris pesan ditambahkan : {total_pesan_sesi_ini}")
print(f"File gagal sesi ini  : {jumlah_gagal_sesi_ini}")
print(f"Hasil tersimpan di : {OUTPUT}")
print(f"Daftar file gagal (kalau ada) : {GAGAL}")
print(f"Kalau jumlah baris di {PROGRESS} + {GAGAL} sudah = {len(file_list)}, berarti semua file sudah dicoba.")