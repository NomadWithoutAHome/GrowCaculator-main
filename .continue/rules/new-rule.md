# Project Guide: GrowCalculator

## Project Overview
GrowCalculator is a modern plant value calculator for Roblox Grow a Garden. It is built using FastAPI, Jinja2 templates, and various services for handling data and user interactions.

**Key Technologies:**
- Python
- FastAPI
- Jinja2 Templates
- Uvicorn
- SQLAlchemy

**High-Level Architecture:**
The project consists of multiple components:
- **API**: Handles HTTP requests and responses.
- **Services**: Manages business logic, data storage, and shared results.
- **Templates**: Render HTML pages using Jinja2.
- **Static Files**: Serve CSS and JavaScript files.

## Getting Started
### Prerequisites
- Python 3.8 or higher
- Uvicorn

### Installation Instructions
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/GrowCalculator.git
   cd GrowCalculator
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up environment variables (e.g., `.env` file).

### Basic Usage Examples
To start the development server:
```sh
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000` in your browser.

### Running Tests
Run tests using PyTest:
```sh
pytest
```

## Project Structure
- **api/**: Contains API endpoints.
  - **index.py**: Main API routes.
- **calculator/**: Handles calculator logic.
  - **service.py**: Business logic for calculations.
- **routes/**: Defines application routes.
  - **api.py**: Routes related to the API.
  - **calculator.py**: Routes related to the calculator.
- **services/**: Manages business logic and data storage.
  - **shared_results_service.py**: Handles shared results.
- **static/**: Stores static files (CSS, JS).
  - **css/style.css**
  - **js/main.js**
- **templates/**: Jinja2 templates for HTML pages.
  - **about.html**
  - **base.html**
  - **index.html**
  - **mutation_calculator.html**
  - **recipes.html**
  - **share.html**
  - **share_recipe.html**
  - **traits.html**
- **data/**: Stores data files.
  - **backup/**: Backup of various data files.

## Development Workflow
### Coding Standards
- Use Python type hints for better code readability and maintenance.
- Follow PEP 8 style guidelines.

### Testing Approach
- Write unit tests for individual components using PyTest.
- Ensure test coverage is at least 90%.

### Build and Deployment Process
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

2. Build the application (if needed):
   ```sh
   # Placeholder for build commands if any
   ```

3. Run the application:
   ```sh
   uvicorn main:app --reload
   ```

### Contribution Guidelines
- Fork the repository.
- Create a new branch for your feature or bug fix.
- Commit your changes with descriptive commit messages.
- Push your changes to your forked repository.
- Submit a pull request.

## Key Concepts
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- **Jinja2**: A popular templating engine that makes it easy to generate dynamic HTML pages.

## Common Tasks
### Creating a New API Endpoint
1. Create a new file in the `routes/api/` directory.
2. Define routes and their corresponding logic.

### Adding a New Service
1. Create a new Python file in the `services/` directory.
2. Implement the business logic and data storage methods.

## Troubleshooting
- **Common Issues**:
  - Ensure all dependencies are installed correctly.
  - Check environment variables for any misconfigurations.
  - Verify that the database is accessible and properly configured.

- **Debugging Tips**:
  - Use logging to track down issues.
  - Run tests to ensure individual components work as expected.

## References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
