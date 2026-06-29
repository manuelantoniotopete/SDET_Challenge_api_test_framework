USER_SCHEMA = {
    "type": "object",
    "required": ["name", "email", "age"],
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 1, "maximum": 150},
    },
    "additionalProperties": False,
}

USER_ARRAY_SCHEMA = {
    "type": "array",
    "items": USER_SCHEMA,
}

USER_CREATE_USER = {
"type": "object",
    "required": ["name", "email", "age"],
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 1, "maximum": 150},
    }
}

ERROR_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {"type": "string"},
    },
    "additionalProperties": False,
}
