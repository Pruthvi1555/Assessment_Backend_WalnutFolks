# app/db.py
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
print("DEBUG: ENVIRONMENT VARIABLES:", dict(os.environ))
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL not set')


engine = create_engine(DATABASE_URL, pool_pre_ping=True)