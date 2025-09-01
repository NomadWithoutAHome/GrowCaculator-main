# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

GrowCaculator is a modern plant value calculator for Roblox "Grow a Garden" with 96-100% accuracy. It's a FastAPI-based web application that calculates plant values based on weight, variant, and mutations. The application also includes recipe generation, plant traits analysis, and result sharing functionality.

## Architecture

### Core Structure
- **FastAPI Application**: Dual entry points for local development (`main.py`) and Vercel serverless deployment (`api/index.py`)
- **MVC Pattern**: Clear separation between models, routes, and services
- **Service Layer**: Business logic encapsulated in dedicated service classes
- **Data-Driven**: All plant, variant, mutation, recipe, and trait data stored in JSON files in `data/`

### Key Components

**Models (`models/`):**
- `calculator.py`: Pydantic models for requests/responses, including plant data, calculations, and shared results

**Routes (`routes/`):**
- `calculator.py`: HTML template routes and API endpoints for sharing/traits/recipes
- `api.py`: Core REST API endpoints for plant calculations

**Services (`services/`):**
- `calculator_service.py`: Core plant value calculation logic
- `traits_service.py`: Plant trait management and search
- `recipe_service.py`: Recipe generation and ingredient resolution
- `shared_results_service.py`: Result sharing functionality
- `vercel_shared_results_service.py`: Vercel-specific shared results implementation
- `discord_webhook_service.py`: Discord integration for notifications

**Data Files (`data/`):**
- `plants.json`: Plant base weights, prices, and rarity values
- `variants.json`: Variant multipliers (Normal, Shiny, etc.)
- `mutations.json`: Mutation value multipliers
- `recipes.json`: Cooking recipes with ingredient requirements
- `traits.json`: Plant trait mappings
- `cooking.json`: Ingredient category mappings
- `shopseeds.json`: List of shop-available seeds

### Calculation Logic
The core value calculation follows this formula:
1. Base value = plant_base_price × (weight / plant_base_weight)
2. Apply variant multiplier
3. Apply mutation multipliers (multiplicative)
4. Final result rounded to integer

### Deployment Architecture
- **Local Development**: Run via `start.py` using Uvicorn
- **Vercel Serverless**: Entry point at `api/index.py` with static file handling
- **Templates**: Jinja2 templates in `templates/` for web UI
- **Static Assets**: CSS and plant images in `static/`

## Development Commands

### Start Development Server
```bash
python start.py
```
Runs the app locally on `127.0.0.1:8000` with auto-reload enabled

### Alternative Development Start
```bash
python main.py
```
Runs via main.py entry point (binds to `0.0.0.0:8000`)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Test Local Vercel Compatibility
```bash
npm test
# Runs: python test_vercel_local.py
```

## Key Development Patterns

### Service Initialization
Services are initialized as global singletons and load data from JSON files in `data/` directory during startup. Services handle URL decoding for plant names (e.g., "Blue%20Lollipop" → "Blue Lollipop").

### Error Handling
- Comprehensive logging throughout all services
- Graceful handling of missing data files
- HTTPException responses with detailed error messages
- Startup/shutdown event handlers for cleanup

### Data Loading Strategy
Services use multiple path resolution strategies to find data files:
1. Local development: `Path(__file__).parent.parent / "data"`
2. Vercel serverless: `Path("/var/task/data")`
3. Fallback: `Path("data")`

### Recipe System
Recipes use category-based ingredient resolution:
- Fixed categories (from `cooking.json`): Bread, Meat, Leafy, etc.
- Trait-based categories: Fruit, Vegetable, Sweet (from `traits.json`)
- Special categories: HerbalBase (non-toxic flowers), Filling (vegetables + meat)

### Shared Results
- Results expire after 24 hours
- Stored with unique share IDs
- Discord webhook notifications on result sharing
- Automatic cleanup on startup/shutdown

## Common Issues

### Data File Loading
If services fail to load data, check:
1. Data files exist in `data/` directory
2. JSON files are valid (no syntax errors)
3. Required fields exist in data structures

### URL Encoding
Plant names in URLs must be properly decoded using `urllib.parse.unquote()` before database lookups.

### Vercel Deployment
The `vercel.json` configuration routes all requests through `api/index.py`. Static files are served via custom route handlers rather than direct mounting.

## API Endpoints

### Core Calculator
- `POST /api/calculate` - Calculate plant values
- `GET /api/plants` - List all plants
- `GET /api/variants` - List all variants
- `GET /api/mutations` - List all mutations

### Traits
- `GET /api/traits/plant/{plant_name}` - Get plant traits
- `GET /api/traits/search/{trait}` - Find plants by trait
- `GET /api/traits/all` - Get all plant traits

### Recipes
- `GET /api/recipes/all` - List all recipes
- `GET /api/recipes/{recipe_name}` - Get specific recipe
- `GET /api/recipes/generate/{recipe_name}` - Generate random recipe

### Sharing
- `POST /api/share` - Create shared result
- `GET /api/share/{share_id}` - Retrieve shared result
