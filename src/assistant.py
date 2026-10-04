import re
from typing import Dict, Any, List
from src.models import FormSchema, SupportAssistance

class FormSupportAssistant:
    def __init__(self, schema: FormSchema):
        self.schema = schema

    def assist_from_natural_language(self, user_explanation: str) -> SupportAssistance:
        mapped = {}
        text = user_explanation.strip()

        # Extract email
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
        if email_match and "email" in self.schema.fields:
            mapped["email"] = email_match.group(0)

        # Extract phone
        phone_match = re.search(r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", text)
        if phone_match and "phone" in self.schema.fields:
            clean_phone = re.sub(r"[^0-9]", "", phone_match.group(0))
            mapped["phone"] = f"{clean_phone[:3]}-{clean_phone[3:6]}-{clean_phone[6:]}"

        # Extract zip
        zip_match = re.search(r"\b\d{5}\b", text)
        if zip_match and "zip_code" in self.schema.fields:
            mapped["zip_code"] = zip_match.group(0)

        # Extract currency/budget numbers specifically
        budget_match = re.search(r"(?:budget(?:\s+of)?|spending|limit)\s*[:=]?\s*\$?(\d+(?:\.\d+)?)\s*(k|thousand)?", text, re.IGNORECASE)
        if not budget_match:
            budget_match = re.search(r"\$(\d+(?:\.\d+)?)\s*(k|thousand)?", text, re.IGNORECASE)
        if budget_match and "monthly_budget" in self.schema.fields:
            val = float(budget_match.group(1))
            unit = (budget_match.group(2) or "").lower()
            if unit in ["k", "thousand"]:
                val *= 1000.0
            mapped["monthly_budget"] = val

        explanation = f"Extracted {len(mapped)} structured field(s) from your explanation."
        confidence = 0.90 if mapped else 0.20
        return SupportAssistance(user_explanation, mapped, explanation, confidence)
