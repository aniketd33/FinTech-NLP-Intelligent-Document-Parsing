"""
Unit Tests for LexiScan Auto API
Week 3 Deliverable: Edge Case Testing
"""

import pytest
from api_app import normalize_date, clean_money, evaluate_ocr_quality


# Test Date Normalization


class TestDateNormalization:
    def test_standard_date(self):
        assert normalize_date("January 1, 2020") == "2020-01-01"
    
    def test_full_month_name(self):
        assert normalize_date("December 31, 2019") == "2019-12-31"
    
    def test_short_month(self):
        assert normalize_date("Jan 15, 2020") == "2020-01-15"
    
    def test_invalid_date_returns_original(self):
        assert normalize_date("Not a date") == "Not a date"
    
    def test_empty_date(self):
        assert normalize_date("") == ""


# Test Money Cleaning


class TestMoneyCleaning: 
    def test_standard_money(self):
        assert clean_money("$5,000") == "5000"
    
    def test_money_with_cents(self):
        assert clean_money("$2,500.00") == "2500.00"
    
    def test_money_no_comma(self):
        assert clean_money("$1000") == "1000"
    
    def test_money_with_spaces(self):
        assert clean_money("$ 5,000") == "5000"


# Test OCR Quality Check


class TestOCRQuality:
    def test_good_quality_text(self):
        text = "This is a sample contract agreement between Party A and Party B. The effective date is January 1, 2020. The total amount is $5,000."
        result = evaluate_ocr_quality(text)
        assert result["is_usable"] == True
        assert result["quality_score"] >= 70
    
    def test_empty_text(self):
        text = ""
        result = evaluate_ocr_quality(text)
        assert result["is_usable"] == False
        assert result["quality_score"] < 50
    
    def test_very_short_text(self):
        text = "Hi"
        result = evaluate_ocr_quality(text)
        assert result["is_usable"] == False
    
    def test_text_with_ocr_errors(self):
        text = "This is a t€st with |ots of §ymb0ls ___ and ??? errors"
        result = evaluate_ocr_quality(text)
        assert len(result["issues"]) > 0


# Run Tests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])