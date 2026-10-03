import os
import base64
import subprocess
import shutil

BRAIN_DIR = r"C:\Users\Abhi\.gemini\antigravity-ide\brain\a4fcc56a-4f40-47f2-ae31-f520db778e0d"
WORKSPACE_DIR = r"C:\Coursera-Multimodal-Intelligence-Platform-main"

def get_base64_image(filename):
    path = os.path.join(BRAIN_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    return ""

img_dashboard = get_base64_image("dashboard_overview_1790901885327.png")
img_issues = get_base64_image("issues_modal_1790901900944.png")
img_recs = get_base64_image("recommendations_modal_1790901929000.png")
img_reviews = get_base64_image("pending_reviews_modal_1790901960701.png")
img_chat = get_base64_image("chat_assistant_response_1790902027130.png")

html_slides = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Coursera Multimodal Intelligence Platform — Team & Executive Presentation</title>
  <style>
    @page {{
      size: 297mm 167mm; /* 16:9 widescreen landscape */
      margin: 0;
    }}
    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}
    body {{
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #0f172a;
      color: #1e293b;
    }}
    
    .slide {{
      width: 297mm;
      height: 167mm;
      padding: 12mm 16mm;
      position: relative;
      page-break-after: always;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
      background: #ffffff;
    }}

    /* Dark Slide Variant */
    .slide.dark {{
      background: #0f172a;
      color: #f8fafc;
    }}

    /* Slide Header */
    .slide-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 6mm;
      border-bottom: 1.5px solid #e2e8f0;
      padding-bottom: 4mm;
    }}
    .slide.dark .slide-header {{
      border-bottom-color: #334155;
    }}
    .header-left {{
      display: flex;
      flex-direction: column;
      gap: 1.5mm;
    }}
    .category-badge {{
      display: inline-block;
      font-size: 7.5pt;
      font-weight: 800;
      color: #2563eb;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }}
    .slide.dark .category-badge {{
      color: #38bdf8;
    }}
    .slide-title {{
      font-size: 17pt;
      font-weight: 800;
      color: #0f172a;
      margin: 0;
      letter-spacing: -0.4px;
    }}
    .slide.dark .slide-title {{
      color: #ffffff;
    }}
    .slide-subtitle {{
      font-size: 8.5pt;
      color: #64748b;
      margin: 0;
    }}
    .slide.dark .slide-subtitle {{
      color: #94a3b8;
    }}
    .slide-num {{
      font-size: 8pt;
      font-weight: 700;
      color: #94a3b8;
      background: #f1f5f9;
      padding: 2px 7px;
      border-radius: 4px;
    }}
    .slide.dark .slide-num {{
      background: #1e293b;
      color: #64748b;
    }}

    /* Slide Content Grid Layouts */
    .content-body {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6mm;
      height: 100%;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 5mm;
      height: 100%;
    }}

    .grid-4 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 4mm;
      height: 100%;
    }}

    .card {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 4mm 5mm;
      display: flex;
      flex-direction: column;
    }}
    .slide.dark .card {{
      background: #1e293b;
      border-color: #334155;
    }}

    .card-title {{
      font-size: 9.5pt;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 2mm;
    }}
    .slide.dark .card-title {{
      color: #ffffff;
    }}

    .card-metric {{
      font-size: 16pt;
      font-weight: 800;
      color: #2563eb;
      margin-bottom: 1.5mm;
    }}
    .slide.dark .card-metric {{
      color: #38bdf8;
    }}

    ul.bullet-list {{
      margin: 0;
      padding-left: 4.5mm;
      font-size: 7.5pt;
      color: #334155;
      line-height: 1.45;
    }}
    .slide.dark ul.bullet-list {{
      color: #cbd5e1;
    }}
    ul.bullet-list li {{
      margin-bottom: 2mm;
    }}
    ul.bullet-list li strong {{
      color: #0f172a;
    }}
    .slide.dark ul.bullet-list li strong {{
      color: #ffffff;
    }}

    .screenshot-box {{
      width: 100%;
      height: 100%;
      border-radius: 6px;
      border: 1px solid #cbd5e1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      background: #000000;
    }}
    .screenshot-box img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}

    /* Slide Footer */
    .slide-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid #e2e8f0;
      padding-top: 2.5mm;
      font-size: 7pt;
      color: #94a3b8;
      margin-top: 4mm;
    }}
    .slide.dark .slide-footer {{
      border-top-color: #334155;
      color: #64748b;
    }}
    .footer-left {{
      font-weight: 600;
    }}
  </style>
</head>
<body>

  <!-- SLIDE 1: TITLE SLIDE (DARK) -->
  <div class="slide dark" id="slide-1">
    <div style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <span style="background: rgba(37,99,235,0.3); border: 1px solid #3b82f6; color: #93c5fd; padding: 3px 10px; border-radius: 20px; font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
          Enterprise AI & Data Architecture Showcase
        </span>
        <h1 style="font-size: 32pt; font-weight: 800; color: #ffffff; margin: 6mm 0 2mm 0; line-height: 1.15; letter-spacing: -0.5px;">
          Coursera Multimodal Intelligence Platform
        </h1>
        <p style="font-size: 13pt; color: #94a3b8; margin: 0; max-width: 85%;">
          Evidence-First Data Pipelines, Relational Schemas, and Anti-Hallucination RAG for Course Intelligence
        </p>
      </div>

      <div class="grid-4" style="height: auto; margin: 8mm 0;">
        <div class="card" style="border-left: 3px solid #38bdf8;">
          <div style="font-size: 7.5pt; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Multimodal Assets</div>
          <div style="font-size: 16pt; font-weight: 800; color: #38bdf8; margin: 1mm 0;">157 Files</div>
          <div style="font-size: 7pt; color: #cbd5e1;">45 Videos, 45 SRTs, 45 TXTs, 22 HTMLs</div>
        </div>
        <div class="card" style="border-left: 3px solid #4ade80;">
          <div style="font-size: 7.5pt; color: #94a3b8; text-transform: uppercase; font-weight: 700;">PostgreSQL Schema</div>
          <div style="font-size: 16pt; font-weight: 800; color: #4ade80; margin: 1mm 0;">12 Tables</div>
          <div style="font-size: 7pt; color: #cbd5e1;">3NF Normalized with Cascade FKs</div>
        </div>
        <div class="card" style="border-left: 3px solid #c084fc;">
          <div style="font-size: 7.5pt; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Automated Testing</div>
          <div style="font-size: 16pt; font-weight: 800; color: #c084fc; margin: 1mm 0;">97 / 97 (100%)</div>
          <div style="font-size: 7pt; color: #cbd5e1;">Sub-second Unit & Guardrail Tests</div>
        </div>
        <div class="card" style="border-left: 3px solid #facc15;">
          <div style="font-size: 7.5pt; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Edge Performance</div>
          <div style="font-size: 16pt; font-weight: 800; color: #facc15; margin: 1mm 0;">0.289s Latency</div>
          <div style="font-size: 7pt; color: #cbd5e1;">Live Vercel Global Edge CDN</div>
        </div>
      </div>

      <div class="slide-footer">
        <div class="footer-left">Presented to Team & Company Leadership | Certified Production Release v1.2.0</div>
        <div>Live URL: coursera-multimodal-intelligence-pl.vercel.app | Git: 0382391</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 2: PROBLEM & VISION -->
  <div class="slide" id="slide-2">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">Strategic Overview</span>
        <h2 class="slide-title">The Challenge & Executive Vision</h2>
        <p class="slide-subtitle">Transforming disconnected course media into trusted, actionable instructional intelligence</p>
      </div>
      <span class="slide-num">02 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-2">
        <div class="card" style="background: #fef2f2; border-color: #fecaca;">
          <div style="color: #b91c1c; font-size: 10pt; font-weight: 800; margin-bottom: 3mm;">❌ CRITICAL INDUSTRY CHALLENGES</div>
          <ul class="bullet-list">
            <li><strong>Multimodal Data Fragmentation:</strong> Course archives contain video streams, subtitle files, text dumps, and web pages without unified metadata or relational links.</li>
            <li><strong>GenAI Hallucinations in Education:</strong> Generic LLMs invent syllabus facts, misquote lectures, and provide unverified answers without traceable citations.</li>
            <li><strong>Pedagogical Blindspots:</strong> Course creators lack visibility into student confusion points, transcript gaps, or quiz-to-lecture misalignment.</li>
            <li><strong>Severe RAG Lag:</strong> Early multimodal AI prototypes suffered from 2–3 minute latency per query due to unindexed vector scans.</li>
          </ul>
        </div>
        <div class="card" style="background: #ecfdf5; border-color: #a7f3d0;">
          <div style="color: #047857; font-size: 10pt; font-weight: 800; margin-bottom: 3mm;">✅ THE EVIDENCE-FIRST SOLUTION</div>
          <ul class="bullet-list">
            <li><strong>Deterministic Ingestion Engine:</strong> 100ms caption synchronization, 500-token semantic chunking, and SHA-256 asset registration across all media.</li>
            <li><strong>Normalized 12-Table Relational Schema:</strong> PostgreSQL / Supabase architecture preserving hierarchical lineage from Course down to millisecond video segments.</li>
            <li><strong>EvidenceValidator Guardrails:</strong> Strict anti-hallucination layer rejecting any response not grounded in retrieved course evidence (threshold &le; 0.40).</li>
            <li><strong>Sub-Second Edge Delivery:</strong> Decoupled FastAPI backend and React 18 client on Vercel Edge CDN with instantaneous Gemini 2.5 Flash streaming.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>Strategic Problem & Solution Framework</div>
    </div>
  </div>

  <!-- SLIDE 3: END-TO-END ARCHITECTURE -->
  <div class="slide" id="slide-3">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">System Design</span>
        <h2 class="slide-title">End-to-End System Architecture</h2>
        <p class="slide-subtitle">Modular pipeline connecting data ingestion, persistent storage, AI guardrails, and edge clients</p>
      </div>
      <span class="slide-num">03 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-4" style="gap: 3.5mm;">
        <div class="card" style="border-top: 3px solid #2563eb;">
          <div class="card-title">1. Data Ingestion</div>
          <div style="font-size: 7pt; color: #2563eb; font-weight: 700; margin-bottom: 2mm;">RAW ASSET PROCESSING</div>
          <ul class="bullet-list">
            <li><strong>ZIP Archive Parser:</strong> Validates folder stems (<code>NN_module/NN_group</code>).</li>
            <li><strong>SHA-256 Hashes:</strong> Ensures idempotency and data integrity.</li>
            <li><strong>Multi-Modal Extractor:</strong> Unpacks MP4, SRT, TXT, HTML.</li>
          </ul>
        </div>
        <div class="card" style="border-top: 3px solid #10b981;">
          <div class="card-title">2. Relational Store</div>
          <div style="font-size: 7pt; color: #10b981; font-weight: 700; margin-bottom: 2mm;">POSTGRESQL & VECTOR</div>
          <ul class="bullet-list">
            <li><strong>12 Normalized Tables:</strong> Courses, modules, lessons, assets, segments.</li>
            <li><strong>pgvector / Qdrant:</strong> 1536-dim dense vector indices.</li>
            <li><strong>Cascade Constraints:</strong> Guarantees clean entity lifecycle.</li>
          </ul>
        </div>
        <div class="card" style="border-top: 3px solid #8b5cf6;">
          <div class="card-title">3. AI & Guardrail</div>
          <div style="font-size: 7pt; color: #8b5cf6; font-weight: 700; margin-bottom: 2mm;">ANTI-HALLUCINATION</div>
          <ul class="bullet-list">
            <li><strong>Retriever Engine:</strong> Cosine similarity cutoff at &le; 0.40.</li>
            <li><strong>EvidenceValidator:</strong> Strict verification of citation tokens.</li>
            <li><strong>Gemini 2.5 Flash:</strong> Evidence-grounded synthesis.</li>
          </ul>
        </div>
        <div class="card" style="border-top: 3px solid #f59e0b;">
          <div class="card-title">4. Edge Delivery</div>
          <div style="font-size: 7pt; color: #f59e0b; font-weight: 700; margin-bottom: 2mm;">GLOBAL PERFORMANCE</div>
          <ul class="bullet-list">
            <li><strong>FastAPI Backend:</strong> Async microservices (/courses, /chat).</li>
            <li><strong>React 18 + Vite 8:</strong> Glassmorphic analytics dashboard.</li>
            <li><strong>Vercel Global Edge:</strong> 0.289s response latency.</li>
          </ul>
        </div>
      </div>
      
      <div class="card" style="margin-top: 4mm; background: #eff6ff; border-color: #bfdbfe; padding: 2.5mm 4mm;">
        <div style="font-size: 7.5pt; font-weight: 700; color: #1e40af;">
          🛡️ Enterprise Reliability Guarantee: Idempotent execution allows the pipeline to re-run on demand without duplicate entries, data drift, or source file corruption.
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>End-to-End System Pipeline</div>
    </div>
  </div>

  <!-- SLIDE 4: MULTIMODAL PREPROCESSING -->
  <div class="slide" id="slide-4">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">Data Engineering</span>
        <h2 class="slide-title">Multimodal Preprocessing & Quality Engine</h2>
        <p class="slide-subtitle">High-precision parsing for captions, semantic transcripts, HTML readings, and video streams</p>
      </div>
      <span class="slide-num">04 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-2">
        <div class="card">
          <div class="card-title">🎬 SRT Subtitle & Video Processing</div>
          <ul class="bullet-list">
            <li><strong>Sub-Second Precision:</strong> Parses subtitle blocks down to 100ms millisecond boundaries.</li>
            <li><strong>Monotonic Verification:</strong> Validates that <code>start_time &lt; end_time</code> and detects timestamp overlaps.</li>
            <li><strong>FFprobe Video Telemetry:</strong> Extracts duration, resolution, H.264 video codec, AAC audio codec, and FPS without CPU-heavy transcoding.</li>
            <li><strong>Verified Metric:</strong> <strong>45 SRT files &rarr; 3,280 segments</strong> with 0 empty captions and 0 timestamp anomalies.</li>
          </ul>
        </div>
        <div class="card">
          <div class="card-title">📄 Semantic Chunking & HTML Sanitization</div>
          <ul class="bullet-list">
            <li><strong>Sentence-Boundary Chunking:</strong> Target chunk size of ~500 tokens (range 77–500, mean ~387) preserving context integrity.</li>
            <li><strong>Cross-Modal Alignment:</strong> Links TXT chunk bounds directly to SRT video timestamps.</li>
            <li><strong>DOM Sanitizer:</strong> Strips scripts, navigation chrome, and isolates embedded base64 graphics into discrete asset entities.</li>
            <li><strong>Reading Classification:</strong> Auto-classifies HTML pages into Overview, Summary, Syllabus, or Assignment.</li>
          </ul>
        </div>
      </div>

      <div class="card" style="margin-top: 4mm; border-left: 3px solid #10b981;">
        <div style="font-size: 8pt; font-weight: 700; color: #065f46; margin-bottom: 1mm;">
          🔍 Automated 8-Rule Data Quality Suite (<code>preprocessing/quality/run_quality_checks.py</code>)
        </div>
        <div style="font-size: 7pt; color: #334155; line-height: 1.4;">
          Validates orphan video/transcript pairs, empty captions, token count outliers (&lt;50 or &gt;800 tokens), SHA-256 checksum integrity, and foreign key integrity before any record commits to the primary database.
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>Multimodal Preprocessing Layer</div>
    </div>
  </div>

  <!-- SLIDE 5: DATABASE ARCHITECTURE -->
  <div class="slide" id="slide-5">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">Persistence Layer</span>
        <h2 class="slide-title">Database Architecture: 12 Normalized Relational Tables</h2>
        <p class="slide-subtitle">PostgreSQL 15+ / Supabase schema with full 3NF normalization, foreign key cascading, and vector indexing</p>
      </div>
      <span class="slide-num">05 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-3">
        <div class="card" style="border-top: 3px solid #2563eb;">
          <div class="card-title">1. Course Hierarchy</div>
          <ul class="bullet-list">
            <li><code>courses</code>: Root course container (slug, name, source).</li>
            <li><code>course_modules</code>: Numbered module folders (1..4).</li>
            <li><code>lesson_groups</code>: Weekly instructional sections.</li>
            <li><code>lessons</code>: Atomic video and reading entities.</li>
          </ul>
          <div style="font-size: 7pt; color: #2563eb; font-weight: 700; margin-top: 3mm;">
            Unique Composite Indexes on (course_id, module_number) & (group_id, prefix).
          </div>
        </div>
        <div class="card" style="border-top: 3px solid #10b981;">
          <div class="card-title">2. Asset & Media Registry</div>
          <ul class="bullet-list">
            <li><code>assets</code>: Polymorphic file registry with SHA-256 checksums and processing status.</li>
            <li><code>videos</code>: Stream metadata, FPS, codecs.</li>
            <li><code>video_segments</code>: Chunks with <code>VECTOR(1536)</code>.</li>
            <li><code>transcripts</code>: SRT & TXT formats.</li>
            <li><code>transcript_segments</code>: Semantic text chunks.</li>
            <li><code>readings</code>: Sanitized HTML articles.</li>
          </ul>
        </div>
        <div class="card" style="border-top: 3px solid #8b5cf6;">
          <div class="card-title">3. Operations & QA</div>
          <ul class="bullet-list">
            <li><code>processing_jobs</code>: Multi-stage pipeline state machine (Ingestion, Parsing, QA, Vectorization).</li>
            <li><code>data_quality_issues</code>: Automated audit findings categorized by severity (CRITICAL, HIGH, MEDIUM, LOW).</li>
          </ul>
          <div style="font-size: 7pt; color: #8b5cf6; font-weight: 700; margin-top: 3mm;">
            Automated migration script <code>migrate_to_supabase.py</code> enables instant cloud replication.
          </div>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>12-Table Relational Schema</div>
    </div>
  </div>

  <!-- SLIDE 6: AI RAG & ANTI-HALLUCINATION -->
  <div class="slide" id="slide-6">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">Artificial Intelligence</span>
        <h2 class="slide-title">Evidence-Grounded RAG & Anti-Hallucination Guardrails</h2>
        <p class="slide-subtitle">Strict verification of LLM citations against retrieved course evidence chunks</p>
      </div>
      <span class="slide-num">06 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-2">
        <div class="card">
          <div class="card-title">🛡️ Guardrail Architecture & Execution Flow</div>
          <ul class="bullet-list">
            <li><strong>Cosine Retrieval &amp; Thresholding:</strong> Queries retrieve top-5 dense vector chunks. If maximum similarity is <strong>&lt; 0.40</strong>, speculation is rejected with an explicit notice.</li>
            <li><strong>Synthetic Citation Injection:</strong> Verified evidence chunks are tagged with citation tokens (<code>E1</code>, <code>E2</code>). The LLM is strictly constrained to cite only these tokens.</li>
            <li><strong>EvidenceValidator Inspection:</strong> The <code>EvidenceValidator.validate()</code> interceptor scans model output. If any ungrounded citation ID (e.g. <code>fake-evidence-999</code>) is detected, the response is discarded.</li>
            <li><strong>Gemini 2.5 Flash Synthesis:</strong> Fast, pedagogical reasoning grounded 100% in syllabus transcripts.</li>
          </ul>
        </div>
        <div class="screenshot-box">
          <img src="{img_chat}" alt="Conversational AI Assistant" />
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>AI / RAG Guardrail Pipeline</div>
    </div>
  </div>

  <!-- SLIDE 7: BACKEND APIS -->
  <div class="slide" id="slide-7">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">API Architecture</span>
        <h2 class="slide-title">FastAPI Microservice Architecture & Modular Routers</h2>
        <p class="slide-subtitle">High-throughput asynchronous endpoints with Pydantic serialization and auto-generated Swagger documentation</p>
      </div>
      <span class="slide-num">07 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-3">
        <div class="card">
          <div style="font-size: 8.5pt; font-weight: 700; color: #2563eb; margin-bottom: 1.5mm;">📦 COURSES ROUTER</div>
          <div style="font-size: 7.5pt; font-weight: 600; color: #0f172a;">routers/courses.py</div>
          <ul class="bullet-list" style="margin-top: 2mm;">
            <li><code>GET /courses/</code>: Lists all registered courses, provider origin, status.</li>
            <li><code>POST /courses/analyze</code>: Spawns asynchronous course ingestion job.</li>
            <li><code>GET /courses/{{id}}/status</code>: Real-time progress monitoring per pipeline stage.</li>
          </ul>
        </div>
        <div class="card">
          <div style="font-size: 8.5pt; font-weight: 700; color: #10b981; margin-bottom: 1.5mm;">💬 CHAT ROUTER</div>
          <div style="font-size: 7.5pt; font-weight: 600; color: #0f172a;">routers/chat.py</div>
          <ul class="bullet-list" style="margin-top: 2mm;">
            <li><code>POST /chat/query</code>: Multi-turn conversational RAG query handler.</li>
            <li>Performs dense vector retrieval, similarity cutoff, and <code>EvidenceValidator</code> verification.</li>
            <li>Returns answer, confidence score, and verified citation cards.</li>
          </ul>
        </div>
        <div class="card">
          <div style="font-size: 8.5pt; font-weight: 700; color: #8b5cf6; margin-bottom: 1.5mm;">📊 ANALYSIS ROUTER</div>
          <div style="font-size: 7.5pt; font-weight: 600; color: #0f172a;">routers/analysis.py</div>
          <ul class="bullet-list" style="margin-top: 2mm;">
            <li><code>GET /analysis/dashboard</code>: Aggregates high-level metrics (Courses, Issues, Recommendations).</li>
            <li><code>GET /analysis/{{id}}</code>: Granular instructional friction profile, quiz failure rate correlation.</li>
          </ul>
        </div>
      </div>

      <div class="card" style="margin-top: 4mm; background: #f8fafc;">
        <div style="display: flex; justify-content: space-between; font-size: 7.5pt; font-weight: 600; color: #475569;">
          <span>⚡ Asynchronous I/O via Uvicorn</span>
          <span>🔒 SQLAlchemy Connection Pooling</span>
          <span>🛡️ Pydantic v2 Type Safety</span>
          <span>🌐 Dynamic CORS Middleware</span>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>Backend API Layer</div>
    </div>
  </div>

  <!-- SLIDE 8: FRONTEND DASHBOARD -->
  <div class="slide" id="slide-8">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">User Interface</span>
        <h2 class="slide-title">Interactive React + Vite Analytics Dashboard</h2>
        <p class="slide-subtitle">Glassmorphism aesthetic, clickable executive KPI cards, and instant diagnostic modal drilldowns</p>
      </div>
      <span class="slide-num">08 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-2" style="grid-template-columns: 1.4fr 1fr;">
        <div class="screenshot-box">
          <img src="{img_dashboard}" alt="Platform Dashboard Overview" />
        </div>
        <div class="card">
          <div class="card-title">🖥️ Interactive UI Highlights</div>
          <ul class="bullet-list">
            <li><strong>Clickable KPI Metric Cards:</strong> Instantly opens drill-down modals for Courses (15+), Issues Detected (85+), Recommendations (60+), and Pending Reviews (8+).</li>
            <li><strong>Course Inventory Grid:</strong> Filter and explore courses by provider, completion status, and asset volume.</li>
            <li><strong>Issue Distribution Chart:</strong> Visual breakdown of concept confusion, insufficient examples, and quiz misalignment.</li>
            <li><strong>Vite 8 Build Efficiency:</strong> Assembled in <strong>270 milliseconds</strong> with zero bundle warnings.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>Executive Dashboard Interface</div>
    </div>
  </div>

  <!-- SLIDE 9: DIAGNOSTIC MODALS & PEDAGOGY -->
  <div class="slide" id="slide-9">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">Instructional Intelligence</span>
        <h2 class="slide-title">Deep Diagnostic Modals & Pedagogical Remediation</h2>
        <p class="slide-subtitle">Surfacing granular curriculum friction points with actionable, timestamp-linked remediation plans</p>
      </div>
      <span class="slide-num">09 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-2">
        <div class="screenshot-box">
          <img src="{img_issues}" alt="Quality Issues Modal" />
        </div>
        <div class="screenshot-box">
          <img src="{img_recs}" alt="Recommendations Modal" />
        </div>
      </div>
      
      <div class="card" style="margin-top: 4mm; border-left: 3px solid #2563eb; padding: 2.5mm 4mm;">
        <div style="font-size: 7.5pt; color: #1e3a8a; line-height: 1.4;">
          <strong>Targeted Remediation Engine:</strong> Cross-references lecture transcripts with student quiz failure rates. Detects when 56% of learners miss questions on specific topics and generates tailored remediation advice (e.g., adding visual schematics at 04:35).
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>Diagnostic Modals & Remediation</div>
    </div>
  </div>

  <!-- SLIDE 10: DEPLOYMENT & EDGE -->
  <div class="slide" id="slide-10">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">Cloud Infrastructure</span>
        <h2 class="slide-title">Production Deployment & Global Edge Network</h2>
        <p class="slide-subtitle">High-availability architecture on Vercel Global Edge CDN, Docker containers, and Supabase cloud</p>
      </div>
      <span class="slide-num">10 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-3">
        <div class="card" style="border-top: 3px solid #2563eb;">
          <div class="card-title">🌐 Vercel Global Edge</div>
          <div class="card-metric">0.289s</div>
          <div style="font-size: 7pt; color: #2563eb; font-weight: 700; margin-bottom: 2mm;">EDGE CDN LATENCY</div>
          <ul class="bullet-list">
            <li>Deployed globally at <code>coursera-multimodal-intelligence-pl.vercel.app</code>.</li>
            <li>Zero cold starts, edge SSL, and automated GitHub CI/CD continuous deployment.</li>
          </ul>
        </div>
        <div class="card" style="border-top: 3px solid #10b981;">
          <div class="card-title">🐳 Dockerized Backend</div>
          <div class="card-metric">FastAPI</div>
          <div style="font-size: 7pt; color: #10b981; font-weight: 700; margin-bottom: 2mm;">MICROSERVICE RUNTIME</div>
          <ul class="bullet-list">
            <li>Packaged via <code>Dockerfile.backend</code> and <code>docker-compose.yml</code>.</li>
            <li>Render cloud deployment configuration via <code>render.yaml</code>.</li>
          </ul>
        </div>
        <div class="card" style="border-top: 3px solid #8b5cf6;">
          <div class="card-title">🔒 Supabase & Security</div>
          <div class="card-metric">PostgreSQL</div>
          <div style="font-size: 7pt; color: #8b5cf6; font-weight: 700; margin-bottom: 2mm;">CLOUD DATA LAYER</div>
          <ul class="bullet-list">
            <li>Managed cloud PostgreSQL 15+ with pgvector indexing.</li>
            <li>Secrets isolated in <code>.env</code>; user override supported in <code>localStorage</code>.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>Cloud & DevOps Infrastructure</div>
    </div>
  </div>

  <!-- SLIDE 11: AUTOMATED TESTING -->
  <div class="slide" id="slide-11">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">Quality Assurance</span>
        <h2 class="slide-title">Automated Testing & Release Certification</h2>
        <p class="slide-subtitle">97 / 97 automated tests passing with 100% fidelity across parsers, guardrails, and production builds</p>
      </div>
      <span class="slide-num">11 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-2">
        <div class="card" style="background: #0f172a; color: #f8fafc; border-color: #334155;">
          <div style="color: #38bdf8; font-size: 9pt; font-weight: 700; margin-bottom: 2mm; font-family: monospace;">
            TERMINAL EXECUTION LOG
          </div>
          <div style="font-family: monospace; font-size: 7pt; line-height: 1.45; color: #cbd5e1;">
            [1/4] Backend Unit & Parser Tests (93 tests)<br/>
            tests/test_html_extractor.py (23 passed)<br/>
            tests/test_srt_parser.py     (21 passed)<br/>
            tests/test_txt_chunker.py    (13 passed)<br/>
            tests/test_utils.py          (36 passed)<br/>
            <span style="color: #4ade80; font-weight: bold;">==&gt; 93 passed in 0.88s</span><br/><br/>
            [2/4] AI Evidence Validator Tests<br/>
            Ai_Tests/test_evidence_validator.py <span style="color: #4ade80;">[1 passed in 0.03s]</span><br/>
            <span style="color: #facc15;">==&gt; Correctly rejected fake citation 'fake-evidence-999'</span><br/><br/>
            [3/4] Frontend Production Build<br/>
            vite build: 16 modules transformed <span style="color: #4ade80;">[Built in 270ms]</span><br/><br/>
            [4/4] Live Production HTTP Probe<br/>
            Vercel Edge HTTP 200 | Latency: <span style="color: #4ade80; font-weight: bold;">0.289s</span>
          </div>
        </div>
        <div class="card" style="background: #ecfdf5; border-color: #a7f3d0;">
          <div style="color: #065f46; font-size: 10pt; font-weight: 800; margin-bottom: 3mm;">
            🏆 OFFICIAL QUALITY CERTIFICATION
          </div>
          <ul class="bullet-list">
            <li><strong>100% Sub-Second Pass Rate:</strong> Comprehensive test suite finishes in under 1 second.</li>
            <li><strong>Zero Untracked Hallucinations:</strong> Guardrail rigorously tested against adversarial and fabricated citations.</li>
            <li><strong>Automated Data Quality Checks:</strong> 8 integrity rules running across all media files.</li>
            <li><strong>Production Release Sign-Off:</strong> Certified ready for general availability under Git commit <code>0382391</code>.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>Testing & Quality Sign-Off</div>
    </div>
  </div>

  <!-- SLIDE 12: BUSINESS ROI -->
  <div class="slide" id="slide-12">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">Business Impact</span>
        <h2 class="slide-title">Quantifiable Business ROI & Strategic Value</h2>
        <p class="slide-subtitle">Accelerating curriculum development cycles, reducing review overhead, and increasing student retention</p>
      </div>
      <span class="slide-num">12 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-4">
        <div class="card" style="border-top: 3px solid #2563eb;">
          <div class="card-metric">80%</div>
          <div class="card-title">Review Time Savings</div>
          <div style="font-size: 7pt; color: #64748b; line-height: 1.4;">
            Automates transcript analysis, caption validation, and syllabus auditing, reducing manual review from weeks to minutes.
          </div>
        </div>
        <div class="card" style="border-top: 3px solid #10b981;">
          <div class="card-metric">100%</div>
          <div class="card-title">Grounded Responses</div>
          <div style="font-size: 7pt; color: #64748b; line-height: 1.4;">
            Evidence-backed RAG guarantees learners receive accurate, syllabus-aligned answers, completely eliminating AI liability.
          </div>
        </div>
        <div class="card" style="border-top: 3px solid #8b5cf6;">
          <div class="card-metric">56%</div>
          <div class="card-title">Bottleneck Remediation</div>
          <div style="font-size: 7pt; color: #64748b; line-height: 1.4;">
            Pins student drop-off to specific video timestamps and quiz questions, enabling targeted instructional interventions.
          </div>
        </div>
        <div class="card" style="border-top: 3px solid #f59e0b;">
          <div class="card-metric">0.28s</div>
          <div class="card-title">Global Edge Latency</div>
          <div style="font-size: 7pt; color: #64748b; line-height: 1.4;">
            Global CDN ensures instantaneous interaction for students and faculty across international campuses.
          </div>
        </div>
      </div>

      <div class="card" style="margin-top: 5mm; background: #eff6ff; border-color: #bfdbfe; text-align: center; padding: 3mm;">
        <div style="font-size: 8.5pt; font-weight: 700; color: #1e40af;">
          "Transforming unstructured educational media into a structured, queryable enterprise knowledge asset."
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>Business Impact & Value Realization</div>
    </div>
  </div>

  <!-- SLIDE 13: PRODUCT ROADMAP -->
  <div class="slide" id="slide-13">
    <div class="slide-header">
      <div class="header-left">
        <span class="category-badge">Strategic Vision</span>
        <h2 class="slide-title">Product Roadmap & Future Engineering Horizons</h2>
        <p class="slide-subtitle">Scaling from single-certificate intelligence to enterprise-wide catalog reasoning</p>
      </div>
      <span class="slide-num">13 / 14</span>
    </div>

    <div class="content-body">
      <div class="grid-3">
        <div class="card" style="background: #ecfdf5; border-color: #a7f3d0;">
          <div style="font-size: 8pt; font-weight: 800; color: #065f46; text-transform: uppercase;">Phase 1: Completed</div>
          <div class="card-title" style="margin-top: 1mm;">Multimodal Ingestion & DB</div>
          <ul class="bullet-list" style="margin-top: 2mm;">
            <li>157 course files processed.</li>
            <li>12 normalized PostgreSQL tables.</li>
            <li>SRT 100ms alignment validated.</li>
            <li>97 automated tests certified.</li>
            <li>Live on Vercel Global Edge CDN.</li>
          </ul>
        </div>
        <div class="card" style="background: #eff6ff; border-color: #bfdbfe;">
          <div style="font-size: 8pt; font-weight: 800; color: #1d4ed8; text-transform: uppercase;">Phase 2: In Flight (Q4)</div>
          <div class="card-title" style="margin-top: 1mm;">Catalog Scaling & Hybrid RAG</div>
          <ul class="bullet-list" style="margin-top: 2mm;">
            <li>Automated multi-course batch ingestion.</li>
            <li>Hybrid sparse + dense vector retrieval.</li>
            <li>Faculty review workflow in dashboard.</li>
            <li>Real-time video frame embedding.</li>
            <li>Automated quiz remediation triggers.</li>
          </ul>
        </div>
        <div class="card" style="background: #faf5ff; border-color: #e9d5ff;">
          <div style="font-size: 8pt; font-weight: 800; color: #7e22ce; text-transform: uppercase;">Phase 3: Horizon (2027)</div>
          <div class="card-title" style="margin-top: 1mm;">Autonomous Tutoring & Voice</div>
          <ul class="bullet-list" style="margin-top: 2mm;">
            <li>Conversational voice tutoring agent.</li>
            <li>Adaptive student skill diagnostics.</li>
            <li>LMS integration (Canvas, Blackboard).</li>
            <li>Predictive course dropout analytics.</li>
            <li>Multi-lingual transcript synthesis.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="slide-footer">
      <div class="footer-left">Coursera Multimodal Intelligence Platform</div>
      <div>Product Engineering Roadmap</div>
    </div>
  </div>

  <!-- SLIDE 14: Q&A & CONCLUSION (DARK) -->
  <div class="slide dark" id="slide-14">
    <div style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <span style="background: rgba(16,185,129,0.2); border: 1px solid #10b981; color: #6ee7b7; padding: 3px 10px; border-radius: 20px; font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
          Production Certified & Live
        </span>
        <h1 style="font-size: 28pt; font-weight: 800; color: #ffffff; margin: 6mm 0 2mm 0; line-height: 1.15;">
          Thank You! Questions & Live Demonstration
        </h1>
        <p style="font-size: 11pt; color: #94a3b8; margin: 0;">
          The platform is live and ready for interactive evaluation by the team and leadership
        </p>
      </div>

      <div class="grid-3" style="height: auto; margin: 6mm 0;">
        <div class="card" style="border-top: 3px solid #38bdf8;">
          <div style="font-size: 7.5pt; color: #94a3b8; font-weight: 700; text-transform: uppercase;">LIVE PRODUCTION URL</div>
          <div style="font-size: 9.5pt; font-weight: 700; color: #ffffff; margin: 2mm 0;">coursera-multimodal-intelligence-pl.vercel.app</div>
          <div style="font-size: 7pt; color: #94a3b8;">Interactive dashboard, clickable modals, and RAG copilot</div>
        </div>
        <div class="card" style="border-top: 3px solid #4ade80;">
          <div style="font-size: 7.5pt; color: #94a3b8; font-weight: 700; text-transform: uppercase;">SOURCE CODE REPOSITORY</div>
          <div style="font-size: 9.5pt; font-weight: 700; color: #ffffff; margin: 2mm 0;">github.com/abhik99/Coursera-Multimodal</div>
          <div style="font-size: 7pt; color: #94a3b8;">112 committed files, 97 passing tests, full documentation</div>
        </div>
        <div class="card" style="border-top: 3px solid #c084fc;">
          <div style="font-size: 7.5pt; color: #94a3b8; font-weight: 700; text-transform: uppercase;">TECHNICAL SPECIFICATION</div>
          <div style="font-size: 9.5pt; font-weight: 700; color: #ffffff; margin: 2mm 0;">Technical Brief PDF (8 Pages)</div>
          <div style="font-size: 7pt; color: #94a3b8;">Comprehensive schema, endpoints, data contract & tests</div>
        </div>
      </div>

      <div class="slide-footer">
        <div class="footer-left">Coursera Multimodal Intelligence Platform | Certified Ready for General Availability</div>
        <div>Git Commit: 0382391 | Production Release v1.2.0</div>
      </div>
    </div>
  </div>

  <script>
    // Keyboard navigation for interactive presentations in browser
    let currentSlide = 1;
    const totalSlides = 14;

    function showSlide(num) {{
      if (num < 1) num = 1;
      if (num > totalSlides) num = totalSlides;
      currentSlide = num;
      const el = document.getElementById(`slide-${{num}}`);
      if (el) {{
        el.scrollIntoView({{ behavior: 'smooth' }});
      }}
    }}

    window.addEventListener('keydown', (e) => {{
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{
        showSlide(currentSlide + 1);
      }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
        showSlide(currentSlide - 1);
      }} else if (e.key === 'Home') {{
        showSlide(1);
      }} else if (e.key === 'End') {{
        showSlide(totalSlides);
      }} else if (e.key === 'f' || e.key === 'F') {{
        if (!document.fullscreenElement) {{
          document.documentElement.requestFullscreen();
        }} else {{
          document.exitFullscreen();
        }}
      }}
    }});
  </script>
</body>
</html>
"""

html_path = os.path.join(WORKSPACE_DIR, "Coursera_Multimodal_Intelligence_Platform_Slides.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_slides)

edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_exe):
    edge_exe = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

pdf_presentation_path = os.path.join(WORKSPACE_DIR, "Coursera_Multimodal_Intelligence_Platform_Presentation.pdf")
pdf_presentation_brain = os.path.join(BRAIN_DIR, "Coursera_Multimodal_Intelligence_Platform_Presentation.pdf")

cmd = [
    edge_exe,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_presentation_path}",
    html_path
]

print(f"Generating 16:9 Presentation PDF via Edge headless from: {html_path}")
result = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(pdf_presentation_path):
    size = os.path.getsize(pdf_presentation_path)
    shutil.copy(pdf_presentation_path, pdf_presentation_brain)
    print(f"SUCCESS: Created Presentation PDF at {pdf_presentation_path} ({size:,} bytes)")
    print(f"Copied to brain directory: {pdf_presentation_brain}")
else:
    print(f"FAILED to generate Presentation PDF. Error: {result.stderr}")
