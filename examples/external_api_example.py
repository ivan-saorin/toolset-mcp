"""
Example: Integrating with external APIs in Atlas Toolset MCP

This example shows how to create a feature that integrates with external APIs.
"""

import httpx
import asyncio
from typing import Dict, Any, List, Optional
from src.remote_mcp.shared.base import BaseFeature, ToolResponse


class ExternalAPIEngine(BaseFeature):
    """Example feature showing external API integration patterns"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("external_api", "1.0.0")
        
        # API configuration
        self.api_key = api_key
        self.base_url = "https://api.example.com/v1"
        self.timeout = httpx.Timeout(10.0, connect=5.0)
        
        # Create HTTP client with retry logic
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_headers()
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Atlas-Toolset-MCP/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of API tools"""
        return [
            {
                "name": "api_fetch_data",
                "description": "Fetch data from external API",
                "parameters": {
                    "endpoint": "API endpoint path",
                    "params": "Query parameters",
                    "method": "HTTP method (GET, POST)"
                }
            },
            {
                "name": "api_cached_fetch",
                "description": "Fetch with caching support",
                "parameters": {
                    "resource": "Resource to fetch",
                    "cache_time": "Cache duration in seconds"
                }
            }
        ]
    
    async def api_fetch_data(self, 
                            endpoint: str, 
                            params: Optional[Dict[str, Any]] = None,
                            method: str = "GET") -> ToolResponse:
        """
        Fetch data from external API with error handling and retry
        
        Args:
            endpoint: API endpoint path
            params: Query parameters or request body
            method: HTTP method
        """
        try:
            # Validate method
            if method.upper() not in ["GET", "POST", "PUT", "DELETE"]:
                return ToolResponse(
                    success=False,
                    error=f"Unsupported HTTP method: {method}"
                )
            
            # Retry logic
            max_retries = 3
            retry_delay = 1.0
            
            for attempt in range(max_retries):
                try:
                    # Make the request
                    if method.upper() == "GET":
                        response = await self.client.get(
                            endpoint,
                            params=params
                        )
                    elif method.upper() == "POST":
                        response = await self.client.post(
                            endpoint,
                            json=params
                        )
                    elif method.upper() == "PUT":
                        response = await self.client.put(
                            endpoint,
                            json=params
                        )
                    else:  # DELETE
                        response = await self.client.delete(
                            endpoint,
                            params=params
                        )
                    
                    # Check response status
                    if response.status_code >= 200 and response.status_code < 300:
                        return ToolResponse(
                            success=True,
                            data=response.json(),
                            metadata={
                                "status_code": response.status_code,
                                "headers": dict(response.headers),
                                "attempt": attempt + 1
                            }
                        )
                    elif response.status_code >= 500:
                        # Server error, retry
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay * (attempt + 1))
                            continue
                        else:
                            return ToolResponse(
                                success=False,
                                error=f"Server error: {response.status_code}",
                                metadata={"response_text": response.text}
                            )
                    else:
                        # Client error, don't retry
                        return ToolResponse(
                            success=False,
                            error=f"Client error: {response.status_code}",
                            metadata={"response_text": response.text}
                        )
                        
                except httpx.TimeoutException:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        return ToolResponse(
                            success=False,
                            error="Request timeout after retries"
                        )
                except httpx.NetworkError as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        return ToolResponse(
                            success=False,
                            error=f"Network error: {str(e)}"
                        )
            
            return ToolResponse(
                success=False,
                error="Failed after all retry attempts"
            )
            
        except Exception as e:
            return self.handle_error("api_fetch_data", e)
    
    async def api_cached_fetch(self, 
                              resource: str,
                              cache_time: int = 300) -> ToolResponse:
        """
        Fetch data with simple in-memory caching
        
        Args:
            resource: Resource identifier
            cache_time: Cache duration in seconds
        """
        try:
            # Simple cache implementation
            # In production, use Redis or similar
            cache_key = f"cache_{resource}"
            
            # Check if we have cached data
            if hasattr(self, '_cache'):
                cached = self._cache.get(cache_key)
                if cached:
                    age = (datetime.now() - cached['timestamp']).total_seconds()
                    if age < cache_time:
                        return ToolResponse(
                            success=True,
                            data=cached['data'],
                            metadata={
                                "from_cache": True,
                                "cache_age_seconds": int(age)
                            }
                        )
            else:
                self._cache = {}
            
            # Fetch fresh data
            response = await self.api_fetch_data(f"/resources/{resource}")
            
            if response.success:
                # Cache the result
                self._cache[cache_key] = {
                    'data': response.data,
                    'timestamp': datetime.now()
                }
                
                # Add cache metadata
                if response.metadata:
                    response.metadata['from_cache'] = False
                else:
                    response.metadata = {'from_cache': False}
            
            return response
            
        except Exception as e:
            return self.handle_error("api_cached_fetch", e)
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()


# Best Practices for External API Integration:
#
# 1. **Authentication**: Store API keys securely (environment variables)
# 2. **Rate Limiting**: Implement rate limiting to avoid hitting API limits
# 3. **Retry Logic**: Implement exponential backoff for transient failures
# 4. **Caching**: Cache responses to reduce API calls and improve performance
# 5. **Error Handling**: Distinguish between client and server errors
# 6. **Timeout Handling**: Set appropriate timeouts for API calls
# 7. **Async Operations**: Use async/await for non-blocking I/O
# 8. **Connection Pooling**: Reuse HTTP connections for efficiency
# 9. **Response Validation**: Validate API responses before processing
# 10. **Monitoring**: Log API calls for debugging and monitoring
#
# Example Usage in server.py:
#
# import os
# from .features.external_api import ExternalAPIEngine
#
# # Initialize with API key from environment
# api_key = os.environ.get("EXTERNAL_API_KEY")
# external_api = ExternalAPIEngine(api_key)
#
# @mcp.tool()
# async def api_fetch_data(endpoint: str, params: Dict = None, method: str = "GET"):
#     response = await external_api.api_fetch_data(endpoint, params, method)
#     return response.to_dict()
#
# # Don't forget to clean up on shutdown
# @app.on_event("shutdown")
# async def shutdown_event():
#     await external_api.close()
