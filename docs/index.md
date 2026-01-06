# UI Module (MCP-UI)

A Server-Driven UI framework exposed as an MCP server. This module allows agents and clients to request abstract UI layouts and handle user interactions through a standardized protocol.

## Features
- **Server-Driven UI**: Define views in YAML, serve them as JSON.
- **MCP-Native**: All interactions happen via MCP Tools.
- **State Management**: Built-in session state handling.
- **Engine/Interface Split**: Clean separation of logic and protocol.

## Usage
1. Install:
   ```bash
   pip install -e .
   ```
2. Run:
   ```bash
   ui-module run --config-dir ./config
   ```

## Configuration
See [STEERING.md](STEERING.md) for architectural details.
Place view definitions in `config/views/*.yaml`.
