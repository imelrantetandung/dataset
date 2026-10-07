import duckdb

SUMBER = 'wildchat_4_8m/data/train-*.parquet'  # ditambah folder wildchat_4_8m

con = duckdb.connect()

con.execute(f"""
    COPY (
        SELECT *
        FROM read_parquet('{SUMBER}')
        LIMIT 1000
    ) TO 'sample_1000_wildchat.csv' (HEADER, DELIMITER ',')
""")

print("Selesai! Tersimpan di sample_1000_wildchat.csv")