import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Award,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  Loader,
  ArrowLeft,
  Download,
} from 'lucide-react';
import interviewService, {
  InterviewSession,
  InterviewFeedback,
} from '@/services/interviewService';

export default function InterviewResultsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [feedback, setFeedback] = useState<InterviewFeedback | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadResults();
    }
  }, [id]);

  const loadResults = async () => {
    try {
      setLoading(true);
      const sessionData = await interviewService.getSession(Number(id));
      setSession(sessionData);

      if (sessionData.status === 'completed') {
        try {
          const feedbackData = await interviewService.getFeedback(Number(id));
          setFeedback(feedbackData);
        } catch (err) {
          console.error('Feedback not yet available:', err);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-100';
    if (percentage >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
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

  if (session.status !== 'completed') {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <AlertCircle className="h-16 w-16 mx-auto mb-4 text-yellow-600" />
          <h2 className="text-2xl font-bold mb-4">Interview Not Completed</h2>
          <p className="text-gray-600 mb-6">
            This interview session hasn't been completed yet.
          </p>
          <Link
            to={`/interviews/${session.id}`}
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Continue Interview
          </Link>
        </div>
      </div>
    );
  }

  const scorePercentage = Math.round((session.total_score / session.max_score) * 100);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/interviews"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Interviews
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Interview Results</h1>
            <p className="text-gray-600">{session.template.name}</p>
            <p className="text-sm text-gray-500">
              Completed on {formatDate(session.completed_at!)}
            </p>
          </div>
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Download className="h-4 w-4" />
            Export PDF
          </button>
        </div>
      </div>

      {/* Overall Score */}
      <div className="bg-white rounded-lg shadow-md p-8 mb-6 text-center">
        <div className={`text-6xl font-bold ${getScoreColor(scorePercentage)} mb-4`}>
          {scorePercentage}%
        </div>
        <div className="text-2xl font-semibold mb-2">
          {session.total_score} / {session.max_score} points
        </div>
        <div className={`inline-block px-6 py-2 rounded-full text-lg font-medium ${getScoreBgColor(scorePercentage)} ${getScoreColor(scorePercentage)}`}>
          {scorePercentage >= 80 ? 'Excellent' : scorePercentage >= 60 ? 'Good' : 'Needs Improvement'}
        </div>

        {feedback?.percentile_rank && (
          <div className="mt-6 pt-6 border-t">
            <p className="text-gray-600 mb-2">You performed better than</p>
            <p className="text-3xl font-bold text-blue-600">{feedback.percentile_rank}%</p>
            <p className="text-gray-600">of test takers</p>
          </div>
        )}
      </div>

      {/* Question Breakdown */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Question Breakdown</h2>
        <div className="space-y-4">
          {session.questions?.map((q, index) => (
            <div key={q.id} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-semibold">Question {index + 1}</span>
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-sm">
                      {q.question.question_type.replace('_', ' ')}
                    </span>
                    {q.is_correct !== undefined && (
                      q.is_correct ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600" />
                      )
                    )}
                  </div>
                  <p className="text-gray-700 mb-2">{q.question.question_text}</p>
                  {q.user_answer && (
                    <div className="mt-2 p-3 bg-gray-50 rounded">
                      <p className="text-sm font-medium text-gray-600 mb-1">Your Answer:</p>
                      <p className="text-gray-800">{q.user_answer}</p>
                    </div>
                  )}
                  {q.feedback && (
                    <div className="mt-2 p-3 bg-blue-50 rounded">
                      <p className="text-sm font-medium text-blue-600 mb-1">Feedback:</p>
                      <p className="text-blue-900">{q.feedback}</p>
                    </div>
                  )}
                </div>
                <div className="text-right ml-4">
                  <div className="text-2xl font-bold text-blue-600">{q.score}</div>
                  <div className="text-sm text-gray-500">/ {q.question.points}</div>
                  {q.time_taken_seconds && (
                    <div className="flex items-center gap-1 text-sm text-gray-500 mt-2">
                      <Clock className="h-3 w-3" />
                      <span>{Math.floor(q.time_taken_seconds / 60)}:{(q.time_taken_seconds % 60).toString().padStart(2, '0')}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Feedback */}
      {feedback && (
        <div className="space-y-6">
          {/* Overall Performance */}
          {feedback.overall_performance && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Award className="h-6 w-6 text-blue-600" />
                Overall Performance
              </h2>
              <p className="text-gray-700 whitespace-pre-line">{feedback.overall_performance}</p>
            </div>
          )}

          {/* Technical Performance */}
          {feedback.technical_performance && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4">Technical Performance</h2>
              <p className="text-gray-700 whitespace-pre-line">{feedback.technical_performance}</p>
            </div>
          )}

          {/* Communication Performance */}
          {feedback.communication_performance && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4">Communication Performance</h2>
              <p className="text-gray-700 whitespace-pre-line">{feedback.communication_performance}</p>
            </div>
          )}

          {/* Strengths & Weaknesses */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Strengths */}
            {feedback.strengths.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-green-600">
                  <TrendingUp className="h-6 w-6" />
                  Strengths
                </h2>
                <ul className="space-y-2">
                  {feedback.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {feedback.weaknesses.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-red-600">
                  <AlertCircle className="h-6 w-6" />
                  Areas for Improvement
                </h2>
                <ul className="space-y-2">
                  {feedback.weaknesses.map((weakness, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Recommendations */}
          {feedback.recommendations.length > 0 && (
            <div className="bg-blue-50 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4 text-blue-900">Recommendations</h2>
              <ul className="space-y-3">
                {feedback.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-600 text-white rounded-full flex-shrink-0 text-sm">
                      {index + 1}
                    </span>
                    <span className="text-blue-900">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="mt-8 flex gap-4 justify-center">
        <Link
          to="/interviews"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Take Another Interview
        </Link>
      </div>
    </div>
  );
}
