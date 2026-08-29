from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.contracts import CaseField, ConfidenceBreakdown, ConfirmationEvidence, FieldStatus, LanguageProfile, LanguageShare


def test_confirmed_field_requires_evidence():
    with pytest.raises(ValidationError):
        CaseField(value="73821", status=FieldStatus.CONFIRMED, confidence=0.9)


def test_confirmed_field_accepts_evidence():
    field = CaseField(value="73821", status=FieldStatus.CONFIRMED, confidence=0.9,
                      confirmation=ConfirmationEvidence(method="read_back", confirmed_at=datetime.now(timezone.utc)))
    assert field.status == "confirmed"


def test_language_distribution_cannot_exceed_one():
    with pytest.raises(ValidationError):
        LanguageProfile(distribution=[LanguageShare(code="hi", share=.7, confidence=.9),
                                      LanguageShare(code="en", share=.5, confidence=.9)])


def test_confidence_formula_is_bounded_and_risk_adjusted():
    score = ConfidenceBreakdown(understanding=1, required_information=1, extraction=1,
                                routing=1, consistency=1, risk=.2)
    assert score.calculated_overall() == .8
