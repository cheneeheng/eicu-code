# DATA INFO
NUM_PATIENTS = 200859
UNIT_TYPES = None
# UNIT_TYPES = "('CCU-CTICU','Cardiac ICU','CSICU','CTICU')"  # 43540
# UNIT_TYPES = "('Cardiac ICU')"
TABLE_LIST_SUBSET = [
    'patient',  # ok
    'treatment',  # ok
    'vitalperiodic',  # ok
    'vitalaperiodic',  # ok
    'nursecharting',  # Very slow, maybe due to large amount of data?
    'lab',  # ok
    'infusiondrug',  # ok
    'intakeoutput',  # Relatively slow, maybe due to large amount of data?
    'diagnosis',  # ok
    'apachepatientresult',  # ok
    'nurseassessment',  # Very slow, maybe due to large amount of data?
    'physicalexam',  # Very slow, maybe due to large amount of data?
    'respiratorycare',  # ok
    'respiratorycharting'  # Very slow, maybe due to large amount of data?
]
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

# MULTIPROCESSING
NUM_PROCESSES = 1

# EXPORTER
CHUNKS = 100
START = 80
EXPORTER_FOLDER = 'outputs/all_dummy'
# EXPORTER_SUBSET_FOLDER = 'outputs/json_data/patientsubset_tablesubset'

# VALIDATE
VALIDATE_INTERVAL = 436
VALIDATE_FOLDER = 'outputs/all_dummy'
