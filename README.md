# Dependency Data Extractor

A Python tool for extracting dependency object properties from MATLAB workspace files based on dependency ID and cycle number, outputting results in JSON format.

## Overview

This tool extracts dependency data from the path `g_PerDepRunnable_m_depPort_out.m_listMemory.m_value.m_value.m_values.m_id` and provides structured JSON output containing all dependency object properties for a given dependency ID and cycle number.

## Features

- Extract dependency properties from MATLAB `.mat` files
- Support for time-series data with cycle-based indexing
- JSON output format for easy integration with other tools
- Summary and exploration capabilities
- Handles complex nested MATLAB structures
- Comprehensive error handling and logging

## Requirements

- Python 3.x
- scipy (for MATLAB file reading)
- numpy (for array processing)

## Installation

The required packages were installed during setup:

```bash
# System packages (already installed)
sudo apt install python3-scipy python3-numpy python3-h5py
```

## Usage

### Basic Usage

Extract dependency properties for a specific dependency ID and cycle:

```bash
python3 dependency_extractor.py <dep_id> <cycle_number>
```

Example:
```bash
python3 dependency_extractor.py 0 0
```

### Summary Information

Get an overview of the dependency data structure:

```bash
python3 dependency_extractor.py --summary
```

### Available Cycles

List all available cycle numbers:

```bash
python3 dependency_extractor.py --cycles
```

## Output Format

The tool outputs JSON with the following structure:

```json
{
  "dep_id": 0,
  "cycle_number": 0,
  "timestamp": 1663942546803.0,
  "properties": {
    "m_values": {
      "m_measuredState": "...",
      "m_predictedState": "...",
      "m_refPoint": "...",
      "m_responsible": "...",
      "m_stateToUpdate": "...",
      "m_type": "...",
      "m_updatedState": "...",
      "m_used": "..."
    }
  },
  "metadata": {
    "extraction_method": "structured_array_navigation",
    "data_source": "g_PerDepRunnable_m_depPort_out",
    "total_cycles": 942,
    "data_shape": "(1, 1)",
    "available_fields": [
      "m_collectionData",
      "m_listMemory",
      "m_listMetaData",
      "m_receivedValidUpdateExternal",
      "m_sequenceNumber",
      "time"
    ]
  }
}
```

### Key Fields

- **dep_id**: The requested dependency ID
- **cycle_number**: The requested cycle number
- **timestamp**: Unix timestamp for the cycle
- **properties**: All dependency object properties and their values
- **metadata**: Information about the extraction process and data structure

## Data Structure

The tool navigates the following MATLAB structure:

```
g_PerDepRunnable_m_depPort_out
└── m_listMemory
    └── m_value
        └── m_value
            └── m_values
                ├── m_measuredState
                ├── m_predictedState
                ├── m_refPoint
                ├── m_responsible
                ├── m_stateToUpdate
                ├── m_type
                ├── m_updatedState
                └── m_used
```

## Available Data

Based on the analysis of `subset.mat`:

- **Total cycles**: 942 (numbered 0 to 941)
- **Time range**: From 1663942546803.0 to 1663942664801.0 (Unix timestamps)
- **Data dimensions**: The dependency data contains multi-dimensional arrays with shape (32, 942) for most fields
- **Dependency variables**: 6 dependency-related variables found in the workspace

## Properties Extracted

The tool extracts various dependency object properties including:

- **m_measuredState**: Current measured state of the dependency
- **m_predictedState**: Predicted state information
- **m_refPoint**: Reference point data
- **m_responsible**: Responsibility flags
- **m_stateToUpdate**: State update information
- **m_type**: Type classification
- **m_updatedState**: Updated state data
- **m_used**: Usage flags
- **m_allActiveSensorTypesContributedInLastCycle**: Sensor contribution data
- **m_timePassedSinceAllActiveSensorTypesContributed**: Time tracking
- **m_totalNumSensorUpdates**: Update counters
- **m_untrustworthyUpdates**: Trust indicators

## Error Handling

The tool provides comprehensive error handling:

- Invalid dependency IDs or cycle numbers
- Missing data structures
- JSON serialization issues
- File access problems

## Examples

### Extract specific dependency data:
```bash
python3 dependency_extractor.py 0 100
```

### Check available cycles:
```bash
python3 dependency_extractor.py --cycles
```

### Get data structure summary:
```bash
python3 dependency_extractor.py --summary
```

## Technical Details

### Data Processing

1. **MATLAB File Loading**: Uses scipy.io.loadmat to read the .mat file
2. **Structure Navigation**: Navigates nested MATLAB structures using field names
3. **Data Extraction**: Extracts data for specific dependency ID and cycle
4. **JSON Conversion**: Converts numpy arrays and complex data types to JSON-serializable formats

### Array Handling

- Large arrays (>100 elements) are summarized with metadata and sample values
- Structured arrays are converted to nested dictionaries
- Multi-dimensional arrays are sliced based on dependency ID and cycle number

### Time Synchronization

- Time data is extracted from the `time` field in the dependency structure
- Cycles are mapped to actual timestamps
- Supports time-based queries and analysis

## Limitations

- Currently designed for the specific MATLAB structure in `subset.mat`
- Dependency IDs are treated as array indices (0-based)
- Large arrays are truncated in JSON output to prevent memory issues
- Requires the exact field structure as found in the analyzed file

## Troubleshooting

### Common Issues

1. **"Dependency data not found"**: Ensure the MATLAB file contains `g_PerDepRunnable_m_depPort_out`
2. **"Index out of bounds"**: Check that dependency ID and cycle number are within valid ranges
3. **"JSON serialization error"**: Some complex numpy types may need additional handling

### Debug Information

The tool provides verbose output including:
- Available fields in the data structure
- Data shapes and types
- Navigation path through the nested structure

## Integration

The JSON output can be easily integrated with:
- Data analysis tools (Python, R, MATLAB)
- Monitoring systems
- Report generation tools
- Database storage systems

## File Structure

```
workspace/
├── subset.mat              # Input MATLAB file
├── dependency_extractor.py # Main extraction tool
├── README.md               # This documentation
├── fetch_insight_data.m    # Original MATLAB analysis script
└── FUS_INDEX_ANALYSIS.md   # Analysis documentation
```

## Future Enhancements

Possible improvements:
- Support for multiple MATLAB file formats
- Batch processing of multiple dependency IDs
- Export to different formats (CSV, XML)
- Real-time monitoring capabilities
- Advanced filtering and querying options