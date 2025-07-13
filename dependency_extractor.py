#!/usr/bin/env python3
"""
Dependency Data Extractor

This script extracts dependency object properties from a MATLAB file
based on dependency ID and cycle number, outputting the results in JSON format.

Usage:
    python dependency_extractor.py <dep_id> <cycle_number>

Example:
    python dependency_extractor.py 1 100
"""

import sys
import json
import numpy as np
import scipy.io
from typing import Dict, Any, List, Optional, Union

class DependencyExtractor:
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
    
    def numpy_to_python(self, obj: Any, max_depth: int = 10, current_depth: int = 0) -> Any:
        """Convert numpy objects to Python native types for JSON serialization."""
        # Prevent infinite recursion by checking depth limit
        if current_depth >= max_depth:
            return {
                "error": "Maximum recursion depth reached",
                "type": "depth_limited_object",
                "original_type": str(type(obj)),
                "current_depth": current_depth
            }
        
        # Handle numpy arrays
        if isinstance(obj, np.ndarray):
            array_size = obj.size  # Define array_size here for all array handling
            
            # Handle structured arrays (arrays with named fields)
            if obj.dtype.names is not None:
                structured_array_fields = obj.dtype.names
                array_shape = obj.shape
                
                if array_size == 1:
                    # Single element structured array - extract all fields
                    field_values = {}
                    for field_name in structured_array_fields:
                        try:
                            field_data = obj[field_name][0]
                            field_values[field_name] = self.numpy_to_python(
                                field_data, max_depth, current_depth + 1
                            )
                        except Exception as field_error:
                            field_values[field_name] = {
                                "error": f"Error extracting field '{field_name}': {str(field_error)}",
                                "field_type": str(type(obj[field_name]))
                            }
                    
                    return {
                        "type": "structured_array",
                        "shape": array_shape,
                        "fields": list(structured_array_fields),
                        "field_values": field_values
                    }
                else:
                    # Multi-element structured array - return metadata only
                    return {
                        "type": "structured_array",
                        "shape": array_shape,
                        "dtype": str(obj.dtype),
                        "fields": list(structured_array_fields),
                        "size": array_size
                    }
            
            # Handle regular arrays
            elif array_size == 1:
                # Single element array - extract the item
                single_item = obj.item()
                return self.numpy_to_python(single_item, max_depth, current_depth + 1)
            
            elif array_size < 100:  # Avoid huge arrays in JSON
                # Small array - convert to list
                array_as_list = obj.tolist()
                return [self.numpy_to_python(item, max_depth, current_depth + 1) for item in array_as_list]
            
            else:
                # Large array - return metadata with sample values
                flattened_array = obj.flatten()
                sample_values = flattened_array[:10].tolist()
                
                return {
                    "type": "large_array",
                    "shape": obj.shape,
                    "dtype": str(obj.dtype),
                    "size": array_size,
                    "sample_values": sample_values
                }
        
        # Handle numpy scalar types
        elif isinstance(obj, (np.integer, np.floating)):
            scalar_value = obj.item()
            return scalar_value
        
        elif isinstance(obj, np.bool_):
            boolean_value = bool(obj)
            return boolean_value
        
        elif isinstance(obj, (np.void, np.generic)):
            string_representation = str(obj)
            return string_representation
        
        # Handle Python containers
        elif isinstance(obj, dict):
            converted_dict = {}
            for dict_key, dict_value in obj.items():
                converted_dict[dict_key] = self.numpy_to_python(
                    dict_value, max_depth, current_depth + 1
                )
            return converted_dict
        
        elif isinstance(obj, (list, tuple)):
            converted_list = []
            for list_item in obj:
                converted_item = self.numpy_to_python(
                    list_item, max_depth, current_depth + 1
                )
                converted_list.append(converted_item)
            return converted_list
        
        # Handle other types
        else:
            return obj
    
    def extract_nested_field(self, data: np.ndarray, field_path: List[str]) -> Any:
        """Extract a nested field from structured numpy array."""
        current = data
        for field in field_path:
            if hasattr(current.dtype, 'names') and field in current.dtype.names:
                current = current[field][0, 0]
            else:
                return None
        return current
    
    def get_dependency_properties(self, dep_id: int, cycle_number: int) -> Dict[str, Any]:
        """Extract all dependency object properties for a given ID and cycle."""
        extraction_result = {
            "dep_id": dep_id,
            "cycle_number": cycle_number,
            "timestamp": None,
            "properties": {},
            "metadata": {
                "extraction_method": "structured_array_navigation",
                "data_source": "g_PerDepRunnable_m_depPort_out"
            }
        }
        
        try:
            # Get time information
            time_data_array = self.time_data
            if time_data_array is not None and 0 <= cycle_number < len(time_data_array):
                current_timestamp = float(time_data_array[cycle_number])
                extraction_result["timestamp"] = current_timestamp
            
            # Navigate to the dependency values
            list_memory_field = self.extract_nested_field(self.dep_data, ['m_listMemory'])
            if list_memory_field is None:
                extraction_result["error"] = "Could not access m_listMemory field"
                return extraction_result
            
            outer_m_value = self.extract_nested_field(list_memory_field, ['m_value'])
            if outer_m_value is None:
                extraction_result["error"] = "Could not access m_value field"
                return extraction_result
            
            inner_m_value = self.extract_nested_field(outer_m_value, ['m_value'])
            if inner_m_value is None:
                extraction_result["error"] = "Could not access inner m_value field"
                return extraction_result
            
            # Check if we have structured dependency data
            structured_data = inner_m_value
            if hasattr(structured_data.dtype, 'names') and structured_data.dtype.names:
                available_field_names = structured_data.dtype.names
                print(f"Available fields in dependency data: {available_field_names}")
                
                # Extract all available fields
                for field_name in available_field_names:
                    try:
                        field_data = structured_data[field_name][0, 0]
                        field_shape = getattr(field_data, 'shape', None)
                        
                        # Handle different data types
                        if field_shape is not None:
                            if field_shape == ():
                                # Scalar value
                                scalar_field_value = self.numpy_to_python(field_data, max_depth=8)
                                extraction_result["properties"][field_name] = scalar_field_value
                            elif len(field_shape) >= 2:
                                # Multi-dimensional array - extract slice for given cycle
                                max_cycle_index = field_shape[-1]
                                if cycle_number < max_cycle_index:
                                    if len(field_shape) == 2:
                                        # 2D array - extract column for cycle
                                        max_dep_id = field_shape[0]
                                        if dep_id < max_dep_id:
                                            cycle_specific_data = field_data[dep_id, cycle_number]
                                            processed_cycle_data = self.numpy_to_python(cycle_specific_data, max_depth=8)
                                            extraction_result["properties"][field_name] = processed_cycle_data
                                        else:
                                            all_deps_cycle_data = field_data[:, cycle_number]
                                            processed_all_deps_data = self.numpy_to_python(all_deps_cycle_data, max_depth=8)
                                            extraction_result["properties"][field_name] = processed_all_deps_data
                                    else:
                                        # Higher dimensional array - extract relevant slice
                                        max_dep_id = field_shape[0]
                                        if dep_id < max_dep_id:
                                            high_dim_slice = field_data[dep_id, ..., cycle_number]
                                            processed_high_dim_data = self.numpy_to_python(high_dim_slice, max_depth=8)
                                            extraction_result["properties"][field_name] = processed_high_dim_data
                                        else:
                                            all_deps_high_dim_slice = field_data[..., cycle_number]
                                            processed_all_deps_high_dim = self.numpy_to_python(all_deps_high_dim_slice, max_depth=8)
                                            extraction_result["properties"][field_name] = processed_all_deps_high_dim
                                else:
                                    cycle_out_of_range_message = f"Cycle {cycle_number} out of range (max: {max_cycle_index-1})"
                                    extraction_result["properties"][field_name] = cycle_out_of_range_message
                            else:
                                # 1D array or other format
                                one_dim_field_data = self.numpy_to_python(field_data, max_depth=8)
                                extraction_result["properties"][field_name] = one_dim_field_data
                        else:
                            # No shape attribute - treat as is
                            unstructured_field_data = self.numpy_to_python(field_data, max_depth=8)
                            extraction_result["properties"][field_name] = unstructured_field_data
                    
                    except Exception as field_extraction_error:
                        error_message = f"Error extracting field: {str(field_extraction_error)}"
                        extraction_result["properties"][field_name] = error_message
                        
            else:
                # If not structured, treat as array data
                unstructured_data = structured_data
                if hasattr(unstructured_data, 'shape') and len(unstructured_data.shape) >= 2:
                    data_shape = unstructured_data.shape
                    max_dep_id = data_shape[0]
                    max_cycle_index = data_shape[-1]
                    
                    if dep_id < max_dep_id and cycle_number < max_cycle_index:
                        array_element = unstructured_data[dep_id, cycle_number]
                        processed_array_element = self.numpy_to_python(array_element, max_depth=8)
                        extraction_result["properties"]["array_data"] = processed_array_element
                    else:
                        bounds_error_message = f"Index out of bounds: dep_id={dep_id}, cycle={cycle_number}, shape={data_shape}"
                        extraction_result["error"] = bounds_error_message
                else:
                    raw_data_converted = self.numpy_to_python(unstructured_data, max_depth=8)
                    extraction_result["properties"]["raw_data"] = raw_data_converted
            
            # Add general metadata
            total_cycles = len(time_data_array) if time_data_array is not None else "unknown"
            data_shape_str = str(self.dep_data.shape)
            available_fields_list = list(self.dep_data.dtype.names) if hasattr(self.dep_data.dtype, 'names') else []
            
            extraction_result["metadata"]["total_cycles"] = total_cycles
            extraction_result["metadata"]["data_shape"] = data_shape_str
            extraction_result["metadata"]["available_fields"] = available_fields_list
            
        except Exception as general_error:
            error_message = f"Error extracting dependency properties: {str(general_error)}"
            extraction_result["error"] = error_message
        
        return extraction_result
    
    def get_available_cycles(self) -> List[int]:
        """Get list of available cycle numbers."""
        if self.time_data is not None:
            return list(range(len(self.time_data)))
        return []
    
    def get_dependency_summary(self) -> Dict[str, Any]:
        """Get a summary of the dependency data structure."""
        summary = {
            "file_path": self.mat_file_path,
            "total_variables": len(self.data.keys()),
            "dependency_variables": [],
            "time_info": {},
            "data_structure": {}
        }
        
        # Find all dependency-related variables
        for key in self.data.keys():
            if 'dep' in key.lower() or 'Dep' in key or 'g_Per' in key:
                summary["dependency_variables"].append(key)
        
        # Time information
        if self.time_data is not None:
            summary["time_info"] = {
                "total_cycles": len(self.time_data),
                "time_range": {
                    "start": float(self.time_data[0]),
                    "end": float(self.time_data[-1])
                },
                "sample_times": self.time_data[:10].tolist()
            }
        
        # Data structure info
        if self.dep_data is not None:
            summary["data_structure"] = {
                "shape": self.dep_data.shape,
                "dtype": str(self.dep_data.dtype),
                "fields": list(self.dep_data.dtype.names) if hasattr(self.dep_data.dtype, 'names') else []
            }
        
        return summary

def main():
    """Main function to handle command line arguments and execute extraction."""
    if len(sys.argv) < 2:
        print("Usage: python dependency_extractor.py <dep_id> <cycle_number>")
        print("       python dependency_extractor.py --summary")
        print("       python dependency_extractor.py --cycles")
        sys.exit(1)
    
    extractor = DependencyExtractor()
    
    if sys.argv[1] == "--summary":
        # Show summary of dependency data
        summary = extractor.get_dependency_summary()
        print(json.dumps(summary, indent=2))
    
    elif sys.argv[1] == "--cycles":
        # Show available cycles
        cycles = extractor.get_available_cycles()
        print(json.dumps({
            "available_cycles": cycles,
            "total_cycles": len(cycles),
            "cycle_range": f"0 to {len(cycles)-1}" if cycles else "No cycles available"
        }, indent=2))
    
    else:
        # Extract dependency properties
        if len(sys.argv) < 3:
            print("Error: Both dep_id and cycle_number are required")
            print("Usage: python dependency_extractor.py <dep_id> <cycle_number>")
            sys.exit(1)
        
        try:
            dep_id = int(sys.argv[1])
            cycle_number = int(sys.argv[2])
            
            result = extractor.get_dependency_properties(dep_id, cycle_number)
            print(json.dumps(result, indent=2))
            
        except ValueError:
            print("Error: dep_id and cycle_number must be integers")
            sys.exit(1)

if __name__ == "__main__":
    main()