import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Play,
  Clock,
  CheckCircle,
  FileText,
  TrendingUp,
  Award,
  Loader,
  Plus,
} from 'lucide-react';
import interviewService, { InterviewTemplate, InterviewSession } from '@/services/interviewService';

export default function InterviewListPage() {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState<InterviewTemplate[]>([]);
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'templates' | 'history'>('templates');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [templatesData, sessionsData] = await Promise.all([
        interviewService.getTemplates(),
        interviewService.getSessions(),
      ]);
      setTemplates(templatesData);
      setSessions(sessionsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleStartInterview = async (templateId: number) => {
    try {
      const session = await interviewService.startSession({ template_id: templateId });
      navigate(`/interviews/${session.id}`);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start interview');
    }
  };

  const getTypeColor = (type: string) => {
    const colors = {
      technical: 'bg-blue-100 text-blue-800',
      behavioral: 'bg-purple-100 text-purple-800',
      case_study: 'bg-green-100 text-green-800',
      system_design: 'bg-orange-100 text-orange-800',
      cultural_fit: 'bg-pink-100 text-pink-800',
      mixed: 'bg-gray-100 text-gray-800',
    };
    return colors[type as keyof typeof colors] || colors.mixed;
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      easy: 'text-green-600',
      medium: 'text-yellow-600',
      hard: 'text-red-600',
    };
    return colors[difficulty as keyof typeof colors] || colors.medium;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
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

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Interview Simulation</h1>
        <p className="text-gray-600">
          Practice with AI-powered mock interviews to improve your skills
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="mb-6 border-b">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('templates')}
            className={`px-4 py-3 border-b-2 transition-colors ${
              activeTab === 'templates'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Available Interviews
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-3 border-b-2 transition-colors ${
              activeTab === 'history'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            My History ({sessions.length})
          </button>
        </div>
      </div>

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div>
          {templates.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <h2 className="text-xl font-semibold mb-2">No templates available</h2>
              <p className="text-gray-600">Check back later for interview templates</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {templates.map(template => (
                <div
                  key={template.id}
                  className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="mb-4">
                    <h3 className="text-xl font-bold mb-2">{template.name}</h3>
                    <p className="text-gray-600 text-sm line-clamp-2">
                      {template.description}
                    </p>
                  </div>

                  <div className="space-y-3 mb-6">
                    <div className="flex items-center justify-between">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTypeColor(template.interview_type)}`}>
                        {template.interview_type.replace('_', ' ')}
                      </span>
                      <span className={`font-semibold capitalize ${getDifficultyColor(template.difficulty)}`}>
                        {template.difficulty}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{template.duration_minutes} min</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <FileText className="h-4 w-4" />
                        <span>{template.total_questions} questions</span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleStartInterview(template.id)}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  >
                    <Play className="h-5 w-5" />
                    Start Interview
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div>
          {sessions.length === 0 ? (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <h2 className="text-xl font-semibold mb-2">No interview history</h2>
              <p className="text-gray-600 mb-6">
                Start your first interview to see your history here
              </p>
              <button
                onClick={() => setActiveTab('templates')}
                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="h-5 w-5" />
                Browse Templates
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {sessions
                .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
                .map(session => (
                  <div
                    key={session.id}
                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold mb-2">{session.template.name}</h3>
                        <div className="flex flex-wrap gap-3 text-sm text-gray-600 mb-3">
                          <div className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            <span>{formatDate(session.started_at)}</span>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTypeColor(session.template.interview_type)}`}>
                            {session.template.interview_type.replace('_', ' ')}
                          </span>
                        </div>

                        {session.status === 'completed' && (
                          <div className="flex items-center gap-6 mt-4">
                            <div>
                              <div className="text-3xl font-bold text-blue-600">
                                {Math.round((session.total_score / session.max_score) * 100)}%
                              </div>
                              <div className="text-sm text-gray-500">Score</div>
                            </div>
                            <div>
                              <div className="text-xl font-semibold">
                                {session.total_score} / {session.max_score}
                              </div>
                              <div className="text-sm text-gray-500">Points</div>
                            </div>
                          </div>
                        )}
                      </div>

                      <div className="flex flex-col gap-2">
                        {session.status === 'completed' ? (
                          <>
                            <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                              <CheckCircle className="h-4 w-4" />
                              Completed
                            </span>
                            <Link
                              to={`/interviews/${session.id}/results`}
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center text-sm font-medium"
                            >
                              View Results
                            </Link>
                          </>
                        ) : session.status === 'in_progress' ? (
                          <>
                            <span className="inline-flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
                              <Clock className="h-4 w-4" />
                              In Progress
                            </span>
                            <Link
                              to={`/interviews/${session.id}`}
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center text-sm font-medium"
                            >
                              Continue
                            </Link>
                          </>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium">
                            Abandoned
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
