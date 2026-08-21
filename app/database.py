"""Engine e sessão do SQLAlchemy + inicialização e auto-migrações (SQLite & PostgreSQL)."""
from __future__ import annotations

import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from . import config, models

# Normaliza URL do PostgreSQL fornecida pelo Render (postgres:// -> postgresql://)
db_url = config.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    models.Base.metadata.create_all(bind=engine)
    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Migrações seguras de colunas em users
            cols_usr = [col[1] for col in cursor.execute("PRAGMA table_info(users)").fetchall()]
            if "name" not in cols_usr:
                cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
            if "two_factor_enabled" not in cols_usr:
                cursor.execute("ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0")
            if "two_factor_secret" not in cols_usr:
                cursor.execute("ALTER TABLE users ADD COLUMN two_factor_secret TEXT")
            if "theme_preference" not in cols_usr:
                cursor.execute("ALTER TABLE users ADD COLUMN theme_preference TEXT DEFAULT 'auto'")
            if "is_verified" not in cols_usr:
                cursor.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT 0")
            if "verification_code" not in cols_usr:
                cursor.execute("ALTER TABLE users ADD COLUMN verification_code TEXT")
            if "reset_password_code" not in cols_usr:
                cursor.execute("ALTER TABLE users ADD COLUMN reset_password_code TEXT")

            # Migrações seguras de colunas em warmup_sessions
            cols_warm = [col[1] for col in cursor.execute("PRAGMA table_info(warmup_sessions)").fetchall()]
            if "account_age" not in cols_warm:
                cursor.execute("ALTER TABLE warmup_sessions ADD COLUMN account_age TEXT DEFAULT 'hoje'")
            if "target_country" not in cols_warm:
                cursor.execute("ALTER TABLE warmup_sessions ADD COLUMN target_country TEXT DEFAULT 'BR'")
            if "current_day" not in cols_warm:
                cursor.execute("ALTER TABLE warmup_sessions ADD COLUMN current_day INTEGER DEFAULT 1")
            if "total_days" not in cols_warm:
                cursor.execute("ALTER TABLE warmup_sessions ADD COLUMN total_days INTEGER DEFAULT 3")
            if "cycles_completed" not in cols_warm:
                cursor.execute("ALTER TABLE warmup_sessions ADD COLUMN cycles_completed INTEGER DEFAULT 0")
            if "next_cycle_at" not in cols_warm:
                cursor.execute("ALTER TABLE warmup_sessions ADD COLUMN next_cycle_at TIMESTAMP")

            # Migrações seguras de colunas em medias
            cols_med = [col[1] for col in cursor.execute("PRAGMA table_info(medias)").fetchall()]
            if "account_id" not in cols_med:
                cursor.execute("ALTER TABLE medias ADD COLUMN account_id INTEGER")
            if "account_name" not in cols_med:
                cursor.execute("ALTER TABLE medias ADD COLUMN account_name TEXT")

            # Migrações seguras de colunas em schedules
            cols_sched = [col[1] for col in cursor.execute("PRAGMA table_info(schedules)").fetchall()]
            if "usertags" not in cols_sched:
                cursor.execute("ALTER TABLE schedules ADD COLUMN usertags TEXT")
            if "target_type" not in cols_sched:
                cursor.execute("ALTER TABLE schedules ADD COLUMN target_type TEXT DEFAULT 'reel'")

            # Migrações seguras de colunas em accounts
            cols_acc = [col[1] for col in cursor.execute("PRAGMA table_info(accounts)").fetchall()]
            new_acc_cols = [
                ("full_name", "TEXT"),
                ("biography", "TEXT"),
                ("external_url", "TEXT"),
                ("follower_count", "INTEGER DEFAULT 0"),
                ("following_count", "INTEGER DEFAULT 0"),
                ("media_count", "INTEGER DEFAULT 0"),
                ("is_verified", "BOOLEAN DEFAULT 0"),
                ("is_private", "BOOLEAN DEFAULT 0"),
                ("instagram_pk", "TEXT"),
                ("profile_pic_url", "TEXT"),
                ("session_data", "TEXT"),
            ]
            for col_name, col_type in new_acc_cols:
                if col_name not in cols_acc:
                    cursor.execute(f"ALTER TABLE accounts ADD COLUMN {col_name} {col_type}")

            conn.commit()
            conn.close()
        except Exception:
            pass
