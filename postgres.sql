CREATE TABLE IF NOT EXISTS playdata (
    id SERIAL PRIMARY KEY,
    initial_state TEXT NOT NULL,
    action TEXT NOT NULL,
    resultant_state TEXT NOT NULL,
    reward REAL NOT NULL
)
