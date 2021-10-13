""" Multiprocessing """
NUM_PROCESSES = 1


""" Raw CSV files"""
RAW_CSV_FOLDER = '/data/physionet.org/files/eicu-crd/2.0'
CSV_FILE_LIST = [
    'admissionDrug',
    'admissionDx',
    'allergy',
    'apacheApsVar',
    'apachePatientResult',
    'apachePredVar',
    'carePlanCareProvider',
    'carePlanEOL',
    'carePlanGeneral',
    'carePlanGoal',
    'carePlanInfectiousDisease',
    'customLab',
    'diagnosis',
    # 'hospital',
    'infusionDrug',
    'intakeOutput',
    'lab',
    'medication',
    'microLab',
    'note',
    'nurseAssessment',
    'nurseCare',
    'nurseCharting',
    'pastHistory',
    'patient',
    'physicalExam',
    'respiratoryCare',
    'respiratoryCharting',
    'treatment',
    'vitalAperiodic',
    'vitalPeriodic',
]


""" Exporter """
CHUNKS = 1
START = 0
EXPORTER_FOLDER = 'outputs/raw_json_data_v1'
# EXPORTER_SUBSET_FOLDER = 'outputs/json_data/patientsubset_tablesubset'


""" Validation """
VALIDATE_INTERVAL = 436
VALIDATE_FOLDER = 'outputs/raw_json_data_v1'


""" Data Info """
NUM_PATIENTS = 200859

# UNIT_TYPES_SQL = None
UNIT_TYPES = ['CCU-CTICU', 'Cardiac ICU', 'CSICU', 'CTICU']  # 43540
UNIT_TYPES_SQL = "('CCU-CTICU','Cardiac ICU','CSICU','CTICU')"  # 43540
# UNIT_TYPES_SQL = "('Cardiac ICU')"

TABLE_LIST = [
    'admissiondrug',
    'admissiondx',
    'allergy',
    'apacheApsVar',
    'apachePatientResult',
    'apachePredVar',
    'carePlanCareProvider',
    'carePlanEOL',
    'carePlanGeneral',
    'carePlanGoal',
    'carePlanInfectiousDisease',
    'customLab',
    'diagnosis',
    # 'hospital',
    'infusionDrug',
    'intakeOutput',
    'lab',
    'medication',
    'microLab',
    'note',
    'nurseAssessment',
    'nurseCare',
    'nurseCharting',
    'pastHistory',
    'patient',
    'physicalExam',
    'respiratoryCare',
    'respiratoryCharting',
    'treatment',
    'vitalAperiodic',
    'vitalPeriodic',
]


""" Data Cleaning """
DATA_CLEANING_INPUT_FOLDER = 'outputs/raw_json_data_v1'
DATA_CLEANING_OUTPUT_FOLDER = 'outputs/structured_json_data_v1'

_RES = 'projects/data_cleaning/resources'
DATA_MAPPING_TSV_FILE = _RES + '/DatasetOverview - Inputs-icd9code.tsv'
ICD9_CSV_FILE = _RES + '/icd9.csv'
ICD10_CSV_FILE = _RES + '/icd10.csv'

# DX_NAME_PATH = [dx.replace(" ", "_").replace(
#     ',', '').replace('/', '_') for dx in DX_SELECTED]

UNIT_CONVERSION_DICT = {
    'mcg/min': 1/1000,
    'mcg/hr': 1/60/1000,
    'mcg/kg/min': 1/1000,
    'mcg/kg/hr': 1/60/1000,

    'mg/min': 1,
    'mg/hr': 1/60,
    'mg/kg/min': 1,
    'mg/kg/hr': 1/60,

    'units/min': 1,
    'units/hr': 1/60,

    'ml/min': 1,
    'ml/hr': 1/60,
}

UNIT_ID_DICT = {
    'mcg/hr': 101,
    'mcg/kg/hr': 102,
    'mcg/kg/min': 103,
    'mcg/min': 104,
    'mg/hr': 105,
    'mg/kg/min': 106,
    'mg/min': 107,
    'units/hr': 108,
    'units/min': 109,
    'ml/hr': 200,
}

DIAGNOSIS_PRIORITY_DICT = {
    '': 0,
    'Primary': 1,
    'Major': 2,
    'Other': 3,
}
