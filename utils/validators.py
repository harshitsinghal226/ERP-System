"""
Field-level validators for data entry forms.
Centralized validation rules for weights, money, dates, and required fields.
"""

from datetime import datetime
from typing import Optional, Tuple

from config.app_config import DATE_FORMAT


class ValidationResult:
    """Result of a validation check."""
    
    def __init__(self, is_valid: bool, message: str = ""):
        self.is_valid = is_valid
        self.message = message
    
    def __bool__(self):
        return self.is_valid


def validate_required(value: str, field_name: str) -> ValidationResult:
    """Check that a field is not empty."""
    if not value or not str(value).strip():
        return ValidationResult(False, f"{field_name} is required")
    return ValidationResult(True)


def validate_positive_number(value, field_name: str) -> ValidationResult:
    """Check that a numeric value is non-negative."""
    try:
        num = float(value)
        if num < 0:
            return ValidationResult(False, f"{field_name} cannot be negative")
        return ValidationResult(True)
    except (ValueError, TypeError):
        return ValidationResult(False, f"{field_name} must be a valid number")


def validate_weight(value, field_name: str = "Weight") -> ValidationResult:
    """Validate a weight field — must be a positive number."""
    result = validate_positive_number(value, field_name)
    if not result:
        return result
    
    num = float(value)
    if num > 100000:  # Sanity check: 100 kg max
        return ValidationResult(False, f"{field_name} seems too large (max 100,000 grams)")
    
    return ValidationResult(True)


def validate_money(value, field_name: str = "Amount") -> ValidationResult:
    """Validate a monetary field — must be non-negative."""
    result = validate_positive_number(value, field_name)
    if not result:
        return result
    
    num = float(value)
    if num > 10000000:  # Sanity check: 1 crore max
        return ValidationResult(False, f"{field_name} seems too large (max ₹1,00,00,000)")
    
    return ValidationResult(True)


def validate_date(value: str, field_name: str = "Date") -> ValidationResult:
    """Validate a date string in DD-MM-YYYY format."""
    if not value or not str(value).strip():
        return ValidationResult(False, f"{field_name} is required")
    
    try:
        parsed = datetime.strptime(str(value).strip(), DATE_FORMAT)
        # Check for future dates (warn but don't block)
        if parsed.date() > datetime.now().date():
            return ValidationResult(False, f"{field_name} cannot be a future date")
        return ValidationResult(True)
    except ValueError:
        return ValidationResult(False, f"{field_name} must be in DD-MM-YYYY format")


def validate_phone(value: str, field_name: str = "Phone") -> ValidationResult:
    """Validate phone number format."""
    if not value or not str(value).strip():
        return ValidationResult(True)  # Phone is optional
    
    cleaned = str(value).strip().replace(" ", "").replace("-", "").replace("+", "")
    if not cleaned.isdigit():
        return ValidationResult(False, f"{field_name} must contain only digits")
    
    if len(cleaned) < 10 or len(cleaned) > 13:
        return ValidationResult(False, f"{field_name} must be 10-13 digits")
    
    return ValidationResult(True)


def validate_dropdown_selection(value, field_name: str) -> ValidationResult:
    """Check that a dropdown has a valid selection (not empty or placeholder)."""
    if not value or value == "" or value == "Select..." or value == "-- Select --":
        return ValidationResult(False, f"Please select a {field_name}")
    return ValidationResult(True)


def validate_scrap_weight(gross: float, labour: float) -> ValidationResult:
    """Validate that labour weight doesn't exceed gross weight."""
    if labour > gross:
        return ValidationResult(
            False,
            f"Labour Weight ({labour}) cannot exceed Gross Weight ({gross})"
        )
    return ValidationResult(True)


def validate_issue_entry(date: str, karigar: str, item_type: str, 
                          weight: str) -> list:
    """
    Validate all fields of an issue entry form.
    
    Returns:
        List of ValidationResult objects for failed validations.
        Empty list means all validations passed.
    """
    errors = []
    
    result = validate_date(date, "Issue Date")
    if not result:
        errors.append(result)
    
    result = validate_dropdown_selection(karigar, "Karigar")
    if not result:
        errors.append(result)
    
    result = validate_dropdown_selection(item_type, "Item Type")
    if not result:
        errors.append(result)
    
    result = validate_weight(weight, "Weight")
    if not result:
        errors.append(result)
    
    return errors


def validate_receive_entry(date: str, karigar: str, item_type: str,
                            gross_weight: str, labour_weight: str) -> list:
    """
    Validate all fields of a receive entry form.
    
    Returns:
        List of ValidationResult objects for failed validations.
    """
    errors = []
    
    result = validate_date(date, "Receive Date")
    if not result:
        errors.append(result)
    
    result = validate_dropdown_selection(karigar, "Karigar")
    if not result:
        errors.append(result)
    
    result = validate_dropdown_selection(item_type, "Item Type")
    if not result:
        errors.append(result)
    
    result = validate_weight(gross_weight, "Gross Weight")
    if not result:
        errors.append(result)
    
    result = validate_weight(labour_weight, "Labour Weight")
    if not result:
        errors.append(result)
    
    # Cross-field validation
    try:
        g = float(gross_weight)
        l = float(labour_weight)
        result = validate_scrap_weight(g, l)
        if not result:
            errors.append(result)
    except (ValueError, TypeError):
        pass  # Already caught by individual field validation
    
    return errors


def validate_karigar(name: str, phone: str = "", opening_balance: str = "0") -> list:
    """
    Validate karigar form fields.
    
    Returns:
        List of ValidationResult objects for failed validations.
    """
    errors = []
    
    result = validate_required(name, "Karigar Name")
    if not result:
        errors.append(result)
    
    result = validate_phone(phone, "Phone Number")
    if not result:
        errors.append(result)
    
    if opening_balance:
        result = validate_positive_number(opening_balance, "Opening Balance")
        if not result:
            errors.append(result)
    
    return errors
