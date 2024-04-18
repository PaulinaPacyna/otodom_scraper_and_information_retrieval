import os

from sqlalchemy import Engine, create_engine


def get_engine() -> Engine:
    user = os.environ["POSTGRES_USERNAME"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_USERNAME"]
    host = os.environ["PG_HOST"]
    port = os.environ["PG_PORT"]
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")
