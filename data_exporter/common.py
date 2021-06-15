# DATA INFO
NUM_PATIENTS = 200859
UNIT_TYPES = "('CCU-CTICU','Cardiac ICU','CSICU','CTICU')"
TABLE_LIST = [
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

# MULTIPROCESSING
NUM_PROCESSES = 60

# EXPORTER
CHUNKS = 100
START = 88
EXPORTER_FOLDER = 'outputs/210612'

# VALIDATE
VALIDATE_INTERVAL = 436
VALIDATE_FOLDER = 'outputs/json_data/all'
