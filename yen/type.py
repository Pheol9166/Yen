from typing import TypedDict, Union
    

JSON = dict[str, Union[None, int, str, bool, list, dict]]

class Config(TypedDict):
    Yen: dict[str, str]

class QuoteType(TypedDict):
    quote: str
    person: str

class QuoteJSON(TypedDict):
    quotes: list[QuoteType]

class DateType(TypedDict):
    name: str
    date: str

class DateJSON():
    user_id: list[DateType]
    
