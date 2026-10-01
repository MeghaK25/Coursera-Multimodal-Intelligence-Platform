# Asset Relationships — IBM Data Science Professional Certificate

> **Inference basis:** Folder structure, filename prefixes, matching stems, and content inspection.  
> **Confidence levels:** HIGH = directly confirmed by folder/filename structure; MEDIUM = inferred from naming pattern; LOW = uncertain.

---

## Primary Relationship Chain

```
IBM Data Science Professional Certificate (course)
        │
        ├── [01] defining-data-science-and-what-data-scientists-do  (module)
        │         │
        │         ├── [01] welcome-to-the-course        (lesson group)
        │         ├── [02] defining-data-science         (lesson group)
        │         └── [03] what-do-data-scientists-do   (lesson group)
        │                   │
        │                   └── [03_02] a-day-in-the-life-of-a-data-scientist  (lesson)
        │                             ├── .mp4     (video)
        │                             ├── .en.srt  (timed transcript — subtitle track)
        │                             └── .en.txt  (clean plain-text transcript)
        │
        ├── [02] data-science-topics                    (module)
        │         ├── [01] big-data-and-data-mining     (lesson group)
        │         └── [02] deep-learning-and-machine-learning  (lesson group)
        │
        ├── [03] applications-and-careers-in-data-science  (module)
        │         ├── [01] data-science-application-domains  (lesson group)
        │         ├── [02] careers-and-recruiting            (lesson group)
        │         ├── [03] final-assignment                  (administrative)
        │         ├── [04] course-wrap-up                    (administrative)
        │         └── [05] digital-badge                     (administrative)
        │
        └── [04] data-literacy-for-data-science-optional  (module — optional)
                  ├── [01] understanding-data          (lesson group)
                  └── [02] data-literacy               (lesson group)
```

---

## Relationship 1: Video ↔ Transcript (SRT + TXT)

**Confidence: HIGH**

Every video lesson has exactly two transcript files sharing the same filename stem:

| Video | SRT Transcript | TXT Transcript |
|-------|---------------|----------------|
| `NN_NN_<title>.mp4` | `NN_NN_<title>.en.srt` | `NN_NN_<title>.en.txt` |

**Evidence:** Confirmed for all 45 video/transcript triples — zero orphans detected.

**Semantic distinction:**
- `.en.srt` — SubRip format, contains start/end timestamps per caption segment. Used for subtitle rendering and fine-grained timestamp alignment.
- `.en.txt` — Plain continuous prose, no timestamps. Used for full-text search, chunking, and embedding.

Both represent the **same spoken content** from the video.

---

## Relationship 2: Lesson Overview HTML ↔ Video Lessons

**Confidence: HIGH**

Each lesson group begins with a `NN_01_lesson-overview-<name>_instructions.html` file that lists the videos in that lesson group.

Example:
```
02_defining-data-science/
    02_01_lesson-overview-defining-data-science_instructions.html   ← overview
    02_02_what-is-data-science.*                                    ← video + transcripts
    02_03_fundamentals-of-data-science.*                            ← video + transcripts
    ...
    02_06_lesson-summary-defining-data-science.*                    ← summary video
```

**Evidence:** Confirmed by inspecting the HTML content of `01_02_course-syllabus_instructions.html`, which lists lesson titles matching actual file stems.

---

## Relationship 3: Summary HTML ↔ Video Lesson Group

**Confidence: HIGH**

Each lesson group that has videos also ends with two summary assets:

1. A **summary video** (`NN_lesson-summary-<name>.mp4` + SRT + TXT)
2. A **summary reading HTML** (`NN_summary-<name>_instructions.html`)

Both recap the same lesson group. They are sibling assets, not parent-child.

---

## Relationship 4: Final Assignment ↔ Lesson Content

**Confidence: MEDIUM**

The final assignment (`03_final-assignment/03_01_a-roadmap-to-your-data-science-journey_instructions.html`) is a peer-reviewed activity that requires knowledge from all prior modules. It is contextually related to `03_applications-and-careers-in-data-science` (Module 3) but draws on content from Modules 1–3.

The assignment HTML embeds a base64-encoded PNG infographic image (~500 KB uncompressed). A companion accessible HTML version is also present.

---

## Relationship 5: Course Syllabus ↔ All Modules

**Confidence: HIGH**

The `01_02_course-syllabus_instructions.html` file provides a human-readable listing of all course content. It acts as the course manifest/table of contents.

---

## Relationship 6: Digital Badge ↔ Course Completion

**Confidence: HIGH**

The `05_01_ibm-digital-badge_instructions.html` file (157 KB) is an administrative asset pointing to an IBM SkillsBuild digital badge. It is not a learning asset but a course-completion credential reference.

---

## Asset Types NOT Found

| Relationship Type | Status |
|-------------------|--------|
| Video → Quiz      | ❌ No quiz files found |
| Video → Slides    | ❌ No slide files found |
| Video → Jupyter Notebook | ❌ Not present |
| Module → Discussion Thread | ❌ Not present |
| Lesson → PDF Reading | ❌ No PDFs in dataset |
| Video segment → Frame image | ❌ No extracted frame images |

---

## Complete Asset Triplet Map (Video + SRT + TXT)

All 45 video lessons confirmed to have all three files:

| Module | Lesson Group | Lesson Item |
|--------|-------------|-------------|
| 01 | 01_welcome | 01_01 course-introduction |
| 01 | 02_defining-ds | 02_02 what-is-data-science |
| 01 | 02_defining-ds | 02_03 fundamentals-of-data-science |
| 01 | 02_defining-ds | 02_04 the-many-paths-to-data-science |
| 01 | 02_defining-ds | 02_05 advice-for-new-data-scientists |
| 01 | 02_defining-ds | 02_06 lesson-summary-defining-data-science |
| 01 | 03_what-ds-do | 03_02 a-day-in-the-life-of-a-data-scientist |
| 01 | 03_what-ds-do | 03_03 data-science-skills-big-data |
| 01 | 03_what-ds-do | 03_04 understanding-different-types-of-file-formats |
| 01 | 03_what-ds-do | 03_05 data-science-topics-and-algorithms |
| 01 | 03_what-ds-do | 03_06 lesson-summary-what-do-data-scientists-do |
| 02 | 01_big-data | 01_02 how-big-data-is-driving-digital-transformation |
| 02 | 01_big-data | 01_03 introduction-to-cloud |
| 02 | 01_big-data | 01_04 cloud-for-data-science |
| 02 | 01_big-data | 01_05 foundations-of-big-data |
| 02 | 01_big-data | 01_06 data-science-and-big-data |
| 02 | 01_big-data | 01_07 what-is-hadoop |
| 02 | 01_big-data | 01_08 big-data-processing-tools-hadoop-hdfs-hive-spark |
| 02 | 01_big-data | 01_09 lesson-summary-big-data-and-data-mining |
| 02 | 02_dl-ml | 02_02 artificial-intelligence-and-data-science |
| 02 | 02_dl-ml | 02_03 generative-ai-and-data-science |
| 02 | 02_dl-ml | 02_04 neural-networks-and-deep-learning |
| 02 | 02_dl-ml | 02_05 applications-of-machine-learning |
| 02 | 02_dl-ml | 02_06 lesson-summary-deep-learning-and-machine-learning |
| 03 | 01_domains | 01_02 how-should-companies-get-started |
| 03 | 01_domains | 01_03 old-problems-new-data-science-solutions |
| 03 | 01_domains | 01_04 applications-of-data-science |
| 03 | 01_domains | 01_05 how-data-science-is-saving-lives |
| 03 | 01_domains | 01_06 lesson-summary-data-science-application-domain |
| 03 | 02_careers | 02_02 how-can-someone-become-a-data-scientist |
| 03 | 02_careers | 02_03 recruiting-for-data-science |
| 03 | 02_careers | 02_04 careers-in-data-science |
| 03 | 02_careers | 02_05 importance-of-mathematics-and-statistics |
| 03 | 02_careers | 02_06 lesson-summary-careers-and-recruiting |
| 04 | 01_understanding | 01_02 understanding-data |
| 04 | 01_understanding | 01_03 data-sources |
| 04 | 01_understanding | 01_04 viewpoints-working-with-varied-data-sources |
| 04 | 01_understanding | 01_05 lesson-summary-understanding-data |
| 04 | 02_data-literacy | 02_02 data-collection-and-organization |
| 04 | 02_data-literacy | 02_03 relational-database-management-system |
| 04 | 02_data-literacy | 02_04 nosql |
| 04 | 02_data-literacy | 02_05 data-marts-data-lakes-etl-and-data-pipelines |
| 04 | 02_data-literacy | 02_06 viewpoints-considerations-for-choice-of-data-repository |
| 04 | 02_data-literacy | 02_07 data-integration-platforms |
| 04 | 02_data-literacy | 02_08 lesson-summary-welcome-to-data-literacy |
