from enum import Enum, auto
from typing import Optional, Union, Literal

from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser


class BoolWithNA(Enum):
    true = "true"
    false = "false"
    no_information = "no_information"


class StructuredAnswers(BaseModel):
    mortgage_register: BoolWithNA = Field(
        description="Is there a land and mortgage register established?"
    )
    lands_regulated: BoolWithNA = Field(description="Are the land plots regulated?")
    rent_administration_fee: Union[float, Literal["no_information"]] = Field(
        description="How much is the rent (administrative fee)?", gt=0
    )
    two_sided: BoolWithNA = Field(description="Is the apartment two-sided?")
