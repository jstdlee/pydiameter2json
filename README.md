# pydiameter2json

A Python library to convert Diameter protocol messages to JSON.

## Features

- Convert Diameter protocol messages into JSON format.
- Built on top of `diameter-codec` and `python-diameter` libraries.
- Command-line interface powered by `typer`.

## Installation

Install the library using pip:

```bash
pip install pydiameter2json
```

## Usage

### Library Usage

```python
from pydiameter2json import message_to_json, avp_to_json

# Example Diameter message
diameter_message = b"..."
json_output = message_to_json(diameter_message)
diameter_avp = b"..."
json_output = message_to_json(diameter_avp)

```

### Command-Line Interface

For more details, use the `--help` flag:

```bash
pydiameter2json --help
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push the branch.
4. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Links

- [Homepage](https://github.com/jstdlee/pydiameter2json)
- [Documentation](https://github.com/jstdlee/pydiameter2json#readme)
- [Source Code](https://github.com/jstdlee/pydiameter2json)
- [Issue Tracker](https://github.com/jstdlee/pydiameter2json/issues)
