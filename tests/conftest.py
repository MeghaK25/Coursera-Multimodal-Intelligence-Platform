"""
tests/conftest.py
===================
Shared pytest fixtures for the test suite.
"""

import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def sample_srt_content():
    return """1
00:00:05,360 --> 00:00:09,920
Welcome to your journey toward an enticing career path.

2
00:00:09,920 --> 00:00:12,690
Data science has witnessed recent remarkable growth.

3
00:00:12,690 --> 00:00:15,730
Due to the abundance of electronic data and computing power.

4
00:00:15,730 --> 00:00:20,420
Advancements in artificial intelligence and demonstrated business value.

5
00:00:20,420 --> 00:00:23,760
In the United States, the Bureau of Labor Statistics projects a 35% growth rate.
"""


@pytest.fixture
def sample_txt_content():
    return (
        "Data Science is a process, not an event. "
        "It is the process of using data to understand different things, to understand the world. "
        "For me, it is when you have a model or hypothesis of a problem, "
        "and you try to validate that hypothesis or model with your data. "
        "Data science is the art of uncovering the insights and trends that are hiding behind data. "
        "It's when you translate data into a story. "
        "So use storytelling to generate insight. "
        "And with these insights, you can make strategic choices for a company or an institution."
    )


@pytest.fixture
def sample_html_lesson_overview():
    return """<meta charset="utf-8"/>
<co-content>
 <p>
  In this lesson, you will learn about data science fundamentals.
 </p>
 <ul>
  <li>What is data science?</li>
  <li>Fundamentals of data science</li>
  <li>The many paths to data science</li>
 </ul>
</co-content>"""


@pytest.fixture
def sample_html_with_base64():
    # Minimal 1x1 pixel PNG in base64
    tiny_png = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+"
        "M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    return f'<html><body><img src="data:image/png;base64,{tiny_png}"/><p>Text</p></body></html>'
