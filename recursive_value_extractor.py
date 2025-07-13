#!/usr/bin/env python3
"""
Recursive Value Extractor

This script recursively extracts and displays all values in the data structure
g_PerDepRunnable_m_depPort_out.m_listMemory.m_value.m_value.m_values
for a given dependency ID and cycle number.

Usage:
    python recursive_value_extractor.py <dep_id> <cycle_number>

Example:
    python recursive_value_extractor.py 0 100
"""

import sys
import json
import numpy as np
import scipy.io
from typing import Dict, Any, List, Optional, Union

class RecursiveValueExtractor:
    def __init__(self, mat_file_path: str = 'subset.mat'):
        """Initialize the extractor with the MATLAB file path."""
        self.mat_file_path = mat_file_path
        self.data = None
        self.dep_data = None
        self.time_data = None
        self.load_data()
    
    def load_data(self):
        """Load the MATLAB file and extract dependency data."""
        try:
            print(f"Loading MATLAB file: {self.mat_file_path}")
            self.data = scipy.io.loadmat(self.mat_file_path)
            
            # Extract dependency data
            if 'g_PerDepRunnable_m_depPort_out' in self.data:
                self.dep_data = self.data['g_PerDepRunnable_m_depPort_out']
                
                # Extract time data
                if hasattr(self.dep_data.dtype, 'names') and 'time' in self.dep_data.dtype.names:
                    self.time_data = self.dep_data['time'][0, 0].flatten()
                
                print(f"Loaded dependency data with shape: {self.dep_data.shape}")
                print(f"Time data points: {len(self.time_data) if self.time_data is not None else 'N/A'}")
            else:
                raise ValueError("Dependency data not found in MATLAB file")
                
        except Exception as e:
            print(f"Error loading MATLAB file: {e}")
            sys.exit(1)
    
    def display_value_info(self, value: Any, indent: int = 0) -> str:
        """Display information about a value in a readable format."""
        prefix = "  " * indent
        
        if isinstance(value, np.ndarray):
            if value.dtype.names is not None:
                return f"{prefix}Structured array with fields: {list(value.dtype.names)}, shape: {value.shape}"
            else:
                return f"{prefix}Array: dtype={value.dtype}, shape={value.shape}"
        elif isinstance(value, (np.integer, np.floating)):
            return f"{prefix}Scalar: {value.item()} (type: {type(value).__name__})"
        elif isinstance(value, np.bool_):
            return f"{prefix}Boolean: {bool(value)}"
        elif isinstance(value, (np.void, np.generic)):
            return f"{prefix}Generic: {str(value)}"
        elif isinstance(value, dict):
            return f"{prefix}Dictionary with {len(value)} keys: {list(value.keys())}"
        elif isinstance(value, (list, tuple)):
            return f"{prefix}List/Tuple with {len(value)} elements"
        else:
            return f"{prefix}Value: {value} (type: {type(value).__name__})"
    
    def recursively_extract_values(self, data: Any, path: str = "", indent: int = 0, max_depth: int = 10) -> Dict[str, Any]:
        """Recursively extract and display all values in the data structure."""
        if indent > max_depth:
            return {"error": "Maximum recursion depth reached"}
        
        result = {}
        prefix = "  " * indent
        
        print(f"{prefix}Exploring path: {path}")
        print(f"{prefix}Data type: {type(data)}")
        
        if isinstance(data, np.ndarray):
            if data.dtype.names is not None:
                # Structured array
                print(f"{prefix}Structured array with fields: {list(data.dtype.names)}")
                print(f"{prefix}Shape: {data.shape}")
                
                result["type"] = "structured_array"
                result["shape"] = data.shape
                result["fields"] = list(data.dtype.names)
                result["field_values"] = {}
                
                for field_name in data.dtype.names:
                    field_path = f"{path}.{field_name}" if path else field_name
                    print(f"{prefix}Field: {field_name}")
                    
                    try:
                        field_data = data[field_name][0, 0] if data.shape == (1, 1) else data[field_name]
                        print(f"{prefix}  {self.display_value_info(field_data, indent + 1)}")
                        
                        # Recursively process field if it's a structured array
                        if hasattr(field_data, 'dtype') and field_data.dtype.names is not None:
                            result["field_values"][field_name] = self.recursively_extract_values(
                                field_data, field_path, indent + 1, max_depth
                            )
                        else:
                            result["field_values"][field_name] = self.convert_to_serializable(field_data)
                    
                    except Exception as e:
                        print(f"{prefix}  Error accessing field {field_name}: {e}")
                        result["field_values"][field_name] = f"Error: {str(e)}"
            
            else:
                # Regular array
                print(f"{prefix}Regular array: dtype={data.dtype}, shape={data.shape}")
                result["type"] = "array"
                result["dtype"] = str(data.dtype)
                result["shape"] = data.shape
                
                if data.size < 100:
                    result["values"] = data.tolist()
                else:
                    result["sample_values"] = data.flatten()[:20].tolist()
                    result["note"] = f"Array too large ({data.size} elements), showing first 20"
        
        else:
            # Scalar or other type
            print(f"{prefix}Scalar/Other: {self.display_value_info(data, indent)}")
            result["type"] = "scalar"
            result["value"] = self.convert_to_serializable(data)
        
        return result
    
    def convert_to_serializable(self, obj: Any) -> Any:
        """Convert numpy objects to Python native types for JSON serialization."""
        if isinstance(obj, np.ndarray):
            if obj.dtype.names is not None:
                if obj.size == 1:
                    result = {}
                    for field in obj.dtype.names:
                        result[field] = self.convert_to_serializable(obj[field][0])
                    return result
                else:
                    return {
                        "type": "structured_array",
                        "shape": obj.shape,
                        "dtype": str(obj.dtype),
                        "fields": list(obj.dtype.names),
                        "size": obj.size
                    }
            elif obj.size == 1:
                return self.convert_to_serializable(obj.item())
            elif obj.size < 100:
                return obj.tolist()
            else:
                return {
                    "type": "large_array",
                    "shape": obj.shape,
                    "dtype": str(obj.dtype),
                    "size": obj.size,
                    "sample_values": obj.flatten()[:10].tolist()
                }
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.void, np.generic)):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self.convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self.convert_to_serializable(item) for item in obj]
        else:
            return obj
    
    def extract_values_for_dep_and_cycle(self, dep_id: int, cycle_number: int) -> Dict[str, Any]:
        """Extract all values recursively for a given dependency ID and cycle number."""
        print(f"\n{'='*60}")
        print(f"EXTRACTING VALUES FOR DEP_ID: {dep_id}, CYCLE: {cycle_number}")
        print(f"{'='*60}")
        
        result = {
            "dep_id": dep_id,
            "cycle_number": cycle_number,
            "timestamp": None,
            "extraction_path": "g_PerDepRunnable_m_depPort_out.m_listMemory.m_value.m_value.m_values",
            "recursive_values": {}
        }
        
        try:
            # Get timestamp
            if self.time_data is not None and 0 <= cycle_number < len(self.time_data):
                result["timestamp"] = float(self.time_data[cycle_number])
                print(f"Timestamp for cycle {cycle_number}: {result['timestamp']}")
            
            # Step 1: Navigate to g_PerDepRunnable_m_depPort_out
            print(f"\nStep 1: Starting from g_PerDepRunnable_m_depPort_out")
            current_data = self.dep_data
            result["recursive_values"]["g_PerDepRunnable_m_depPort_out"] = self.recursively_extract_values(
                current_data, "g_PerDepRunnable_m_depPort_out", 0, 2
            )
            
            # Step 2: Navigate to m_listMemory
            print(f"\nStep 2: Navigating to m_listMemory")
            if hasattr(current_data.dtype, 'names') and 'm_listMemory' in current_data.dtype.names:
                current_data = current_data['m_listMemory'][0, 0]
                result["recursive_values"]["m_listMemory"] = self.recursively_extract_values(
                    current_data, "m_listMemory", 0, 3
                )
            else:
                result["error"] = "m_listMemory field not found"
                return result
            
            # Step 3: Navigate to m_value (first level)
            print(f"\nStep 3: Navigating to first m_value")
            if hasattr(current_data.dtype, 'names') and 'm_value' in current_data.dtype.names:
                current_data = current_data['m_value'][0, 0]
                result["recursive_values"]["m_value_first"] = self.recursively_extract_values(
                    current_data, "m_value (first)", 0, 3
                )
            else:
                result["error"] = "First m_value field not found"
                return result
            
            # Step 4: Navigate to m_value (second level)
            print(f"\nStep 4: Navigating to second m_value")
            if hasattr(current_data.dtype, 'names') and 'm_value' in current_data.dtype.names:
                current_data = current_data['m_value'][0, 0]
                result["recursive_values"]["m_value_second"] = self.recursively_extract_values(
                    current_data, "m_value (second)", 0, 3
                )
            else:
                result["error"] = "Second m_value field not found"
                return result
            
            # Step 5: Navigate to m_values and extract for specific dep_id and cycle
            print(f"\nStep 5: Navigating to m_values and extracting for dep_id={dep_id}, cycle={cycle_number}")
            if hasattr(current_data.dtype, 'names'):
                available_fields = list(current_data.dtype.names)
                print(f"Available fields at this level: {available_fields}")
                
                result["recursive_values"]["m_values"] = {
                    "available_fields": available_fields,
                    "field_values": {}
                }
                
                # Extract values for each field
                for field_name in available_fields:
                    try:
                        field_data = current_data[field_name][0, 0]
                        print(f"\nProcessing field: {field_name}")
                        print(f"Field data type: {type(field_data)}")
                        print(f"Field data shape: {getattr(field_data, 'shape', 'N/A')}")
                        
                        # Handle multi-dimensional arrays
                        if hasattr(field_data, 'shape') and len(field_data.shape) >= 2:
                            print(f"Multi-dimensional array detected: shape={field_data.shape}")
                            
                            if cycle_number < field_data.shape[-1]:
                                if len(field_data.shape) == 2:
                                    # 2D array
                                    if dep_id < field_data.shape[0]:
                                        extracted_value = field_data[dep_id, cycle_number]
                                        print(f"Extracted value for dep_id={dep_id}, cycle={cycle_number}: {extracted_value}")
                                        result["recursive_values"]["m_values"]["field_values"][field_name] = {
                                            "extracted_value": self.convert_to_serializable(extracted_value),
                                            "extraction_indices": [dep_id, cycle_number],
                                            "array_shape": field_data.shape
                                        }
                                    else:
                                        # Extract entire column for the cycle
                                        extracted_values = field_data[:, cycle_number]
                                        print(f"Extracted all values for cycle={cycle_number}: shape={extracted_values.shape}")
                                        result["recursive_values"]["m_values"]["field_values"][field_name] = {
                                            "extracted_values": self.convert_to_serializable(extracted_values),
                                            "extraction_indices": ["all", cycle_number],
                                            "array_shape": field_data.shape
                                        }
                                else:
                                    # Higher dimensional array
                                    if dep_id < field_data.shape[0]:
                                        extracted_value = field_data[dep_id, ..., cycle_number]
                                        print(f"Extracted value from {len(field_data.shape)}D array: shape={extracted_value.shape}")
                                        result["recursive_values"]["m_values"]["field_values"][field_name] = {
                                            "extracted_value": self.convert_to_serializable(extracted_value),
                                            "extraction_indices": [dep_id, "...", cycle_number],
                                            "array_shape": field_data.shape
                                        }
                                    else:
                                        extracted_values = field_data[..., cycle_number]
                                        print(f"Extracted all values for cycle={cycle_number}: shape={extracted_values.shape}")
                                        result["recursive_values"]["m_values"]["field_values"][field_name] = {
                                            "extracted_values": self.convert_to_serializable(extracted_values),
                                            "extraction_indices": ["all", cycle_number],
                                            "array_shape": field_data.shape
                                        }
                            else:
                                result["recursive_values"]["m_values"]["field_values"][field_name] = {
                                    "error": f"Cycle {cycle_number} out of range (max: {field_data.shape[-1]-1})"
                                }
                        else:
                            # 1D array or scalar
                            result["recursive_values"]["m_values"]["field_values"][field_name] = {
                                "full_value": self.convert_to_serializable(field_data),
                                "note": "Full value extracted (not cycle-specific)"
                            }
                    
                    except Exception as e:
                        result["recursive_values"]["m_values"]["field_values"][field_name] = {
                            "error": f"Error extracting field: {str(e)}"
                        }
            else:
                result["error"] = "No structured fields found at m_values level"
                return result
            
        except Exception as e:
            result["error"] = f"Error during extraction: {str(e)}"
        
        return result

def main():
    """Main function to handle command line arguments and execute extraction."""
    if len(sys.argv) < 3:
        print("Usage: python recursive_value_extractor.py <dep_id> <cycle_number>")
        print("Example: python recursive_value_extractor.py 0 100")
        sys.exit(1)
    
    try:
        dep_id = int(sys.argv[1])
        cycle_number = int(sys.argv[2])
        
        extractor = RecursiveValueExtractor()
        result = extractor.extract_values_for_dep_and_cycle(dep_id, cycle_number)
        
        print(f"\n{'='*60}")
        print("FINAL RESULT (JSON FORMAT)")
        print(f"{'='*60}")
        print(json.dumps(result, indent=2))
        
    except ValueError:
        print("Error: dep_id and cycle_number must be integers")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()