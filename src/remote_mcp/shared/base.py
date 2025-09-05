"""
Base classes for Atlas Toolset MCP features
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolResponse:
    """Standard response structure for all tools"""
    success: bool
    data: Dict[str, Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {"success": self.success}
        if self.data is not None:
            result["data"] = self.data
        if self.error:
            result["error"] = self.error
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class BaseFeature(ABC):
    """Base class for all feature implementations"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.logger = logging.getLogger(f"feature.{name}")
        self.logger.info(f"Initialized {name} feature v{version}")
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of tools provided by this feature"""
        pass
    
    def validate_input(self, data: Dict[str, Any], required: List[str]) -> Optional[str]:
        """
        Validate that required fields are present
        
        Args:
            data: Input data to validate
            required: List of required field names
            
        Returns:
            Error message if validation fails, None if valid
        """
        missing = [field for field in required if field not in data or data[field] is None]
        if missing:
            return f"Missing required fields: {', '.join(missing)}"
        return None
    
    def handle_error(self, operation: str, error: Exception) -> ToolResponse:
        """
        Standard error handling for feature operations
        
        Args:
            operation: Name of the operation that failed
            error: The exception that occurred
            
        Returns:
            ToolResponse with error information
        """
        error_msg = f"{operation} failed: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        return ToolResponse(
            success=False,
            error=error_msg,
            metadata={"operation": operation, "feature": self.name}
        )
