# 🌱 GrowCalculator - FastAPI Web Application

The most accurate plant value calculator for Roblox Grow a Garden, built with FastAPI, Tailwind CSS, and reverse-engineered from actual game source code to achieve 96-100% accuracy.

## 🚀 Features

- **🎯 Highly Accurate Calculations** - 96-100% accuracy based on exact game source code
- **💰 Bulk Value Calculations** - Calculate values for multiple plants at once
- **⚖️ Expected Weight Ranges** - Shows realistic weight expectations for each plant
- **🧬 Interactive Mutation Selection** - Easy-to-use interface for 72+ mutations
- **⚡ Real-time Calculations** - Instant updates as you modify inputs
- **📱 Mobile-Responsive Design** - Works perfectly on all devices
- **🎨 Modern UI/UX** - Beautiful, intuitive interface with Tailwind CSS
- **🔧 RESTful API** - Clean API endpoints for integration

## 📊 Accuracy & Data

### **🎯 Proven Accuracy**
- **High-value plants (500k+)**: 100% accurate
- **Medium-value plants (1k-100k)**: 98-99% accurate  
- **Low-value plants (<1k)**: 96-97% accurate (±1-2 Sheckles)

### **📋 Complete Game Data**
- **176 plants** with exact base weights, prices, and rarities
- **72 mutations** with precise value multipliers
- **4 variants** (Normal, Silver, Gold, Rainbow) with correct multipliers
- **Additive mutation formula** exactly matching game behavior

## 📁 Project Structure

```
Website/
├── main.py                 # FastAPI application entry point
├── start.py               # Development server startup script
├── requirements.txt       # Python dependencies
├── models/               # Pydantic models
│   ├── __init__.py
│   └── calculator.py     # Request/response models with validation
├── routes/               # API routes
│   ├── __init__.py
│   ├── calculator.py     # HTML page routes
│   └── api.py           # RESTful API endpoints
├── services/            # Business logic
│   ├── __init__.py
│   └── calculator_service.py  # Core calculator logic
├── templates/           # Jinja2 HTML templates
│   ├── base.html       # Base template with navigation
│   ├── index.html      # Main calculator page
│   ├── mutation_calculator.html  # Dedicated mutation calculator
│   └── about.html      # About page with project information
├── static/             # Static assets
│   ├── js/
│   │   └── main.js     # JavaScript functionality
│   └── css/
│       └── style.css   # Custom CSS styles
└── data/               # JSON data files extracted from game
    ├── plants.json     # Complete plant database
    ├── variants.json   # Variant multipliers
    └── mutations.json  # Mutation value multipliers
```

## 🛠️ Installation & Setup

1. **Clone or navigate to the Website directory:**
   ```bash
   cd Website
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server:**
   ```bash
   python start.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

4. **Open your browser and visit:**
   ```
   http://localhost:8000
   ```

## 🎯 API Endpoints

### **Main Pages**
- `GET /` - Main calculator page with plant selection and calculations
- `GET /mutation-calculator` - Dedicated mutation combination calculator
- `GET /about` - About page with accuracy information and project details

### **API Endpoints**
- `POST /api/calculate` - Calculate plant value with all parameters
- `GET /api/plants` - Get list of all available plants
- `GET /api/variants` - Get all variants with multipliers
- `GET /api/mutations` - Get all mutations with value multipliers
- `GET /api/plant/{plant_name}` - Get specific plant data
- `GET /api/weight-range/{plant_name}` - Get expected weight range for plant
- `POST /api/mutation-multiplier` - Calculate mutation multiplier only

### **Example API Request**
```json
POST /api/calculate
{
  "plant_name": "Carrot",
  "variant": "Gold",
  "weight": 0.5,
  "mutations": ["Tranquil", "Celestial"],
  "plant_amount": 10
}
```

### **Example API Response**
```json
{
  "plant_name": "Carrot",
  "variant": "Gold", 
  "weight": 0.5,
  "mutations": ["Tranquil", "Celestial"],
  "mutation_multiplier": 39.0,
  "final_value": 25565,
  "plant_amount": 10,
  "total_value": 255650
}
```

## 📊 Key Features

### **🧮 Plant Value Calculator**
- Select from 176 plants with auto-complete
- Choose growth variants (Normal=1x, Silver=5x, Gold=20x, Rainbow=50x)
- Apply up to 72 environmental mutations
- Bulk calculations for multiple plants
- Expected weight ranges for realistic planning
- Real-time value updates

### **🧬 Mutation Calculator**
- Interactive mutation selection interface
- Real-time multiplier calculations using exact game formula
- Predefined optimal combinations
- Visual mutation breakdown
- Export and share combinations

### **📱 Responsive Design**
- Mobile-first design approach
- Touch-friendly interface for all devices
- Optimized loading and smooth animations
- Accessibility features

## 🔧 Technical Implementation

### **🏗️ Architecture**
- **FastAPI** - Modern, fast web framework with automatic API documentation
- **Pydantic** - Runtime data validation and serialization
- **Jinja2** - Server-side template rendering
- **Tailwind CSS** - Utility-first CSS framework for rapid UI development
- **Vanilla JavaScript** - Lightweight, no external dependencies

### **📊 Data Management**
- JSON-based data storage extracted from game source code
- Service layer pattern for clean separation of concerns
- Type-safe models with comprehensive validation
- Automatic input sanitization and error handling

### **⚡ Performance**
- Async/await support throughout the application
- Efficient data loading with minimal memory footprint
- Optimized JavaScript for smooth user interactions
- CDN-delivered CSS framework for fast loading

## 🎨 Design Philosophy

The website follows these core principles:

- **🎯 Accuracy First**: Every calculation matches the game exactly
- **👤 User-Centered**: Intuitive interface requiring no learning curve
- **⚡ Performance**: Sub-100ms response times for all calculations
- **♿ Accessibility**: Works for all users, devices, and assistive technologies
- **🔧 Maintainability**: Clean, well-documented code following best practices

## 🧪 Testing & Validation

### **🔬 Accuracy Testing**
- Tested against hundreds of in-game plant combinations
- Verified calculation formulas against game source code
- Continuous validation with community feedback
- Documented edge cases and their handling

### **🎯 Test Cases**
- **Silver Poseidon Plant (3.74kg)**: 100% accuracy (509,421 Sheckles)
- **Blueberry (0.25kg)**: 96.8% accuracy (30 vs 31 Sheckles)
- **High-value mutations**: Perfect formula matching
- **Bulk calculations**: Accurate multiplication across all scenarios

## 🚀 Deployment

### **Development**
```bash
python start.py
# Runs on http://127.0.0.1:8000
```

### **Production with Gunicorn**
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### **Environment Variables**
```bash
# Optional configuration
HOST=127.0.0.1
PORT=8000
RELOAD=true
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Code Style**: Follow PEP 8 guidelines
2. **Architecture**: Maintain separation of concerns
3. **Type Safety**: Add type hints to all functions
4. **Testing**: Verify accuracy against in-game values
5. **Documentation**: Update relevant documentation

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with hot reload
python start.py

# Format code
black .

# Type checking
mypy .
```

## 📋 Changelog

### **v2.0.0** (Current)
- ✅ Bulk value calculations for multiple plants
- ✅ Expected weight ranges for all plants
- ✅ Replaced codes page with comprehensive about page
- ✅ Improved accuracy information (96-100% documented)
- ✅ Enhanced UI with better mobile support

### **v1.0.0**
- ✅ Initial FastAPI website with accurate calculations
- ✅ Mutation calculator with real-time updates
- ✅ Mobile-responsive design
- ✅ RESTful API endpoints

## 📝 License & Disclaimer

This project is created for educational and informational purposes by the community. We are not affiliated with Do Big Studios or the official "Grow a Garden" game. All trademarks and game content belong to their respective owners.

**Accuracy Guarantee**: While we strive for perfect accuracy and achieve 96-100% in testing, plant values in the actual game may be affected by hidden mechanics or game updates.

---

**Made with ❤️ for the Roblox Grow a Garden community**

**🌱 Ready to optimize your garden? [Start calculating now!](http://localhost:8000)**