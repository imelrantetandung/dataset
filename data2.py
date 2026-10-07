import duckdb

SUMBER = 'wildchat_4_8m/data/train-*.parquet'
con = duckdb.connect()

con.execute(f"""
    COPY (
        SELECT 
            conversation_hash,
            model,
            timestamp,
            to_json(conversation) AS conversation_json,
            turn,
            language,
            toxic,
            redacted,
            country
        FROM read_parquet('{SUMBER}')
        LIMIT 10000,
    ) TO 'sample_10000_wildchat_v2.csv' (HEADER, DELIMITER ',')
""")
print("Selesai!")