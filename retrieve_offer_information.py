import json
import re
from typing import Tuple

from dotenv import load_dotenv
from langchain.memory import ChatMessageHistory
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_openai import ChatOpenAI
from sqlalchemy import text

from database import get_engine
from json_parser import StructuredAnswers


load_dotenv()


def list_offers():
    with get_engine().connect() as cur:
        result = cur.execute(
            text("SELECT distinct url from apartments"),
        )
        return [row[0] for row in result.fetchall()]


def get_questions():
    with open("questions.json", "r") as file:
        return json.load(file)["questions"]


def information_already_exist(link):
    with get_engine().connect() as cur:
        result = cur.execute(
            text("SELECT * from retrieved_information where url=:url"),
            parameters={"url": link},
        )
        return bool(result.rowcount)


class OfferInformationRetriever:
    real_estate_agent_prompt = (
        "Jesteś doradcą w agencji nieruchomości, który potrafi określić "
        "czy dana oferta spełnia konkretne, sprecyzowane wymagania "
        "klienta. Wiesz, że skrót od księga wieczysta to KW lub kw. "
        "Odpowiadasz na pytania na podstawie opisu, więc jeśli nie wiesz "
        "jaka jest odpowiedź, powiedz, że nie ma danej informacji."
    )
    # ENG: You work in a real estate agency, you are concise,
    # KW is a shortcut for "ksiega wieczysta" (mortgage mortgage_register),
    # if you don't know then don't make up

    answer_question_template = (
        "Zapoznaj się z poniższą ofertą. Poniżej znajdziesz "
        "najważniejsze "
        "informacje: {short_desc} i opis od sprzedającego: {desc} Odpowiedz na "
        "poniższe pytania kupującego. Stosuj poniższy format:  \n"
        "Pytanie: ... \n"
        "Odpowiedź: ...  \n"
        "Pytania od kupujacego: {question} "
    )
    # ENG: read the offer, here are two different descriptions,
    # follow a specific format, answer the questions

    translate_prompt = (
        "Translate the previous message from polish to english. "
        "Stick "
        "to the same format as in polish:\n"
        "\n"
        "Question: ... \n"
        "Answer: ... \n"
    )

    def __init__(self, url, model=ChatOpenAI()):
        self.url = url
        self.chat_history = ChatMessageHistory()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.real_estate_agent_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        self.model = model
        self.chain = prompt | self.model

        self.parser = JsonOutputParser(pydantic_object=StructuredAnswers)

    def get_offer_info(self) -> Tuple[str, str]:
        with get_engine().connect() as cur:
            result = cur.execute(
                text("SELECT table_dump, description from apartments where url=:url"),
                {"url": self.url},
            )
            short_desc, desc = result.fetchone()
            return short_desc, desc

    def get_answers_natural_lang_pl(self):

        short_desc, desc = self.get_offer_info()
        question = "\n".join(get_questions())
        self.chat_history.add_user_message(
            self.answer_question_template.format(
                short_desc=short_desc, desc=desc, question=question
            )
        )

        ans = self.chain.invoke({"messages": self.chat_history.messages})
        return ans

    def extract_json_from_answer(self, ans):
        self.chat_history.add_ai_message(ans)
        self.chat_history.add_user_message(self.translate_prompt)
        ans_eng = self.chain.invoke({"messages": self.chat_history.messages})

        # from now we are forgetting the history which includes sentences in polish
        # in order to not confuse the model
        parsing_prompt = PromptTemplate(
            template="Parse those questions and answers to json.\n"
            "{format_instructions}\n{q_a}\n",
            input_variables=["q_a"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        parsing_chain = parsing_prompt | self.model
        output = parsing_chain.invoke({"q_a": ans_eng.content})
        json = self.parser.invoke(output)
        return json


def insert_into_retrieved_information(
    url,
    long_answer,
    mortgage_register,
    lands_regulated,
    rent_administration_fee,
    two_sided,
):
    with get_engine().connect() as cur:
        sql = text(
            """INSERT INTO retrieved_information(url, long_answer, 
            mortgage_register, lands_regulated, rent_administration_fee, two_sided) 
            VALUES(:url, :long_answer, :mortgage_register, :lands_regulated, 
            :rent_administration_fee, :two_sided);"""
        )
        fee = rent_administration_fee
        if not isinstance(fee, (float, int)):
            fee = None if not fee else float(re.sub(r"[^\d\.]", "", str(fee)))
        cur.execute(
            sql,
            {
                "url": url,
                "long_answer": long_answer,
                "mortgage_register": mortgage_register,
                "lands_regulated": lands_regulated,
                "rent_administration_fee": fee,
                "two_sided": two_sided,
            },
        )
        cur.commit()


def main():
    for url in list_offers():
        if information_already_exist(url):
            print(f"Skipping {url} as it is already processed")
            continue
        tool = OfferInformationRetriever(url)
        long_answer = tool.get_answers_natural_lang_pl()
        long_answer_content = long_answer.content
        json_answer = tool.extract_json_from_answer(long_answer)
        insert_into_retrieved_information(
            url=url,
            long_answer=long_answer_content,
            mortgage_register=json_answer["mortgage_register"],
            lands_regulated=json_answer["lands_regulated"],
            rent_administration_fee=json_answer["rent_administration_fee"],
            two_sided=json_answer["two_sided"],
        )


if __name__ == "__main__":
    # TODO: add this as a button in streamlit
    main()
