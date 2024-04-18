from enum import Enum
from typing import Union, Literal, List

from pydantic import BaseModel, Field


class BoolWithNA(Enum):
    true = "true"
    false = "false"
    no_information = "no_information"

    @classmethod
    def get_values(cls) -> List[str]:
        return [key.value for key in cls]


class StructuredAnswers(BaseModel):
    mortgage_register: BoolWithNA = Field(
        description="Is there a land and mortgage register established?"
    )
    lands_regulated: BoolWithNA = Field(description="Are the land plots regulated?")
    rent_administration_fee: Union[float, Literal[None]] = Field(
        description="How much is the rent (administrative fee)?",
        gt=0,
    )
    two_sided: BoolWithNA = Field(description="Is the apartment two-sided?")
