"""
Enhanced Calculator Engine with advanced mathematical operations
"""

import math
from typing import Dict, Any, List, Union, Optional
from statistics import mean, median, mode, stdev, variance
from ...shared.base import BaseFeature, ToolResponse
from ...shared.types import MathOperation


class CalculatorEngine(BaseFeature):
    """Advanced calculator with scientific and statistical functions"""
    
    def __init__(self):
        super().__init__("calculator", "2.0.0")
        self.memory = {}  # Store calculation results
        self.history = []  # Keep calculation history
        self.max_history = 100
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of calculator tools"""
        return [
            {
                "name": "calculate",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "a": "First number or list of numbers",
                    "b": "Second number (optional for some operations)",
                    "operation": f"Operation: {', '.join(MathOperation.values())}"
                }
            },
            {
                "name": "calculate_advanced",
                "description": "Advanced calculations with expressions",
                "parameters": {
                    "expression": "Mathematical expression to evaluate",
                    "variables": "Optional dict of variables"
                }
            },
            {
                "name": "calculate_statistics",
                "description": "Statistical calculations on data",
                "parameters": {
                    "data": "List of numbers",
                    "operations": "List of operations: mean, median, mode, stdev, variance, sum, min, max"
                }
            },
            {
                "name": "calculate_financial",
                "description": "Financial calculations",
                "parameters": {
                    "type": "compound_interest, loan_payment, roi, present_value",
                    "params": "Parameters specific to calculation type"
                }
            }
        ]
    
    def calculate(self, a: Union[float, List[float]], b: Optional[float] = None, 
                  operation: str = "add") -> ToolResponse:
        """
        Perform mathematical calculations
        
        Args:
            a: First number or list of numbers
            b: Second number (optional for some operations)
            operation: Mathematical operation to perform
        """
        try:
            op = MathOperation(operation.lower())
            
            # Single number operations
            if op == MathOperation.SQRT:
                if isinstance(a, list):
                    result = [math.sqrt(x) for x in a if x >= 0]
                else:
                    if a < 0:
                        return ToolResponse(success=False, error="Cannot calculate square root of negative number")
                    result = math.sqrt(a)
            
            elif op == MathOperation.FACTORIAL:
                if isinstance(a, list):
                    result = [math.factorial(int(x)) for x in a if x >= 0 and x == int(x)]
                else:
                    if a < 0 or a != int(a):
                        return ToolResponse(success=False, error="Factorial requires non-negative integer")
                    result = math.factorial(int(a))
            
            elif op == MathOperation.AVERAGE:
                if isinstance(a, list):
                    result = mean(a)
                else:
                    return ToolResponse(success=False, error="Average requires a list of numbers")
            
            # Two number operations
            elif b is None:
                return ToolResponse(success=False, error=f"Operation {operation} requires two numbers")
            
            elif op == MathOperation.ADD:
                result = a + b
            elif op == MathOperation.SUBTRACT:
                result = a - b
            elif op == MathOperation.MULTIPLY:
                result = a * b
            elif op == MathOperation.DIVIDE:
                if b == 0:
                    return ToolResponse(success=False, error="Division by zero")
                result = a / b
            elif op == MathOperation.POWER:
                result = a ** b
            elif op == MathOperation.MODULO:
                if b == 0:
                    return ToolResponse(success=False, error="Modulo by zero")
                result = a % b
            elif op == MathOperation.PERCENTAGE:
                result = (a * b) / 100
            else:
                return ToolResponse(success=False, error=f"Unknown operation: {operation}")
            
            # Store in history
            self._add_to_history(operation, {"a": a, "b": b}, result)
            
            return ToolResponse(
                success=True,
                data={
                    "operation": operation,
                    "inputs": {"a": a, "b": b} if b is not None else {"a": a},
                    "result": result,
                    "expression": self._format_expression(a, b, operation, result)
                }
            )
            
        except Exception as e:
            return self.handle_error(f"calculate({operation})", e)
    
    def calculate_advanced(self, expression: str, variables: Optional[Dict[str, float]] = None) -> ToolResponse:
        """
        Evaluate mathematical expressions safely
        
        Args:
            expression: Mathematical expression (e.g., "2 * pi * r")
            variables: Optional dictionary of variables
        """
        try:
            # Safe evaluation context
            safe_dict = {
                'pi': math.pi,
                'e': math.e,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'abs': abs,
                'round': round,
                'floor': math.floor,
                'ceil': math.ceil,
                'pow': pow,
            }
            
            if variables:
                safe_dict.update(variables)
            
            # Simple expression validation (prevent dangerous operations)
            forbidden = ['import', 'exec', 'eval', '__', 'open', 'file', 'input', 'compile']
            for word in forbidden:
                if word in expression:
                    return ToolResponse(success=False, error=f"Forbidden keyword in expression: {word}")
            
            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            self._add_to_history("advanced", {"expression": expression, "variables": variables}, result)
            
            return ToolResponse(
                success=True,
                data={
                    "expression": expression,
                    "variables": variables,
                    "result": result,
                    "type": type(result).__name__
                }
            )
            
        except Exception as e:
            return self.handle_error(f"calculate_advanced('{expression}')", e)
    
    def calculate_statistics(self, data: List[float], operations: List[str]) -> ToolResponse:
        """
        Perform statistical calculations on data
        
        Args:
            data: List of numbers
            operations: List of statistical operations to perform
        """
        try:
            if not data:
                return ToolResponse(success=False, error="No data provided")
            
            results = {}
            
            for op in operations:
                op_lower = op.lower()
                
                if op_lower == "mean":
                    results["mean"] = mean(data)
                elif op_lower == "median":
                    results["median"] = median(data)
                elif op_lower == "mode":
                    try:
                        results["mode"] = mode(data)
                    except:
                        results["mode"] = "No unique mode"
                elif op_lower == "stdev":
                    if len(data) > 1:
                        results["stdev"] = stdev(data)
                    else:
                        results["stdev"] = "Need at least 2 data points"
                elif op_lower == "variance":
                    if len(data) > 1:
                        results["variance"] = variance(data)
                    else:
                        results["variance"] = "Need at least 2 data points"
                elif op_lower == "sum":
                    results["sum"] = sum(data)
                elif op_lower == "min":
                    results["min"] = min(data)
                elif op_lower == "max":
                    results["max"] = max(data)
                elif op_lower == "range":
                    results["range"] = max(data) - min(data)
                elif op_lower == "count":
                    results["count"] = len(data)
                else:
                    results[op] = f"Unknown operation: {op}"
            
            return ToolResponse(
                success=True,
                data={
                    "data_points": len(data),
                    "results": results,
                    "data_preview": data[:10] if len(data) > 10 else data
                }
            )
            
        except Exception as e:
            return self.handle_error("calculate_statistics", e)
    
    def calculate_financial(self, calc_type: str, params: Dict[str, float]) -> ToolResponse:
        """
        Perform financial calculations
        
        Args:
            calc_type: Type of financial calculation
            params: Parameters specific to the calculation
        """
        try:
            calc_type = calc_type.lower()
            
            if calc_type == "compound_interest":
                # A = P(1 + r/n)^(nt)
                principal = params.get("principal", 0)
                rate = params.get("rate", 0) / 100  # Convert percentage to decimal
                time = params.get("time", 0)
                compounds_per_year = params.get("compounds_per_year", 1)
                
                amount = principal * (1 + rate/compounds_per_year) ** (compounds_per_year * time)
                interest = amount - principal
                
                return ToolResponse(
                    success=True,
                    data={
                        "type": "compound_interest",
                        "principal": principal,
                        "rate": params.get("rate"),
                        "time": time,
                        "compounds_per_year": compounds_per_year,
                        "final_amount": round(amount, 2),
                        "interest_earned": round(interest, 2)
                    }
                )
            
            elif calc_type == "loan_payment":
                # Monthly payment formula
                principal = params.get("principal", 0)
                annual_rate = params.get("annual_rate", 0) / 100
                years = params.get("years", 0)
                
                monthly_rate = annual_rate / 12
                num_payments = years * 12
                
                if monthly_rate == 0:
                    payment = principal / num_payments
                else:
                    payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                             ((1 + monthly_rate)**num_payments - 1)
                
                total_paid = payment * num_payments
                total_interest = total_paid - principal
                
                return ToolResponse(
                    success=True,
                    data={
                        "type": "loan_payment",
                        "principal": principal,
                        "annual_rate": params.get("annual_rate"),
                        "years": years,
                        "monthly_payment": round(payment, 2),
                        "total_paid": round(total_paid, 2),
                        "total_interest": round(total_interest, 2)
                    }
                )
            
            elif calc_type == "roi":
                # Return on Investment
                initial = params.get("initial_investment", 0)
                final = params.get("final_value", 0)
                
                if initial == 0:
                    return ToolResponse(success=False, error="Initial investment cannot be zero")
                
                roi = ((final - initial) / initial) * 100
                profit = final - initial
                
                return ToolResponse(
                    success=True,
                    data={
                        "type": "roi",
                        "initial_investment": initial,
                        "final_value": final,
                        "profit": round(profit, 2),
                        "roi_percentage": round(roi, 2)
                    }
                )
            
            elif calc_type == "present_value":
                # PV = FV / (1 + r)^n
                future_value = params.get("future_value", 0)
                rate = params.get("rate", 0) / 100
                periods = params.get("periods", 0)
                
                present_value = future_value / ((1 + rate) ** periods)
                
                return ToolResponse(
                    success=True,
                    data={
                        "type": "present_value",
                        "future_value": future_value,
                        "rate": params.get("rate"),
                        "periods": periods,
                        "present_value": round(present_value, 2)
                    }
                )
            
            else:
                return ToolResponse(
                    success=False,
                    error=f"Unknown financial calculation type: {calc_type}"
                )
                
        except Exception as e:
            return self.handle_error(f"calculate_financial({calc_type})", e)
    
    def get_history(self, limit: int = 10) -> ToolResponse:
        """Get calculation history"""
        return ToolResponse(
            success=True,
            data={
                "history": self.history[-limit:],
                "total_calculations": len(self.history)
            }
        )
    
    def clear_history(self) -> ToolResponse:
        """Clear calculation history"""
        count = len(self.history)
        self.history.clear()
        return ToolResponse(
            success=True,
            data={"cleared": count}
        )
    
    def _add_to_history(self, operation: str, inputs: Dict, result: Any):
        """Add calculation to history"""
        from datetime import datetime
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "inputs": inputs,
            "result": result
        }
        
        self.history.append(entry)
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def _format_expression(self, a: Any, b: Any, operation: str, result: Any) -> str:
        """Format a calculation as a readable expression"""
        op_symbols = {
            "add": "+",
            "subtract": "-",
            "multiply": "×",
            "divide": "÷",
            "power": "^",
            "modulo": "%",
            "percentage": "% of"
        }
        
        if operation in ["sqrt", "factorial", "average"]:
            if operation == "sqrt":
                return f"√{a} = {result}"
            elif operation == "factorial":
                return f"{a}! = {result}"
            elif operation == "average":
                return f"avg({a}) = {result}"
        
        symbol = op_symbols.get(operation, operation)
        
        if b is not None:
            if operation == "percentage":
                return f"{b}% of {a} = {result}"
            return f"{a} {symbol} {b} = {result}"
        
        return f"{operation}({a}) = {result}"
