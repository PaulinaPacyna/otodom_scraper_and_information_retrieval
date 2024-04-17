import json
from typing import Dict, Tuple

from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from sqlalchemy import text
from langchain.memory import ChatMessageHistory
from apartments import get_engine
from langchain_openai import ChatOpenAI, OpenAI

from json_parser import parser

model = ChatOpenAI()


def list_offers():
    with get_engine().connect() as cur:
        result = cur.execute(
            text("SELECT distinct url from apartments"),
        )
        return [row[0] for row in result.fetchall()]


def get_offer_info(url) -> Tuple[str, str]:
    with get_engine().connect() as cur:
        result = cur.execute(
            text("SELECT table_dump, description from apartments where url=:url"),
            {"url": url},
        )
        short_desc, desc = result.fetchone()
        return short_desc, desc


def get_questions():
    with open("questions.json", "r") as file:
        return json.load(file)


if __name__ == "__main__":
    for url in list_offers()[:1]:
        chat_history = ChatMessageHistory()
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Jesteś doradcą w agencji nieruchomości, który potrafi określić "
                    "czy dana oferta spełnia konkretne, sprecyzowane wymagania "
                    "klienta. Wiesz, że skrót od księga wieczysta to KW lub kw. "
                    "Odpowiadasz na pytania na podstawie opisu, więc jeśli nie wiesz "
                    "jaka jest odpowiedź, powiedz, że nie ma danej informacji.",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        short_desc, desc = get_offer_info(url)
        question = "\n".join(get_questions())
        chat_history.add_user_message(
            f"Zapoznaj się z poniższą ofertą. Poniżej znajdziesz najważniejsze "
            f"informacje: {short_desc} i opis od sprzedającego: {desc} Odpowiedz na "
            f"poniższe pytania kupującego. Stosuj poniższy format:  \n"
            f"Pytanie: ... \n"
            f"Odpowiedź: ...  \n"
            f"Pytania od kupujacego: {question} "
        )
        chain = prompt | model

        ans = chain.invoke({"messages": chat_history.messages})

        chat_history.add_ai_message(ans)
        chat_history.add_user_message(
            "Translate the previous message from polish to english. Stick "
            "to the same format as in polish:\n"
            "\n"
            "Question: ... \n"
            "Answer: ... \n"
        )
        ans = chain.invoke({"messages": chat_history.messages})

        print(chat_history)
        print(ans)
        prompt = PromptTemplate(
            template="Parse those previous and anwers to json.\n"
            "{format_instructions}\n{q_a}\n",
            input_variables=["q_a"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | model
        output = chain.invoke({"q_a": ans.content})
        json = parser.invoke(output)
        print(json)
