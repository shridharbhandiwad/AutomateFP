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
    
    def numpy_to_python(self, obj: Any, depth: int = 0, visited: Optional[set] = None) -> Any:
        """Convert numpy objects to Python native types for JSON serialization."""
        # Initialize visited set for circular reference detection
        if visited is None:
            visited = set()
        
        # Check for maximum recursion depth
        if depth > 50:
            return {"error": "Maximum recursion depth reached", "type": str(type(obj))}
        
        # Check for circular references for objects that can be tracked
        obj_id = id(obj)
        if hasattr(obj, 'shape') and obj_id in visited:
            return {"error": "Circular reference detected", "type": str(type(obj))}
        
        if isinstance(obj, np.ndarray):
            # Add to visited set for circular reference detection
            visited.add(obj_id)
            
            try:
                # Handle structured arrays
                if obj.dtype.names is not None:
                    if obj.size == 1:
                        result = {}
                        for field in obj.dtype.names:
                            try:
                                result[field] = self.numpy_to_python(obj[field][0], depth + 1, visited.copy())
                            except Exception as e:
                                result[field] = {"error": f"Field extraction failed: {str(e)}"}
                        return result
                    else:
                        return {
                            "type": "structured_array",
                            "shape": obj.shape,
                            "dtype": str(obj.dtype),
                            "fields": obj.dtype.names,
                            "size": obj.size
                        }
                elif obj.size == 1:
                    return self.numpy_to_python(obj.item(), depth + 1, visited.copy())
                elif obj.size < 100:  # Avoid huge arrays in JSON
                    return obj.tolist()
                else:
                    return {
                        "type": "large_array",
                        "shape": obj.shape,
                        "dtype": str(obj.dtype),
                        "size": obj.size,
                        "sample_values": obj.flatten()[:10].tolist()
                    }
            except Exception as e:
                return {"error": f"Array processing failed: {str(e)}", "type": str(type(obj))}
            finally:
                # Remove from visited set when done processing
                visited.discard(obj_id)
                
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.void, np.generic)):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self.numpy_to_python(v, depth + 1, visited.copy()) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self.numpy_to_python(item, depth + 1, visited.copy()) for item in obj]
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
        result = {
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
            if self.time_data is not None and 0 <= cycle_number < len(self.time_data):
                result["timestamp"] = float(self.time_data[cycle_number])
            
            # Navigate to the dependency values
            list_memory = self.extract_nested_field(self.dep_data, ['m_listMemory'])
            if list_memory is None:
                result["error"] = "Could not access m_listMemory field"
                return result
            
            m_value = self.extract_nested_field(list_memory, ['m_value'])
            if m_value is None:
                result["error"] = "Could not access m_value field"
                return result
            
            inner_m_value = self.extract_nested_field(m_value, ['m_value'])
            if inner_m_value is None:
                result["error"] = "Could not access inner m_value field"
                return result
            
            # Check if we have structured dependency data
            if hasattr(inner_m_value.dtype, 'names') and inner_m_value.dtype.names:
                print(f"Available fields in dependency data: {inner_m_value.dtype.names}")
                
                # Extract all available fields
                for field_name in inner_m_value.dtype.names:
                    try:
                        field_data = inner_m_value[field_name][0, 0]
                        
                        # Handle different data types
                        if hasattr(field_data, 'shape'):
                            if field_data.shape == ():
                                # Scalar value
                                result["properties"][field_name] = self.numpy_to_python(field_data)
                            elif len(field_data.shape) >= 2:
                                # Multi-dimensional array - extract slice for given cycle
                                if cycle_number < field_data.shape[-1]:
                                    if len(field_data.shape) == 2:
                                        # 2D array - extract column for cycle
                                        if dep_id < field_data.shape[0]:
                                            result["properties"][field_name] = self.numpy_to_python(field_data[dep_id, cycle_number])
                                        else:
                                            result["properties"][field_name] = self.numpy_to_python(field_data[:, cycle_number])
                                    else:
                                        # Higher dimensional array - extract relevant slice
                                        if dep_id < field_data.shape[0]:
                                            result["properties"][field_name] = self.numpy_to_python(field_data[dep_id, ..., cycle_number])
                                        else:
                                            result["properties"][field_name] = self.numpy_to_python(field_data[..., cycle_number])
                                else:
                                    result["properties"][field_name] = f"Cycle {cycle_number} out of range (max: {field_data.shape[-1]-1})"
                            else:
                                # 1D array or other format
                                result["properties"][field_name] = self.numpy_to_python(field_data)
                        else:
                            result["properties"][field_name] = self.numpy_to_python(field_data)
                    
                    except Exception as e:
                        result["properties"][field_name] = f"Error extracting field: {str(e)}"
                        
            else:
                # If not structured, treat as array data
                if hasattr(inner_m_value, 'shape') and len(inner_m_value.shape) >= 2:
                    if dep_id < inner_m_value.shape[0] and cycle_number < inner_m_value.shape[-1]:
                        result["properties"]["array_data"] = self.numpy_to_python(inner_m_value[dep_id, cycle_number])
                    else:
                        result["error"] = f"Index out of bounds: dep_id={dep_id}, cycle={cycle_number}, shape={inner_m_value.shape}"
                else:
                    result["properties"]["raw_data"] = self.numpy_to_python(inner_m_value)
            
            # Add general metadata
            result["metadata"]["total_cycles"] = len(self.time_data) if self.time_data is not None else "unknown"
            result["metadata"]["data_shape"] = str(self.dep_data.shape)
            result["metadata"]["available_fields"] = list(self.dep_data.dtype.names) if hasattr(self.dep_data.dtype, 'names') else []
            
        except Exception as e:
            result["error"] = f"Error extracting dependency properties: {str(e)}"
        
        return result
    
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