"""Data processing nodes for transformations and validations."""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph
from pydantic import BaseModel
import json
import pandas as pd


class JSONTransformerState(BaseModel):
    data: Dict[str, Any] = {}
    transformed_data: Dict[str, Any] = {}


class JSONTransformerNode:
    """Node for transforming JSON data structures.
    
    Args:
        transformation_map: Dict mapping input keys to output keys
    """
    
    def __init__(self, transformation_map: Optional[Dict[str, str]] = None):
        self.transformation_map = transformation_map or {}
    
    def __call__(self, state: JSONTransformerState) -> JSONTransformerState:
        """Transform JSON data according to mapping.
        
        Args:
            state: JSONTransformerState containing input data
            
        Returns:
            Updated state with transformed data
        """
        if not self.transformation_map:
            state.transformed_data = state.data
            return state
        
        result = {}
        for old_key, new_key in self.transformation_map.items():
            if old_key in state.data:
                result[new_key] = state.data[old_key]
        
        # Include unmapped keys
        for key, value in state.data.items():
            if key not in self.transformation_map and key not in result:
                result[key] = value
        
        state.transformed_data = result
        return state


class DataValidatorState(BaseModel):
    data: Dict[str, Any] = {}
    valid: bool = False
    errors: List[str] = []


class DataValidatorNode:
    """Node for validating data against schemas.
    
    Args:
        required_fields: List of required field names
        field_types: Dict mapping field names to expected types
    """
    
    def __init__(self, required_fields: List[str], field_types: Optional[Dict[str, type]] = None):
        self.required_fields = required_fields
        self.field_types = field_types or {}
    
    def __call__(self, state: DataValidatorState) -> DataValidatorState:
        """Validate data structure and types.
        
        Args:
            state: DataValidatorState containing data to validate
            
        Returns:
            Updated state with validation results
        """
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in state.data:
                errors.append(f"Missing required field: {field}")
        
        # Check field types
        for field, expected_type in self.field_types.items():
            if field in state.data and not isinstance(state.data[field], expected_type):
                errors.append(
                    f"Field '{field}' has incorrect type. "
                    f"Expected {expected_type.__name__}, got {type(state.data[field]).__name__}"
                )
        
        state.valid = len(errors) == 0
        state.errors = errors
        
        return state