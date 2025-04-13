# Health Record Manager Contract

# Define a record structure to hold health-related data.
# The record contains transcription, prescription, appointment date, and summary.
struct HealthRecord:
    transcription: String[1000]
    prescription: String[1000]
    appointment_date: uint256
    summary: String[1000]

# Define mappings to store health records by patient address
patientRecords: public(HashMap[address, HealthRecord])

# Define an admin address to authorize who can add records (e.g., a doctor or healthcare provider).
admin: public(address)

# Constructor to set the admin address when deploying the contract.
@deploy
def __init__(_admin: address):
    self.admin = _admin

# Modifier to ensure only the admin can add records
@internal
def only_admin():
    assert msg.sender == self.admin, "Only admin can add records"

# Function to add health record for a specific patient
@external
def add_record(
    _patient: address, 
    _transcription: String[1000], 
    _prescription: String[1000], 
    _appointment_date: uint256, 
    _summary: String[1000]
):
    # Ensure only the admin can add records
    self.only_admin()

    # Create a new health record
    new_record: HealthRecord = HealthRecord({
        transcription: _transcription,
        prescription: _prescription,
        appointment_date: _appointment_date,
        summary: _summary
    })

    # Store the record for the patient
    self.patientRecords[_patient] = new_record

# Function to retrieve the health record of a specific patient
@external
def get_record(_patient: address) -> (String[1000], String[1000], uint256, String[1000]):
    record: HealthRecord = self.patientRecords[_patient]
    return (record.transcription, record.prescription, record.appointment_date, record.summary)

# Function to change the admin (if necessary, for instance, if the admin changes role)
@external
def change_admin(new_admin: address):
    self.only_admin()
    self.admin = new_admin