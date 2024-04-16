import os
from time import sleep

from dotenv import load_dotenv
from numpy.random import normal
from sqlalchemy import create_engine, text, Engine

from parseotom import get_all_offers, parse_description, parse_table

load_dotenv()


def apartment_already_exist(link):
    with get_engine().connect() as cur:
        result = cur.execute(
            text("SELECT * from apartments where url=:url"), parameters={"url": link}
        )
        return bool(result.rowcount)


def get_engine() -> Engine:
    user = os.environ["POSTGRES_USERNAME"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_USERNAME"]
    host = os.environ["PG_HOST"]
    port = os.environ["PG_PORT"]
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")


def scrape_offers_and_save():
    url = (
        "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa"
        "/warszawa/warszawa/ursynow?priceMax=1000000&areaMin=50&viewType=listing"
    )
    offers = get_all_offers(url)
    for link in offers[:3]:
        print(link)
        if apartment_already_exist(link):
            print(f"Skipping {link}")
            continue
        with get_engine().connect() as cur:
            wait()
            desc = parse_description(link)
            wait()
            table = parse_table(link)
            sql = text(
                """INSERT INTO apartments(url, table_dump, description, 
                created_at) VALUES(:link, :table, :desc, NOW());"""
            )
            cur.execute(sql, {"link": link, "table": table, "desc": desc})
            cur.commit()


def wait():
    sleep(abs(normal(1)))


if __name__ == "__main__":
    scrape_offers_and_save()
