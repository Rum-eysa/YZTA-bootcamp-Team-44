"""CoverLetterRequest şema testleri (US-049: extra_prompt validasyonu)"""
import pytest
from app.schemas.cover_letter import EXTRA_PROMPT_MAX_LENGTH, CoverLetterRequest
from pydantic import ValidationError


def test_extra_prompt_defaults_to_none():
    request = CoverLetterRequest(listing_id="listing-1")
    assert request.extra_prompt is None


def test_extra_prompt_is_trimmed():
    request = CoverLetterRequest(listing_id="listing-1", extra_prompt="  takım çalışması  ")
    assert request.extra_prompt == "takım çalışması"


def test_whitespace_only_extra_prompt_becomes_none():
    request = CoverLetterRequest(listing_id="listing-1", extra_prompt="   ")
    assert request.extra_prompt is None


def test_extra_prompt_within_max_length_is_accepted():
    text = "a" * EXTRA_PROMPT_MAX_LENGTH
    request = CoverLetterRequest(listing_id="listing-1", extra_prompt=text)
    assert request.extra_prompt == text


def test_extra_prompt_exceeding_max_length_is_rejected():
    text = "a" * (EXTRA_PROMPT_MAX_LENGTH + 1)
    with pytest.raises(ValidationError):
        CoverLetterRequest(listing_id="listing-1", extra_prompt=text)
