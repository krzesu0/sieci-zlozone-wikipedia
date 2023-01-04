from requests import Session

_DEFAULT_SESSION = Session()

def _get_continue(data: dict, name: str):
    if "continue" in data and name in data["continue"]:
        return data["continue"][name]
    return False