"""
Script buat NGINTIP isi dataset WildChat-4.8M yang sudah kamu download,
TANPA nyaring bahasa apapun dulu. Tujuannya cuma biar kamu lihat dulu
bentuk keseluruhan datanya: kolom apa aja yang ada, berapa total datanya,
bahasa apa aja yang ada di dalamnya, dan gimana bentuk satu percakapan.

Cara pakai:
1. Taruh file ini di folder E:\dataset (sejajar sama folder wildchat_4_8m),
   atau ubah FOLDER_DATASET di bawah sesuai lokasi foldermu.
2. pip install -U duckdb pandas pyarrow  (kalau belum pernah install)
3. python lihat_semua_data_wildchat.py
"""

import duckdb

FOLDER_DATASET = r"E:\dataset\wildchat_4_8m"
SUMBER = f"{FOLDER_DATASET}/data/*.parquet"

con = duckdb.connect()

# ============================================================
# 1. Lihat kolom apa aja yang ada di dataset
# ============================================================
print("=== Struktur/kolom dataset ===")
skema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{SUMBER}') LIMIT 1").fetchdf()
print(skema.to_string())

# ============================================================
# 2. Hitung total jumlah percakapan di seluruh dataset
# ============================================================
print("\n=== Total jumlah percakapan ===")
total = con.execute(f"SELECT COUNT(*) FROM read_parquet('{SUMBER}')").fetchone()[0]
print(f"Total percakapan: {total:,}")

# ============================================================
# 3. Lihat 10 bahasa dengan jumlah percakapan terbanyak
# ============================================================
print("\n=== 10 bahasa terbanyak dalam dataset ===")
bahasa = con.execute(f"""
    SELECT language, COUNT(*) AS jumlah
    FROM read_parquet('{SUMBER}')
    GROUP BY language
    ORDER BY jumlah DESC
    LIMIT 10
""").fetchdf()
print(bahasa.to_string(index=False))

# ============================================================
# 4. Ambil beberapa baris contoh (kolom ringkas dulu, tanpa isi
#    percakapan penuh, biar gampang dibaca di terminal)
# ============================================================
print("\n=== Contoh 20 baris data (ringkas) ===")
contoh = con.execute(f"""
    SELECT conversation_hash, model, language, country, turn, redacted, toxic, timestamp
    FROM read_parquet('{SUMBER}')
    LIMIT 20
""").fetchdf()
print(contoh.to_string(index=False))

# Simpan 500 baris contoh (kolom ringkas) ke CSV biar bisa dibuka & di-scroll di Excel
contoh_500 = con.execute(f"""
    SELECT conversation_hash, model, language, country, turn, redacted, toxic, timestamp
    FROM read_parquet('{SUMBER}')
    LIMIT 500
""").fetchdf()
contoh_500.to_csv("contoh_data_wildchat.csv", index=False)
print("\nSudah disimpan 500 baris contoh (tanpa isi percakapan) ke contoh_data_wildchat.csv")
print("Buka file itu di Excel kalau mau lihat-lihat datanya lebih santai.")

# ============================================================
# 5. Lihat isi SATU percakapan penuh, biar kelihatan strukturnya
#    (kolom "conversation" itu isinya list pesan user & AI bergantian)
# ============================================================
print("\n=== Contoh isi 1 percakapan lengkap ===")
satu = con.execute(f"""
    SELECT conversation
    FROM read_parquet('{SUMBER}')
    LIMIT 1
""").fetchone()[0]
for i, pesan in enumerate(satu, start=1):
    isi = pesan.get('content', '') or ''
    potongan = isi[:300] + ('...' if len(isi) > 300 else '')
    print(f"--- Pesan {i} (peran: {pesan.get('role')}) ---")
    print(potongan)