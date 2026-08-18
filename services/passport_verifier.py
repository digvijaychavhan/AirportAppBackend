"""
Legacy Re-Export Wrapper for Passport Authenticity Verifier
"""

from app.modules.wifi.service import (
    VALID_COUNTRY_CODES,
    calculate_icao_check_digit,
    clean_mrz_line,
    normalize_digit_char,
    normalize_letter_char,
    validate_mrz_date,
    parse_and_validate_mrz_text,
    extract_passport_with_groq_ai,
    verify_passport_image,
    generate_wifi_qr_payload
)

__all__ = [
    "VALID_COUNTRY_CODES",
    "calculate_icao_check_digit",
    "clean_mrz_line",
    "normalize_digit_char",
    "normalize_letter_char",
    "validate_mrz_date",
    "parse_and_validate_mrz_text",
    "extract_passport_with_groq_ai",
    "verify_passport_image",
    "generate_wifi_qr_payload"
]
