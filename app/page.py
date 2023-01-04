from dataclasses import dataclass
from datetime import datetime
from app.revision import Revision
from app.constants import get_revisions_url, get_urls_url

from . import _DEFAULT_SESSION, _get_continue

from typing import List, Optional

@dataclass
class Page:
    name: str
    revisions: Optional[List[Revision]]
    page_id: Optional[int]

    def __init__(self, name: str):
        self.name = name
        self.page_id = None
        self.revisions = None
        

    def _get_revisions(self) -> List[Revision]:
        revisions = []
        data = _DEFAULT_SESSION.get(get_revisions_url(self.name)).json()
        _continue = _get_continue(data, "rvcontinue")

        self.page_id = list(data["query"]["pages"].keys())[0]
        for revision_data in data["query"]["pages"][self.page_id]["revisions"]:
            revisions.append(Revision.from_json(revision_data))

        while _continue:
            data = _DEFAULT_SESSION.get(get_revisions_url(self.name, _continue=_continue)).json()
            _continue = _get_continue(data, "rvcontinue")
            for revision_data in data["query"]["pages"][self.page_id]["revisions"]:
                revisions.append(Revision.from_json(revision_data))
        return revisions

    def find_revision(self, timestamp: datetime) -> Optional[Revision]:
        if self.revisions == None:
            self.revisions = self._get_revisions()
        
        for revision in self.revisions:
            if revision.timestamp <= timestamp:
                return revision
        return None
