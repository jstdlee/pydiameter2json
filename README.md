# 🚀 PyDiameter2JSON

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](pyproject.toml)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)
[![uv](https://img.shields.io/badge/Managed-uv-purple.svg)](https://github.com/astral-sh/uv)

*Decode Diameter messages and AVPs (RFC 6733) from hex into JSON or a tree view*

</div>

## ✨ Features

<div align="center">

| 🎯 **Core Features** | 🛠 **Technical Excellence** |
|:-------------------|:-------------------------|
| 🔍 **Hex to JSON/tree** | ⚡ **Typer CLI** |
| 📊 **JSON Output** | 🎯 **Wire-order AVPs** |
| 🎨 **CLI Interface** | 🧪 **Comprehensive Tests** |
| 🔧 **AVP Extraction** | 📈 **Alpha** |
| 🌐 **Grouped and vendor AVPs** | 🪄 **Built on python-diameter** |

</div>

## 🌟 Why PyDiameter2JSON?

**PyDiameter2JSON** turns Diameter messages and AVPs (hex) into JSON or a tree. It uses [python-diameter](https://github.com/mensonen/diameter) to decode the AVPs. Only the AVPs are shown; the message header (command code, flags, identifiers) is not part of the output.

### 🎯 Perfect For
- 📡 **Telecom Network Analysis**
- 🔬 **Protocol Debugging**
- 📊 **Data Analytics**
- 🚀 **CI/CD Testing**
- 🎓 **Learning & Research**

## 🚀 Quick Start

### 📦 Installation

```bash
git clone https://github.com/jstdlee/pydiameter2json.git
cd pydiameter2json
uv sync
uv run pydiameter2json --help
```

### 🎯 Basic Usage

#### 🐍 **Library Usage**

The functions take `python-diameter` objects (not hex strings) and return Python
lists and dicts. Use `json.dumps` to get text.

```python
import json
from diameter.message import Avp, Message
from pydiameter2json.main import avp_to_json, message_to_json

# A whole message: list of AVP dicts, in wire order
message = Message.from_bytes(bytes.fromhex(message_hex), plain_msg=True)
print(json.dumps(message_to_json(message), indent=4))

# One AVP: a single dict
print(avp_to_json(Avp.from_bytes(bytes.fromhex(avp_hex))))
```

Use `plain_msg=True`. Without it, python-diameter reorders the AVPs and adds
default AVPs (for example `Auth-Application-Id`) that are not in the message.

Each AVP dict has `avp_hex`, `code`, `length`, `name`, `value` and `value_hex`.
`value` is a number, text, an ISO 8601 UTC string (Time AVPs), an address string
(Address AVPs), hex (undecodable or non-text OctetString), or a list of AVP dicts
(Grouped AVPs).

#### 🖥️ **CLI**

The hex is a command argument. It may start with `0x` and may contain spaces.
Use `$(cat file)` to read from a file.

```bash
pydiameter2json message2json "0100006c80000118..."          # tree (default)
pydiameter2json message2json --format json "0100006c..."    # JSON
pydiameter2json avp2json "0000010840000031..."
pydiameter2json message2json "$(cat message.hex)"
pydiameter2json --help
```

The CLI exits with code 1 and a message on stderr for bad hex, truncated input,
a wrong length field or an unsupported Diameter version.

### 🔍 **Real Examples**

#### 📊 **Device-Watchdog-Request**
```bash
pydiameter2json message2json "0100006c8000011800000000a3734495a375f3e40000010840000031707473642d362e6d6f64756c652d322e54504550545330312e74616977616e6d6f62696c652e636f6d000000000001284000001874616977616e6d6f62696c652e636f6d000001164000000c5416d236"

# Output: (code, length), name, value, value_hex
# ├── (264, 49), Origin-Host, ptsd-6.module-2.TPEPTS01.taiwanmobile.com, 707473...
# ├── (296, 24), Origin-Realm, taiwanmobile.com, 74616977...
# └── (278, 12), Origin-State-Id, 1410781750, 5416d236
```

#### 🔧 **Individual AVP**
```bash
# Origin-Host AVP parsing
pydiameter2json avp2json "0000010840000031707473642d362e6d6f64756c652d322e54504550545330312e74616977616e6d6f62696c652e636f6d000000"

# Output:
# └── (264, 49), Origin-Host, ptsd-6.module-2.TPEPTS01.taiwanmobile.com, 707473...
```

## 🧪 **Testing**

<div align="center">

### ✅ **Test Suite**

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run --with pytest-cov pytest tests/ --cov=pydiameter2json

# Run specific test
uv run pytest tests/test_message_parser.py::TestDiameterMessageParsing::test_origin_host_avp -v
```

### 🎯 **Test Coverage**
- ✅ **Gx Interface Messages**
- ✅ **AVP Extraction**
- ✅ **Error Handling**
- ✅ **Edge Cases**

</div>

## 📚 **API Reference**

### `message_to_json(message: Message) → list[dict]`
AVPs of a `diameter.message.Message`, in wire order. Grouped AVPs are nested.

### `avp_to_json(avp: Avp) → dict`
One AVP (recursive for Grouped AVPs).

### `json_to_tree(data) → list[str]`
Tree lines for the output of the two functions above. `print_json_tree(data)` prints them.

## 🛠️ **Development**

### 🏗️ **Setup Development Environment**

```bash
# Clone repository
git clone https://github.com/jstdlee/pydiameter2json.git
cd pydiameter2json

# Install with dev dependencies
uv sync --dev
```

### 🧪 **Running Tests**

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=pydiameter2json
```

## 🎯 **Contributing**

We love contributions! Here's how to get started:

### 🚀 **Quick Contribution Guide**

1. **🍴 Fork the repository**
2. **🌿 Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **🧪 Add tests**
   ```bash
   uv run pytest tests/
   ```
4. **📤 Push and create PR**

### 📋 **Contributing Guidelines**
- ✅ **Tests required** for new features
- ✅ **Documentation** updates for API changes
- ✅ **Conventional commits** preferred

## 📄 **License**

**MIT License** (see `pyproject.toml`).

## 🌟 **Support**

<div align="center">

### 📞 **Get Help**

- 🐛 **Report bugs**: [GitHub Issues](https://github.com/jstdlee/pydiameter2json/issues)
- 💡 **Feature requests**: [GitHub Discussions](https://github.com/jstdlee/pydiameter2json/discussions)
- 📧 **Email**: [Issues Page](https://github.com/jstdlee/pydiameter2json/issues)

### 🔗 **Links**

| 🎯 **Resource** | 🔗 **Link** |
|:----------------|:------------|
| 📖 **Documentation** | [GitHub Wiki](https://github.com/jstdlee/pydiameter2json/wiki) |
| 🏠 **Homepage** | [GitHub Repository](https://github.com/jstdlee/pydiameter2json) |
| 🐛 **Issue Tracker** | [GitHub Issues](https://github.com/jstdlee/pydiameter2json/issues) |
| 📊 **Releases** | [GitHub Releases](https://github.com/jstdlee/pydiameter2json/releases) |

</div>

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

*Made with ❤️ by the PyDiameter2JSON team*

</div>
