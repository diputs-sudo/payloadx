# PayloadBuilder X (PBX) v0.0.2

**PayloadBuilder X (PBX)** is an experimental modular payload generator designed for flexibility and future extensibility. This is a **very early beta release**, mainly for testing and internal development.

---

## Project Status: Alpha / Experimental

This project is in **pre-release**. Many features are unimplemented or incomplete. Use it only for testing and experimentation.

---

## What Works (v0.0.2)

- Basic payload block loading from `/builder/blocks/`
- Standardized block naming convention
- `METADATA` structure for each block
- Early-stage `compiler.py` logic
- Preliminary support for plugin `.pbx` files (non-functional)

---

## Directory Structure

```
/builder/
├── compiler.py    # Core build logic
├── loader.py      # Block discovery and loading
├── blocks/
│ ├── base/
│ │ └── reverse_shell.macos.python.base.short.py.py
│ ├── stealth/
│ │ └── obfuscate_vars.all.python.stealth.default.py
│ ├── persistence/
│ │ └── mac_launch_agent.macos.python.persistence.default.py
```

---

## Block File Format

Each payload block file must follow this format:

`<category><name><platform><language><variant>.py`

Each must define a `METADATA` dictionary:

```python
METADATA = {
    "name": "example",
    "platform": "win",
    "language": "py",
    "variant": "default",
    "author": "YourName",
    "description": "Example base block.",
    "version": "0.0.1"
}
```

---

## Known Limitations (v0.0.2)

- **Single-block only**: Pipelines with multiple stages (e.g., base → stealth → addon) are not yet supported.
- **Platform-specific only**: Currently limited to hardcoded platforms (e.g., Windows); cross-platform behavior is unimplemented.
- **No validation**: Block metadata is assumed to be correct; no schema enforcement or conflict detection.
- **Plugins inactive**: `.pbx` plugin files are recognized but not executed.
- **No output formatting**: Payloads are raw code snippets with no wrapping, obfuscation, or encoding.
- **No dependency handling**: Blocks do not yet declare or resolve external requirements.

---

## Roadmap

PBX is in early development. Here are the upcoming goals and improvements planned for future versions:

### v0.0.2 (Current)
- [x] Single-block compilation
- [x] Basic block structure and metadata
- [x] Initial `compiler.py` and `loader.py` prototypes

### Planned for v0.0.3+
- [ ] Support for multi-stage build pipelines (e.g., base → stealth → addon)
- [ ] Cross-platform payload generation support
- [ ] Plugin execution system for `.pbx` files
- [ ] Output formatting and payload wrapping
- [ ] Block dependency resolution
- [ ] Obfuscation modules and modifier system
- [ ] Metadata validation and schema checking
- [ ] Logging and error reporting
- [ ] Test suite (unit + integration)
- [ ] Developer documentation and templates

---

## Contributing

Contributions are welcome and encouraged!

### How to Contribute:
- Submit new payload blocks using the proper naming and metadata format
- Report issues or suggest features in the issue tracker
- Review and improve core files (`compiler.py`, `loader.py`, etc.)

> PBX is under active development. Expect frequent changes to structure and API.

---

## Acknowledgments

Thanks to early testers and contributors experimenting with the concept and structure. Your feedback shapes PBX’s direction.

---

## License

This project is licensed under a **MIT-Based License with PBX Security Conditions**.  
Use of this software is subject to specific [Conditions of Use](./LICENSE) regarding lawful, ethical, and responsible security practices.  

See the [LICENSE](./LICENSE) file for full details.

---

## Conditions of Use

PayloadBuilder X is intended solely for lawful, ethical, and responsible security research and educational purposes.

By using this software, you agree to comply with the [Conditions of Use](./LICENSE) defined in the project's license.

Unauthorized use of this software for malicious purposes — including the development or deployment of malware, unauthorized system access, or any illegal activity — is strictly prohibited.

Violation of these terms may result in legal consequences and immediate termination of your license to use this software.

---

*PBX is intended for **educational and research purposes only**. Use responsibly and only in controlled environments.*

