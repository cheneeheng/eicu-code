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
EXPORTER_FOLDER = 'outputs/all_dummy'
# EXPORTER_SUBSET_FOLDER = 'outputs/json_data/patientsubset_tablesubset'


""" Validation """
VALIDATE_INTERVAL = 436
VALIDATE_FOLDER = 'outputs/all_dummy'


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


""" Preprocessing """
PREPROCESS_INPUT_FOLDER = 'outputs/all'
PREPROCESS_OUTPUT_FOLDER = ''
DATA_MAPPING_TSV_FILE = 'projects/data/resource/DatasetOverview - Inputs.tsv'
ICD9_CSV_FILE = 'projects/data/resource/icd9.csv'
ICD10_CSV_FILE = 'projects/data/resource/icd10.csv'

DEMO_ITEMS = ['patientunitstayid', 'age', 'gender',
              'apacheadmissiondx', 'unitdischargestatus',
              'hospitaldischargestatus']

DX_SELECTED = [
    'Infarction, acute myocardial (MI)',
    'CABG alone, coronary artery bypass grafting',
    'CABG with aortic valve replacement',
    'CHF, congestive heart failure',
    'Aortic valve replacement (isolated)',
    'Cardiac arrest (with or without respiratory arrest; for respiratory arrest see Respiratory System)',  # noqa
    'Arrest, respiratory (without cardiac arrest)',
    'Angina, unstable (angina interferes w/quality of life or meds are tolerated poorly)',  # noqa
    'Angina, stable (asymp or stable pattern of symptoms w/meds)',
    'Rhythm disturbance (atrial, supraventricular)',
    'Rhythm disturbance (conduction defect)',
    'Rhythm disturbance (ventricular)',
    'Cardiovascular medical, other',
    'Cardiomyopathy',
    'Mitral valve repair',
    'Mitral valve replacement',
    'Shock, cardiogenic',
    'Cardiovascular surgery, other',
    'Ablation or mapping of cardiac conduction pathway',
    'Thrombus, arterial',
    'Pericardial effusion/tamponade',
    'Efffusion, pericardial',
    'Aortic and Mitral valve replacement',
    'Hypertension, uncontrolled (for cerebrovascular accident-see Neurological System)',  # noqa
]

# DX_NAME_PATH = [dx.replace(" ", "_").replace(
#     ',', '').replace('/', '_') for dx in DX_SELECTED]

AGE_RANGES = [str(i) for i in range(0, 90, 10)] + ['> 89']

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
