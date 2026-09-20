VALIDATION_RULES = {

    "R001": {
        "name": "Required field missing",
        "severity": "HIGH",
        "category": "COMPLETENESS"
    },

    "R002": {
        "name": "Duplicate primary key",
        "severity": "HIGH",
        "category": "UNIQUENESS"
    },

    "R003": {
        "name": "Duplicate complete record",
        "severity": "MEDIUM",
        "category": "UNIQUENESS"
    },

    "R004": {
        "name": "Invalid data type",
        "severity": "HIGH",
        "category": "SCHEMA"
    },

    "R005": {
        "name": "Orphan agency reference",
        "severity": "HIGH",
        "category": "REFERENTIAL_INTEGRITY"
    },

    "R006": {
        "name": "Orphan route reference",
        "severity": "HIGH",
        "category": "REFERENTIAL_INTEGRITY"
    },

    "R007": {
        "name": "Orphan service reference",
        "severity": "HIGH",
        "category": "REFERENTIAL_INTEGRITY"
    },

    "R008": {
        "name": "Orphan trip reference",
        "severity": "HIGH",
        "category": "REFERENTIAL_INTEGRITY"
    },

    "R009": {
        "name": "Orphan stop reference",
        "severity": "HIGH",
        "category": "REFERENTIAL_INTEGRITY"
    },

    "R010": {
        "name": "Orphan shape reference",
        "severity": "HIGH",
        "category": "REFERENTIAL_INTEGRITY"
    },

    "R011": {
        "name": "Invalid latitude",
        "severity": "HIGH",
        "category": "GEOGRAPHIC"
    },

    "R012": {
        "name": "Invalid longitude",
        "severity": "HIGH",
        "category": "GEOGRAPHIC"
    },

    "R013": {
        "name": "Suspicious geographic location",
        "severity": "MEDIUM",
        "category": "GEOGRAPHIC"
    },

    "R014": {
        "name": "Invalid stop sequence",
        "severity": "HIGH",
        "category": "TIMETABLE"
    },

    "R015": {
        "name": "Invalid arrival/departure time",
        "severity": "HIGH",
        "category": "TIMETABLE"
    },

    "R016": {
        "name": "Departure before arrival",
        "severity": "HIGH",
        "category": "TIMETABLE"
    },

    "R017": {
        "name": "Invalid service date range",
        "severity": "MEDIUM",
        "category": "SERVICE"
    },

    "R018": {
        "name": "Invalid service-day configuration",
        "severity": "MEDIUM",
        "category": "SERVICE"
    },

    "R019": {
        "name": "Missing shape",
        "severity": "HIGH",
        "category": "ROUTE_SHAPE"
    },

    "R020": {
        "name": "Route/shape inconsistency",
        "severity": "MEDIUM",
        "category": "ROUTE_SHAPE"
    },

    "R021": {
        "name": "Suspicious duplicate stop",
        "severity": "MEDIUM",
        "category": "SEMANTIC"
    },

    "R022": {
        "name": "Missing important field",
        "severity": "MEDIUM",
        "category": "COMPLETENESS"
    },

    "R023": {
        "name": "Invalid categorical value",
        "severity": "HIGH",
        "category": "DOMAIN"
    }
}