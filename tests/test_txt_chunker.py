"""
tests/test_txt_chunker.py
==========================
Unit tests for the TXT transcript chunking and SRT alignment logic.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.transcript.process_txt import (
    split_into_sentences,
    chunk_text,
    align_chunks_to_srt,
)
from preprocessing.common.models import SRTBlock, TimestampConfidence


SAMPLE_TEXT = (
    "Data science is a process, not an event. "
    "It is the process of using data to understand different things. "
    "For me it is when you have a model or hypothesis. "
    "You try to validate that hypothesis with your data. "
    "Data science is the art of uncovering insights. "
    "Insights that are hiding behind data. "
    "It is when you translate data into a story. "
    "Use storytelling to generate insight. "
    "With these insights you can make strategic choices."
)


class TestSplitSentences:
    def test_basic(self):
        sents = split_into_sentences("Hello world. How are you? I am fine!")
        assert len(sents) == 3

    def test_single_sentence(self):
        sents = split_into_sentences("Just one sentence")
        assert len(sents) == 1

    def test_empty(self):
        sents = split_into_sentences("")
        assert sents == []


class TestChunkText:
    def test_returns_at_least_one_chunk(self):
        chunks = chunk_text(SAMPLE_TEXT, target_tokens=500, overlap_tokens=50)
        assert len(chunks) >= 1

    def test_chunk_indices_sequential(self):
        chunks = chunk_text(SAMPLE_TEXT, target_tokens=100, overlap_tokens=20)
        for i, c in enumerate(chunks):
            assert c["segment_index"] == i

    def test_small_target_creates_multiple_chunks(self):
        chunks = chunk_text(SAMPLE_TEXT, target_tokens=30, overlap_tokens=5)
        assert len(chunks) > 1

    def test_no_empty_chunks(self):
        chunks = chunk_text(SAMPLE_TEXT, target_tokens=100, overlap_tokens=20)
        for c in chunks:
            assert c["text"].strip() != ""

    def test_token_count_populated(self):
        chunks = chunk_text(SAMPLE_TEXT, target_tokens=100, overlap_tokens=20)
        for c in chunks:
            assert c["token_count"] >= 0

    def test_start_end_char_present(self):
        chunks = chunk_text(SAMPLE_TEXT, target_tokens=100, overlap_tokens=20)
        for c in chunks:
            assert c["start_char"] is not None
            assert c["end_char"] is not None

    def test_large_target_single_chunk(self):
        """A very large target tokens should produce just one chunk."""
        chunks = chunk_text(SAMPLE_TEXT, target_tokens=100_000, overlap_tokens=50)
        assert len(chunks) == 1


class TestAlignChunksToSrt:
    def _make_srt(self):
        return [
            SRTBlock(sequence_number=1, start_seconds=0.0, end_seconds=5.0, text="First."),
            SRTBlock(sequence_number=2, start_seconds=5.0, end_seconds=10.0, text="Second."),
            SRTBlock(sequence_number=3, start_seconds=10.0, end_seconds=15.0, text="Third."),
        ]

    def test_with_srt_blocks_sets_timestamps(self):
        chunks = chunk_text(SAMPLE_TEXT, target_tokens=100, overlap_tokens=20)
        srt_blocks = self._make_srt()
        aligned = align_chunks_to_srt(chunks, len(SAMPLE_TEXT), srt_blocks)
        # At least the first chunk should get a timestamp
        has_ts = any(c.get("start_time_seconds") is not None for c in aligned)
        assert has_ts

    def test_without_srt_all_none(self):
        chunks = chunk_text(SAMPLE_TEXT, target_tokens=100, overlap_tokens=20)
        aligned = align_chunks_to_srt(chunks, len(SAMPLE_TEXT), [])
        for c in aligned:
            assert c["start_time_seconds"] is None
            assert c["timestamp_confidence"] == TimestampConfidence.NONE.value

    def test_empty_text_no_crash(self):
        chunks = chunk_text("Hello.", target_tokens=500, overlap_tokens=50)
        aligned = align_chunks_to_srt(chunks, len("Hello."), self._make_srt())
        assert len(aligned) >= 1
