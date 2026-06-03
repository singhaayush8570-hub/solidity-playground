import math
import re
from decimal import Decimal, getcontext
from typing import Union, Tuple

getcontext().prec = 50

class CalculatorEngine:
    """Advanced calculator engine with scientific operations"""
    
    def __init__(self):
        self.last_result = 0
        self.variables = {}
        self.operation_count = {}
    
    def evaluate(self, expression: str) -> Tuple[str, str]:
        try:
            expression = expression.strip()
            expression = self._replace_functions(expression)
            op_type = self._detect_operation_type(expression)
            result = self._safe_eval(expression)
            self.last_result = result
            self.operation_count[op_type] = self.operation_count.get(op_type, 0) + 1
            formatted_result = self._format_result(result)
            return formatted_result, op_type
            
        except ZeroDivisionError:
            return "Error: Division by zero", "error"
        except ValueError as e:
            return f"Error: Invalid input - {str(e)}", "error"
        except Exception as e:
            return f"Error: {str(e)}", "error"
    
    def _replace_functions(self, expr: str) -> str:
        replacements = {
            r'\bsin\b': 'math.sin',
            r'\bcos\b': 'math.cos',
            r'\btan\b': 'math.tan',
            r'\basin\b': 'math.asin',
            r'\bacos\b': 'math.acos',
            r'\batan\b': 'math.atan',
            r'\bsqrt\b': 'math.sqrt',
            r'\blog\b': 'math.log10',
            r'\bln\b': 'math.log',
            r'\bexp\b': 'math.exp',
            r'\bceil\b': 'math.ceil',
            r'\bfloor\b': 'math.floor',
            r'\bfabs\b': 'math.fabs',
            r'\bpi\b': 'math.pi',
            r'\be\b': 'math.e',
        }
        for pattern, replacement in replacements.items():
            expr = re.sub(pattern, replacement, expr)
        return expr
    
    def _safe_eval(self, expr: str) -> Union[float, complex]:
        safe_dict = {
            'math': math,
            '__builtins__': {},
            'pi': math.pi,
            'e': math.e,
        }
        result = eval(expr, safe_dict)
        return result
    
    def _detect_operation_type(self, expr: str) -> str:
        if any(func in expr for func in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']):
            return 'trigonometric'
        elif any(func in expr for func in ['sqrt', 'log', 'ln', 'exp']):
            return 'logarithmic'
        elif any(op in expr for op in ['**', '^']):
            return 'power'
        elif '/' in expr or '%' in expr:
            return 'division'
        elif '+' in expr or '-' in expr:
            return 'addition_subtraction'
        elif '*' in expr:
            return 'multiplication'
        else:
            return 'general'
    
    def _format_result(self, result: Union[float, complex]) -> str:
        if isinstance(result, complex):
            return f"{result.real:.10g} + {result.imag:.10g}i"
        if isinstance(result, float):
            if result == int(result):
                return str(int(result))
            else:
                return f"{result:.15g}"
        return str(result)
    
    def solve_quadratic(self, a: float, b: float, c: float) -> dict:
        if a == 0:
            raise ValueError("Coefficient 'a' cannot be zero")
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            real_part = -b / (2*a)
            imag_part = math.sqrt(-discriminant) / (2*a)
            return {
                'x1': f"{real_part:.6f} + {imag_part:.6f}i",
                'x2': f"{real_part:.6f} - {imag_part:.6f}i",
                'discriminant': discriminant,
                'type': 'complex'
            }
        else:
            x1 = (-b + math.sqrt(discriminant)) / (2*a)
            x2 = (-b - math.sqrt(discriminant)) / (2*a)
            return {
                'x1': f"{x1:.6f}",
                'x2': f"{x2:.6f}",
                'discriminant': discriminant,
                'type': 'real'
            }
    
    def factorial(self, n: int) -> int:
        if not isinstance(n, int) or n < 0:
            raise ValueError("Factorial requires non-negative integer")
        return math.factorial(n)
    
    def fibonacci(self, n: int) -> list:
        if n <= 0:
            raise ValueError("n must be positive")
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        return fib[:n]
    
    def prime_factors(self, n: int) -> list:
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors
    
    def combination(self, n: int, r: int) -> int:
        if n < 0 or r < 0 or r > n:
            raise ValueError("Invalid combination parameters")
        return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))
    
    def permutation(self, n: int, r: int) -> int:
        if n < 0 or r < 0 or r > n:
            raise ValueError("Invalid permutation parameters")
        return math.factorial(n) // math.factorial(n - r)
    
    def gcd(self, a: int, b: int) -> int:
        return math.gcd(a, b)
    
    def lcm(self, a: int, b: int) -> int:
        return abs(a * b) // math.gcd(a, b)
