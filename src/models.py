from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable

@dataclass
class FormField:
    name: str
    label: str
    field_type: str  # text, email, number, select, date
    required: bool = True
    regex_pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: List[str] = field(default_factory=list)
    help_text: str = ""

@dataclass
class FormSchema:
    form_id: str
    title: str
    description: str
    fields: Dict[str, FormField]

@dataclass
class ValidationError:
    field_name: str
    error_code: str
    message: str
    suggested_fix: Optional[str] = None

@dataclass
class SupportAssistance:
    user_intent: str
    mapped_fields: Dict[str, Any]
    explanation: str
    confidence: float
