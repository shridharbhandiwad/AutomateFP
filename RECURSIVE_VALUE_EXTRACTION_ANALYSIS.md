# Recursive Value Extraction Analysis

## Overview

This analysis provides a comprehensive tool for recursively extracting and displaying all values in the MATLAB data structure path:
```
g_PerDepRunnable_m_depPort_out.m_listMemory.m_value.m_value.m_values
```

The tool navigates through nested MATLAB structures and displays all values at each level for a given dependency ID and cycle number.

## Key Findings

### Data Structure Overview
- **Total Cycles**: 942 (numbered 0 to 941)
- **Time Range**: 1663942546803.0 to 1663942664801.0 (Unix timestamps)
- **Data Structure Shape**: (1, 1) at root level
- **Available Fields**: m_collectionData, m_listMemory, m_listMetaData, m_receivedValidUpdateExternal, m_sequenceNumber, time

### Navigation Path Analysis

#### 1. Root Level: `g_PerDepRunnable_m_depPort_out`
- **Type**: Structured array with 6 fields
- **Shape**: (1, 1)
- **Available Fields**:
  - m_collectionData: Collection metadata
  - m_listMemory: Main memory structure
  - m_listMetaData: Metadata information
  - m_receivedValidUpdateExternal: External update flags
  - m_sequenceNumber: Sequence numbering
  - time: Timestamp data

#### 2. Level 2: `m_listMemory`
- **Type**: Structured array with 2 fields
- **Shape**: (1, 1)
- **Available Fields**:
  - m_ownership: Ownership information
  - m_value: Next level value structure

#### 3. Level 3: `m_value` (First Level)
- **Type**: Structured array with 3 fields
- **Shape**: (1, 1)
- **Available Fields**:
  - m_next: Next pointer
  - m_prev: Previous pointer
  - m_value: Second level value structure

#### 4. Level 4: `m_value` (Second Level)
- **Type**: Structured array with 2 fields
- **Shape**: (1, 1)
- **Available Fields**:
  - m_memory: Memory data
  - m_usedElements: Used elements tracking

#### 5. Level 5: `m_values` (Target Fields)
- **Type**: Structured array with 8 main fields
- **Shape**: (1, 1)
- **Available Fields**:
  - **m_measuredState**: Current measured state (shape: 32x942)
  - **m_predictedState**: Predicted state information (shape: 32x942)
  - **m_refPoint**: Reference point data (shape: 32x942)
  - **m_responsible**: Responsibility flags (shape: 32x942)
  - **m_stateToUpdate**: State update information (shape: 32x942)
  - **m_type**: Type classification (shape: 32x942)
  - **m_updatedState**: Updated state data (shape: 32x942)
  - **m_used**: Usage flags (shape: 32x942)

### Field Details

#### Measured State (`m_measuredState`)
- **Data Type**: Multi-dimensional array
- **Shape**: (32, 942)
- **Content**: Contains covariance matrix and mu vector data
- **Sub-fields**:
  - m_covarianceMatrix: Statistical covariance data
  - m_muVector: Mean vector data

#### Predicted State (`m_predictedState`)
- **Data Type**: Multi-dimensional array
- **Shape**: (32, 942)
- **Content**: Prediction algorithms output
- **Values**: Mostly zeros with some non-zero entries for active dependencies

#### Reference Point (`m_refPoint`)
- **Data Type**: Multi-dimensional array
- **Shape**: (32, 942)
- **Content**: Reference point coordinates and metadata
- **Values**: Contains both zero and non-zero reference coordinates

#### Responsibility (`m_responsible`)
- **Data Type**: Boolean array
- **Shape**: (32, 942)
- **Content**: Flags indicating which dependencies are responsible
- **Values**: Binary flags (0 or 1)

#### State to Update (`m_stateToUpdate`)
- **Data Type**: Numerical array
- **Shape**: (32, 942)
- **Content**: State update information
- **Values**: Various numerical values including timestamps

#### Type (`m_type`)
- **Data Type**: Categorical array
- **Shape**: (32, 942)
- **Content**: Type classification for each dependency
- **Values**: Integer codes representing different types

#### Updated State (`m_updatedState`)
- **Data Type**: Multi-dimensional array
- **Shape**: (32, 942)
- **Content**: Post-update state information
- **Values**: Updated state vectors and matrices

#### Used (`m_used`)
- **Data Type**: Boolean array
- **Shape**: (32, 942)
- **Content**: Usage flags for each dependency
- **Values**: Binary flags indicating usage status

### Additional Fields Found

During recursive exploration, several additional fields were discovered:
- **m_allActiveSensorTypesContributedInLastCycle**: Sensor contribution tracking
- **m_timePassedSinceAllActiveSensorTypesContributed**: Time tracking
- **m_totalNumSensorUpdates**: Update counters
- **m_untrustworthyUpdates**: Trust indicators
- **m_updatesSinceLastSensorUpdate**: Update sequence tracking
- **m_visualSignalStatus**: Visual signal status information

## Usage Examples

### Basic Usage
```bash
python3 recursive_value_extractor.py <dep_id> <cycle_number>
```

### Example 1: Extract values for dependency 0 at cycle 0
```bash
python3 recursive_value_extractor.py 0 0
```

### Example 2: Extract values for dependency 1 at cycle 100
```bash
python3 recursive_value_extractor.py 1 100
```

### Example 3: Extract values for dependency 5 at cycle 500
```bash
python3 recursive_value_extractor.py 5 500
```

## Output Format

The tool provides:
1. **Step-by-step navigation** through the data structure
2. **Field exploration** at each level
3. **Data type information** for each field
4. **Shape and size** information
5. **Extracted values** for the specified dependency ID and cycle
6. **JSON formatted output** for easy parsing

## Technical Implementation

### Key Features
- **Recursive traversal**: Navigates through nested structures automatically
- **Type-aware extraction**: Handles different numpy data types correctly
- **Index-based access**: Extracts specific values using dependency ID and cycle number
- **Error handling**: Graceful handling of missing or invalid data
- **JSON serialization**: Converts numpy arrays to JSON-compatible format

### Data Access Pattern
1. Navigate to `g_PerDepRunnable_m_depPort_out`
2. Access `m_listMemory` field
3. Navigate to first `m_value` level
4. Navigate to second `m_value` level
5. Access `m_values` structure
6. Extract field values using `[dep_id, cycle_number]` indexing

### Array Handling
- **2D Arrays**: Extract value at `[dep_id, cycle_number]`
- **Multi-dimensional Arrays**: Extract slice at `[dep_id, ..., cycle_number]`
- **Large Arrays**: Summarize with sample values to prevent memory issues
- **Structured Arrays**: Recursively process nested fields

## Performance Considerations

### Memory Usage
- Large arrays are sampled to prevent memory overflow
- Structured arrays are processed recursively with depth limits
- JSON output is optimized for readability vs. size

### Processing Speed
- Direct numpy array access for efficiency
- Minimal data copying during extraction
- Efficient indexing for large datasets

## Error Handling

The tool handles various error conditions:
- **Index out of bounds**: When dep_id or cycle_number exceed array dimensions
- **Missing fields**: When expected structure fields are not present
- **Type errors**: When data types don't match expected formats
- **JSON serialization errors**: When numpy types can't be converted

## Limitations

1. **Memory constraints**: Large arrays are truncated in output
2. **Structure dependency**: Assumes specific MATLAB structure format
3. **Index-based access**: Requires valid dependency ID and cycle number
4. **Depth limits**: Recursive traversal has maximum depth protection

## Future Enhancements

Potential improvements:
1. **Interactive exploration**: Web-based interface for data exploration
2. **Batch processing**: Extract multiple dependencies/cycles at once
3. **Data visualization**: Graphical representation of values
4. **Export formats**: Support for CSV, Excel, and other formats
5. **Query system**: SQL-like queries for complex data extraction

## Conclusion

The recursive value extraction tool provides comprehensive access to all values in the nested MATLAB data structure. It successfully navigates through the complex hierarchy and extracts specific values based on dependency ID and cycle number, making it valuable for:

- **Debug analysis**: Understanding data flow and values
- **Performance monitoring**: Tracking changes across cycles
- **Data validation**: Verifying expected values and ranges
- **Research analysis**: Extracting data for further processing

The tool demonstrates the complexity of the dependency tracking system and provides insights into the multi-dimensional nature of the sensor fusion and state estimation processes.