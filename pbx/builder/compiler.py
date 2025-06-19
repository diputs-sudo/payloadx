# pbx/builder/compiler.py

import time
from pathlib import Path 

from .loader import load_blocks
from .modifiers import apply_modifiers 
from .utils import validate_config, get_extension_for_language

def build(cfg):
    # step 1: Validate 
    errors = validate_config(cfg)
    if errors:
        raise ValueError(f"Config validation failed: {errors}")
    
    #step 2: Load relevant blocks
    blocks = load_blocks(cfg)

    #step 3: Apply modifiers 
    modified_blocks = apply_modifiers(blocks, cfg)

    #step : Combine into final payload
    final_code = "\n".join(modified_blocks)

    #step 5: Output 
    language = cfg.get("language", "python")
    ext = get_extension_for_language(language)
    filename = f"{cfg['payload_type']}_{int(time.time())}.{ext}"
    output_path = Path("./output") / filename
    output_path.parent.mkdir(parent=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(final_code)

    return output_path