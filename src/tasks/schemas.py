from typing import List

from pydantic import BaseModel


class LinksRequest(BaseModel):
    links: List[str]