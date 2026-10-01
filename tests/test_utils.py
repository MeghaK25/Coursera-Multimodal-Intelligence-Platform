"""
tests/test_utils.py
=====================
Unit tests for shared utility functions.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.common.utils import (
    sha256_bytes,
    slug_from_path,
    title_from_slug,
    extract_lesson_prefix,
    extract_module_number,
    normalize_whitespace,
    count_words,
    mime_from_extension,
    asset_category_from_file,
    rag_enabled_for_category,
)


class TestSha256Bytes:
    def test_deterministic(self):
        d = b"hello world"
        assert sha256_bytes(d) == sha256_bytes(d)

    def test_known_hash(self):
        # SHA-256("abc") verified against Python's hashlib reference
        import hashlib
        expected = hashlib.sha256(b"abc").hexdigest()
        assert sha256_bytes(b"abc") == expected

    def test_empty_bytes(self):
        h = sha256_bytes(b"")
        assert len(h) == 64


class TestSlugFromPath:
    def test_backslashes_normalised(self):
        assert slug_from_path(r"a\b\c") == "a/b/c"

    def test_leading_slash_stripped(self):
        assert slug_from_path("/a/b/c") == "a/b/c"

    def test_forward_slash(self):
        assert slug_from_path("a/b/c") == "a/b/c"


class TestTitleFromSlug:
    def test_strips_numeric_prefix(self):
        t = title_from_slug("02_02_what-is-data-science")
        assert "02" not in t
        assert "What Is Data Science" in t

    def test_handles_extension(self):
        t = title_from_slug("02_02_what-is-data-science.mp4")
        assert ".mp4" not in t


class TestExtractLessonPrefix:
    def test_standard(self):
        assert extract_lesson_prefix("02_04_title.mp4") == "02_04"

    def test_no_prefix(self):
        assert extract_lesson_prefix("README.md") == ""

    def test_short_filename(self):
        assert extract_lesson_prefix("01_01_intro.html") == "01_01"


class TestExtractModuleNumber:
    def test_standard(self):
        assert extract_module_number("01_defining-data-science") == 1

    def test_double_digit(self):
        assert extract_module_number("12_some-module") == 12

    def test_no_number(self):
        assert extract_module_number("no-number-here") == 0


class TestNormalizeWhitespace:
    def test_collapses_spaces(self):
        assert normalize_whitespace("a   b") == "a b"

    def test_strips(self):
        assert normalize_whitespace("  hello  ") == "hello"

    def test_normalizes_crlf(self):
        assert "\r" not in normalize_whitespace("a\r\nb")

    def test_max_newlines(self):
        result = normalize_whitespace("a\n\n\n\n\nb")
        assert "\n\n\n" not in result


class TestCountWords:
    def test_basic(self):
        assert count_words("hello world foo") == 3

    def test_empty(self):
        assert count_words("") == 0

    def test_single(self):
        assert count_words("hello") == 1


class TestMimeFromExtension:
    def test_mp4(self):
        assert mime_from_extension(".mp4") == "video/mp4"

    def test_srt(self):
        assert mime_from_extension(".srt") == "text/srt"

    def test_html(self):
        assert mime_from_extension(".html") == "text/html"

    def test_unknown(self):
        assert mime_from_extension(".xyz") == "application/octet-stream"

    def test_case_insensitive(self):
        assert mime_from_extension(".MP4") == "video/mp4"


class TestAssetCategoryFromFile:
    def test_mp4(self):
        assert asset_category_from_file("02_04_video.mp4") == "video"

    def test_srt(self):
        assert asset_category_from_file("02_04_video.en.srt") == "transcript_srt"

    def test_txt(self):
        assert asset_category_from_file("02_04_video.en.txt") == "transcript_txt"

    def test_badge_is_administrative(self):
        assert asset_category_from_file("05_01_ibm-digital-badge_instructions.html") == "administrative"

    def test_infographic(self):
        assert asset_category_from_file("03_01_roadmap_200457 088 Infograph on roadmap.html") == "infographic"

    def test_assignment(self):
        assert asset_category_from_file("03_01_a-roadmap-to-your-data-science-journey_instructions.html") == "assignment"

    def test_reading(self):
        assert asset_category_from_file("02_01_lesson-overview_instructions.html") == "reading"


class TestRagEnabledForCategory:
    def test_video_enabled(self):
        assert rag_enabled_for_category("video") is True

    def test_administrative_disabled(self):
        assert rag_enabled_for_category("administrative") is False

    def test_transcript_enabled(self):
        assert rag_enabled_for_category("transcript_txt") is True
