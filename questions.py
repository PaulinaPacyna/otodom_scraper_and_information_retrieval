import json
from typing import Dict

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy import text

from apartments import get_engine
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()


def list_offers():
    with get_engine().connect() as cur:
        result = cur.execute(
            text("SELECT distinct url from apartments"),
        )
        return [row[0] for row in result.fetchall()]


def get_offer_info(url) -> Dict[str, str]:
    with get_engine().connect() as cur:
        result = cur.execute(
            text("SELECT table_dump, description from apartments where url=:url"),
            {"url": url},
        )
        short_desc, desc = result.fetchone()
        return {"short_desc": short_desc, "desc": desc}


def get_questions():
    with open("questions.json", "r") as file:
        return json.load(file)


if __name__ == "__main__":
    for url in list_offers():

        template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Jesteś doradcą w agencji nieruchomości, który świetnie potrafi 
             podpowiedzieć czy dana oferta spełnia konkretne, sprecyzowane wymagania klienta.
             Wiesz, że skrót od księga wieczysta to KW lub kw.  Jeśli nie wiesz jaka jest odpowiedź, 
             powiedz, że nie ma danej informacji.""",
                ),
                (
                    "user",
                    """
            Zapoznaj się z poniższą ofertą. Poniżej znajdziesz najważniejsze informacje:
            
            {short_desc}
            
            i opis od sprzedającego:
            
            {desc}
            
            Odpowiedz na poniższe pytania kupującego.
            
            {question}
            """,
                ),
            ],
        ).format_messages(**get_offer_info(url), question="\n".join(get_questions()))
        ans = llm.invoke(template)
        print(get_offer_info(url))
        print(ans.content)
