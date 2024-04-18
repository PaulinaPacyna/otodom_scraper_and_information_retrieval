from time import sleep

from dotenv import load_dotenv
from numpy.random import normal
from sqlalchemy import text

from database import get_engine
from otodom_parser import get_all_offers, parse_description, parse_table

load_dotenv()


def apartment_already_exist(link):
    with get_engine().connect() as cur:
        result = cur.execute(
            text("SELECT * from apartments where url=:url"), parameters={"url": link}
        )
        return bool(result.rowcount)


def scrape_offers_and_save(url):

    offers = get_all_offers(url)
    for link in offers:
        print(link)
        if apartment_already_exist(link):
            print(f"Skipping {link}")
            continue
        wait()
        desc = parse_description(link)
        wait()
        table = parse_table(link)
        with get_engine().connect() as cur:
            sql = text(
                """INSERT INTO apartments(url, table_dump, description, 
                created_at) VALUES(:link, :table, :desc, NOW());"""
            )
            cur.execute(sql, {"link": link, "table": table, "desc": desc})
            cur.commit()


def wait():
    sleep(abs(normal(1)))


if __name__ == "__main__":
    # todo move to streamlit
    url = (
        "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/mazowieckie/warszawa"
        "/warszawa/warszawa/ursynow?priceMax=1000000&areaMin=50&viewType=listing"
    )
    scrape_offers_and_save(url)
    for page in range(5):  # TODO scrape more than 5 (infer nr of pages)
        scrape_offers_and_save(url + f"&page={page}")
