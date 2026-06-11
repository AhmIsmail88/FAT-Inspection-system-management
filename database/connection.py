from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import Engine
from config.settings import DATABASE_PATH
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def create_db_engine():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    db_url = f"sqlite:///{DATABASE_PATH}"
    engine = create_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    return engine


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@event.listens_for(Engine, "connect")
def set_sqlite_pragmas(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    # WAL: multiple readers + one writer simultaneously (network share safe)
    cursor.execute("PRAGMA journal_mode=WAL")
    # Wait up to 5 sec if DB locked by another writer
    cursor.execute("PRAGMA busy_timeout=5000")
    # Faster writes on network drive without risking corruption
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def get_session():
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    from models import (  # noqa: F401
        project, supplier, supplier_contact,
        consultant, consultant_contact,
        fat_record, attachment, user, audit_log,
    )
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database ready at: {DATABASE_PATH}")
