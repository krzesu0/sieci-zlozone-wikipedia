from dataclasses import dataclass
from dateutil import parser
from datetime import datetime
from app.constants import get_urls_url

from . import _DEFAULT_SESSION, _get_continue

from typing import List, Type, Optional

@dataclass(repr=False, order=True)
class Revision:
    timestamp: datetime
    oldid: str

    @classmethod
    def from_json(cls: Type["Revision"], json: dict):
        return cls(parser.parse(json["timestamp"]), json["revid"])

    def __repr__(self):
        return f"Revision(time={self.timestamp:%d.%m.%y %X}, id={self.id})"
        
    def get_subpages_names(self) -> List[str]:
        links = []
        data = _DEFAULT_SESSION.get(get_urls_url(self.oldid)).json()
        self.page_id = list(data["query"]["pages"].keys())[0]
        _continue = _get_continue(data, "plcontinue")

        if "missing" in data["query"]["pages"][self.page_id]:
            return links
        try:
            for link_data in data["query"]["pages"][self.page_id]["links"]:
                links.append(link_data["title"])
        except KeyError:
            return links

        while _continue:
            data = _DEFAULT_SESSION.get(get_urls_url(self.oldid, _continue=_continue)).json()
            _continue = _get_continue(data, "plcontinue")
            for link_data in data["query"]["pages"][self.page_id]["links"]:
                links.append(link_data["title"])
        return links

    @property
    def id(self):
        return self.oldid