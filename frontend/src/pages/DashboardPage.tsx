import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { LearnerLevel } from '../context/AuthContext';
import { listDocuments, uploadDocument, deleteDocument } from '../services/api';
import './DashboardPage.css';

interface Document {
  id: number;
  filename: string;
  chunk_count: number;
  category: string;
  uploaded_at: string;
}

const DOCUMENT_CATEGORIES: { value: string; label: string; icon: string; description: string }[] = [
  { value: 'LECTURE_NOTES',    label: 'Lecture Notes',      icon: '📖', description: 'Slides, lecture summaries, or typed notes' },
  { value: 'TEXTBOOK_CHAPTER', label: 'Textbook Chapter',   icon: '📗', description: 'Textbook excerpts or book chapters' },
  { value: 'PAST_EXAM',        label: 'Past Exam Paper',    icon: '📋', description: 'Previous examination papers' },
  { value: 'LEARNING_OUTCOMES',label: 'Learning Outcomes',  icon: '🎯', description: 'Module or unit learning objectives' },
  { value: 'NOTES',            label: 'Personal Notes',     icon: '📝', description: 'Handwritten or general study notes' },
  { value: 'TEACHING_DIPLOMA', label: 'Teaching Diploma',   icon: '🎓', description: 'Teaching Diploma or professional qualification materials' },
];

const LEARNER_LEVELS: { value: LearnerLevel; label: string; icon: string; description: string }[] = [
  { value: 'undergraduate', label: 'Undergraduate',   icon: '🎓', description: 'Apply & understand core concepts' },
  { value: 'postgraduate',  label: 'Postgraduate',    icon: '🔬', description: 'Analyse, synthesise & critique' },
  { value: 'professional',  label: 'Professional / CPD', icon: '💼', description: 'Evaluate & create at expert level' },
];

const CATEGORY_LABEL: Record<string, string> = Object.fromEntries(
  DOCUMENT_CATEGORIES.map((c) => [c.value, c.label])
);

export default function DashboardPage() {
  const { username, logout, geminiApiKey, setGeminiApiKey, learnerLevel, setLearnerLevel } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('LECTURE_NOTES');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const fetchDocuments = async () => {
    try {
      const data = await listDocuments();
      setDocuments(data.documents);
    } catch {
      setError('Failed to load documents.');
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError('');
    setSuccess('');
    setUploading(true);

    try {
      const doc = await uploadDocument(file, selectedCategory);
      setSuccess(`"${doc.filename}" uploaded successfully (${doc.chunk_count} chunks).`);
      fetchDocuments();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Upload failed.';
      setError(message);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (docId: number, filename: string) => {
    if (!confirm(`Delete "${filename}"? This cannot be undone.`)) return;
    try {
      await deleteDocument(docId);
      setSuccess(`"${filename}" deleted.`);
      fetchDocuments();
    } catch {
      setError('Failed to delete document.');
    }
  };

  const handlePractice = (docId: number) => {
    if (!geminiApiKey) {
      setError('Please enter your Groq API key first.');
      return;
    }
    navigate(`/practice/${docId}`);
  };

  const activeCategoryMeta = DOCUMENT_CATEGORIES.find((c) => c.value === selectedCategory)!;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="dashboard-brand">
          <span className="brand-icon">🎓</span>
          <h1>Streamline</h1>
        </div>
        <div className="dashboard-user">
          <span className="user-badge">{username}</span>
          <button className="btn btn-secondary btn-sm" onClick={logout} id="logout-btn">
            Sign Out
          </button>
        </div>
      </header>

      <main className="dashboard-main">

        {/* Learner Profile Section */}
        <section className="config-section card learner-profile-section">
          <div className="section-heading">
            <span className="section-icon">🧠</span>
            <div>
              <h2>Your Learner Profile</h2>
              <p className="config-hint">Set your level so challenges are calibrated to your depth of study.</p>
            </div>
          </div>
          <div className="learner-level-grid" role="radiogroup" aria-label="Learner level">
            {LEARNER_LEVELS.map((lvl) => (
              <button
                key={lvl.value}
                id={`learner-level-${lvl.value}`}
                className={`learner-level-card${learnerLevel === lvl.value ? ' active' : ''}`}
                onClick={() => setLearnerLevel(lvl.value)}
                role="radio"
                aria-checked={learnerLevel === lvl.value}
              >
                <span className="level-icon">{lvl.icon}</span>
                <strong>{lvl.label}</strong>
                <span className="level-desc">{lvl.description}</span>
              </button>
            ))}
          </div>
        </section>

        {/* API Key Section */}
        <section className="config-section card">
          <div className="section-heading">
            <span className="section-icon">⚙️</span>
            <div>
              <h2>Groq API Key</h2>
              <p className="config-hint">
                Stored locally, sent per-request. Get a free key at{' '}
                <a href="https://console.groq.com/keys" target="_blank" rel="noopener">
                  console.groq.com/keys
                </a>
              </p>
            </div>
          </div>
          <input
            id="gemini-api-key-input"
            type="password"
            className="input-field"
            value={geminiApiKey}
            onChange={(e) => setGeminiApiKey(e.target.value)}
            placeholder="Enter your Groq API key"
          />
        </section>

        {/* Upload Section */}
        <section className="upload-section card">
          <div className="section-heading">
            <span className="section-icon">📤</span>
            <div>
              <h2>Upload Study Material</h2>
              <p className="config-hint">Select a document type, then upload your PDF.</p>
            </div>
          </div>

          {/* Category Tabs */}
          <div className="category-tabs" role="tablist" aria-label="Document category">
            {DOCUMENT_CATEGORIES.map((cat) => (
              <button
                key={cat.value}
                id={`category-tab-${cat.value.toLowerCase()}`}
                className={`category-tab${selectedCategory === cat.value ? ' active' : ''}`}
                onClick={() => setSelectedCategory(cat.value)}
                role="tab"
                aria-selected={selectedCategory === cat.value}
              >
                <span>{cat.icon}</span>
                <span className="tab-label">{cat.label}</span>
              </button>
            ))}
          </div>

          {/* Upload drop zone */}
          <div className="category-description">
            <strong>{activeCategoryMeta.icon} {activeCategoryMeta.label}</strong> —{' '}
            {activeCategoryMeta.description}
          </div>

          <label className="upload-area" htmlFor="pdf-upload-main">
            <input
              id="pdf-upload-main"
              type="file"
              accept=".pdf,.docx,.pptx"
              onChange={handleUpload}
              disabled={uploading}
              hidden
            />
            <div className="upload-content">
              <span className="upload-icon">{uploading ? '⏳' : '📤'}</span>
              <span>{uploading ? 'Processing file...' : 'Click to upload PDF, Word, or PPT (max 10 MB)'}</span>
              <span className="upload-sub">Will be tagged as: {activeCategoryMeta.label}</span>
            </div>
          </label>
        </section>

        {/* Messages */}
        {error && <div className="dash-error">{error}</div>}
        {success && <div className="dash-success">{success}</div>}

        {/* Document List */}
        <section className="documents-section">
          <h2>📚 Your Documents</h2>
          {documents.length === 0 ? (
            <div className="empty-state card">
              <p>No documents uploaded yet. Upload a PDF to get started.</p>
            </div>
          ) : (
            <div className="documents-grid">
              {documents.map((doc) => (
                <div key={doc.id} className="doc-card card">
                  <div className="doc-info">
                    <h3 className="doc-name">{doc.filename}</h3>
                    <p className="doc-meta">
                      <span className="doc-category-badge">
                        {CATEGORY_LABEL[doc.category] ?? doc.category.replace(/_/g, ' ')}
                      </span>
                      <span className="doc-chunks">{doc.chunk_count} chunks</span>
                      <span className="doc-date">{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                    </p>
                  </div>
                  <div className="doc-actions">
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => handlePractice(doc.id)}
                      id={`practice-btn-${doc.id}`}
                    >
                      ✨ Practice
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(doc.id, doc.filename)}
                      id={`delete-btn-${doc.id}`}
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
