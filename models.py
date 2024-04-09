import requests
from typing import Union, TypedDict

class ApiResponse(TypedDict):
    query: str
    answer: str
    source_text: str


class ApiError(TypedDict):
    error: Union[str, requests.exceptions.RequestException]