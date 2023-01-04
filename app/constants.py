from enum import Enum
from urllib.parse import urlencode
from typing import Dict, Any, Optional

BASE_URL = "https://pl.wikipedia.org/w/api.php?"

# https://pl.wikipedia.org/w/api.php?action=parse&format=json&prop=links&oldid=57705342
# https://pl.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Kategoria:Informatyka&cmlimit=max

GET_REVISIONS_PARAMS = {
    "action":"query",
    "prop":"revisions",
    "rvprop":"timestamp|ids",
    "rvlimit":"max",
}

GET_URLS_PARAMS = {
    "action": "query",
    "prop": "links",
    "plnamespace": 0,
    "pllimit": "max",
}

GET_CATEGORIES_PARAMS = {
    "action": "query",
    "prop": "categories",
    "cllimit": "max",
}

GET_CATEGORIES_MEMBERS = {
    "action":"query",
    "list":"categorymembers",
    "cmlimit":"max",
    "cmprop":"ids|title|timestamp",
}

DEFAULT_HEADERS = {}
DEFAULT_PARAMS = {"maxlag": 10, "format": "json"}

class CM_TYPE(Enum):
    PAGE = "page"
    SUBCAT = "subcat"


def get_revisions_url(name: str, _continue: Optional[str] = None, add_param: Optional[Dict[str, Any]] = {}):
    params = DEFAULT_PARAMS.copy()
    params.update(**GET_REVISIONS_PARAMS, **add_param, titles=name)
    if _continue:
        params.update(rvcontinue=_continue)
    print(f"Generating revisions url for: {name}")
    return BASE_URL + urlencode(params)

def get_urls_url(revids: str, _continue: Optional[str] = None, add_param: Optional[Dict[str, Any]] = {}):
    params = DEFAULT_PARAMS.copy()
    params.update(**GET_URLS_PARAMS, **add_param, revids=revids)
    if _continue:
        params.update(plcontinue=_continue)
    print(f"Generating urls url for: {revids}")
    return BASE_URL + urlencode(params)

def get_categories_url(name: str, _continue: Optional[str] = None, cmtype: CM_TYPE = CM_TYPE.PAGE, add_param: Optional[Dict[str, Any]] = {}):
    params = DEFAULT_PARAMS.copy()
    params.update(**GET_CATEGORIES_MEMBERS, **add_param, cmtitle=name, cmtype=cmtype.value)
    if _continue:
        params.update(cmcontinue=_continue)
    print(f"Generating categories url for: {name}, type: {cmtype.value}")
    return BASE_URL + urlencode(params)

def get_page_categories(name: str, add_param: Optional[Dict[str, Any]] = {}):
    params = DEFAULT_PARAMS.copy()
    params.update(**GET_CATEGORIES_PARAMS, **add_param, titles=name)
    print(f"Generating list categories url for: {name}")
    return BASE_URL + urlencode(params)
