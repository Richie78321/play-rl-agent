CREATE TABLE IF NOT EXISTS playdata (
    id SERIAL PRIMARY KEY,
    initial_state INTEGER NOT NULL,
    action INTEGER NOT NULL,
    resultant_state INTEGER NOT NULL,
    reward REAL NOT NULL
)
