import json
from typing import Optional, Dict, Any, Union

def parse_reply_markup(markup: Optional[Union[Dict[str, Any], str]]) -> Optional[Dict[str, Any]]:
    if not markup:
        return None
    if isinstance(markup, str):
        try:
            return json.loads(markup)
        except Exception:
            return None
    if isinstance(markup, dict):
        return markup
    return None
