"""
Script buat NGINTIP isi file wildchat_semua_pesan.csv (hasil export
lengkap kamu), TANPA perlu buka Excel, soalnya filenya kemungkinan
kegedean buat Excel (bisa jutaan baris).

Cara pakai:
1. Taruh file ini SEJAJAR sama wildchat_semua_pesan.csv (folder E:\dataset).
2. python lihat_hasil_export_csv.py
"""

import duckdb

FILE_CSV = "wildchat_semua_pesan.csv"
con = duckdb.connect()python lihat_hasil_export_csv.py

# ignore_errors=true biar kalau ada baris "kotor" (kayak kasus kemarin),
# baris itu dilewati, bukan bikin seluruh proses gagal.
SUMBER = f"read_csv('{FILE_CSV}', ignore_errors=true)"

# ============================================================
# 1. Total jumlah baris (pesan) di file
# ============================================================
print("=== Total baris (pesan) di file ===")
total = con.execute(f"SELECT COUNT(*) FROM {SUMBER}").fetchone()[0]
print(f"Total baris: {total:,}")

# ============================================================
# 2. Lihat 20 baris pertama
# ============================================================
print("\n=== 20 baris pertama ===")
contoh = con.execute(f"SELECT * FROM {SUMBER} LIMIT 20").fetchdf()
print(contoh.to_string())

# ============================================================
# 3. Jumlah baris per bahasa (10 bahasa terbanyak)
# ============================================================
print("\n=== Jumlah baris per bahasa (10 terbanyak) ===")
bahasa = con.execute(f"""
    SELECT bahasa, COUNT(*) AS jumlah
    FROM {SUMBER}
    GROUP BY bahasa
    ORDER BY jumlah DESC
    LIMIT 10
""").fetchdf()
print(bahasa.to_string(index=False))

# ============================================================
# 4. Contoh baris berbahasa Indonesia
# ============================================================
print("\n=== Contoh 20 baris berbahasa Indonesia ===")
indo = con.execute(f"""
    SELECT *
    FROM {SUMBER}
    WHERE bahasa = 'Indonesian'
    LIMIT 20
""").fetchdf()
print(indo.to_string())

# ============================================================
# 5. BONUS: pisahkan subset bahasa Indonesia ke file baru yang lebih kecil,
#    biar kamu bisa buka dengan nyaman di Excel
# ============================================================
print("\nMenyimpan subset bahasa Indonesia ke file terpisah (lebih kecil, bisa dibuka di Excel)...")
con.execute(f"""
    COPY (
        SELECT * FROM {SUMBER} WHERE bahasa = 'Indonesian'
    ) TO 'wildchat_pesan_indonesia.csv' (FORMAT CSV, HEADER TRUE)
""")
jumlah_indo = con.execute(f"SELECT COUNT(*) FROM read_csv('wildchat_pesan_indonesia.csv', ignore_errors=true)").fetchone()[0]
print(f"Selesai. wildchat_pesan_indonesia.csv berisi {jumlah_indo:,} baris, sudah bisa dibuka nyaman di Excel.")