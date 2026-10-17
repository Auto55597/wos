# Workspace OS (WOS) Core Engine

Workspace OS is a lean, data-driven middleware core that translates incoming
technology and device payloads into a consistent universal context. External
mapping rules let developers adapt integrations without hardcoding each
source-specific transformation into the kernel.

## Vision & Philosophy

### The problem

Technology platforms and APIs are often locked in siloed “walled gardens”.
Developers must repeatedly write integration boilerplate to connect systems
that describe similar data in incompatible ways.

### The vision

WOS aims to be a seamless, flexible bridge between technology ecosystems and
users: a universal, data-driven middleware core that normalizes incoming data
through external rules.

### Core philosophy

- **Lean Micro-Core (Less is More):** keep the kernel focused and modular.
- **Zero-Hardcoding:** load integration mappings from external configuration.
- **Heavy-Lifting for Developers:** make common data normalization declarative
  rather than repetitive integration code.
- **Open Community Growth:** provide an open foundation that developers can
  adapt and extend.

## Quickstart

Use Python 3.10 or newer. From the repository root, install dependencies and
point WOS to the included example rules:

```powershell
python -m pip install -r requirements.txt
$env:WOS_MAPPING_FILE = "configs\example_rules.json"
python main.py
```

The API listens on `http://127.0.0.1:8000`. Send a payload to
`POST /api/v1/ingest`; select the mapping with `mapping_rule_id` in the query
string or the `X-Mapping-Rule` header. The included configuration has one rule,
so it is selected automatically if no identifier is provided. Check
`GET /health` for service status.

Example request:

```json
{
  "source_id": "sensor-17",
  "payload_type": "json",
  "data": {
    "device": { "name": "north wing" },
    "reading": { "temperature_c": 21.5 }
  }
}
```

## Mapping features

Rules are loaded from the JSON file specified by `WOS_MAPPING_FILE`. Each rule
defines a normalized `source`, `action`, and `parameters` map. A parameter can
use a string path or an object with a `path` and optional transformations:

- **Dot notation:** traverse nested input dictionaries, such as
  `reading.temperature_c`.
- **Type casts:** `str`, `int`, `float`, or `bool`.
- **Formatting:** `uppercase`, `lowercase`, or a Python format specifier such
  as `.2f`.
- **Arithmetic:** apply numeric `multiply` and `add` values.
- **Units:** append a string with `unit`.

Transformations are applied in this order: cast, arithmetic, formatting, then
unit suffix. A transformation example is included in
[`configs/example_rules.json`](configs/example_rules.json).

## Architecture

- `schema.py` — strict Pydantic models for raw payloads and unified contexts.
- `config_loader.py` — validates and loads external JSON mapping rules.
- `engine.py` — applies mappings and transformations with error metadata.
- `core.py` — FastAPI ingest and health endpoints.
- `main.py` — Rich startup banner and Uvicorn entry point.

## License

WOS is distributed under the GNU General Public License, version 3.0
(GPL-3.0). See [LICENSE](LICENSE) for the full license text.
