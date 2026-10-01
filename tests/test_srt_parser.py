"""
tests/test_srt_parser.py
==========================
Unit tests for the SRT parsing module.
No DB connection required — tests pure parsing logic.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.transcript.process_srt import (
    parse_srt_content,
    parse_timestamp,
    clean_srt_text,
    validate_srt_blocks,
)


# ---------------------------------------------------------------------------
# parse_timestamp
# ---------------------------------------------------------------------------

class TestParseTimestamp:
    def test_basic(self):
        assert parse_timestamp("00", "01", "05", "500") == 65.5

    def test_zero(self):
        assert parse_timestamp("00", "00", "00", "000") == 0.0

    def test_hours(self):
        assert parse_timestamp("01", "00", "00", "000") == 3600.0

    def test_milliseconds(self):
        assert parse_timestamp("00", "00", "05", "360") == pytest.approx(5.36)


# ---------------------------------------------------------------------------
# clean_srt_text
# ---------------------------------------------------------------------------

class TestCleanSrtText:
    def test_removes_html_tags(self):
        assert clean_srt_text("<i>italic</i> text") == "italic text"

    def test_removes_bold(self):
        assert clean_srt_text("<b>bold</b>") == "bold"

    def test_preserves_plain(self):
        assert clean_srt_text("Hello world") == "Hello world"

    def test_normalizes_whitespace(self):
        assert clean_srt_text("a   b") == "a b"

    def test_empty(self):
        assert clean_srt_text("") == ""


# ---------------------------------------------------------------------------
# parse_srt_content
# ---------------------------------------------------------------------------

VALID_SRT = """1
00:00:05,360 --> 00:00:09,920
Welcome to your journey.

2
00:00:09,920 --> 00:00:12,690
Data science has witnessed remarkable growth.

3
00:00:12,690 --> 00:00:15,730
Due to the abundance of electronic data.
"""


class TestParseSrtContent:
    def test_basic_parse(self):
        blocks = parse_srt_content(VALID_SRT)
        assert len(blocks) == 3

    def test_first_block(self):
        blocks = parse_srt_content(VALID_SRT)
        b = blocks[0]
        assert b.sequence_number == 1
        assert b.start_seconds == pytest.approx(5.36)
        assert b.end_seconds == pytest.approx(9.92)
        assert "Welcome" in b.text

    def test_sequence_numbers(self):
        blocks = parse_srt_content(VALID_SRT)
        assert [b.sequence_number for b in blocks] == [1, 2, 3]

    def test_timestamps_increase(self):
        blocks = parse_srt_content(VALID_SRT)
        for i in range(1, len(blocks)):
            assert blocks[i].start_seconds >= blocks[i - 1].start_seconds

    def test_empty_content(self):
        blocks = parse_srt_content("")
        assert blocks == []

    def test_invalid_content(self):
        blocks = parse_srt_content("not an srt file\n\nrandom text")
        assert blocks == []

    def test_malformed_timestamp_skipped(self):
        malformed = """1
BADTIMESTAMP
Some text.

2
00:00:01,000 --> 00:00:02,000
Good block.
"""
        blocks = parse_srt_content(malformed)
        assert len(blocks) == 1
        assert blocks[0].sequence_number == 2

    def test_strips_html_in_text(self):
        srt = """1
00:00:01,000 --> 00:00:02,000
<i>italics</i> and <b>bold</b>
"""
        blocks = parse_srt_content(srt)
        assert blocks[0].text == "italics and bold"

    def test_comma_and_dot_separator(self):
        """SRT files may use dot instead of comma in timestamps."""
        srt = """1
00:00:01.000 --> 00:00:02.500
Dot separator.
"""
        blocks = parse_srt_content(srt)
        assert len(blocks) == 1
        assert blocks[0].start_seconds == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# validate_srt_blocks
# ---------------------------------------------------------------------------

class TestValidateSrtBlocks:
    def test_valid_blocks_no_issues(self):
        blocks = parse_srt_content(VALID_SRT)
        issues = validate_srt_blocks(blocks)
        assert issues == []

    def test_detects_non_sequential(self):
        srt = """1
00:00:01,000 --> 00:00:02,000
First.

3
00:00:02,000 --> 00:00:03,000
Gap in sequence.
"""
        blocks = parse_srt_content(srt)
        issues = validate_srt_blocks(blocks)
        assert any("Non-sequential" in i for i in issues)

    def test_end_before_start_raises(self):
        """SRTBlock model should reject end < start."""
        from pydantic import ValidationError
        from preprocessing.common.models import SRTBlock
        with pytest.raises(ValidationError):
            SRTBlock(sequence_number=1, start_seconds=5.0, end_seconds=3.0, text="bad")
