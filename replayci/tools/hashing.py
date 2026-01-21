import hashlib
import json
from typing import Any, Dict

def compute_args_hash(args: Dict[str, Any]) -> str:
    """
    Compute a stable SHA256 hash of the arguments dictionary.
    
    Args:
        args: Dictionary of arguments
        
    Returns:
        Hex digest of the SHA256 hash of the canonical JSON representation.
    """
    # Canonical JSON: sorted keys, no extra whitespace
    canonical = json.dumps(args, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
