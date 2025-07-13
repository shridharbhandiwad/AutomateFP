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
        self.extraction_cache = {}  # Cache for processed objects
        self.processing_stack = set()  # Track objects being processed to detect cycles
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
        """
        Convert numpy objects to Python native types for JSON serialization.
        
        Args:
            obj: The object to convert
            max_depth: Maximum recursion depth to prevent stack overflow
            current_depth: Current recursion depth
            
        Returns:
            Python native object suitable for JSON serialization
        """
        # Prevent excessive recursion
        if current_depth > max_depth:
            return {
                "type": "max_depth_exceeded",
                "current_depth": current_depth,
                "max_depth": max_depth,
                "object_type": str(type(obj)),
                "object_repr": str(obj)[:100] + "..." if len(str(obj)) > 100 else str(obj)
            }
        
        # Check for circular references using object id
        obj_id = id(obj)
        if obj_id in self.processing_stack:
            return {
                "type": "circular_reference",
                "object_id": obj_id,
                "object_type": str(type(obj)),
                "depth": current_depth
            }
        
        # Check cache for already processed objects
        if obj_id in self.extraction_cache:
            return self.extraction_cache[obj_id]
        
        # Add to processing stack
        self.processing_stack.add(obj_id)
        
        try:
            result = None
            
            if isinstance(obj, np.ndarray):
                # Handle structured arrays
                if obj.dtype.names is not None:
                    if obj.size == 1:
                        structured_result = {}
                        for field in obj.dtype.names:
                            field_value = obj[field][0]
                            structured_result[field] = self.numpy_to_python(
                                field_value, max_depth, current_depth + 1
                            )
                        result = structured_result
                    else:
                        # Store metadata for large structured arrays
                        field_info = {}
                        for field in obj.dtype.names:
                            field_data = obj[field]
                            field_info[field] = {
                                "shape": field_data.shape,
                                "dtype": str(field_data.dtype),
                                "size": field_data.size
                            }
                        
                        result = {
                            "type": "structured_array",
                            "shape": obj.shape,
                            "dtype": str(obj.dtype),
                            "fields": obj.dtype.names,
                            "field_info": field_info,
                            "size": obj.size
                        }
                elif obj.size == 1:
                    # Single element array
                    result = self.numpy_to_python(obj.item(), max_depth, current_depth + 1)
                elif obj.size < 100:  # Avoid huge arrays in JSON
                    # Small arrays - convert to list
                    result = obj.tolist()
                else:
                    # Large arrays - store metadata and sample
                    sample_size = min(10, obj.size)
                    flattened = obj.flatten()
                    sample_values = []
                    for i in range(sample_size):
                        sample_values.append(self.numpy_to_python(
                            flattened[i], max_depth, current_depth + 1
                        ))
                    
                    result = {
                        "type": "large_array",
                        "shape": obj.shape,
                        "dtype": str(obj.dtype),
                        "size": obj.size,
                        "sample_values": sample_values,
                        "statistics": {
                            "min": float(np.min(obj)) if obj.size > 0 else None,
                            "max": float(np.max(obj)) if obj.size > 0 else None,
                            "mean": float(np.mean(obj)) if obj.size > 0 else None,
                            "std": float(np.std(obj)) if obj.size > 0 else None
                        }
                    }
                    
            elif isinstance(obj, (np.integer, np.floating)):
                result = obj.item()
            elif isinstance(obj, np.bool_):
                result = bool(obj)
            elif isinstance(obj, (np.void, np.generic)):
                result = str(obj)
            elif isinstance(obj, dict):
                dict_result = {}
                for key, value in obj.items():
                    dict_result[key] = self.numpy_to_python(value, max_depth, current_depth + 1)
                result = dict_result
            elif isinstance(obj, (list, tuple)):
                list_result = []
                for item in obj:
                    list_result.append(self.numpy_to_python(item, max_depth, current_depth + 1))
                result = list_result
            else:
                # Handle other types
                result = obj
            
            # Cache the result
            self.extraction_cache[obj_id] = result
            return result
            
        except Exception as e:
            error_result = {
                "type": "conversion_error",
                "error": str(e),
                "object_type": str(type(obj)),
                "depth": current_depth
            }
            self.extraction_cache[obj_id] = error_result
            return error_result
        finally:
            # Remove from processing stack
            self.processing_stack.discard(obj_id)
    
    def extract_nested_field(self, data: np.ndarray, field_path: List[str]) -> Any:
        """Extract a nested field from structured numpy array."""
        current_data = data
        traversal_path = []
        
        for field in field_path:
            traversal_path.append(field)
            
            if hasattr(current_data.dtype, 'names') and field in current_data.dtype.names:
                current_data = current_data[field][0, 0]
            else:
                print(f"Field '{field}' not found in path {' -> '.join(traversal_path)}")
                print(f"Available fields: {current_data.dtype.names if hasattr(current_data.dtype, 'names') else 'None'}")
                return None
                
        return current_data
    
    def get_dependency_properties(self, dep_id: int, cycle_number: int) -> Dict[str, Any]:
        """Extract all dependency object properties for a given ID and cycle."""
        # Initialize meaningful variable storage
        extraction_metadata = {
            "dep_id": dep_id,
            "cycle_number": cycle_number,
            "extraction_timestamp": None,
            "processing_stats": {
                "cache_hits": 0,
                "cache_misses": 0,
                "circular_references": 0,
                "max_depth_exceeded": 0,
                "conversion_errors": 0
            }
        }
        
        dependency_properties = {}
        time_information = {}
        data_structure_info = {}
        extraction_errors = []
        
        # Clear cache and processing stack for new extraction
        self.extraction_cache.clear()
        self.processing_stack.clear()
        
        try:
            # Get time information
            if self.time_data is not None and 0 <= cycle_number < len(self.time_data):
                time_information = {
                    "cycle_timestamp": float(self.time_data[cycle_number]),
                    "total_cycles": len(self.time_data),
                    "cycle_index": cycle_number,
                    "time_range": {
                        "start": float(self.time_data[0]),
                        "end": float(self.time_data[-1])
                    }
                }
                extraction_metadata["extraction_timestamp"] = time_information["cycle_timestamp"]
            
            # Navigate to the dependency values with improved error handling
            list_memory_data = self.extract_nested_field(self.dep_data, ['m_listMemory'])
            if list_memory_data is None:
                extraction_errors.append("Could not access m_listMemory field")
                return self._create_error_result(extraction_metadata, extraction_errors)
            
            m_value_data = self.extract_nested_field(list_memory_data, ['m_value'])
            if m_value_data is None:
                extraction_errors.append("Could not access m_value field")
                return self._create_error_result(extraction_metadata, extraction_errors)
            
            inner_m_value_data = self.extract_nested_field(m_value_data, ['m_value'])
            if inner_m_value_data is None:
                extraction_errors.append("Could not access inner m_value field")
                return self._create_error_result(extraction_metadata, extraction_errors)
            
            # Store data structure information
            data_structure_info = {
                "data_shape": str(self.dep_data.shape),
                "data_dtype": str(self.dep_data.dtype),
                "available_fields": list(self.dep_data.dtype.names) if hasattr(self.dep_data.dtype, 'names') else [],
                "inner_data_shape": str(inner_m_value_data.shape) if hasattr(inner_m_value_data, 'shape') else "N/A",
                "inner_data_dtype": str(inner_m_value_data.dtype) if hasattr(inner_m_value_data, 'dtype') else "N/A"
            }
            
            # Check if we have structured dependency data
            if hasattr(inner_m_value_data.dtype, 'names') and inner_m_value_data.dtype.names:
                available_fields = inner_m_value_data.dtype.names
                print(f"Available fields in dependency data: {available_fields}")
                
                # Extract all available fields with improved processing
                for field_name in available_fields:
                    try:
                        field_data = inner_m_value_data[field_name][0, 0]
                        processed_field_data = self._process_field_data(
                            field_data, field_name, dep_id, cycle_number
                        )
                        dependency_properties[field_name] = processed_field_data
                        
                    except Exception as e:
                        error_msg = f"Error extracting field '{field_name}': {str(e)}"
                        extraction_errors.append(error_msg)
                        dependency_properties[field_name] = {
                            "type": "field_extraction_error",
                            "error": error_msg,
                            "field_name": field_name
                        }
                        
            else:
                # If not structured, treat as array data
                processed_array_data = self._process_array_data(
                    inner_m_value_data, dep_id, cycle_number
                )
                dependency_properties["array_data"] = processed_array_data
            
            # Calculate processing statistics
            self._calculate_processing_stats(extraction_metadata)
            
        except Exception as e:
            extraction_errors.append(f"Error extracting dependency properties: {str(e)}")
        
        # Compile final result
        final_result = {
            "metadata": extraction_metadata,
            "time_information": time_information,
            "data_structure_info": data_structure_info,
            "dependency_properties": dependency_properties,
            "extraction_errors": extraction_errors,
            "cache_statistics": {
                "total_cached_objects": len(self.extraction_cache),
                "processing_stack_size": len(self.processing_stack)
            }
        }
        
        return final_result
    
    def _process_field_data(self, field_data: Any, field_name: str, dep_id: int, cycle_number: int) -> Dict[str, Any]:
        """Process individual field data with proper error handling."""
        field_result = {
            "field_name": field_name,
            "data_type": str(type(field_data)),
            "processed_value": None,
            "extraction_method": "unknown"
        }
        
        try:
            # Handle different data types
            if hasattr(field_data, 'shape'):
                if field_data.shape == ():
                    # Scalar value
                    field_result["processed_value"] = self.numpy_to_python(field_data)
                    field_result["extraction_method"] = "scalar_extraction"
                    
                elif len(field_data.shape) >= 2:
                    # Multi-dimensional array - extract slice for given cycle
                    if cycle_number < field_data.shape[-1]:
                        if len(field_data.shape) == 2:
                            # 2D array - extract column for cycle
                            if dep_id < field_data.shape[0]:
                                extracted_value = field_data[dep_id, cycle_number]
                                field_result["processed_value"] = self.numpy_to_python(extracted_value)
                                field_result["extraction_method"] = "2d_indexed_extraction"
                            else:
                                extracted_value = field_data[:, cycle_number]
                                field_result["processed_value"] = self.numpy_to_python(extracted_value)
                                field_result["extraction_method"] = "2d_column_extraction"
                        else:
                            # Higher dimensional array - extract relevant slice
                            if dep_id < field_data.shape[0]:
                                extracted_value = field_data[dep_id, ..., cycle_number]
                                field_result["processed_value"] = self.numpy_to_python(extracted_value)
                                field_result["extraction_method"] = "nd_indexed_extraction"
                            else:
                                extracted_value = field_data[..., cycle_number]
                                field_result["processed_value"] = self.numpy_to_python(extracted_value)
                                field_result["extraction_method"] = "nd_slice_extraction"
                    else:
                        field_result["processed_value"] = {
                            "type": "index_out_of_range",
                            "requested_cycle": cycle_number,
                            "max_cycle": field_data.shape[-1] - 1,
                            "field_shape": field_data.shape
                        }
                        field_result["extraction_method"] = "index_error"
                else:
                    # 1D array or other format
                    field_result["processed_value"] = self.numpy_to_python(field_data)
                    field_result["extraction_method"] = "1d_array_extraction"
                    
                # Add shape information
                field_result["data_shape"] = field_data.shape
                field_result["data_size"] = field_data.size
                
            else:
                field_result["processed_value"] = self.numpy_to_python(field_data)
                field_result["extraction_method"] = "direct_conversion"
                
        except Exception as e:
            field_result["processed_value"] = {
                "type": "field_processing_error",
                "error": str(e),
                "field_name": field_name
            }
            field_result["extraction_method"] = "error"
            
        return field_result
    
    def _process_array_data(self, array_data: Any, dep_id: int, cycle_number: int) -> Dict[str, Any]:
        """Process array data when structured fields are not available."""
        array_result = {
            "data_type": str(type(array_data)),
            "processed_value": None,
            "extraction_method": "unknown"
        }
        
        try:
            if hasattr(array_data, 'shape') and len(array_data.shape) >= 2:
                if dep_id < array_data.shape[0] and cycle_number < array_data.shape[-1]:
                    extracted_value = array_data[dep_id, cycle_number]
                    array_result["processed_value"] = self.numpy_to_python(extracted_value)
                    array_result["extraction_method"] = "indexed_array_extraction"
                else:
                    array_result["processed_value"] = {
                        "type": "index_out_of_bounds",
                        "requested_indices": {"dep_id": dep_id, "cycle": cycle_number},
                        "array_shape": array_data.shape
                    }
                    array_result["extraction_method"] = "index_error"
            else:
                array_result["processed_value"] = self.numpy_to_python(array_data)
                array_result["extraction_method"] = "raw_data_extraction"
                
            # Add shape information
            if hasattr(array_data, 'shape'):
                array_result["data_shape"] = array_data.shape
                array_result["data_size"] = array_data.size
                
        except Exception as e:
            array_result["processed_value"] = {
                "type": "array_processing_error",
                "error": str(e)
            }
            array_result["extraction_method"] = "error"
            
        return array_result
    
    def _calculate_processing_stats(self, metadata: Dict[str, Any]) -> None:
        """Calculate processing statistics from cached results."""
        stats = metadata["processing_stats"]
        
        for cached_result in self.extraction_cache.values():
            if isinstance(cached_result, dict):
                result_type = cached_result.get("type", "")
                if result_type == "circular_reference":
                    stats["circular_references"] += 1
                elif result_type == "max_depth_exceeded":
                    stats["max_depth_exceeded"] += 1
                elif result_type == "conversion_error":
                    stats["conversion_errors"] += 1
        
        stats["cache_hits"] = len(self.extraction_cache)
    
    def _create_error_result(self, metadata: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """Create a standardized error result."""
        return {
            "metadata": metadata,
            "time_information": {},
            "data_structure_info": {},
            "dependency_properties": {},
            "extraction_errors": errors,
            "cache_statistics": {
                "total_cached_objects": len(self.extraction_cache),
                "processing_stack_size": len(self.processing_stack)
            }
        }

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