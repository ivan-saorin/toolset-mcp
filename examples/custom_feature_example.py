"""
Example: Creating a custom feature for Atlas Toolset MCP

This example shows how to create a weather feature following the architecture pattern.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from src.remote_mcp.shared.base import BaseFeature, ToolResponse


class WeatherEngine(BaseFeature):
    """Example weather feature following the architecture pattern"""
    
    def __init__(self):
        super().__init__("weather", "1.0.0")
        
        # Mock weather data for example
        self.mock_data = {
            "Bologna": {
                "temp": 22,
                "condition": "Sunny",
                "humidity": 65,
                "wind_speed": 10
            },
            "Milano": {
                "temp": 20,
                "condition": "Cloudy",
                "humidity": 70,
                "wind_speed": 15
            },
            "Roma": {
                "temp": 25,
                "condition": "Clear",
                "humidity": 60,
                "wind_speed": 8
            }
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of weather tools"""
        return [
            {
                "name": "weather_current",
                "description": "Get current weather for a city",
                "parameters": {
                    "city": "City name",
                    "units": "Temperature units (celsius, fahrenheit)"
                }
            },
            {
                "name": "weather_forecast",
                "description": "Get weather forecast",
                "parameters": {
                    "city": "City name",
                    "days": "Number of days (1-7)"
                }
            }
        ]
    
    def weather_current(self, city: str, units: str = "celsius") -> ToolResponse:
        """
        Get current weather for a city
        
        Args:
            city: City name
            units: Temperature units (celsius or fahrenheit)
        """
        try:
            # Validate input
            error = self.validate_input(
                {"city": city},
                required=["city"]
            )
            if error:
                return ToolResponse(success=False, error=error)
            
            # Get weather data (mock)
            city_key = city.capitalize()
            if city_key not in self.mock_data:
                return ToolResponse(
                    success=False,
                    error=f"No weather data for {city}"
                )
            
            data = self.mock_data[city_key]
            temp = data["temp"]
            
            # Convert units if needed
            if units.lower() == "fahrenheit":
                temp = (temp * 9/5) + 32
                unit_symbol = "°F"
            else:
                unit_symbol = "°C"
            
            return ToolResponse(
                success=True,
                data={
                    "city": city_key,
                    "temperature": temp,
                    "unit": unit_symbol,
                    "condition": data["condition"],
                    "humidity": data["humidity"],
                    "wind_speed": data["wind_speed"],
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return self.handle_error("weather_current", e)
    
    def weather_forecast(self, city: str, days: int = 3) -> ToolResponse:
        """
        Get weather forecast for multiple days
        
        Args:
            city: City name
            days: Number of days to forecast (1-7)
        """
        try:
            # Validate input
            if days < 1 or days > 7:
                return ToolResponse(
                    success=False,
                    error="Days must be between 1 and 7"
                )
            
            city_key = city.capitalize()
            if city_key not in self.mock_data:
                return ToolResponse(
                    success=False,
                    error=f"No weather data for {city}"
                )
            
            # Generate mock forecast
            base_data = self.mock_data[city_key]
            forecast = []
            
            for day in range(days):
                # Simple variation for mock data
                temp_variation = day * 2 - 3
                forecast.append({
                    "day": day + 1,
                    "date": datetime.now().date().isoformat(),
                    "high": base_data["temp"] + temp_variation + 3,
                    "low": base_data["temp"] + temp_variation - 2,
                    "condition": base_data["condition"],
                    "precipitation_chance": (day * 10) % 50
                })
            
            return ToolResponse(
                success=True,
                data={
                    "city": city_key,
                    "days": days,
                    "forecast": forecast,
                    "generated_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return self.handle_error("weather_forecast", e)


# How to integrate this feature into the main server:
# 
# 1. Place this file in: src/remote_mcp/features/weather/engine.py
# 
# 2. Create __init__.py in the weather directory:
#    from .engine import WeatherEngine
#    __all__ = ['WeatherEngine']
# 
# 3. In the main server.py, import and initialize:
#    from .features.weather import WeatherEngine
#    weather = WeatherEngine()
# 
# 4. Add MCP tool decorators for each method:
#    @mcp.tool()
#    async def weather_current(city: str, units: str = "celsius") -> Dict[str, Any]:
#        response = weather.weather_current(city, units)
#        return response.to_dict()
# 
# That's it! Your feature is now part of the Atlas Toolset MCP server.
