from enum import Enum, auto
from typing import Optional, Union, Literal

from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser


class BoolWithNA(Enum):
    true = "true"
    false = "false"
    no_information = "no_information"


class StructuredAnswers(BaseModel):
    register: BoolWithNA = Field(
        description="Is there a land and mortgage register established?"
    )
    lands_regulated: BoolWithNA = Field(description="Are the land plots regulated?")
    administration_fee: Union[float, Literal["no_information"]] = Field(
        description="What is the administration fee?", gt=0
    )
    two_sided: BoolWithNA = Field(description="Is the apartment two-sided?")


parser = JsonOutputParser(pydantic_object=StructuredAnswers)
