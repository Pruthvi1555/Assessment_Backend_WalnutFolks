# create_table.py
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL is not set in environment')


engine = create_engine(DATABASE_URL)


create_sql = '''
CREATE TABLE IF NOT EXISTS transactions (
id SERIAL PRIMARY KEY,
transaction_id TEXT NOT NULL UNIQUE,
source_account TEXT,
destination_account TEXT,
amount NUMERIC(18,2),
currency TEXT,
status TEXT NOT NULL CHECK (status IN ('PROCESSING','PROCESSED','FAILED')),
created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
processed_at TIMESTAMP WITH TIME ZONE NULL,
last_error TEXT
);
'''


with engine.begin() as conn:
    conn.execute(text(create_sql))
    print('Ensured `transactions` table exists')