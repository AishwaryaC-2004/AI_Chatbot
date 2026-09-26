import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# =========================================================
# ENVIRONMENT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


if not DB_NAME:
    raise RuntimeError(
        f"DB_NAME is missing.\n"
        f"Check: {ENV_FILE}"
    )

if not DB_USER:
    raise RuntimeError(
        f"DB_USER is missing.\n"
        f"Check: {ENV_FILE}"
    )

if DB_PASSWORD is None:
    raise RuntimeError(
        f"DB_PASSWORD is missing.\n"
        f"Check: {ENV_FILE}"
    )


# =========================================================
# DATABASE URL
# =========================================================

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


print("========================================")
print("DATABASE CONFIGURATION")
print("========================================")
print("ENV FILE:", ENV_FILE)
print("ENV EXISTS:", ENV_FILE.exists())
print("DATABASE:", DB_NAME)
print("HOST:", DB_HOST)
print("PORT:", DB_PORT)
print("USER:", DB_USER)
print("========================================")


# =========================================================
# ENGINE
# =========================================================

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)


# =========================================================
# SESSION
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================================================
# BASE
# =========================================================

Base = declarative_base()


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()