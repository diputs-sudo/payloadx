# builder/loader.py
"""
Dynamic block loader for PayloadBuilder X
Supports filename format:
    name.platform.language.category[.variant].py or .pbx
Each block must expose:
    METADATA (optional)
    generate(...) – required function
"""

import importlib.util
from pathlib import Path
from typing import Dict, Optional, Callable
from types import ModuleType

from builder.utils import pbx_decrypt

BLOCKS_DIR = Path(__file__).parent / "blocks"
BLOCK_REGISTRY: Dict[str, Dict] = {}

def _parse_filename(path: Path) -> Optional[Dict]:
    parts = path.stem.split(".")
    if len(parts) < 4:
        return None
    name, platform, language, category, *variant = parts
    return {
        "name": name.lower(),
        "platform": platform.lower(),
        "language": language.lower(),
        "category": category.lower(),
        "variant": variant[0].lower() if variant else "default",
        "path": path,
    }

def _load_module_from_code(code: str, module_name: str) -> Optional[ModuleType]:
    import types
    mod = types.ModuleType(module_name)
    try:
        exec(code, mod.__dict__)
        return mod
    except Exception as e:
        print(f"[!] Failed to exec .pbx block {module_name}: {e}")
        return None

def discover_blocks() -> None:
    """Scan builder/blocks/ and register all valid .py/.pbx blocks."""
    for path in BLOCKS_DIR.rglob("*"):
        if path.name == "__init__.py":
            continue
        if not path.suffix in {".py", ".pbx"}:
            continue

        meta = _parse_filename(path)
        if not meta:
            continue

        key = f"{meta['name']}.{meta['platform']}.{meta['language']}.{meta['variant']}"

        # === .py blocks ===
        if path.suffix == ".py":
            try:
                spec = importlib.util.spec_from_file_location(key, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception as e:
                print(f"[!] Failed to load .py block {key}: {e}")
                continue

        # === .pbx blocks ===
        elif path.suffix == ".pbx":
            try:
                decrypted_code = pbx_decrypt.decrypt_pbx(str(path))
                module = _load_module_from_code(decrypted_code, key)
                if not module:
                    continue
            except Exception as e:
                print(f"[!] Failed to decrypt/load .pbx block {key}: {e}")
                continue

        # === Extract and validate generate() ===
        generate_fn = getattr(module, "generate", None)
        if not callable(generate_fn):
            print(f"[!] Block {key} missing generate() function")
            continue

        BLOCK_REGISTRY[key] = {
            "metadata": getattr(module, "METADATA", {}),
            "generate": generate_fn,
            "filename_meta": meta,
            "module": module,
        }

def get_block(name: str, platform: str = "all", language: str = "all", variant: str = "default") -> Optional[Callable]:
    candidates = [
        f"{name}.{platform}.{language}.{variant}",
        f"{name}.{platform}.{language}.default",
        f"{name}.{platform}.all.{variant}",
        f"{name}.all.{language}.{variant}",
        f"{name}.all.all.{variant}",
        f"{name}.all.all.default",
    ]
    for key in candidates:
        if key in BLOCK_REGISTRY:
            return BLOCK_REGISTRY[key]["generate"]
    return None
