# Dashr AI Coding Instructions

## Project Overview

Dashr is a Python-based platformer game engine with level editor capabilities. The architecture follows a client-server separation pattern with shared common components.

## Core Architecture

### Directory Structure

- **`client/`** - Main game client (Pygame-based)
- **`server/`** - Game server (currently minimal)
- **`common/`** - Shared level/tile data structures

### Key Entry Points

- Main game: `python3 -m client.src.main`
- Install via script: `client/scripts/install.sh` (creates virtual env, launcher)
- User data stored at: `~/dashr-data/` (separate from installation)

## Development Workflow

### Running & Testing

```bash
# From project root
python3 -m client.src.main

# Debug mode (F3 key toggles FPS display)
# Escape key exits application
```

### Dependencies

- Core: `pygame`, `Pillow`, `numpy` (see `client/src/requirements.txt`)
- No build system - pure Python modules
- Virtual environment recommended (`client/scripts/install.sh` handles this)

### Installation System

The project uses a sophisticated bash installer that:

- Creates `~/dashr/` for installation, `~/dashr-data/` for user data
- Sets up virtual environment and system launcher
- Handles Linux desktop integration (`~/.local/share/applications/`)

## Asset System Patterns

### Font Loading (`client/src/asset/font/`)

Fonts use bitmap sheets with JSON metadata:

```json
{
  "size": 8,
  "chars": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz..."
}
```

- `font.png` contains character grid
- `FontLoader` splits into individual `FontCharacter` objects
- Automatic horizontal trimming preserves vertical spacing

### Tile System (`client/src/asset/tile/`)

Tiles use directory structure with JSON configuration:

```
tiles/default/
├── tileset.json             # Tile properties (solid, kill, boost, etc.)
└── tiles/                   # Individual PNG files
    ├── tile_green_full.png
    └── tile_boost_red.png
```

- Each PNG becomes an `AssetTile` with computed hash
- Properties loaded from `tileset.json` define game behavior

### Rendering Pipeline (`client/src/renderer/`)

- Text: PIL → Pygame conversion with per-pixel recoloring
- Tiles: PIL → Pygame with scaling support
- Custom spacing: 1px between chars, 3px after punctuation/spaces

## Game Logic Patterns

### Input Management (`client/src/input/manager.py`)

Thread-based input system with callback registration:

```python
input_manager.on_key_press(pygame.K_F3, lambda key: toggle_debug())
input_manager.on_key_hold(pygame.K_SPACE, handle_continuous_input)
```

- Separate press/release/hold events
- Thread-safe with proper cleanup

### Level Data (`common/level/`)

Shared data structures between client/server:

- `Level` class manages tile collections with position-based lookup
- `Tile` class includes game properties (solid, kill, boost, spawn, etc.)
- Position-based coordinate system for tile placement

### Settings System (`client/src/settings/`)

Two-tier configuration:

- `default.json` (currently empty) for defaults
- `~/dashr/user_settings.json` for user overrides
- Automatic merging with user settings taking precedence

## Development Conventions

### Path Handling

Always use `os.path.join()` for cross-platform compatibility:

```python
font_dir = os.path.join("client", "assets", "font")
```

### Asset Loading

Assets loaded at startup, not dynamically:

- Fonts and tiles loaded in `main.py` initialization
- Directory-based loading with metadata files

### Error Handling

Asset loaders use descriptive `FileNotFoundError` and `ValueError` messages:

```python
if not os.path.isfile(tileset_json_path):
    raise FileNotFoundError(f"tileset.json not found in directory: {directory}")
```

### Window Management

Pygame setup includes Linux-specific optimizations:

```python
os.environ["SDL_VIDEO_X11_WMCLASS"] = "Dashr"  # For window class
os.environ["SDL_VIDEO_WINDOW_POS"] = "SDL_WINDOWPOS_CENTERED"
```

## Integration Points

### Client-Server Boundary

- `common/` package provides shared data structures
- Client handles all rendering and input
- Server directory exists but minimal implementation

### External Dependencies

- Installation scripts handle system integration
- Desktop file template with path substitution
- User data separation allows updates without data loss

When working with Dashr, prioritize understanding the asset loading system and the client-server architecture boundaries. The input management system is sophisticated - use its callback patterns rather than polling. Always test asset loading paths and remember the installation system's separation of code vs. user data.
