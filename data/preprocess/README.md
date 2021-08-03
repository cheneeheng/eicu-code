# How we preprocess the raw data from eICU?
### General process:
- entries with invalid data (nan, None) are omitted.
- entries are sorted by timestamp


### Specific process for data groups:
1. Lab test  
The entry values for lab test are strings. They can contain symbols, such as __"> 200"__, __"< 0.5"__. It can be possibly caused by the limited range that can be measured by the lab devices.    
We omitted the symbols and converted the value to float number.
2. Infusion drug  
Same infusions can have different units for drug rate, e.g. __"mcg/min"__,  __"mg/hr"__. For later reference, we saved the original unit in the "Unit" column.
The units are then unified into 
   - mg/min,
   - ml/min,
   - unit/min.   

3. Diagnosis  
Delete duplicate entries with the same timestamp



# Output data structure
For each patient, we generate 2 csv file from the raw data. The name of each file is the patient unit ID (pid.csv).
One stores static data, e.g. patient demographics, admission diagnoses.
The other one stores temporal data during one's stay in the ICU, e.g. vital signals, lab tests, intake and output, infusions, diagnoses.

The static data is a Nx2 table, containing entry UID and entry value. In the following example table, it stores data of patient unit id, gender and age.  
| UID | Value |
| --- | --- |
| 1 | 141233 |
| 3 | Female |
| 4 | 81 |

The temporal data is a Mx4 table, containing entry UID, timestamp (offset), entry value, and the unit for the value.
| Offset | UID | Value | Unit |
| --- | --- | --- | --- |
| t1 | 10000x | vital1 | 
| t2 | 10000x | vital1 | 
| t1 | 10000x | vital2 | 
| t2 | 10000x | vital2 | 
| t3 | 40000x | lab1 |
| t4 | 50000x | infusion1 | unit1 |
| t5 | 50000x | infusion1 | unit2 |
| t3 | 70000x | dx1 |
| ... | ... | ... | ... |
