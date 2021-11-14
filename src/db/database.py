from typing import Callable
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session as SessionType
import google.cloud.bigquery

# https://stackoverflow.com/q/34009296
# there isn't anything multi-threaded here so i haven't a clue
# why i'm getting thread issues. sqlalchemy bug maybe?
# if there are db corruption issues, check_same_thread=False
# is almost certainly the cause (right now it just generates exceptions
# on the thread)


engine = create_engine(os.getenv("BIGQUERY_PATH"), credentials_path=os.getenv("RW_SERVICE_PATH", "service-account.json"))

Session: Callable[[], SessionType] = sessionmaker(bind=engine, expire_on_commit=False)