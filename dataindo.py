r"""
Versi ini TIDAK mengganti nama kolom apapun dari dataset asli, dan
menyertakan SEMUA isi kolom yang ada (termasuk kolom-kolom di level
pesan yang sebelumnya belum ditampilkan, misalnya hashed_ip, header,
state, turn_identifier, dsb, tergantung apa yang benar-benar ada di
datasetnya).

Catatan penting: dataset WildChat punya kolom level PERCAKAPAN
(conversation_hash, model, timestamp, turn, language, country,
redacted, toxic) dan level PESAN (di dalam kolom "conversation", tiap
pesan juga py punya field bernama language/country/redacted/toxic/
timestamp sendiri-sendiri). Karena namanya SAMA PERSIS di dua level
itu, kalau digabung apa adanya akan saling menimpa. Makanya kolom
level percakapan diberi awalan "percakapan_" (HANYA yang bentrok nama),
sedangkan semua kolom di level pesan tetap persis apa adanya, tidak
diganti sama sekali.

Cara pakai:
1. Taruh file ini di folder E:\dataset.
2. python ambil_data_negara_indonesia_lengkap.py
3. Mau ambil lebih banyak/semua? Ubah BATAS_PERCAKAPAN jadi None.
"""

import duckdb
import pandas as pd

FOLDER_DATASET = r"E:\dataset\wildchat_4_8m"
SUMBER = f"{FOLDER_DATASET}/data/*.parquet"
BATAS_PERCAKAPAN = None  # ganti jadi None kalau mau ambil SEMUA
OUTPUT = "wildchat_negara_indonesia_lengkap.csv"

con = duckdb.connect()

# ============================================================
# LANGKAH 1: cek nilai kolom country yang berkaitan dengan Indonesia
# ============================================================
print("Mengecek nilai kolom country yang berkaitan dengan Indonesia...")
cek = con.execute(f"""
    SELECT DISTINCT country, COUNT(*) AS jumlah
    FROM read_parquet('{SUMBER}')
    WHERE country ILIKE '%indonesia%' OR country = 'ID'
    GROUP BY country
    ORDER BY jumlah DESC
""").fetchdf()
print(cek.to_string(index=False))

if cek.empty:
    print("\nTIDAK ditemukan nilai country yang cocok dengan Indonesia.")
    raise SystemExit(1)

nilai_country = cek["country"].tolist()
nilai_country_sql = ", ".join(f"'{v}'" for v in nilai_country)
print(f"\nMenggunakan nilai country: {nilai_country}")

# ============================================================
# LANGKAH 2: ambil SEMUA kolom (SELECT *) buat percakapan dengan
# country itu, dibatasi jumlahnya
# ============================================================
query = f"""
    SELECT *
    FROM read_parquet('{SUMBER}')
    WHERE country IN ({nilai_country_sql})
"""
if BATAS_PERCAKAPAN:
    query += f" LIMIT {BATAS_PERCAKAPAN}"

print("\nMengambil data percakapan (mohon tunggu)...")
df = con.execute(query).fetchdf()
print(f"Berhasil mengambil {len(df)} percakapan.")
print(f"Kolom level percakapan yang ditemukan: {list(df.columns)}")

# ============================================================
# LANGKAH 3: pecah jadi satu baris per pesan, SEMUA kolom disertakan,
# nama kolom TIDAK diganti (kecuali yang bentrok, diberi prefiks
# "percakapan_" biar ga saling menimpa)
# ============================================================
kolom_percakapan = [c for c in df.columns if c != "conversation"]

baris_pesan = []
for _, percakapan in df.iterrows():
    isi_pesan_list = percakapan["conversation"]
    for pesan in isi_pesan_list:
        baris = {}

        # Kolom level percakapan
        for kolom in kolom_percakapan:
            if kolom in ("conversation_hash", "model"):
                # nama-nama ini unik, tidak ada duplikat di level pesan,
                # jadi tetap apa adanya
                baris[kolom] = percakapan[kolom]
            else:
                # berpotensi bentrok nama sama field di level pesan
                baris[f"percakapan_{kolom}"] = percakapan[kolom]

        # Semua field di level pesan, PERSIS apa adanya, tidak diganti
        for k, v in pesan.items():
            baris[k] = v

        baris_pesan.append(baris)

pesan_df = pd.DataFrame(baris_pesan)
print(f"\nKolom akhir di CSV: {list(pesan_df.columns)}")

pesan_df.to_csv(OUTPUT, index=False, encoding="utf-8")

print(f"\nSELESAI.")
print(f"Percakapan diambil : {len(df)}")
print(f"Baris pesan dihasilkan : {len(pesan_df)}")
print(f"Tersimpan di : {OUTPUT}")