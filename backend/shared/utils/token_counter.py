"""
Generic token estimation utility.
"""

import json
from typing import Any, Dict, Union


def estimate_tokens(content: Union[str, Dict[str, Any], list]) -> int:
    """
    Estimate token count for a text string, dictionary, or list.
    Rough approximation: ~4 characters per token.
    """
    if isinstance(content, (dict, list)):
        text = json.dumps(content)
    else:
        text = str(content)
    return max(1, len(text) // 4)
