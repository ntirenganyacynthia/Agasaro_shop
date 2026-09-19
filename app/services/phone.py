import re

from fastapi import HTTPException


RWANDA_MOBILE_RE = re.compile(r"^2507\d{8}$")


def normalize_rwanda_phone(value: str) -> str:
    raw = re.sub(r"[\s().-]", "", value.strip())
    if raw.startswith("+"):
        raw = raw[1:]
    if raw.startswith("00"):
        raw = raw[2:]
    if raw.startswith("07") and len(raw) == 10:
        raw = "250" + raw[1:]
    if not RWANDA_MOBILE_RE.fullmatch(raw):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid Rwanda MTN mobile number, for example 0781234567.",
        )
    return raw


def mask_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    return f"+{phone[:5]}***{phone[-2:]}"
