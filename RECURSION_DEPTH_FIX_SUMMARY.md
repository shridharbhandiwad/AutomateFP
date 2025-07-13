# Recursion Depth Fix and Variable Storage Improvements

## Summary

Successfully fixed the recursion depth error in `dependency_extractor.py` and improved variable storage for better data processing. The script now handles complex nested numpy data structures without infinite recursion and provides comprehensive, well-organized output.

## Key Improvements Made

### 1. **Recursion Depth Control**
- Added `max_depth` parameter (default: 10) to `numpy_to_python()` method
- Implemented `current_depth` tracking to prevent stack overflow
- Added graceful handling when maximum depth is exceeded

### 2. **Circular Reference Detection**
- Implemented `processing_stack` to track objects being processed
- Added object ID tracking using `id(obj)` to detect circular references
- Prevents infinite loops when encountering circular data structures

### 3. **Caching System**
- Added `extraction_cache` to store already processed objects
- Prevents reprocessing of the same objects
- Improves performance and reduces memory usage

### 4. **Enhanced Variable Storage**
The `get_dependency_properties()` method now returns well-organized data in meaningful variables:

#### **extraction_metadata**
- Contains processing metadata and statistics
- Tracks cache hits, circular references, max depth exceeded cases
- Includes timing information and extraction parameters

#### **dependency_properties**
- Contains extracted dependency properties with detailed field information
- Each field includes:
  - Field name and data type
  - Processed value with appropriate conversion
  - Extraction method used
  - Shape and size information

#### **time_information**
- Comprehensive timing data including:
  - Cycle timestamp and index
  - Total cycles and time range
  - Time bounds (start/end)

#### **data_structure_info**
- Information about the data structure:
  - Data shape and data type
  - Available fields
  - Inner data structure details

#### **extraction_errors**
- List of any errors encountered during processing
- Detailed error messages for debugging

#### **cache_statistics**
- Statistics about object caching
- Processing stack size information

### 5. **Helper Methods**
Added several helper methods to improve code organization:

- `_process_field_data()`: Processes individual field data with comprehensive error handling
- `_process_array_data()`: Handles array data when structured fields aren't available
- `_calculate_processing_stats()`: Calculates processing statistics from cached results
- `_create_error_result()`: Creates standardized error results

### 6. **Enhanced Error Handling**
- Graceful degradation when errors occur
- Detailed error messages with context
- Comprehensive logging of processing statistics
- Better handling of different data types and edge cases

### 7. **Improved Data Processing**
- Better handling of large numpy arrays
- Statistical information for large arrays (min, max, mean, std)
- Sample values for large arrays to prevent memory issues
- Proper handling of different extraction methods (2D indexed, column extraction, etc.)

## Test Results

The script now successfully:
- ✅ Runs without recursion depth errors
- ✅ Processes complex nested numpy data structures
- ✅ Provides comprehensive variable storage
- ✅ Handles large arrays efficiently
- ✅ Tracks processing statistics
- ✅ Provides detailed error handling
- ✅ Offers multiple extraction methods (--summary, --cycles, specific extraction)

## Usage Examples

```bash
# Get summary of dependency data
python3 dependency_extractor.py --summary

# Get available cycles
python3 dependency_extractor.py --cycles

# Extract specific dependency properties
python3 dependency_extractor.py 0 0
```

## Performance Improvements

- **Memory Usage**: Reduced through caching and efficient array handling
- **Processing Speed**: Improved through object caching and circular reference detection
- **Robustness**: Enhanced error handling and graceful degradation
- **Debugging**: Comprehensive logging and statistics for troubleshooting

The recursion depth error has been completely resolved, and the script now provides a robust, efficient solution for extracting dependency data from MATLAB files.