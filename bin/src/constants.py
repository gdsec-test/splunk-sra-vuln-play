APPNAMESPACE = "sra_vuln_play_to_snow"

STATE_COLLECTION_NAME = "gd_" + APPNAMESPACE

BASE_DOMAIN = 'https://godaddy'

SERVICENOW_REQUEST_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

MANDATORY_CONFIG = [
    'environment',
    'from_raw',
    'ticket_dsr',
    'table',
    'ticket_state',
    'ticket_title',
    'ticket_impact',
    'ticket_urgency'
]

# # Tables added here should be added to /default/data/ui/alerts/create_service_now_ticket.html as well
TABLE_FIELDS = {
    "direct": {
        "ticket_state": "u_state"
    },
    "string": {
        "ticket_title": "u_title",
        "ticket_impact": "u_impact",
        "ticket_urgency": "u_urgency",
        "ticket_summary": "u_summary",
        "ticket_assignment_group": "u_assignment_group",
        "ticket_category": "u_category",
        "ticket_sub_category": "u_sub_category",
        "ticket_detection_method": "u_detection_method"
    },
    "datetime": {
        "ticket_detect_time": "u_detect_time",
        "ticket_event_time": "u_event_time"
    },
    "boolean": {
        "ticket_dsr": "u_dsr"
    }
}

PARAMETER_REGEX = r"\{\{\S+?\}\}"

SNOW_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
