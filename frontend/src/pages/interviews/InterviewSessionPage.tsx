import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clock, ChevronRight, Loader, AlertCircle } from 'lucide-react';
import interviewService, {
  InterviewSession,
  SessionQuestion,
  Question,
} from '@/services/interviewService';

export default function InterviewSessionPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<SessionQuestion | null>(null);
  const [answer, setAnswer] = useState('');
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadSession();
    }
  }, [id]);

  useEffect(() => {
    if (session && session.status === 'in_progress') {
      const timer = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [session]);

  const loadSession = async () => {
    try {
      setLoading(true);
      const data = await interviewService.getSession(Number(id));
      setSession(data);
      
      if (data.questions && data.questions.length > 0) {
        const unanswered = data.questions.find(q => !q.answered_at);
        setCurrentQuestion(unanswered || data.questions[data.questions.length - 1]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load session');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!session || !currentQuestion || !answer.trim()) {
      alert('Please provide an answer');
      return;
    }

    try {
      setSubmitting(true);
      await interviewService.submitAnswer({
        session_id: session.id,
        question_id: currentQuestion.question.id,
        answer: answer.trim(),
        time_taken_seconds: timeElapsed,
      });

      // Reset for next question
      setAnswer('');
      setTimeElapsed(0);

      // Reload session to get next question
      await loadSession();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to submit answer');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCompleteSession = async () => {
    if (!session) return;

    if (!confirm('Are you sure you want to complete this interview?')) return;

    try {
      await interviewService.completeSession(session.id);
      navigate(`/interviews/${session.id}/results`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to complete session');
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const isLastQuestion = () => {
    if (!session || !currentQuestion) return false;
    const answeredCount = session.questions?.filter(q => q.answered_at).length || 0;
    return answeredCount >= (session.template.total_questions - 1);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-800">
          {error || 'Session not found'}
        </div>
      </div>
    );
  }

  if (session.status === 'completed') {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <AlertCircle className="h-16 w-16 mx-auto mb-4 text-blue-600" />
          <h2 className="text-2xl font-bold mb-4">Interview Completed</h2>
          <p className="text-gray-600 mb-6">
            This interview session has already been completed.
          </p>
          <button
            onClick={() => navigate(`/interviews/${session.id}/results`)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            View Results
          </button>
        </div>
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <p className="text-gray-600">No questions available</p>
        </div>
      </div>
    );
  }

  const answeredCount = session.questions?.filter(q => q.answered_at).length || 0;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">{session.template.name}</h1>
          <div className="flex items-center gap-2 text-blue-600">
            <Clock className="h-5 w-5" />
            <span className="text-xl font-mono">{formatTime(timeElapsed)}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{
                width: `${(answeredCount / session.template.total_questions) * 100}%`,
              }}
            />
          </div>
          <span className="text-sm font-medium text-gray-600">
            {answeredCount} / {session.template.total_questions}
          </span>
        </div>
      </div>

      {/* Question */}
      <div className="bg-white rounded-lg shadow-md p-8 mb-6">
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              {currentQuestion.question.question_type.replace('_', ' ')}
            </span>
            <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium capitalize">
              {currentQuestion.question.difficulty}
            </span>
            <span className="text-sm text-gray-600">
              {currentQuestion.question.points} points
            </span>
          </div>
          
          <h2 className="text-xl font-semibold mb-4">
            {currentQuestion.question.question_text}
          </h2>
        </div>

        {/* Multiple Choice Options */}
        {currentQuestion.question.question_type === 'multiple_choice' &&
          currentQuestion.question.options && (
            <div className="space-y-3 mb-6">
              {currentQuestion.question.options.map((option, index) => (
                <label
                  key={index}
                  className="flex items-center gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                >
                  <input
                    type="radio"
                    name="answer"
                    value={option}
                    checked={answer === option}
                    onChange={(e) => setAnswer(e.target.value)}
                    className="w-4 h-4"
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          )}

        {/* Text Answer */}
        {(currentQuestion.question.question_type === 'open_ended' ||
          currentQuestion.question.question_type === 'behavioral' ||
          currentQuestion.question.question_type === 'system_design') && (
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here..."
            rows={8}
            className="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 mb-6"
          />
        )}

        {/* Coding Answer */}
        {currentQuestion.question.question_type === 'coding' && (
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Write your code here..."
            rows={12}
            className="w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 font-mono text-sm mb-6"
          />
        )}

        <div className="flex gap-4">
          {isLastQuestion() ? (
            <button
              onClick={handleCompleteSession}
              className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              Complete Interview
            </button>
          ) : (
            <button
              onClick={handleSubmitAnswer}
              disabled={!answer.trim() || submitting}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {submitting ? 'Submitting...' : 'Submit & Next'}
              <ChevronRight className="h-5 w-5" />
            </button>
          )}
        </div>
      </div>

      {/* Help Text */}
      <div className="bg-blue-50 rounded-lg p-4 text-sm text-blue-800">
        <p className="font-medium mb-1">Tips:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>Take your time to think through your answer</li>
          <li>Be specific and provide examples when possible</li>
          <li>You cannot go back to previous questions</li>
        </ul>
      </div>
    </div>
  );
}
