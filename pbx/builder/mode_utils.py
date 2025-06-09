# builder/mode_utils.py

import random
import string
import uuid
from typing import Dict, Any


# === Build Mode Logic ===

def is_distribution_mode(spec: Dict[str, str]) -> bool:
    """
    Return True if build mode is 'release' and intended for obfuscation/distribution.
    """
    return spec.get("build_mode", "debug") == "release" or spec.get("mode_tag") == "distribution"


# === Filename Obfuscation ===

def get_obfuscated_name(length: int = 8) -> str:
    """
    Generate a randomized filename using hex or alphanum.
    """
    return uuid.uuid4().hex[:length]


def get_descriptive_name(spec: Dict[str, str]) -> str:
    """
    Generate a filename based on the build spec (human-readable).
    Example: revshell_macos_xor_obf.py
    """
    parts = [
        spec.get("payload_type", "payload"),
        spec.get("platform", "all"),
        "_".join(sorted(spec.get("stealth", "").split(","))) if "stealth" in spec else "",
    ]
    return "_".join(filter(None, parts))


# === Metadata Sanitizer ===

def strip_metadata(meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove sensitive or identifying keys from block metadata for stealth.
    """
    sensitive_keys = ["tags", "returns", "args", "author", "description"]
    return {k: v for k, v in meta.items() if k not in sensitive_keys}


# === Build Context Wrapper ===

def get_filename(spec: Dict[str, str], extension="py") -> str:
    """
    Return either an obfuscated or descriptive filename based on mode.
    """
    if is_distribution_mode(spec):
        return f"{get_obfuscated_name()}.{extension}"
    return f"{get_descriptive_name(spec)}.{extension}"
