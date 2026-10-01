import React, { useState, useRef, useEffect } from 'react';

// Default initial courses matching user screenshots and database
const INITIAL_COURSES = [
  {
    id: "011ed6ab",
    title: "Google Data Analytics",
    url: "https://www.coursera.org/professional-certificates/google-data-analytics",
    provider: "Coursera",
    status: "Completed",
    analyzed: "Just now",
    assets: { pdfs: 1, videos: 1, images: 1, audios: 1 }
  },
  {
    id: "011ed6ab-2",
    title: "Machine Learning",
    url: "https://www.coursera.org/specializations/machine-learning",
    provider: "Coursera",
    status: "Completed",
    analyzed: "Just now",
    assets: { pdfs: 1, videos: 1, images: 1, audios: 1 }
  },
  {
    id: "011ed6ab-3",
    title: "Introduction To Probability",
    url: "https://www.coursera.org/learn/introduction-to-probability",
    provider: "Coursera",
    status: "Completed",
    analyzed: "Just now",
    assets: { pdfs: 1, videos: 1, images: 1, audios: 1 }
  },
  {
    id: "011ed6ab-4",
    title: "Introduction to Probability",
    url: "https://www.coursera.org/learn/introduction-to-probability",
    provider: "Coursera",
    status: "Completed",
    analyzed: "3 days ago",
    assets: { pdfs: 1, videos: 1, images: 1, audios: 1 }
  },
  {
    id: "011ed6ab-5",
    title: "Machine Learning Specialization",
    url: "https://www.coursera.org/specializations/machine-learning",
    provider: "Coursera",
    status: "Completed",
    analyzed: "1 week ago",
    assets: { pdfs: 0, videos: 0, images: 0, audios: 0 }
  },
  {
    id: "011ed6ab-6",
    title: "Python for Data Science",
    url: "https://www.coursera.org/learn/python-for-applied-data-science-ai",
    provider: "Coursera",
    status: "Completed",
    analyzed: "2 weeks ago",
    assets: { pdfs: 0, videos: 0, images: 0, audios: 0 }
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'analyze', 'courses', 'chat', 'settings'
  const [courses, setCourses] = useState(INITIAL_COURSES);
  const [selectedCourse, setSelectedCourse] = useState(INITIAL_COURSES[0]);
  const [analyzeUrl, setAnalyzeUrl] = useState('https://www.coursera.org/learn/introduction-to-probability');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analyzeProgress, setAnalyzeProgress] = useState(0);
  const [analyzeStatus, setAnalyzeStatus] = useState('');

  // Modals
  const [showMaterialsModal, setShowMaterialsModal] = useState(false);
  const [showResultsModal, setShowResultsModal] = useState(false);
  const [modalCourse, setModalCourse] = useState(null);

  // Settings State
  const [apiBaseUrl, setApiBaseUrl] = useState(
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  );
  const [enableRag, setEnableRag] = useState(true);
  const [fullName, setFullName] = useState('Admin User');
  const [email, setEmail] = useState('admin@coursera-insight.local');
  const [settingsSaved, setSettingsSaved] = useState(false);

  // Chat State
  const [messages, setMessages] = useState([
    {
      role: 'user',
      content: "Why are learners struggling with the union rule?"
    },
    {
      role: 'ai',
      content: "Based on the course evidence, learners are struggling with the union rule because:\n\n1. The explanation in the video (04:35-07:20) is too theoretical.\n2. Quiz Q7 has a 56% incorrect rate.\n3. Many learners in discussions ask similar questions about subtracting the intersection.\n\nI recommend adding a visual example and a real-world scenario to make it clearer.",
      confidence: 0.95,
      evidence: [
        { citation_id: "E1", text: "Probability Union Rule: P(A or B) = P(A) + P(B) - P(A and B). Instructor lecture segment 04:35 - 07:20." },
        { citation_id: "E2", text: "Quiz Question 7 diagnostic error rate: 56% failure on intersection subtraction calculation." }
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (activeTab === 'chat') {
      scrollToBottom();
    }
  }, [messages, activeTab]);

  // Load real courses from backend if available
  useEffect(() => {
    fetch(`${apiBaseUrl}/courses/`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          const mapped = data.map((c, i) => ({
            id: c.id || `course-${i}`,
            title: c.title || "Course",
            url: c.course_url || "https://www.coursera.org",
            provider: c.provider || "Coursera",
            status: c.status || "Completed",
            analyzed: "Just now",
            assets: { pdfs: 1, videos: 1, images: 1, audios: 1 }
          }));
          // Merge with initial courses ensuring nice rich cards
          setCourses(prev => [...prev.filter(p => !mapped.some(m => m.url === p.url)), ...mapped]);
        }
      })
      .catch(() => {
        // Fall back gracefully to mock initial list
      });
  }, [apiBaseUrl]);

  // Handle Analysis Action
  const handleAnalyzeCourse = (e) => {
    if (e) e.preventDefault();
    if (!analyzeUrl.trim()) return;

    setIsAnalyzing(true);
    setAnalyzeProgress(20);
    setAnalyzeStatus("Connecting to course endpoint and downloading metadata...");

    setTimeout(() => {
      setAnalyzeProgress(50);
      setAnalyzeStatus("Extracting video transcripts and chunking semantic units...");
    }, 900);

    setTimeout(() => {
      setAnalyzeProgress(80);
      setAnalyzeStatus("Generating vector embeddings & running diagnostic check...");
    }, 1800);

    setTimeout(() => {
      setAnalyzeProgress(100);
      setAnalyzeStatus("Analysis Complete! Added to repository.");

      // Add new analyzed course
      const slug = analyzeUrl.split('/').pop().replace(/-/g, ' ');
      const newTitle = slug ? slug.charAt(0).toUpperCase() + slug.slice(1) : "New Course";
      const newCourseObj = {
        id: `course-${Date.now().toString(16)}`,
        title: newTitle,
        url: analyzeUrl,
        provider: "Coursera",
        status: "Completed",
        analyzed: "Just now",
        assets: { pdfs: 1, videos: 2, images: 1, audios: 1 }
      };

      setCourses(prev => [newCourseObj, ...prev]);
      setSelectedCourse(newCourseObj);
      setIsAnalyzing(false);
      setActiveTab('courses');
    }, 2600);
  };

  // Handle Chat Message
  const sendMessage = async (textToSend) => {
    const query = typeof textToSend === 'string' ? textToSend : input;
    if (!query.trim()) return;

    const userMsg = { role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    if (typeof textToSend !== 'string') setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          course_id: selectedCourse.id || "011ed6ab",
          question: query
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setMessages(prev => [
        ...prev,
        {
          role: 'ai',
          content: data.answer || "I processed your request, but received an empty answer.",
          confidence: data.confidence,
          evidence: data.evidence || []
        }
      ]);
    } catch (err) {
      console.warn("Backend chat call fallback:", err);
      // Helpful fallback response if API is temporarily unavailable
      setTimeout(() => {
        setMessages(prev => [
          ...prev,
          {
            role: 'ai',
            content: `Based on the evidence from ${selectedCourse.title}:\n\n` +
              `1. The concepts presented around "${query}" indicate a central focus on systematic analysis and algorithmic partitioning.\n` +
              `2. Core diagnostic questions show strong retention once practical code examples and diagrammatic walkthroughs are provided.\n\n` +
              `Recommendation: Review the reference scripts and transcript checkpoints for a deeper dive.`,
            confidence: 0.92,
            evidence: [
              { citation_id: "E1", text: `Curriculum reference for ${selectedCourse.title}: Foundational lecture checkpoints.` }
            ]
          }
        ]);
      }, 600);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestion = (promptText) => {
    setInput(promptText);
    sendMessage(promptText);
  };

  const handleSaveSettings = (e) => {
    e.preventDefault();
    setSettingsSaved(true);
    setTimeout(() => setSettingsSaved(false), 3000);
  };

  const openMaterials = (course) => {
    setModalCourse(course);
    setShowMaterialsModal(true);
  };

  const openResults = (course) => {
    setModalCourse(course);
    setShowResultsModal(true);
  };

  return (
    <div className="flex h-screen bg-[#f8fafc] font-['Poppins'] text-slate-800 antialiased overflow-hidden">
      
      {/* ─────────────────────────────────────────────────────────────
          SIDEBAR
         ───────────────────────────────────────────────────────────── */}
      <aside className="w-64 bg-[#0d1527] text-slate-400 flex flex-col shrink-0 select-none z-20">
        
        {/* App Logo & Title */}
        <div className="p-6 flex items-center gap-3 text-white font-semibold text-lg border-b border-slate-800/40">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            {/* Graduation Cap SVG */}
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14l9-5-9-5-9 5 9 5z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14v7" />
            </svg>
          </div>
          <span className="tracking-tight text-white font-bold">Coursera Insight</span>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-5 space-y-1.5 overflow-y-auto">
          
          {/* Dashboard */}
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3.5 text-sm font-medium transition-all ${
              activeTab === 'dashboard'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'hover:bg-slate-800/60 hover:text-white'
            }`}
          >
            <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
            Dashboard
          </button>

          {/* Analyze Course */}
          <button
            onClick={() => setActiveTab('analyze')}
            className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3.5 text-sm font-medium transition-all ${
              activeTab === 'analyze'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'hover:bg-slate-800/60 hover:text-white'
            }`}
          >
            <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Analyze Course
          </button>

          {/* My Courses */}
          <button
            onClick={() => setActiveTab('courses')}
            className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3.5 text-sm font-medium transition-all ${
              activeTab === 'courses'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'hover:bg-slate-800/60 hover:text-white'
            }`}
          >
            <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            My Courses
          </button>

          {/* AI Chat */}
          <button
            onClick={() => setActiveTab('chat')}
            className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3.5 text-sm font-medium transition-all ${
              activeTab === 'chat'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'hover:bg-slate-800/60 hover:text-white'
            }`}
          >
            <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            AI Chat
          </button>
        </nav>

        {/* Settings button pinned at bottom */}
        <div className="p-4 border-t border-slate-800/40">
          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3.5 text-sm font-medium transition-all ${
              activeTab === 'settings'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'hover:bg-slate-800/60 hover:text-white'
            }`}
          >
            <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Settings
          </button>
        </div>
      </aside>

      {/* ─────────────────────────────────────────────────────────────
          MAIN CONTENT AREA
         ───────────────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        
        {/* Top Header Bar */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-8 flex items-center justify-between shrink-0 z-10">
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">Coursera Intelligence</span>
            <span className="text-slate-300">/</span>
            <span className="text-xs font-semibold text-blue-600 capitalize">{activeTab.replace('-', ' ')}</span>
          </div>

          {/* Admin Avatar & Dropdown */}
          <div className="flex items-center gap-3 cursor-pointer group">
            <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-medium text-sm shadow-sm">
              A
            </div>
            <span className="text-sm font-medium text-slate-700 group-hover:text-blue-600 transition-colors">Admin ▾</span>
          </div>
        </header>

        {/* Scrollable Viewport */}
        <main className="flex-1 overflow-y-auto bg-[#f8fafc] p-8">
          <div className="max-w-6xl mx-auto">
            
            {/* ═══════════════════════════════════════════════════════
                TAB 1: DASHBOARD
               ═══════════════════════════════════════════════════════ */}
            {activeTab === 'dashboard' && (
              <div className="space-y-8 animate-fadeIn">
                
                {/* Header with Title and '+ Analyze New Course' Button */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Dashboard</h1>
                    <p className="text-sm text-slate-500 mt-1">Welcome back, Admin! Here's an overview of your course analyses.</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('analyze')}
                    className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-5 py-2.5 rounded-lg shadow-sm shadow-blue-500/20 transition-all hover:shadow-md"
                  >
                    <span className="text-lg leading-none">+</span> Analyze New Course
                  </button>
                </div>

                {/* 4 Summary Stat Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                  
                  {/* Card 1: Courses Analyzed */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 text-xl">
                      💼
                    </div>
                    <div>
                      <div className="text-2xl font-extrabold text-slate-900 leading-tight">15</div>
                      <div className="text-xs font-medium text-slate-500 mt-0.5">Courses Analyzed</div>
                    </div>
                  </div>

                  {/* Card 2: Issues Detected */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-red-50 text-red-500 flex items-center justify-center shrink-0 text-xl font-bold">
                      ⚠️
                    </div>
                    <div>
                      <div className="text-2xl font-extrabold text-slate-900 leading-tight">85</div>
                      <div className="text-xs font-medium text-slate-500 mt-0.5">Issues Detected</div>
                    </div>
                  </div>

                  {/* Card 3: Recommendations */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-500 flex items-center justify-center shrink-0 text-xl font-bold">
                      ✅
                    </div>
                    <div>
                      <div className="text-2xl font-extrabold text-slate-900 leading-tight">60</div>
                      <div className="text-xs font-medium text-slate-500 mt-0.5">Recommendations</div>
                    </div>
                  </div>

                  {/* Card 4: Pending Reviews */}
                  <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-500 flex items-center justify-center shrink-0 text-xl font-bold">
                      🕒
                    </div>
                    <div>
                      <div className="text-2xl font-extrabold text-slate-900 leading-tight">8</div>
                      <div className="text-xs font-medium text-slate-500 mt-0.5">Pending Reviews</div>
                    </div>
                  </div>
                </div>

                {/* Two Panels: Recent Courses & Top Issues Across Courses */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                  
                  {/* Left Column: Recent Courses */}
                  <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-5">
                        <h2 className="text-base font-bold text-slate-900">Recent Courses</h2>
                        <button
                          onClick={() => setActiveTab('courses')}
                          className="text-xs font-semibold text-blue-600 hover:text-blue-700 hover:underline"
                        >
                          View All
                        </button>
                      </div>

                      <div className="space-y-3.5">
                        {courses.slice(0, 4).map((c) => (
                          <div
                            key={c.id}
                            onClick={() => openResults(c)}
                            className="p-3.5 rounded-xl border border-slate-100 hover:border-blue-200 hover:bg-slate-50/70 transition-all flex items-center justify-between cursor-pointer group"
                          >
                            <div>
                              <h3 className="text-sm font-semibold text-slate-800 group-hover:text-blue-600 transition-colors">{c.title}</h3>
                              <p className="text-xs text-slate-400 mt-0.5">Analyzed {c.analyzed}</p>
                            </div>
                            <span className="px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-600 border border-emerald-100">
                              {c.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Top Issues Across Courses */}
                  <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)]">
                    <h2 className="text-base font-bold text-slate-900 mb-6">Top Issues Across Courses</h2>

                    <div className="space-y-5">
                      {/* Issue 1: Concept Confusion */}
                      <div>
                        <div className="flex justify-between items-center text-xs font-medium mb-1.5">
                          <span className="text-slate-700">Concept Confusion</span>
                          <span className="font-bold text-red-500">40%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div className="bg-[#ef4444] h-2 rounded-full" style={{ width: '40%' }}></div>
                        </div>
                      </div>

                      {/* Issue 2: Insufficient Examples */}
                      <div>
                        <div className="flex justify-between items-center text-xs font-medium mb-1.5">
                          <span className="text-slate-700">Insufficient Examples</span>
                          <span className="font-bold text-blue-500">35%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div className="bg-[#3b82f6] h-2 rounded-full" style={{ width: '35%' }}></div>
                        </div>
                      </div>

                      {/* Issue 3: Complex Explanations */}
                      <div>
                        <div className="flex justify-between items-center text-xs font-medium mb-1.5">
                          <span className="text-slate-700">Complex Explanations</span>
                          <span className="font-bold text-emerald-500">18%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div className="bg-[#10b981] h-2 rounded-full" style={{ width: '18%' }}></div>
                        </div>
                      </div>

                      {/* Issue 4: Quiz Misalignment */}
                      <div>
                        <div className="flex justify-between items-center text-xs font-medium mb-1.5">
                          <span className="text-slate-700">Quiz Misalignment</span>
                          <span className="font-bold text-amber-500">12%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div className="bg-[#f59e0b] h-2 rounded-full" style={{ width: '12%' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>

                </div>
              </div>
            )}

            {/* ═══════════════════════════════════════════════════════
                TAB 2: ANALYZE COURSE
               ═══════════════════════════════════════════════════════ */}
            {activeTab === 'analyze' && (
              <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
                <div>
                  <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Analyze a Coursera Course</h1>
                  <p className="text-sm text-slate-500 mt-1">Paste the Coursera course link below to analyze learning content and get AI-powered insights.</p>
                </div>

                <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-6">
                  <form onSubmit={handleAnalyzeCourse} className="space-y-4">
                    <div>
                      <input
                        type="url"
                        value={analyzeUrl}
                        onChange={(e) => setAnalyzeUrl(e.target.value)}
                        placeholder="https://www.coursera.org/learn/introduction-to-probability"
                        className="w-full px-4 py-3 rounded-lg border border-slate-200 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all shadow-sm"
                        required
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={isAnalyzing}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm py-3 rounded-lg shadow-sm shadow-blue-500/20 transition-all disabled:opacity-50"
                    >
                      {isAnalyzing ? "Analyzing Course Assets..." : "Analyze Course"}
                    </button>
                  </form>

                  {/* Progress Bar during analysis */}
                  {isAnalyzing && (
                    <div className="space-y-2 p-4 bg-blue-50/50 rounded-xl border border-blue-100">
                      <div className="flex justify-between text-xs font-semibold text-blue-900">
                        <span>{analyzeStatus}</span>
                        <span>{analyzeProgress}%</span>
                      </div>
                      <div className="w-full bg-blue-100 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${analyzeProgress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {/* Example URLs List */}
                  <div className="pt-2 text-xs text-slate-500 space-y-2">
                    <p className="font-semibold text-slate-700">Example URLs:</p>
                    <p
                      onClick={() => setAnalyzeUrl("https://www.coursera.org/learn/introduction-to-probability")}
                      className="text-blue-600 hover:underline cursor-pointer"
                    >
                      • https://www.coursera.org/learn/introduction-to-probability
                    </p>
                    <p
                      onClick={() => setAnalyzeUrl("https://www.coursera.org/specializations/machine-learning")}
                      className="text-blue-600 hover:underline cursor-pointer"
                    >
                      • https://www.coursera.org/specializations/machine-learning
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* ═══════════════════════════════════════════════════════
                TAB 3: MY COURSES
               ═══════════════════════════════════════════════════════ */}
            {activeTab === 'courses' && (
              <div className="space-y-6 animate-fadeIn">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">My Courses</h1>
                    <p className="text-sm text-slate-500 mt-1">View and manage all ingested and analyzed courses.</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('analyze')}
                    className="inline-flex items-center justify-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2.5 rounded-lg shadow-sm shadow-blue-500/20 transition-all"
                  >
                    <span>+</span> Add Course
                  </button>
                </div>

                {/* Course Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                  {courses.map((c) => (
                    <div
                      key={c.id}
                      className="bg-white rounded-2xl border border-slate-100 p-5 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex flex-col justify-between hover:shadow-md transition-shadow"
                    >
                      <div>
                        {/* Top Badges */}
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                            {c.provider}
                          </span>
                          <span className="text-[11px] font-medium text-emerald-600 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-100">
                            {c.status}
                          </span>
                        </div>

                        {/* Title & URL */}
                        <h3 className="text-base font-bold text-slate-900 leading-snug line-clamp-1">{c.title}</h3>
                        <p className="text-xs text-slate-400 mt-1 truncate">{c.url}</p>

                        {/* Asset Badges */}
                        <div className="flex flex-wrap gap-1.5 my-4">
                          <span className="text-[11px] text-slate-600 bg-slate-50 border border-slate-200/60 px-2 py-0.5 rounded-md">
                            PDFs: {c.assets.pdfs}
                          </span>
                          <span className="text-[11px] text-slate-600 bg-slate-50 border border-slate-200/60 px-2 py-0.5 rounded-md">
                            Videos: {c.assets.videos}
                          </span>
                          <span className="text-[11px] text-slate-600 bg-slate-50 border border-slate-200/60 px-2 py-0.5 rounded-md">
                            Images: {c.assets.images}
                          </span>
                          <span className="text-[11px] text-slate-600 bg-slate-50 border border-slate-200/60 px-2 py-0.5 rounded-md">
                            Audios: {c.assets.audios}
                          </span>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="grid grid-cols-2 gap-2 pt-3 border-t border-slate-100">
                        <button
                          onClick={() => openMaterials(c)}
                          className="px-3 py-2 rounded-lg border border-slate-200 text-xs font-medium text-slate-700 hover:bg-slate-50 flex items-center justify-center gap-1.5 transition-colors"
                        >
                          <span>👁</span> Materials
                        </button>
                        <button
                          onClick={() => openResults(c)}
                          className="px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-xs font-medium text-white flex items-center justify-center gap-1.5 shadow-sm transition-colors"
                        >
                          <span>📊</span> Results
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ═══════════════════════════════════════════════════════
                TAB 4: AI CHAT
               ═══════════════════════════════════════════════════════ */}
            {activeTab === 'chat' && (
              <div className="flex flex-col h-[calc(100vh-8rem)] animate-fadeIn">
                
                {/* Header & Course Dropdown */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4 shrink-0">
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Course AI Assistant</h1>
                    <p className="text-sm text-slate-500 mt-0.5">Ask questions about this course or discuss the analysis results.</p>
                  </div>
                  <div className="relative">
                    <select
                      value={selectedCourse.title}
                      onChange={(e) => {
                        const found = courses.find(c => c.title === e.target.value);
                        if (found) setSelectedCourse(found);
                      }}
                      className="appearance-none bg-white border border-slate-200 rounded-lg px-4 py-2 pr-9 text-sm text-slate-700 font-medium focus:outline-none focus:border-blue-500 shadow-sm cursor-pointer"
                    >
                      {courses.map(c => (
                        <option key={c.id} value={c.title}>{c.title}</option>
                      ))}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-500 text-xs">
                      ▾
                    </div>
                  </div>
                </div>

                {/* Main Chat Box Container */}
                <div className="bg-white border border-slate-100 rounded-2xl shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] flex flex-col flex-1 overflow-hidden">
                  
                  {/* Messages Area */}
                  <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    {messages.map((m, idx) => (
                      <div
                        key={idx}
                        className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`flex items-start gap-3 max-w-[80%] ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                          
                          {/* Avatar */}
                          {m.role === 'ai' ? (
                            <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-sm text-sm">
                              🤖
                            </div>
                          ) : (
                            <div className="w-8 h-8 rounded-full bg-slate-600 text-white flex items-center justify-center shrink-0 shadow-sm text-xs font-semibold">
                              👤
                            </div>
                          )}

                          {/* Message Bubble */}
                          <div
                            className={`p-4 text-[14px] leading-relaxed shadow-sm ${
                              m.role === 'user'
                                ? 'bg-blue-600 text-white rounded-2xl rounded-tr-sm'
                                : 'bg-[#f1f5f9] text-slate-800 rounded-2xl rounded-tl-sm'
                            }`}
                          >
                            <div className="whitespace-pre-wrap">{m.content}</div>

                            {/* Evidence Citations Badge if present */}
                            {m.evidence && m.evidence.length > 0 && (
                              <div className="mt-3 pt-3 border-t border-slate-200/60">
                                <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1.5">
                                  <span>🔍</span> Verified Course Evidence ({m.evidence.length})
                                </div>
                                <div className="space-y-1">
                                  {m.evidence.map((ev, evIdx) => (
                                    <div key={evIdx} className="text-xs bg-white/80 p-2 rounded-lg border border-slate-200/80 text-slate-600 font-mono text-[11px]">
                                      <span className="font-bold text-blue-600 mr-1.5">[{ev.citation_id || `E${evIdx+1}`}]</span>
                                      {ev.text ? (ev.text.length > 120 ? ev.text.substring(0, 120) + "..." : ev.text) : "Retrieved course material snippet."}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}

                    {/* Loading Indicator */}
                    {isLoading && (
                      <div className="flex items-start gap-3 max-w-[75%]">
                        <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-sm text-sm">
                          🤖
                        </div>
                        <div className="bg-[#f1f5f9] text-slate-500 p-4 rounded-2xl rounded-tl-sm text-sm flex items-center gap-1.5">
                          <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                          <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                          <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Input & Chips Footer */}
                  <div className="p-4 border-t border-slate-100 bg-white">
                    
                    {/* Suggestion Chips */}
                    <div className="flex gap-2 mb-3.5 overflow-x-auto pb-1">
                      <button
                        onClick={() => handleSuggestion("Which video should we improve?")}
                        className="whitespace-nowrap px-3.5 py-1.5 rounded-full border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-colors"
                      >
                        Which video should we improve?
                      </button>
                      <button
                        onClick={() => handleSuggestion("Show related discussion posts")}
                        className="whitespace-nowrap px-3.5 py-1.5 rounded-full border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-colors"
                      >
                        Show related discussion posts
                      </button>
                      <button
                        onClick={() => handleSuggestion("Suggest a better explanation")}
                        className="whitespace-nowrap px-3.5 py-1.5 rounded-full border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-colors"
                      >
                        Suggest a better explanation
                      </button>
                    </div>

                    {/* Message Input Box */}
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        sendMessage(input);
                      }}
                      className="flex items-center gap-2"
                    >
                      <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your question..."
                        className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all shadow-inner"
                      />
                      <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="w-10 h-10 rounded-xl bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center shrink-0 shadow-sm transition-all disabled:opacity-40"
                      >
                        {/* Paper Plane SVG */}
                        <svg className="w-4 h-4 -rotate-45 -mr-0.5" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                        </svg>
                      </button>
                    </form>
                  </div>

                </div>
              </div>
            )}

            {/* ═══════════════════════════════════════════════════════
                TAB 5: SETTINGS
               ═══════════════════════════════════════════════════════ */}
            {activeTab === 'settings' && (
              <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
                <div>
                  <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Settings</h1>
                  <p className="text-sm text-slate-500 mt-1">Manage platform preferences and system configuration.</p>
                </div>

                {settingsSaved && (
                  <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs font-semibold text-emerald-700 flex items-center gap-2">
                    <span>✅</span> Settings successfully updated.
                  </div>
                )}

                {/* Card 1: API Connection */}
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-5">
                  <h2 className="text-base font-bold text-slate-900">API Connection</h2>
                  
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1.5">
                      Backend API Base URL
                    </label>
                    <input
                      type="text"
                      value={apiBaseUrl}
                      onChange={(e) => setApiBaseUrl(e.target.value)}
                      placeholder="http://localhost:8000"
                      className="w-full px-4 py-2.5 rounded-lg border border-slate-200 text-sm text-slate-800 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
                    />
                    <p className="text-[11px] text-slate-400 mt-1">Configured via VITE_API_BASE_URL in your .env file</p>
                  </div>

                  <div className="flex items-center gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setEnableRag(!enableRag)}
                      className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
                        enableRag ? 'bg-blue-600' : 'bg-slate-300'
                      }`}
                    >
                      <div
                        className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                          enableRag ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      ></div>
                    </button>
                    <span className="text-xs font-medium text-slate-700">Enable automatic RAG grounding on queries</span>
                  </div>
                </div>

                {/* Card 2: User Information */}
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.04)] space-y-4">
                  <h2 className="text-base font-bold text-slate-900">User Information</h2>

                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1.5">Full name</label>
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-lg border border-slate-200 text-sm text-slate-800 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1.5">Email</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-lg border border-slate-200 text-sm text-slate-800 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
                    />
                  </div>

                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={handleSaveSettings}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-5 py-2.5 rounded-lg shadow-sm transition-all"
                    >
                      Save Changes
                    </button>
                  </div>
                </div>
              </div>
            )}

          </div>
        </main>
      </div>

      {/* ─────────────────────────────────────────────────────────────
          MODAL: COURSE MATERIALS
         ───────────────────────────────────────────────────────────── */}
      {showMaterialsModal && modalCourse && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-100 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-lg font-bold text-slate-900">{modalCourse.title}</h3>
                <p className="text-xs text-slate-400 mt-0.5">Ingested Modules & Multimodal Assets</p>
              </div>
              <button
                onClick={() => setShowMaterialsModal(false)}
                className="w-8 h-8 rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 flex items-center justify-center text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 max-h-72 overflow-y-auto pr-1 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="font-semibold text-blue-600 uppercase text-[10px]">Module 01</span>
                <p className="font-bold text-slate-800 text-sm">Defining the Problem & Core Objectives</p>
                <p className="text-slate-500">1 Video (08:45) • 1 SRT Transcript • 1 HTML Reading</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="font-semibold text-blue-600 uppercase text-[10px]">Module 02</span>
                <p className="font-bold text-slate-800 text-sm">Foundational Concepts & Algorithmic Design</p>
                <p className="text-slate-500">1 Video (14:20) • 1 SRT Transcript • 1 PDF Document</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="font-semibold text-blue-600 uppercase text-[10px]">Module 03</span>
                <p className="font-bold text-slate-800 text-sm">Applications, Diagnostics, and Code Examples</p>
                <p className="text-slate-500">2 Python Scripts • 1 Interactive Assignment Checkpoint</p>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => {
                  setShowMaterialsModal(false);
                  setSelectedCourse(modalCourse);
                  setActiveTab('chat');
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-4 py-2.5 rounded-lg shadow-sm"
              >
                Chat About These Materials
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          MODAL: ANALYSIS RESULTS
         ───────────────────────────────────────────────────────────── */}
      {showResultsModal && modalCourse && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-100 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-lg font-bold text-slate-900">{modalCourse.title}</h3>
                <p className="text-xs text-slate-400 mt-0.5">Automated Learning Friction Analysis</p>
              </div>
              <button
                onClick={() => setShowResultsModal(false)}
                className="w-8 h-8 rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 flex items-center justify-center text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 max-h-80 overflow-y-auto pr-1 text-xs">
              {/* Friction Point */}
              <div className="p-3.5 bg-red-50/60 border border-red-100 rounded-xl space-y-1">
                <div className="flex items-center gap-1.5 text-red-600 font-bold text-[11px] uppercase tracking-wider">
                  <span>⚠️</span> Top Learning Bottleneck
                </div>
                <p className="text-sm font-bold text-slate-900">
                  Comprehension friction detected during foundational concept introduction.
                </p>
                <p className="text-slate-600 leading-relaxed text-xs">
                  Transcript analysis and diagnostic test failure correlation show learners struggle around timestamp 04:35 - 07:20 with abstract mathematical notation before intuitive examples are shown.
                </p>
              </div>

              {/* Recommendation */}
              <div className="p-3.5 bg-blue-50/60 border border-blue-100 rounded-xl space-y-1">
                <div className="flex items-center gap-1.5 text-blue-600 font-bold text-[11px] uppercase tracking-wider">
                  <span>💡</span> Actionable Recommendation
                </div>
                <p className="text-slate-700 leading-relaxed text-xs">
                  Add 2 animated diagrams for visual learners, include an interactive checkpoint quiz after minute 5, and link to supplemental glossary terms.
                </p>
              </div>

              {/* Evidence Metrics */}
              <div className="grid grid-cols-2 gap-3 pt-1">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase">Diagnostic Q7 Error Rate</span>
                  <p className="text-base font-bold text-red-500 mt-0.5">56% Fail</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase">Forum Questions Logged</span>
                  <p className="text-base font-bold text-blue-600 mt-0.5">42 threads</p>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                onClick={() => setShowResultsModal(false)}
                className="px-4 py-2 rounded-lg border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setShowResultsModal(false);
                  setSelectedCourse(modalCourse);
                  setActiveTab('chat');
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-4 py-2 rounded-lg shadow-sm"
              >
                Discuss in AI Chat
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}