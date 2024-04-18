from urllib.request import Request
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs


def get_all_offers(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = bs(urlopen(req).read(), "html5lib")
    result = []
    for offer in soup.find_all("a", attrs={"data-cy": "listing-item-link"}):
        result.append("https://www.otodom.pl" + offer.get("href"))
    return result


def parse_table(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = bs(urlopen(req).read(), "html5lib")
    table = soup.find("div", attrs={"data-testid": "ad.top-information.table"})
    table_dump = ""
    for div in table.find_all(
        lambda tag: tag.name == "div"
        and (
            "data-testid" in tag.attrs
            and tag["data-testid"].startswith("table-value")
            or ("data-cy" in tag.attrs and tag["data-cy"].startswith("table-label"))
        )
    ):
        table_dump += div.get_text() + (" " if "data-cy" in div.attrs else ", ")
    return table_dump


def parse_description(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = bs(urlopen(req).read(), "html5lib")
    desc = soup.find("div", attrs={"data-cy": "adPageAdDescription"})
    return desc.get_text()
