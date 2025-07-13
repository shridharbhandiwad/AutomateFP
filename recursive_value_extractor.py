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
        # Properly handle depth limit to prevent recursion depth errors
        if indent >= max_depth:
            return {
                "error": "Maximum recursion depth reached",
                "path": path,
                "depth": indent,
                "max_depth": max_depth,
                "type": str(type(data)),
                "data_info": self.display_value_info(data, 0)
            }
        
        # Initialize result with meaningful variables
        result = {
            "extraction_path": path,
            "current_depth": indent,
            "max_depth": max_depth,
            "data_type": str(type(data)),
            "extraction_status": "success"
        }
        
        prefix = "  " * indent
        
        print(f"{prefix}Exploring path: {path}")
        print(f"{prefix}Data type: {type(data)}")
        print(f"{prefix}Current depth: {indent}/{max_depth}")
        
        try:
            if isinstance(data, np.ndarray):
                if data.dtype.names is not None:
                    # Structured array processing
                    print(f"{prefix}Structured array with fields: {list(data.dtype.names)}")
                    print(f"{prefix}Shape: {data.shape}")
                    
                    # Store meaningful variables for structured arrays
                    structured_array_info = {
                        "array_type": "structured",
                        "shape": data.shape,
                        "field_names": list(data.dtype.names),
                        "field_count": len(data.dtype.names),
                        "total_size": data.size,
                        "dtype": str(data.dtype)
                    }
                    
                    result.update(structured_array_info)
                    result["field_values"] = {}
                    
                    # Process each field with proper depth control
                    for field_name in data.dtype.names:
                        field_path = f"{path}.{field_name}" if path else field_name
                        print(f"{prefix}Processing field: {field_name}")
                        
                        try:
                            # Extract field data safely
                            field_data = data[field_name][0, 0] if data.shape == (1, 1) else data[field_name]
                            field_info = self.display_value_info(field_data, indent + 1)
                            print(f"{prefix}  {field_info}")
                            
                            # Store field metadata
                            field_metadata = {
                                "field_name": field_name,
                                "field_path": field_path,
                                "field_type": str(type(field_data)),
                                "field_info": field_info
                            }
                            
                            # Recursively process field if it's a structured array and we haven't reached max depth
                            if (hasattr(field_data, 'dtype') and 
                                field_data.dtype.names is not None and 
                                indent + 1 < max_depth):
                                
                                field_metadata["recursive_extraction"] = self.recursively_extract_values(
                                    field_data, field_path, indent + 1, max_depth
                                )
                            else:
                                # Store the converted value without recursion
                                field_metadata["converted_value"] = self.convert_to_serializable(field_data)
                                if indent + 1 >= max_depth:
                                    field_metadata["recursion_stopped"] = "Max depth reached"
                            
                            result["field_values"][field_name] = field_metadata
                        
                        except Exception as e:
                            error_info = {
                                "field_name": field_name,
                                "error": str(e),
                                "error_type": type(e).__name__,
                                "field_path": field_path
                            }
                            print(f"{prefix}  Error accessing field {field_name}: {e}")
                            result["field_values"][field_name] = error_info
                
                else:
                    # Regular array processing
                    print(f"{prefix}Regular array: dtype={data.dtype}, shape={data.shape}")
                    
                    # Store meaningful variables for regular arrays
                    array_info = {
                        "array_type": "regular",
                        "dtype": str(data.dtype),
                        "shape": data.shape,
                        "total_size": data.size,
                        "ndim": data.ndim
                    }
                    
                    result.update(array_info)
                    
                    # Handle different array sizes appropriately
                    if data.size == 0:
                        result["array_content"] = "empty_array"
                    elif data.size == 1:
                        result["array_content"] = "single_value"
                        result["single_value"] = self.convert_to_serializable(data.item())
                    elif data.size <= 100:
                        result["array_content"] = "small_array"
                        result["values"] = data.tolist()
                    else:
                        result["array_content"] = "large_array"
                        result["sample_values"] = data.flatten()[:20].tolist()
                        result["sample_note"] = f"Array too large ({data.size} elements), showing first 20"
            
            else:
                # Scalar or other type processing
                print(f"{prefix}Scalar/Other: {self.display_value_info(data, indent)}")
                
                # Store meaningful variables for scalars
                scalar_info = {
                    "data_category": "scalar_or_other",
                    "original_type": str(type(data)),
                    "converted_value": self.convert_to_serializable(data)
                }
                
                result.update(scalar_info)
                
                # Add specific handling for common numpy types
                if isinstance(data, (np.integer, np.floating)):
                    result["numeric_value"] = data.item()
                    result["numpy_type"] = type(data).__name__
                elif isinstance(data, np.bool_):
                    result["boolean_value"] = bool(data)
                elif isinstance(data, (np.void, np.generic)):
                    result["void_string"] = str(data)
        
        except Exception as e:
            # Handle any unexpected errors
            result["extraction_status"] = "error"
            result["error"] = str(e)
            result["error_type"] = type(e).__name__
            print(f"{prefix}Error during extraction: {e}")
        
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
        
        # Initialize result with meaningful variables
        extraction_result = {
            "extraction_metadata": {
                "dep_id": dep_id,
                "cycle_number": cycle_number,
                "timestamp": None,
                "extraction_path": "g_PerDepRunnable_m_depPort_out.m_listMemory.m_value.m_value.m_values",
                "extraction_status": "in_progress",
                "max_recursion_depth": 8,  # Reduced for safety
                "extraction_levels": {}
            },
            "navigation_steps": {},
            "extracted_values": {},
            "errors": []
        }
        
        try:
            # Get timestamp information
            timestamp_info = self._extract_timestamp_info(cycle_number)
            extraction_result["extraction_metadata"]["timestamp"] = timestamp_info["timestamp"]
            extraction_result["extraction_metadata"]["timestamp_valid"] = timestamp_info["valid"]
            
            # Step 1: Navigate to g_PerDepRunnable_m_depPort_out (Root level)
            print(f"\nStep 1: Starting from g_PerDepRunnable_m_depPort_out")
            root_data = self.dep_data
            root_extraction = self.recursively_extract_values(
                root_data, "g_PerDepRunnable_m_depPort_out", 0, 3
            )
            extraction_result["navigation_steps"]["step_1_root"] = {
                "level_name": "g_PerDepRunnable_m_depPort_out",
                "description": "Root level dependency data",
                "extraction_result": root_extraction,
                "success": root_extraction.get("extraction_status") == "success"
            }
            
            # Step 2: Navigate to m_listMemory
            print(f"\nStep 2: Navigating to m_listMemory")
            listmemory_data, listmemory_success = self._navigate_to_field(root_data, 'm_listMemory')
            if listmemory_success:
                listmemory_extraction = self.recursively_extract_values(
                    listmemory_data, "m_listMemory", 0, 4
                )
                extraction_result["navigation_steps"]["step_2_listmemory"] = {
                    "level_name": "m_listMemory",
                    "description": "List memory structure",
                    "extraction_result": listmemory_extraction,
                    "success": True
                }
            else:
                self._add_navigation_error(extraction_result, "step_2_listmemory", "m_listMemory field not found")
                return extraction_result
            
            # Step 3: Navigate to m_value (first level)
            print(f"\nStep 3: Navigating to first m_value")
            first_value_data, first_value_success = self._navigate_to_field(listmemory_data, 'm_value')
            if first_value_success:
                first_value_extraction = self.recursively_extract_values(
                    first_value_data, "m_value (first)", 0, 4
                )
                extraction_result["navigation_steps"]["step_3_first_value"] = {
                    "level_name": "m_value (first)",
                    "description": "First level value structure",
                    "extraction_result": first_value_extraction,
                    "success": True
                }
            else:
                self._add_navigation_error(extraction_result, "step_3_first_value", "First m_value field not found")
                return extraction_result
            
            # Step 4: Navigate to m_value (second level)
            print(f"\nStep 4: Navigating to second m_value")
            second_value_data, second_value_success = self._navigate_to_field(first_value_data, 'm_value')
            if second_value_success:
                second_value_extraction = self.recursively_extract_values(
                    second_value_data, "m_value (second)", 0, 4
                )
                extraction_result["navigation_steps"]["step_4_second_value"] = {
                    "level_name": "m_value (second)",
                    "description": "Second level value structure",
                    "extraction_result": second_value_extraction,
                    "success": True
                }
            else:
                self._add_navigation_error(extraction_result, "step_4_second_value", "Second m_value field not found")
                return extraction_result
            
            # Step 5: Navigate to m_values and extract specific values
            print(f"\nStep 5: Navigating to m_values and extracting for dep_id={dep_id}, cycle={cycle_number}")
            final_values_extraction = self._extract_final_values(second_value_data, dep_id, cycle_number)
            extraction_result["navigation_steps"]["step_5_final_values"] = {
                "level_name": "m_values",
                "description": "Final values extraction",
                "extraction_result": final_values_extraction,
                "success": final_values_extraction.get("extraction_status") == "success"
            }
            
            # Store all extracted values in meaningful variables
            extraction_result["extracted_values"] = self._organize_extracted_values(
                extraction_result["navigation_steps"], dep_id, cycle_number
            )
            
            # Update extraction status
            extraction_result["extraction_metadata"]["extraction_status"] = "completed"
            
        except Exception as e:
            extraction_result["extraction_metadata"]["extraction_status"] = "error"
            extraction_result["errors"].append({
                "error_type": type(e).__name__,
                "error_message": str(e),
                "error_location": "main_extraction_loop"
            })
            print(f"Error during extraction: {e}")
        
        return extraction_result
    
    def _extract_timestamp_info(self, cycle_number: int) -> Dict[str, Any]:
        """Extract timestamp information for the given cycle."""
        timestamp_info = {
            "cycle_number": cycle_number,
            "timestamp": None,
            "valid": False,
            "total_cycles": len(self.time_data) if self.time_data is not None else 0
        }
        
        if self.time_data is not None and 0 <= cycle_number < len(self.time_data):
            timestamp_info["timestamp"] = float(self.time_data[cycle_number])
            timestamp_info["valid"] = True
            print(f"Timestamp for cycle {cycle_number}: {timestamp_info['timestamp']}")
        else:
            print(f"Warning: Cycle {cycle_number} out of range or no time data available")
        
        return timestamp_info
    
    def _navigate_to_field(self, data: Any, field_name: str) -> tuple[Any, bool]:
        """Safely navigate to a field in structured data."""
        try:
            if hasattr(data.dtype, 'names') and field_name in data.dtype.names:
                field_data = data[field_name][0, 0]
                return field_data, True
            else:
                print(f"Field '{field_name}' not found in data structure")
                return None, False
        except Exception as e:
            print(f"Error navigating to field '{field_name}': {e}")
            return None, False
    
    def _add_navigation_error(self, result: Dict[str, Any], step_name: str, error_message: str):
        """Add a navigation error to the result."""
        result["navigation_steps"][step_name] = {
            "level_name": step_name,
            "description": "Navigation failed",
            "extraction_result": {"error": error_message},
            "success": False
        }
        result["errors"].append({
            "error_type": "NavigationError",
            "error_message": error_message,
            "error_location": step_name
        })
        result["extraction_metadata"]["extraction_status"] = "error"
    
    def _extract_final_values(self, data: Any, dep_id: int, cycle_number: int) -> Dict[str, Any]:
        """Extract final values from the m_values structure."""
        final_extraction = {
            "extraction_status": "success",
            "dep_id": dep_id,
            "cycle_number": cycle_number,
            "available_fields": [],
            "field_extractions": {},
            "extraction_summary": {}
        }
        
        try:
            if hasattr(data.dtype, 'names'):
                available_fields = list(data.dtype.names)
                final_extraction["available_fields"] = available_fields
                
                print(f"Available fields at final level: {available_fields}")
                
                # Extract values for each field
                for field_name in available_fields:
                    field_extraction = self._extract_field_values(
                        data, field_name, dep_id, cycle_number
                    )
                    final_extraction["field_extractions"][field_name] = field_extraction
                
                # Create extraction summary
                final_extraction["extraction_summary"] = self._create_extraction_summary(
                    final_extraction["field_extractions"]
                )
                
            else:
                final_extraction["extraction_status"] = "error"
                final_extraction["error"] = "No structured fields found at final level"
                
        except Exception as e:
            final_extraction["extraction_status"] = "error"
            final_extraction["error"] = str(e)
            final_extraction["error_type"] = type(e).__name__
        
        return final_extraction
    
    def _extract_field_values(self, data: Any, field_name: str, dep_id: int, cycle_number: int) -> Dict[str, Any]:
        """Extract values from a specific field."""
        field_extraction = {
            "field_name": field_name,
            "extraction_status": "success",
            "field_metadata": {},
            "extracted_data": {},
            "extraction_method": "unknown"
        }
        
        try:
            field_data = data[field_name][0, 0]
            
            # Store field metadata
            field_extraction["field_metadata"] = {
                "field_type": str(type(field_data)),
                "field_shape": getattr(field_data, 'shape', 'N/A'),
                "field_size": getattr(field_data, 'size', 'N/A'),
                "field_dtype": str(getattr(field_data, 'dtype', 'N/A'))
            }
            
            print(f"\nProcessing field: {field_name}")
            print(f"Field metadata: {field_extraction['field_metadata']}")
            
            # Handle multi-dimensional arrays
            if hasattr(field_data, 'shape') and len(field_data.shape) >= 2:
                field_extraction["extraction_method"] = "multi_dimensional_array"
                field_extraction["extracted_data"] = self._extract_from_multidim_array(
                    field_data, dep_id, cycle_number
                )
            else:
                # 1D array or scalar
                field_extraction["extraction_method"] = "scalar_or_1d_array"
                field_extraction["extracted_data"] = {
                    "full_value": self.convert_to_serializable(field_data),
                    "extraction_note": "Full value extracted (not cycle-specific)"
                }
            
        except Exception as e:
            field_extraction["extraction_status"] = "error"
            field_extraction["error"] = str(e)
            field_extraction["error_type"] = type(e).__name__
        
        return field_extraction
    
    def _extract_from_multidim_array(self, field_data: Any, dep_id: int, cycle_number: int) -> Dict[str, Any]:
        """Extract values from multi-dimensional arrays."""
        extraction_data = {
            "array_shape": field_data.shape,
            "extraction_success": False,
            "extracted_values": {},
            "extraction_indices": []
        }
        
        try:
            if cycle_number < field_data.shape[-1]:
                if len(field_data.shape) == 2:
                    # 2D array
                    if dep_id < field_data.shape[0]:
                        # Extract specific value
                        extracted_value = field_data[dep_id, cycle_number]
                        extraction_data["extracted_values"]["specific_value"] = self.convert_to_serializable(extracted_value)
                        extraction_data["extraction_indices"] = [dep_id, cycle_number]
                        extraction_data["extraction_type"] = "specific_value"
                    else:
                        # Extract entire column for the cycle
                        extracted_values = field_data[:, cycle_number]
                        extraction_data["extracted_values"]["column_values"] = self.convert_to_serializable(extracted_values)
                        extraction_data["extraction_indices"] = ["all", cycle_number]
                        extraction_data["extraction_type"] = "column_values"
                else:
                    # Higher dimensional array
                    if dep_id < field_data.shape[0]:
                        extracted_value = field_data[dep_id, ..., cycle_number]
                        extraction_data["extracted_values"]["multidim_value"] = self.convert_to_serializable(extracted_value)
                        extraction_data["extraction_indices"] = [dep_id, "...", cycle_number]
                        extraction_data["extraction_type"] = "multidim_specific"
                    else:
                        extracted_values = field_data[..., cycle_number]
                        extraction_data["extracted_values"]["multidim_slice"] = self.convert_to_serializable(extracted_values)
                        extraction_data["extraction_indices"] = ["all", cycle_number]
                        extraction_data["extraction_type"] = "multidim_slice"
                
                extraction_data["extraction_success"] = True
                print(f"Successfully extracted values: {extraction_data['extraction_type']}")
                
            else:
                extraction_data["error"] = f"Cycle {cycle_number} out of range (max: {field_data.shape[-1]-1})"
                print(f"Error: {extraction_data['error']}")
                
        except Exception as e:
            extraction_data["error"] = str(e)
            extraction_data["error_type"] = type(e).__name__
        
        return extraction_data
    
    def _create_extraction_summary(self, field_extractions: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of all extracted values."""
        summary = {
            "total_fields_processed": len(field_extractions),
            "successful_extractions": 0,
            "failed_extractions": 0,
            "extraction_methods": {},
            "extracted_value_types": {},
            "meaningful_values": {}
        }
        
        for field_name, field_extraction in field_extractions.items():
            if field_extraction["extraction_status"] == "success":
                summary["successful_extractions"] += 1
                
                # Track extraction methods
                method = field_extraction["extraction_method"]
                summary["extraction_methods"][method] = summary["extraction_methods"].get(method, 0) + 1
                
                # Store meaningful values
                if "extracted_data" in field_extraction:
                    summary["meaningful_values"][field_name] = field_extraction["extracted_data"]
                
            else:
                summary["failed_extractions"] += 1
        
        return summary
    
    def _organize_extracted_values(self, navigation_steps: Dict[str, Any], dep_id: int, cycle_number: int) -> Dict[str, Any]:
        """Organize all extracted values into meaningful variables."""
        organized_values = {
            "extraction_parameters": {
                "dep_id": dep_id,
                "cycle_number": cycle_number
            },
            "navigation_data": {},
            "final_extracted_values": {},
            "value_hierarchy": {},
            "extraction_statistics": {}
        }
        
        # Process navigation steps
        for step_name, step_data in navigation_steps.items():
            if step_data["success"]:
                organized_values["navigation_data"][step_name] = {
                    "level_name": step_data["level_name"],
                    "description": step_data["description"],
                    "key_fields": step_data["extraction_result"].get("field_names", []),
                    "data_type": step_data["extraction_result"].get("array_type", "unknown")
                }
        
        # Process final values
        if "step_5_final_values" in navigation_steps:
            final_step = navigation_steps["step_5_final_values"]
            if final_step["success"]:
                extraction_result = final_step["extraction_result"]
                
                # Store final extracted values
                organized_values["final_extracted_values"] = extraction_result.get("field_extractions", {})
                
                # Create value hierarchy
                organized_values["value_hierarchy"] = self._create_value_hierarchy(
                    extraction_result.get("field_extractions", {})
                )
                
                # Store extraction statistics
                organized_values["extraction_statistics"] = extraction_result.get("extraction_summary", {})
        
        return organized_values
    
    def _create_value_hierarchy(self, field_extractions: Dict[str, Any]) -> Dict[str, Any]:
        """Create a hierarchical view of extracted values."""
        hierarchy = {
            "numeric_values": {},
            "array_values": {},
            "structured_values": {},
            "error_values": {}
        }
        
        for field_name, field_extraction in field_extractions.items():
            if field_extraction["extraction_status"] == "success":
                extracted_data = field_extraction.get("extracted_data", {})
                
                # Categorize values
                if "specific_value" in extracted_data:
                    hierarchy["numeric_values"][field_name] = extracted_data["specific_value"]
                elif "column_values" in extracted_data:
                    hierarchy["array_values"][field_name] = extracted_data["column_values"]
                elif "multidim_value" in extracted_data:
                    hierarchy["structured_values"][field_name] = extracted_data["multidim_value"]
                elif "full_value" in extracted_data:
                    hierarchy["structured_values"][field_name] = extracted_data["full_value"]
            else:
                hierarchy["error_values"][field_name] = field_extraction.get("error", "Unknown error")
        
        return hierarchy

def main():
    """Main function to handle command line arguments and execute extraction."""
    if len(sys.argv) < 3:
        print("Usage: python recursive_value_extractor.py <dep_id> <cycle_number>")
        print("Example: python recursive_value_extractor.py 0 100")
        sys.exit(1)
    
    try:
        dep_id = int(sys.argv[1])
        cycle_number = int(sys.argv[2])
        
        print(f"Initializing RecursiveValueExtractor with improved recursion depth control...")
        extractor = RecursiveValueExtractor()
        
        print(f"Starting extraction for dep_id={dep_id}, cycle_number={cycle_number}")
        extraction_result = extractor.extract_values_for_dep_and_cycle(dep_id, cycle_number)
        
        # Display extraction summary
        print(f"\n{'='*60}")
        print("EXTRACTION SUMMARY")
        print(f"{'='*60}")
        
        metadata = extraction_result.get("extraction_metadata", {})
        print(f"Extraction Status: {metadata.get('extraction_status', 'unknown')}")
        print(f"Dep ID: {metadata.get('dep_id', 'N/A')}")
        print(f"Cycle Number: {metadata.get('cycle_number', 'N/A')}")
        print(f"Timestamp: {metadata.get('timestamp', 'N/A')}")
        print(f"Max Recursion Depth: {metadata.get('max_recursion_depth', 'N/A')}")
        
        # Display navigation steps summary
        navigation_steps = extraction_result.get("navigation_steps", {})
        print(f"\nNavigation Steps: {len(navigation_steps)}")
        for step_name, step_data in navigation_steps.items():
            status = "✓" if step_data.get("success", False) else "✗"
            print(f"  {status} {step_data.get('level_name', step_name)}: {step_data.get('description', 'N/A')}")
        
        # Display extracted values summary
        extracted_values = extraction_result.get("extracted_values", {})
        if "extraction_statistics" in extracted_values:
            stats = extracted_values["extraction_statistics"]
            print(f"\nExtraction Statistics:")
            print(f"  Total Fields Processed: {stats.get('total_fields_processed', 0)}")
            print(f"  Successful Extractions: {stats.get('successful_extractions', 0)}")
            print(f"  Failed Extractions: {stats.get('failed_extractions', 0)}")
            
            # Show extraction methods
            methods = stats.get('extraction_methods', {})
            if methods:
                print(f"  Extraction Methods Used:")
                for method, count in methods.items():
                    print(f"    - {method}: {count}")
        
        # Display meaningful values summary
        if "value_hierarchy" in extracted_values:
            hierarchy = extracted_values["value_hierarchy"]
            print(f"\nExtracted Values Summary:")
            print(f"  Numeric Values: {len(hierarchy.get('numeric_values', {}))}")
            print(f"  Array Values: {len(hierarchy.get('array_values', {}))}")
            print(f"  Structured Values: {len(hierarchy.get('structured_values', {}))}")
            print(f"  Error Values: {len(hierarchy.get('error_values', {}))}")
        
        # Display any errors
        errors = extraction_result.get("errors", [])
        if errors:
            print(f"\nErrors Encountered: {len(errors)}")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error.get('error_type', 'Unknown')}: {error.get('error_message', 'N/A')}")
        
        print(f"\n{'='*60}")
        print("FULL RESULT (JSON FORMAT)")
        print(f"{'='*60}")
        print(json.dumps(extraction_result, indent=2))
        
        # Save result to file for easier analysis
        output_filename = f"extraction_result_dep{dep_id}_cycle{cycle_number}.json"
        with open(output_filename, 'w') as f:
            json.dump(extraction_result, f, indent=2)
        print(f"\nResult saved to: {output_filename}")
        
    except ValueError as e:
        print(f"Error: Invalid input - {e}")
        print("dep_id and cycle_number must be integers")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExtraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()