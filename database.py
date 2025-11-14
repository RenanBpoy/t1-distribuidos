from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.db_retry import retry_session

WRITE_DATABASE_URL = (
    "postgresql://neondb_owner:npg_9ulJ0EXpzDZx@"
    "ep-fragrant-firefly-adtsg2z1-pooler.c-2.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

READ_REPLICA_1_DATABASE_URL = (
    "postgresql://neondb_owner:npg_9ulJ0EXpzDZx@"
    "ep-shy-recipe-adt7v32j-pooler.c-2.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

READ_REPLICA_2_DATABASE_URL = (
    "postgresql://neondb_owner:npg_9ulJ0EXpzDZx@"
    "ep-cool-block-adqfn5hx-pooler.c-2.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

READ_REPLICA_3_DATABASE_URL = (
    "postgresql://neondb_owner:npg_9ulJ0EXpzDZx@"
    "ep-plain-silence-adekjk4n-pooler.c-2.us-east-1.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

read_engines = [
    create_engine(READ_REPLICA_1_DATABASE_URL, pool_size=5, max_overflow=10),
    create_engine(READ_REPLICA_2_DATABASE_URL, pool_size=5, max_overflow=10),
    create_engine(READ_REPLICA_3_DATABASE_URL, pool_size=5, max_overflow=10),
]


write_engine = create_engine(
    WRITE_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
)

WriteSession = sessionmaker(autocommit=False, autoflush=False, bind=write_engine)
ReadSessions = [sessionmaker(autocommit=False, autoflush=False, bind=e) for e in read_engines]

_rr_index = 0
def get_read_sessionmaker():
    global _rr_index
    sm = ReadSessions[_rr_index]
    _rr_index = (_rr_index + 1) % len(ReadSessions)
    return sm
    
Base = declarative_base()

def get_write_db():
    db = retry_session(WriteSession)
    try:
        yield db
    finally:
        db.close()


def get_read_db():
    sessionmaker_fn = get_read_sessionmaker()
    db = retry_session(sessionmaker_fn)
    try:
        yield db
    finally:
        db.close()