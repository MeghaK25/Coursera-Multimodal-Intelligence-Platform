"""
tests/test_html_extractor.py
==============================
Unit tests for HTML extraction, base64 image detection, and classification.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.html_proc.process_html import (
    extract_text,
    classify_html,
    rag_for_subtype,
    extract_base64_images,
)
from preprocessing.common.models import ReadingSubtype


class TestExtractText:
    def test_basic_html(self):
        html = "<html><body><p>Hello world</p></body></html>"
        text = extract_text(html)
        assert "Hello world" in text

    def test_strips_script_tags(self):
        html = "<html><body><script>alert('x')</script><p>Real text</p></body></html>"
        text = extract_text(html)
        assert "alert" not in text
        assert "Real text" in text

    def test_strips_style_tags(self):
        html = "<html><head><style>body {color:red}</style></head><body><p>OK</p></body></html>"
        text = extract_text(html)
        assert "color" not in text
        assert "OK" in text

    def test_unwraps_co_content(self):
        html = "<co-content><p>Inside co-content</p></co-content>"
        text = extract_text(html)
        assert "Inside co-content" in text

    def test_empty_html(self):
        text = extract_text("")
        assert text == ""

    def test_meta_charset_only(self):
        html = '<meta charset="utf-8"/>'
        text = extract_text(html)
        # Should not crash and return minimal/empty text
        assert isinstance(text, str)

    def test_list_items_extracted(self):
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        text = extract_text(html)
        assert "Item 1" in text
        assert "Item 2" in text


class TestClassifyHtml:
    @pytest.mark.parametrize("filename, expected", [
        ("01_01_lesson-overview-understanding-data_instructions.html", ReadingSubtype.LESSON_OVERVIEW),
        ("02_06_lesson-summary-big-data.en.html", ReadingSubtype.LESSON_SUMMARY),
        ("01_02_course-syllabus_instructions.html", ReadingSubtype.COURSE_SYLLABUS),
        ("01_04_helpful-tips-for-course-completion_instructions.html", ReadingSubtype.TIPS),
        ("03_01_a-roadmap-to-your-data-science-journey_instructions.html", ReadingSubtype.ASSIGNMENT),
        ("03_01_a-roadmap_200457 088 Infograph on roadmap.html", ReadingSubtype.INFOGRAPHIC),
        ("05_01_ibm-digital-badge_instructions.html", ReadingSubtype.ADMINISTRATIVE),
        ("04_02_congrats-next-steps_instructions.html", ReadingSubtype.ADMINISTRATIVE),
        ("04_03_course-team-and-acknowledgements_instructions.html", ReadingSubtype.ADMINISTRATIVE),
        ("some_other_file.html", ReadingSubtype.OTHER),
    ])
    def test_classifications(self, filename, expected):
        assert classify_html(filename) == expected


class TestRagForSubtype:
    def test_administrative_is_false(self):
        assert rag_for_subtype(ReadingSubtype.ADMINISTRATIVE) is False

    def test_lesson_overview_is_true(self):
        assert rag_for_subtype(ReadingSubtype.LESSON_OVERVIEW) is True

    def test_assignment_is_true(self):
        assert rag_for_subtype(ReadingSubtype.ASSIGNMENT) is True

    def test_infographic_is_true(self):
        assert rag_for_subtype(ReadingSubtype.INFOGRAPHIC) is True


class TestBase64Detection:
    def test_no_image_returns_none(self):
        html = "<p>Plain text</p>"
        cleaned, img_path = extract_base64_images(html, "test_slug")
        assert img_path is None
        assert cleaned == html

    def test_image_detected(self, tmp_path, monkeypatch):
        """Patch processed_data_dir so images_dir resolves inside tmp_path."""
        from preprocessing.common import config
        monkeypatch.setattr(config.settings, "processed_data_dir", str(tmp_path))
        # Tiny 1x1 white PNG in base64
        tiny_png_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        html = f'<img src="data:image/png;base64,{tiny_png_b64}"/>'
        cleaned, img_path = extract_base64_images(html, "test/slug.html")
        assert img_path is not None
        assert "extracted://" in cleaned
        assert "data:image/png;base64" not in cleaned
