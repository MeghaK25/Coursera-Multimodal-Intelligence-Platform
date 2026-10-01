# 🌐 Production Cloud Deployment: Supabase + Render + Vercel (100% Free Tier)

This guide provides step-by-step instructions to deploy the complete **Coursera Insight** multimodal AI application to production for free using:
- **Database**: [Supabase](https://supabase.com) (PostgreSQL 16 + `pgvector` with 9,479 embeddings)
- **Backend API**: [Render](https://render.com) (FastAPI + Sentence Transformers + Gemini AI)
- **Frontend SPA**: [Vercel](https://vercel.com) (React 19 + Tailwind CSS)

---

## 🗺️ Architecture & Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant Vercel as Vercel (Frontend React)
    participant Render as Render (FastAPI Backend)
    participant Supabase as Supabase (Postgres + pgvector)
    participant Gemini as Google Gemini 2.5 Flash

    User->>Vercel: Load Dashboard / Chat UI
    User->>Render: POST /chat/ (Course ID, Query)
    Render->>Render: SentenceTransformer encode query (384-dim)
    Render->>Supabase: Vector cosine similarity search (<=> operator)
    Supabase-->>Render: Top-k transcript & reading chunks
    Render->>Gemini: Synthesize grounded response with citations
    Gemini-->>Render: Markdown response + evidence
    Render-->>User: JSON response rendered in chat bubble
```

---

## 🗄️ Step 1: Set Up & Migrate Supabase Database

### 1.1 Create Free Supabase Project
1. Go to [supabase.com](https://supabase.com) and create an account.
2. Click **New Project**:
   - **Name**: `coursera-insight`
   - **Database Password**: Choose a strong password (remember this!).
   - **Region**: Choose the region closest to you or Render's region (e.g. `US East (N. Virginia)`).
3. Wait 1-2 minutes for the database to provision.

### 1.2 Enable the pgvector Extension
1. In your Supabase project dashboard, navigate to **SQL Editor** on the left menu.
2. Click **New Query**, paste the following, and click **Run**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### 1.3 Copy Your Connection String
1. Go to **Project Settings** (gear icon) ➔ **Database**.
2. Scroll to **Connection string** ➔ Select the **URI** tab.
3. Switch the mode dropdown from "Transaction" to **Session** (or direct connection port 5432).
4. Copy the connection string. It will look like:
   ```text
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
   *(Replace `[YOUR-PASSWORD]` with the actual database password you chose in Step 1.1).*

### 1.4 Migrate Local Data & Embeddings to Supabase (1-Click)
Run the migration script already configured in your repository:
```powershell
python scripts/migrate_to_supabase.py "postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
```
> **What this does:** Automatically migrates the schema, enum types, all course assets, 186 readings, and all 9,479 vector embeddings directly from your local Docker container into Supabase!

---

## ⚡ Step 2: Deploy Backend to Render

### 2.1 Push Code to GitHub
Ensure your repository is pushed to GitHub:
```powershell
git add .
git commit -m "Configure production deployment for Supabase, Render, and Vercel"
git push origin main
```

### 2.2 Create Web Service on Render
1. Go to [render.com](https://render.com) and sign in.
2. Click **New +** ➔ **Web Service**.
3. Select **Build and deploy from a Git repository** and connect your repository.
4. Fill in the deployment settings:
   - **Name**: `coursera-insight-backend`
   - **Region**: Same or close to your Supabase region (e.g., `Oregon (US West)` or `Ohio (US East)`)
   - **Branch**: `main`
   - **Root Directory**: *(leave blank — runs from project root)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### 2.3 Set Environment Variables on Render
Under the **Environment Variables** section, add:

| Key | Value |
| :--- | :--- |
| `DATABASE_URL` | Your Supabase connection URI from Step 1.3 (e.g., `postgresql://postgres.xxx:pass@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require`) |
| `GEMINI_API_KEY` | Your Google Gemini API Key (`AIzaSy...`) |
| `PYTHON_VERSION` | `3.11.9` |

### 2.4 Deploy & Verify
1. Click **Create Web Service**.
2. Render will build the service and output logs. Once finished, you will see a green checkmark: `Your service is live 🎉`.
3. Copy your live Render URL (e.g., `https://coursera-insight-backend.onrender.com`).
4. Test the health check endpoint in your browser:
   ```text
   https://coursera-insight-backend.onrender.com/health
   ```
   It should return: `{"status": "healthy"}`.

---

## 🎨 Step 3: Deploy Frontend to Vercel

### 3.1 Import Project in Vercel
1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** ➔ **Project**.
3. Select your GitHub repository.

### 3.2 Configure Build & Output Settings
1. **Framework Preset**: `Vite`
2. **Root Directory**: Click "Edit" and choose **`frontend`**.
3. **Build Command**: `npm run build`
4. **Output Directory**: `dist`

### 3.3 Add Environment Variable
Expand the **Environment Variables** section and add:

| Key | Value |
| :--- | :--- |
| `VITE_API_BASE_URL` | Your live Render backend URL from Step 2.4 (e.g., `https://coursera-insight-backend.onrender.com`) |

*(Do not add a trailing slash)*

### 3.4 Deploy
1. Click **Deploy**.
2. Vercel will install dependencies, build the static assets, and deploy globally across its edge network in ~30 seconds.
3. You will receive your live URL: `https://coursera-insight-xxxx.vercel.app`!

---

## 🧪 Step 4: Verification & Live Testing

1. Open your live Vercel URL in your browser.
2. **Dashboard**: Verify the 4 KPI cards, Recent Courses list, and Top Issues progress bars load.
3. **AI Chat**:
   - Go to the **AI Chat** tab.
   - Click one of the suggestion chips (e.g., *"Why are learners struggling with the union rule?"*) or type your own question.
   - Click **Send**.
   - Confirm that the response streams back with citations, similarity scores, and grounded context from Supabase!
4. **Settings**:
   - The API Base URL will automatically be pre-filled with your Render backend URL. You can also test or update it directly from the UI.

---

## 💡 Troubleshooting & Tips

- **Render Cold Starts**: Render's free tier spins down after 15 minutes of inactivity. The first request after sleep may take ~30–45 seconds to wake up. Once awake, requests respond instantly.
- **Supabase SSL Mode**: If you receive a connection error from Render, ensure `?sslmode=require` is appended to your `DATABASE_URL`.
- **CORS**: The backend is already configured with `allow_origins=["*"]`, so requests from your Vercel domain will never be blocked.
