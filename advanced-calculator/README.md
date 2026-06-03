# 🧮 Advanced Calculator Pro - Premium Edition

**A professional-grade scientific calculator with beautiful glassmorphism UI, advanced mathematical functions, and persistent SQLite database.**

## ✨ Features

### 🎨 Premium UI
- **Glassmorphism Design**: Modern frosted glass effect with backdrop blur
- **Dark Theme Support**: Eye-friendly dark mode
- **Smooth Animations**: Buttery smooth transitions and interactions
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Real-time Display**: Instant calculation feedback

### 🧮 Scientific Functions
- **Trigonometric**: sin, cos, tan, asin, acos, atan
- **Logarithmic**: sqrt, log (base 10), ln (natural log), exp
- **Constants**: π (pi), e (Euler's number)
- **Advanced**: Power operations, modulo, factorial

### 🔬 Advanced Tools
- **Quadratic Solver**: Solve ax² + bx + c = 0 with complex roots support
- **Fibonacci Generator**: Generate Fibonacci sequences
- **Factorial Calculator**: Calculate n! up to 170
- **Prime Factorization**: Find prime factors of any number

### 📊 Data Management
- **SQLite Database**: All calculations automatically saved
- **Search History**: Find past calculations instantly
- **Statistics**: Track usage patterns and most used operations
- **Persistent Storage**: Data survives app restarts

### ⌨️ Keyboard Support
- Full keyboard integration
- Shortcuts: Enter (calculate), Backspace (delete), Escape (clear)

---

## 🚀 Quick Start (Termux)

### Installation
```bash
# Navigate to the directory
cd advanced-calculator

# Install dependencies
pip install -r requirements.txt
```

### Run the Server
```bash
python app.py
```

### Access the App
```bash
# Open in browser
termux-open http://localhost:5000
```

---

## 📁 Project Structure

```
advanced-calculator/
├── app.py                  # Flask web server
├── calculator_engine.py    # Core math engine
├── database.py            # SQLite database management
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Premium UI template
├── static/
│   ├── css/
│   │   └── style.css     # Advanced styling with glassmorphism
│   └── js/
│       └── app.js        # Frontend logic with keyboard support
└── calculator_history.db  # Auto-generated database
```

---

## 🎯 API Endpoints

### Basic Calculation
```
POST /api/calculate
{"expression": "2 + 3 * 4"}
```

### Get History
```
GET /api/history?limit=100
GET /api/history/search?q=sqrt
```

### Advanced Functions
```
POST /api/advanced/quadratic      {a, b, c}
POST /api/advanced/fibonacci      {n}
POST /api/advanced/factorial      {n}
POST /api/advanced/prime-factors  {n}
```

### Statistics
```
GET /api/statistics
```

---

## 💡 Examples

### Basic Calculations
```
2 + 3 × 4           → 14
10 ÷ 2 - 3          → 2
2 ^ 8               → 256
```

### Scientific Functions
```
sin(π/2)            → 1
cos(0)              → 1
sqrt(16)            → 4
log(100)            → 2
```

### Advanced Operations
```
Quadratic: 1x² - 5x + 6 = 0     → x₁ = 2, x₂ = 3
Factorial: 5!                   → 120
Fibonacci: 10 terms             → 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
Prime Factors: 24               → 2 × 2 × 2 × 3
```

---

## 🔧 Customization

### Change Port
Edit `app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Change Theme Colors
Edit `static/css/style.css` `:root` variables:
```css
--primary: #6366f1;
--secondary: #ec4899;
```

---

## 📱 Features by Device

| Feature | Desktop | Tablet | Mobile |
|---------|---------|--------|--------|
| Full Calculator | ✅ | ✅ | ✅ |
| Advanced Tools | ✅ | ✅ | ✅ |
| History Search | ✅ | ✅ | ✅ |
| Keyboard Support | ✅ | ❌ | ❌ |
| Touch Optimized | ❌ | ✅ | ✅ |

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
python -c "from app import app; app.run(port=5001)"
```

### Module Not Found
```bash
pip install --upgrade -r requirements.txt
```

### Database Issues
```bash
# Reset database
rm calculator_history.db
python app.py
```

---

## 📊 Database Schema

### History Table
```sql
id (INTEGER PRIMARY KEY)
expression (TEXT)
result (TEXT)
operation_type (TEXT)
timestamp (DATETIME)
status (TEXT)
```

---

## 🎓 Technology Stack

- **Backend**: Python 3, Flask
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Database**: SQLite3
- **Styling**: Modern CSS with Glassmorphism
- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Outfit)

---

## 📈 Performance

- ⚡ High-precision calculations (50 decimal places)
- 🚀 Instant UI response
- 💾 Efficient database queries
- 📦 Lightweight (~150KB total)

---

## 📄 License

MIT License - Free to use and modify

---

## 🙌 Credits

Built with ❤️ for developers  
Power by Python, Flask & Modern Web Technologies

---

**Version**: 2.0.0 Premium Edition  
**Last Updated**: 2026  
**Status**: ✅ Production Ready
