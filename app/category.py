from datetime import datetime
from dataclasses import dataclass
from dateutil import parser

from typing import Optional, List, Type, Set

from . import _DEFAULT_SESSION, _get_continue
from .constants import get_categories_url, get_page_categories, CM_TYPE
from .page import Page as RevisionPage

def check_if_in_category(title: str, category: List[str]) -> bool:
    data = _DEFAULT_SESSION.get(get_page_categories(title)).json()
    id = list(data["query"]["pages"].keys())[0]
    try:
        for cat in data["query"]["pages"][id]["categories"]:
            if cat["title"] in category:
                return True
    except KeyError:
        pass
    return False

@dataclass(repr=False, order=True, frozen=True)
class Page:
    pageid: int
    title: str
    timestamp: datetime

    @classmethod
    def from_json(cls: Type["Page"], data: dict):
        return cls(int(data["pageid"]), data["title"], parser.parse(data["timestamp"]))

    def __hash__(self) -> int:
        return self.pageid

    def to_page(self):
        return RevisionPage(self.title)


class Category:
    name: str
    timestamp: Optional[datetime]
    pages: Set[Page]
    subcats: List["Category"]
    page_id: Optional[int]

    def __init__(self, name: str, main_category: str, timestamp=None) -> None:
        self.name = name
        self.main_category = main_category
        self.timestamp = timestamp
        self.pages = self._get_pages()
        self.subcats = self._get_subcats()

    @classmethod
    def from_json(cls: Type["Category"], data: dict, main_category):
        return cls(data["title"], main_category, parser.parse(data["timestamp"]))

        
    def _get_pages(self) -> List[Page]:
        pages = set()
        data = _DEFAULT_SESSION.get(get_categories_url(self.name, cmtype=CM_TYPE.PAGE)).json()
        _continue = _get_continue(data, "cmcontinue")

        for category_data in data["query"]["categorymembers"]:
            pages.add(Page.from_json(category_data))

        while _continue:
            data = _DEFAULT_SESSION.get(get_categories_url(self.name, _continue=_continue, cmtype=CM_TYPE.PAGE)).json()
            _continue = _get_continue(data, "cmcontinue")
            for category_data in data["query"]["categorymembers"]:
                pages.add(Page.from_json(category_data))
        return pages

    def _get_subcats(self) -> List["Category"]:
        subcat = []
        data = _DEFAULT_SESSION.get(get_categories_url(self.name, cmtype=CM_TYPE.SUBCAT)).json()
        _continue = _get_continue(data, "cmcontinue")

        for category_data in data["query"]["categorymembers"]:
            if self.name == self.main_category:
                subcat.append(Category.from_json(category_data, self.main_category))
            elif check_if_in_category(category_data["title"], self.main_category):
                subcat.append(Category.from_json(category_data, self.main_category))

        while _continue:
            data = _DEFAULT_SESSION.get(get_categories_url(self.name, _continue=_continue, cmtype=CM_TYPE.SUBCAT)).json()
            _continue = _get_continue(data, "cmcontinue")
            for category_data in data["query"]["categorymembers"]:
                if self.name == self.main_category:
                    subcat.append(Category.from_json(category_data, self.main_category))
                elif check_if_in_category(category_data["title"], self.main_category):
                    subcat.append(Category.from_json(category_data, self.main_category))
        return subcat
    
    def find_categories(self, timestamp: datetime) -> Set[Page]:
        ret = set()
        for page in self.pages:
            if page.timestamp <= timestamp:
                ret.add(page)
        for subcat in self.subcats:
            ret.update(subcat.find_categories(timestamp))
        return ret

