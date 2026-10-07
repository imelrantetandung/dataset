"""
Ambil SEMUA percakapan berbahasa Indonesia dari WildChat-4.8M,
dengan struktur PERSIS SAMA seperti dataset aslinya:
- nama kolom tidak diubah
- urutan kolom tidak diubah
- isi kolom tidak diubah (termasuk kolom 'conversation' yang berisi daftar pesan)
- tidak ada penggabungan atau pemecahan baris

Satu-satunya yang berbeda: barisnya difilter, hanya yang language = Indonesian.

Output:
1. wildchat_indonesia.parquet  -> salinan persis dataset asli (format sama), ini file utamanya
2. wildchat_indonesia.csv      -> versi CSV supaya gampang dibuka (nama kolom sama persis;
                                  kolom yang isinya bersarang, seperti 'conversation',
                                  ditulis sebagai teks JSON karena CSV tidak bisa menyimpan
                                  struktur bersarang)

Cara pakai:
1. Sesuaikan FOLDER_DATASET dengan lokasi folder file .parquet kamu.
2. Jalankan: python ambil_bahasa_indonesia_asli.py
"""

import duckdb

# ========== PENGATURAN ==========
FOLDER_DATASET = r"E:\dataset\wildchat_4_8m"   # folder tempat file .parquet asli
FILE_PARQUET = "wildchat_indonesia.parquet"
FILE_CSV = "wildchat_indonesia.csv"
BUAT_CSV = True                                  # False kalau CSV tidak diperlukan
# ================================

glob_parquet = FOLDER_DATASET.replace("\\", "/").rstrip("/") + "/**/*.parquet"
sumber = f"read_parquet('{glob_parquet}', union_by_name=true)"

con = duckdb.connect()

print("Membaca skema dataset asli...")
skema = con.execute(f"DESCRIBE SELECT * FROM {sumber}").fetchall()
for nama, tipe, *_ in skema:
    print(f"  {nama}: {tipe}")

kolom_nama = [s[0] for s in skema]
if "language" not in kolom_nama:
    raise SystemExit("Kolom 'language' tidak ditemukan, cek ulang datasetnya.")

print("\nNilai kolom 'language' yang mengandung kata 'indonesia':")
nilai_bahasa = [
    r[0] for r in con.execute(
        f"SELECT DISTINCT language FROM {sumber} WHERE language ILIKE '%indonesia%'"
    ).fetchall()
]
print(" ", nilai_bahasa)
if not nilai_bahasa:
    raise SystemExit("Tidak ada nilai bahasa Indonesia ditemukan.")

daftar = ", ".join("'" + v.replace("'", "''") + "'" for v in nilai_bahasa)
filter_sql = f"language IN ({daftar})"

print("\nMenghitung total percakapan Indonesia...")
total = con.execute(f"SELECT COUNT(*) FROM {sumber} WHERE {filter_sql}").fetchone()[0]
print(f"  Total percakapan: {total}")

print(f"\nMenyimpan ke {FILE_PARQUET} (struktur sama persis dengan aslinya)...")
con.execute(f"""
    COPY (SELECT * FROM {sumber} WHERE {filter_sql})
    TO '{FILE_PARQUET}' (FORMAT PARQUET)
""")

if BUAT_CSV:
    print(f"Menyimpan ke {FILE_CSV} ...")
    # kolom bersarang (STRUCT/LIST/MAP) diubah jadi teks JSON, kolom lain tidak diubah
    kolom_bersarang = [
        n for n, t, *_ in skema
        if t.startswith("STRUCT") or t.endswith("]") or t.startswith("MAP")
    ]
    if kolom_bersarang:
        ganti = ", ".join(f'to_json("{k}")::VARCHAR AS "{k}"' for k in kolom_bersarang)
        select_csv = f"SELECT * REPLACE ({ganti})"
    else:
        select_csv = "SELECT *"
    con.execute(f"""
        COPY ({select_csv} FROM read_parquet('{FILE_PARQUET}'))
        TO '{FILE_CSV}' (FORMAT CSV, HEADER)
    """)

print("\nVerifikasi hasil...")
skema_hasil = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{FILE_PARQUET}')").fetchall()
jumlah_hasil = con.execute(f"SELECT COUNT(*) FROM read_parquet('{FILE_PARQUET}')").fetchone()[0]
print("  Skema sama dengan dataset asli:", [s[:2] for s in skema] == [s[:2] for s in skema_hasil])
print(f"  Jumlah baris hasil: {jumlah_hasil} (harus sama dengan {total})")
print("\nSelesai.")