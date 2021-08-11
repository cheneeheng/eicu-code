""" Multiprocessing """
NUM_PROCESSES = 1


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

UNIT_TYPES = None
# UNIT_TYPES = "('CCU-CTICU','Cardiac ICU','CSICU','CTICU')"  # 43540
# UNIT_TYPES = "('Cardiac ICU')"

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
