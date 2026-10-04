import re
from typing import Dict, List, Any
from src.models import FormSchema, ValidationError

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$|^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$")
ZIP_REGEX = re.compile(r"^\d{5}(-\d{4})?$")

class FormValidator:
    def __init__(self, schema: FormSchema):
        self.schema = schema

    def validate(self, data: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        for name, field_spec in self.schema.fields.items():
            val = data.get(name)
            if field_spec.required and (val is None or str(val).strip() == ""):
                errors.append(ValidationError(name, "REQUIRED_FIELD_MISSING", f"'{field_spec.label}' is required."))
                continue

            if val is not None and str(val).strip() != "":
                s_val = str(val).strip()
                if field_spec.field_type == "email" and not EMAIL_REGEX.match(s_val):
                    errors.append(ValidationError(name, "INVALID_EMAIL", "Please enter a valid email address.", suggested_fix="e.g. user@domain.com"))
                elif field_spec.field_type == "phone" and not PHONE_REGEX.match(s_val):
                    errors.append(ValidationError(name, "INVALID_PHONE", "Please enter a valid phone number (10 digits).", suggested_fix="e.g. 555-0199"))
                elif field_spec.field_type == "zip" and not ZIP_REGEX.match(s_val):
                    errors.append(ValidationError(name, "INVALID_ZIP", "ZIP code must be 5 digits (e.g. 94043)."))
                elif field_spec.field_type == "number":
                    try:
                        n = float(val)
                        if field_spec.min_value is not None and n < field_spec.min_value:
                            errors.append(ValidationError(name, "VALUE_TOO_LOW", f"Must be at least {field_spec.min_value}."))
                        if field_spec.max_value is not None and n > field_spec.max_value:
                            errors.append(ValidationError(name, "VALUE_TOO_HIGH", f"Must be at most {field_spec.max_value}."))
                    except ValueError:
                        errors.append(ValidationError(name, "NOT_A_NUMBER", "Value must be numeric."))
        return errors
