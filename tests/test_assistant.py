import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models import FormField, FormSchema
from src.validator import FormValidator
from src.assistant import FormSupportAssistant

class TestDynamicFormAssistant(unittest.TestCase):
    def setUp(self):
        self.schema = FormSchema(
            form_id="customer_onboarding",
            title="Customer Onboarding",
            description="Onboarding intake form",
            fields={
                "full_name": FormField("full_name", "Full Name", "text", required=True),
                "email": FormField("email", "Email", "email", required=True),
                "phone": FormField("phone", "Phone", "phone", required=False),
                "zip_code": FormField("zip_code", "ZIP Code", "zip", required=False),
                "monthly_budget": FormField("monthly_budget", "Monthly Budget", "number", required=False, min_value=100.0)
            }
        )

    def test_validation_rules(self):
        validator = FormValidator(self.schema)
        # Empty missing required
        errors = validator.validate({})
        self.assertEqual(len(errors), 2)  # full_name, email missing

        # Invalid email and budget
        errors = validator.validate({
            "full_name": "Alex Smith",
            "email": "invalid-email-string",
            "monthly_budget": 50.0  # below min
        })
        self.assertEqual(len(errors), 2)
        err_codes = [e.error_code for e in errors]
        self.assertIn("INVALID_EMAIL", err_codes)
        self.assertIn("VALUE_TOO_LOW", err_codes)

    def test_natural_language_auto_correction(self):
        assistant = FormSupportAssistant(self.schema)
        nl_input = "You can reach me at dev.support@cloudcorp.com or 415-555-0199, living in 94043 with budget of 5k"
        res = assistant.assist_from_natural_language(nl_input)
        self.assertEqual(res.mapped_fields.get("email"), "dev.support@cloudcorp.com")
        self.assertEqual(res.mapped_fields.get("phone"), "415-555-0199")
        self.assertEqual(res.mapped_fields.get("zip_code"), "94043")
        self.assertEqual(res.mapped_fields.get("monthly_budget"), 5000.0)
        self.assertGreaterEqual(res.confidence, 0.85)

if __name__ == "__main__":
    unittest.main()
