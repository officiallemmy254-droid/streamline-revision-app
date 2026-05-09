import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { generateScenario, getFeedback } from '../services/api';
import './PracticePage.css';

const LEVEL_LABELS: Record<string, string> = {
  undergraduate: 'Undergraduate',
  postgraduate: 'Postgraduate',
  professional: 'Professional / CPD',
};

const LEVEL_ICONS: Record<string, string> = {
  undergraduate: '🎓',
  postgraduate: '🔬',
  professional: '💼',
};

export default function PracticePage() {
  const { documentId } = useParams<{ documentId: string }>();
  const { geminiApiKey, learnerLevel } = useAuth();
  const navigate = useNavigate();

  const [scenario, setScenario] = useState('');
  const [documentName, setDocumentName] = useState('');
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState('');
  const [loadingScenario, setLoadingScenario] = useState(false);
  const [loadingFeedback, setLoadingFeedback] = useState(false);
  const [error, setError] = useState('');

  const docId = Number(documentId);

  const handleGenerateScenario = async () => {
    setError('');
    setFeedback('');
    setUserAnswer('');
    setLoadingScenario(true);

    try {
      const data = await generateScenario(docId, geminiApiKey, learnerLevel);
      setScenario(data.scenario);
      setDocumentName(data.document_name);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to generate challenge.';
      setError(message);
    } finally {
      setLoadingScenario(false);
    }
  };

  const handleGetFeedback = async () => {
    if (!userAnswer.trim()) {
      setError('Please write your response before requesting feedback.');
      return;
    }

    setError('');
    setLoadingFeedback(true);

    try {
      const data = await getFeedback(docId, scenario, userAnswer, geminiApiKey, learnerLevel);
      setFeedback(data.feedback);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to get feedback.';
      setError(message);
    } finally {
      setLoadingFeedback(false);
    }
  };

  return (
    <div className="practice">
      <header className="practice-header">
        <button className="btn btn-secondary btn-sm" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
        <h1>Practice Session</h1>
        <div className="practice-meta">
          {documentName && <span className="practice-doc-name">📄 {documentName}</span>}
          <span className="practice-level-badge">
            {LEVEL_ICONS[learnerLevel]} {LEVEL_LABELS[learnerLevel]}
          </span>
        </div>
      </header>

      {error && <div className="practice-error">{error}</div>}

      <div className="practice-layout">
        {/* Left Column: Challenge + Answer */}
        <div className="practice-panel">
          <div className="panel-header">
            <h2>⚡ Academic Challenge</h2>
            <button
              className="btn btn-primary btn-sm"
              onClick={handleGenerateScenario}
              disabled={loadingScenario}
              id="generate-scenario-btn"
            >
              {loadingScenario ? '⏳ Generating...' : '✨ New Challenge'}
            </button>
          </div>

          {scenario ? (
            <div className="scenario-box card">
              <p>{scenario}</p>
            </div>
          ) : (
            <div className="scenario-empty card">
              <p>Click <strong>"New Challenge"</strong> to generate an academic challenge based on your uploaded document.</p>
            </div>
          )}

          {scenario && (
            <div className="answer-section">
              <h3>Your Response</h3>
              <textarea
                id="user-answer-input"
                className="input-field answer-textarea"
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                placeholder="Draw on the concepts from your document. Explain your reasoning clearly..."
                rows={8}
              />
              <button
                className="btn btn-primary"
                onClick={handleGetFeedback}
                disabled={loadingFeedback || !userAnswer.trim()}
                id="get-feedback-btn"
              >
                {loadingFeedback ? '⏳ Evaluating...' : '🚀 Get Qualitative Feedback'}
              </button>
            </div>
          )}
        </div>

        {/* Right Column: Feedback */}
        <div className="practice-panel">
          <h2>🎓 Feedback &amp; Reflection</h2>
          {feedback ? (
            <div className="feedback-box card">
              <div className="feedback-content" dangerouslySetInnerHTML={{
                __html: feedback
                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/\n/g, '<br />')
              }} />
            </div>
          ) : (
            <div className="feedback-empty card">
              <p>
                {scenario
                  ? 'Submit your response to receive expert-level feedback calibrated to your learner profile.'
                  : 'Generate a challenge to begin your practice session.'}
              </p>
            </div>
          )}
        </div>
      </div>

      <footer className="practice-footer">
        <p>🛡️ Minimal Risk AI — Educational feedback only · No personal data stored</p>
      </footer>
    </div>
  );
}
