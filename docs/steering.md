# Steering Document: UI Module (MCP-UI)

## Vision
A portable, "lego block" MCP module that acts as a Backend-for-Frontend (BFF). It serves abstract UI definitions to clients, managing state and layout resolution without enforcing specific rendering technologies.

## Core Architecture: Engine vs Interface

### 1. The Engine (The "Brain")
- **Location**: `src/ui_module/engine/`
- **Responsibility**: Pure Python logic.
    - Loads View definitions (YAML).
    - Manages Session State (In-Memory/Interface implementation).
    - Resolves Routes.
    - Compiles Views into Render Trees.
- **Constraints**:
    - ZERO dependencies on MCP.
    - Must be testable in isolation.
    - No HTML generation (returns JSON/dict abstract trees).

### 2. The Interface (The "Hands")
- **Location**: `src/ui_module/server.py`
- **Responsibility**: MCP Server exposure.
    - Maps MCP Tools to Engine calls.
    - Handles Request/Response envelopes.
- **Constraints**:
    - No business logic.
    - Strict validation of inputs.

## Tool Surface
The MCP API is the **Public API**.
- `ui.get_capabilities`: Discovery.
- `ui.render_view`: Main render loop.
- `ui.handle_event`: Event processing loop.

## Authoring & Security
- Authoring tools (create/edit views) are **DANGEROUS**.
- They must be:
    - Disabled by default.
    - Enabled only if `UI_ENABLE_AUTHORING_TOOLS=1`.
    - Restricted to the `config_dir`.

## Data Flow
Client (MCP Client) -> `ui.render_view` -> MCP Server -> Engine -> Router -> View Resolver -> (Jinja2 + Context) -> JSON Layout -> Client
