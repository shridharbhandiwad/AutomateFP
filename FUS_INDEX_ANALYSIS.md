# FUS Index Analysis Report

## Objective
Find the FUS index for the activation cycle using the path: `g_PerEimTprRunnable_m_fusObjPort_out.FusObj_st.m_value_Handle_ub`

## Analysis Results

### File Structure
- **File**: `subset.mat` (MATLAB 5.0 format, 20MB)
- **Platform**: PCWIN64
- **Created**: Sun Jul 13 07:59:06 2025
- **Variable Count**: 27,389 unique variable names identified

### Search Results

#### Direct Path Components - NOT FOUND
The specific path components were not found in the .mat file:
- ❌ `g_PerEimTprRunnable` - No direct matches
- ❌ `fusObjPort` - No direct matches  
- ❌ `FusObj` - No direct matches
- ❌ `Handle_ub` - No direct matches
- ❌ `activation` - No direct matches
- ❌ `cycle` - No direct matches

#### Related Patterns - FOUND
The following related patterns were identified:

**FUS-Related Variables:**
- ✅ `fus` - Found 3 instances
- ✅ `FUs` - Found 1 instance
- ✅ `fuS` - Found 1 instance
- 🔍 FUS pattern found in binary data at position 6306772

**Global Variables (g_ prefix):**
- ✅ Found 92 variables starting with `g_`
- Examples: `Ag_B`, `Aqg_`, `Bg_`, `Cg_`, `D3tg_`, etc.

**Member Variables (m_ prefix):**
- ✅ Found 74 variables starting with `m_`
- Examples: `Dm_`, `Dm_z`, `Fm_7`, `G3om_`, `Gm_`, etc.

**Index-Related Variables:**
- ✅ `idx` - Found 2 instances
- ✅ `idxo` - Found 1 instance
- ✅ `IDX` - Found 1 instance
- ✅ `iDxc` - Found 1 instance

**AUTOSAR/Automotive-Related:**
- ✅ `swc` - Found 6 instances (Software Component)
- ✅ `Prte` - Found 1 instance (Runtime Environment)
- ✅ `Portu` - Found 1 instance (Port-related)

## Findings Summary

### What Was Found
1. **FUS-related content exists** in the binary data
2. **Global variables** with `g_` prefix are present (92 variables)
3. **Member variables** with `m_` prefix are present (74 variables)
4. **Index-related** variables exist
5. **AUTOSAR/automotive** terminology is present

### What Was NOT Found
1. The specific variable path `g_PerEimTprRunnable_m_fusObjPort_out.FusObj_st.m_value_Handle_ub`
2. Direct matches for `PerEimTprRunnable`, `fusObjPort`, `FusObj`, `Handle_ub`
3. Activation cycle related variables
4. Clear numeric index values associated with FUS

## Recommendations

### 1. Check Alternative Sources
The specific path `g_PerEimTprRunnable_m_fusObjPort_out.FusObj_st.m_value_Handle_ub` suggests this might be:
- Generated code (C/C++ headers)
- AUTOSAR RTE generated files
- Simulink model generated code
- A different MATLAB workspace file

### 2. Look for Additional Files
Search for these file types in your project:
- `*.h` - Header files with RTE definitions
- `*.c` - Source files with runnable implementations
- `*.slx` - Simulink models
- `*.arxml` - AUTOSAR XML files
- `*.mat` - Other MATLAB workspace files

### 3. Search Patterns for FUS Index
Based on the findings, search for:
```
# In source code files:
g_PerEimTprRunnable*
*fusObjPort*
*FusObj*
*Handle_ub*

# In binary/data files:
Look for numeric values near FUS-related patterns
```

### 4. Potential Index Extraction Methods
If you find the correct file/location:

1. **Direct Variable Access** (if in MATLAB):
   ```matlab
   fusIndex = g_PerEimTprRunnable_m_fusObjPort_out.FusObj_st.m_value_Handle_ub;
   ```

2. **Structure Field Access**:
   ```matlab
   % Navigate the structure hierarchy
   runnable = g_PerEimTprRunnable_m_fusObjPort_out;
   fusObj = runnable.FusObj_st;
   fusIndex = fusObj.m_value_Handle_ub;
   ```

3. **Binary Data Parsing** (if in compiled code):
   - Look for memory offsets
   - Parse structure layouts
   - Extract numeric values

### 5. Next Steps
1. **Search the entire project** for files containing `PerEimTprRunnable`
2. **Check RTE generated files** in your AUTOSAR project
3. **Look for Simulink generated code** directories
4. **Search for .mat files** with different names
5. **Check the model hierarchy** in Simulink for FUS-related blocks

## Conclusion
The `subset.mat` file contains FUS-related content and automotive/AUTOSAR variables, but not the specific path you're looking for. The variable path suggests this is likely in generated code or a different workspace file. The presence of FUS-related patterns in the binary data confirms that FUS functionality exists in your project, but you'll need to locate the correct source files to find the specific index value.

## File Locations to Check
- `Rte_*.h` - RTE interface headers
- `*_private.h` - Private headers from code generation
- `ert_main.c` - Generated main function
- `*.sldd` - Simulink data dictionary
- Model-specific generated folders

The FUS index you're looking for is likely a numeric value (0-based or 1-based index) that identifies which FUS (Functional Unit System) to use for the activation cycle.