"""
Tests for preprocessor module
"""
import sys
sys.path.insert(0, '../src')

from modules.preprocessor import SloganPreprocessor


def test_normalize_text():
    """Test text normalization"""
    prep = SloganPreprocessor()
    
    # HTML entities
    assert prep.normalize_text("Test&nbsp;text") == "Test text"
    
    # Multiple spaces
    assert prep.normalize_text("Test   multiple    spaces") == "Test multiple spaces"
    
    # Quotes
    assert prep.normalize_text("«Test»") == '"Test"'


def test_is_valid_slogan():
    """Test slogan validation"""
    prep = SloganPreprocessor()
    
    # Valid
    assert prep.is_valid_slogan("Just do it") == True
    assert prep.is_valid_slogan("Think different") == True
    
    # Invalid - too short
    assert prep.is_valid_slogan("Hi") == False
    
    # Invalid - metadata
    assert prep.is_valid_slogan("Бренд: Nike") == False
    assert prep.is_valid_slogan("=== Header ===") == False
    
    # Invalid - just numbers
    assert prep.is_valid_slogan("123") == False


def test_extract_slogan():
    """Test slogan extraction"""
    prep = SloganPreprocessor()
    
    # Remove numbering
    assert prep.extract_slogan("1. Just do it") == "Just do it"
    
    # Split by separator
    result = prep.extract_slogan("Think different&emsp;Apple")
    assert result == "Think different"


def test_compute_hash():
    """Test hash computation"""
    prep = SloganPreprocessor()
    
    # Same text = same hash
    hash1 = prep.compute_hash("Test")
    hash2 = prep.compute_hash("test")  # lowercase
    assert hash1 == hash2
    
    # Different text = different hash
    hash3 = prep.compute_hash("Different")
    assert hash1 != hash3


def test_deduplicate_exact():
    """Test exact deduplication"""
    prep = SloganPreprocessor()
    
    slogans = [
        "Just do it",
        "Think different",
        "Just do it",  # duplicate
        "I'm lovin' it"
    ]
    
    unique = prep.deduplicate_exact(slogans)
    assert len(unique) == 3
    assert "Just do it" in unique
    assert "Think different" in unique


if __name__ == "__main__":
    test_normalize_text()
    test_is_valid_slogan()
    test_extract_slogan()
    test_compute_hash()
    test_deduplicate_exact()
    
    print("✅ All preprocessor tests passed!")
