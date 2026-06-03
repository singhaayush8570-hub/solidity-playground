from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from calculator_engine import CalculatorEngine
from database import CalculatorDatabase
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

calc_engine = CalculatorEngine()
db = CalculatorDatabase()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        expression = data.get('expression', '').strip()
        
        if not expression:
            return jsonify({'error': 'Empty expression'}), 400
        
        result, op_type = calc_engine.evaluate(expression)
        db.add_history(expression, result, op_type, 'success' if not 'Error' in result else 'error')
        
        return jsonify({
            'expression': expression,
            'result': result,
            'operation_type': op_type,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        limit = request.args.get('limit', 100, type=int)
        operation_type = request.args.get('type', None)
        history = db.get_history(limit, operation_type)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/search', methods=['GET'])
def search_history():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        results = db.search_history(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/<int:item_id>', methods=['DELETE'])
def delete_history_item(item_id):
    try:
        db.delete_history_item(item_id)
        return jsonify({'message': 'Deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/clear', methods=['DELETE'])
def clear_history():
    try:
        db.clear_history()
        return jsonify({'message': 'History cleared successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        stats = db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced/quadratic', methods=['POST'])
def quadratic_solver():
    try:
        data = request.json
        a = float(data.get('a'))
        b = float(data.get('b'))
        c = float(data.get('c'))
        result = calc_engine.solve_quadratic(a, b, c)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced/fibonacci', methods=['POST'])
def fibonacci():
    try:
        data = request.json
        n = int(data.get('n'))
        result = calc_engine.fibonacci(n)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced/factorial', methods=['POST'])
def factorial():
    try:
        data = request.json
        n = int(data.get('n'))
        result = calc_engine.factorial(n)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced/prime-factors', methods=['POST'])
def prime_factors():
    try:
        data = request.json
        n = int(data.get('n'))
        result = calc_engine.prime_factors(n)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("🚀 Advanced Calculator Pro Starting...")
    print("🌐 Access at: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
