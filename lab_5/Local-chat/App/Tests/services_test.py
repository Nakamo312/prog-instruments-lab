import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from ..regex_processor import RegexProcessor
from ..logger import ChatLogger



@pytest.mark.parametrize("input_text,expected_output", [
    ("Visit https://example.com for info", "Visit ****** for info"),
    ("Contact me at test@example.com", "Contact me at ******"),
    ("Call me at +12345678901", "Call me at ******"),
])
def test_regex_processing(input_text, expected_output):
    processor = RegexProcessor()
    output = processor.regex_processing(input_text)
    assert output == expected_output


def test_chat_logger_initialization():
    logger = ChatLogger().getLogger("TestLogger")
    assert isinstance(logger, logging.Logger) 