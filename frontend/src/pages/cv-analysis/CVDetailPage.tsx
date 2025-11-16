import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  FileText,
  Download,
  Trash2,
  Briefcase,
  GraduationCap,
  Award,
  TrendingUp,
  Mail,
  Phone,
  Linkedin,
  Github,
  Loader,
  ArrowLeft,
  Target,
} from 'lucide-react';
import cvAnalysisService, { CVDetail, JobMatch } from '@/services/cvAnalysisService';

export default function CVDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [cv, setCv] = useState<CVDetail | null>(null);
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [matchingLoading, setMatchingLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'experience' | 'education' | 'matches'>('overview');

  useEffect(() => {
    if (id) {
      loadCVDetail();
      loadMatches();
    }
  }, [id]);

  const loadCVDetail = async () => {
    try {
      setLoading(true);
      const data = await cvAnalysisService.getCVDetail(Number(id));
      setCv(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load CV details');
    } finally {
      setLoading(false);
    }
  };

  const loadMatches = async () => {
    try {
      const data = await cvAnalysisService.getMatches(Number(id));
      setMatches(data);
    } catch (err: any) {
      console.error('Failed to load matches:', err);
    }
  };

  const handleMatchCV = async () => {
    try {
      setMatchingLoading(true);
      const data = await cvAnalysisService.matchCV(Number(id));
      setMatches(data);
      setActiveTab('matches');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to match CV');
    } finally {
      setMatchingLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this CV?')) return;

    try {
      await cvAnalysisService.deleteCV(Number(id));
      navigate('/cv-analysis/cvs');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete CV');
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (error || !cv) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-800">
          {error || 'CV not found'}
        </div>
      </div>
    );
  }

  const analysis = cv.analysis;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/cv-analysis/cvs"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to CVs
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">{cv.file_name}</h1>
            {analysis?.full_name && (
              <p className="text-xl text-gray-600">{analysis.full_name}</p>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleMatchCV}
              disabled={matchingLoading}
              className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"
            >
              <Target className="h-4 w-4" />
              {matchingLoading ? 'Matching...' : 'Match Jobs'}
            </button>
            <button
              onClick={handleDelete}
              className="inline-flex items-center gap-2 px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Contact Info */}
      {analysis && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {analysis.email && (
              <div className="flex items-center gap-2">
                <Mail className="h-5 w-5 text-gray-400" />
                <a href={`mailto:${analysis.email}`} className="text-blue-600 hover:underline">
                  {analysis.email}
                </a>
              </div>
            )}
            {analysis.phone && (
              <div className="flex items-center gap-2">
                <Phone className="h-5 w-5 text-gray-400" />
                <span>{analysis.phone}</span>
              </div>
            )}
            {analysis.linkedin_url && (
              <div className="flex items-center gap-2">
                <Linkedin className="h-5 w-5 text-gray-400" />
                <a href={analysis.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  LinkedIn
                </a>
              </div>
            )}
            {analysis.github_url && (
              <div className="flex items-center gap-2">
                <Github className="h-5 w-5 text-gray-400" />
                <a href={analysis.github_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  GitHub
                </a>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Scores */}
      {analysis && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">CV Analysis Scores</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
            {[
              { label: 'Overall', score: analysis.overall_score },
              { label: 'Experience', score: analysis.experience_score },
              { label: 'Education', score: analysis.education_score },
              { label: 'Skills', score: analysis.skills_score },
              { label: 'Formatting', score: analysis.formatting_score },
            ].map(({ label, score }) => (
              <div key={label} className="text-center">
                <div className={`text-4xl font-bold ${getScoreColor(score)} mb-2`}>
                  {score}
                </div>
                <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getScoreBgColor(score)} ${getScoreColor(score)}`}>
                  {label}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-6 border-t">
            <div className="flex items-center gap-2 mb-2">
              <Briefcase className="h-5 w-5 text-gray-600" />
              <span className="font-medium">Total Experience:</span>
              <span>{analysis.total_experience_years} years</span>
            </div>
          </div>
        </div>
      )}

      {/* Insights */}
      {analysis && (analysis.strengths.length > 0 || analysis.weaknesses.length > 0 || analysis.suggestions.length > 0) && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">AI-Generated Insights</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {analysis.strengths.length > 0 && (
              <div>
                <h3 className="font-semibold text-green-600 mb-3 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Strengths
                </h3>
                <ul className="space-y-2">
                  {analysis.strengths.map((strength, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-green-600">✓</span>
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {analysis.weaknesses.length > 0 && (
              <div>
                <h3 className="font-semibold text-red-600 mb-3">Weaknesses</h3>
                <ul className="space-y-2">
                  {analysis.weaknesses.map((weakness, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-red-600">⚠</span>
                      <span>{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {analysis.suggestions.length > 0 && (
              <div>
                <h3 className="font-semibold text-blue-600 mb-3">Suggestions</h3>
                <ul className="space-y-2">
                  {analysis.suggestions.map((suggestion, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-blue-600">💡</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="border-b">
          <div className="flex">
            {[
              { key: 'skills', label: 'Skills', icon: Award },
              { key: 'experience', label: 'Experience', icon: Briefcase },
              { key: 'education', label: 'Education', icon: GraduationCap },
              { key: 'matches', label: 'Job Matches', icon: Target, badge: matches.length },
            ].map(({ key, label, icon: Icon, badge }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as typeof activeTab)}
                className={`flex items-center gap-2 px-6 py-4 border-b-2 transition-colors ${
                  activeTab === key
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon className="h-5 w-5" />
                {label}
                {badge !== undefined && badge > 0 && (
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-600 rounded-full text-xs font-medium">
                    {badge}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {/* Skills Tab */}
          {activeTab === 'skills' && (
            <div>
              {cv.skills && cv.skills.length > 0 ? (
                <div className="grid gap-4">
                  {['technical', 'soft', 'language', 'certification', 'tool', 'other'].map(category => {
                    const categorySkills = cv.skills?.filter(s => s.skill.category === category);
                    if (!categorySkills || categorySkills.length === 0) return null;
                    
                    return (
                      <div key={category}>
                        <h3 className="font-semibold mb-3 capitalize">{category} Skills</h3>
                        <div className="flex flex-wrap gap-2">
                          {categorySkills.map(cvSkill => (
                            <div
                              key={cvSkill.id}
                              className="px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg"
                            >
                              <div className="font-medium text-blue-900">{cvSkill.skill.name}</div>
                              <div className="text-sm text-blue-600">
                                {cvSkill.proficiency_level}
                                {cvSkill.years_of_experience && ` • ${cvSkill.years_of_experience}y`}
                                {' • '}
                                {Math.round(cvSkill.confidence_score)}% confidence
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-gray-600">No skills extracted</p>
              )}
            </div>
          )}

          {/* Experience Tab */}
          {activeTab === 'experience' && (
            <div>
              {cv.experiences && cv.experiences.length > 0 ? (
                <div className="space-y-6">
                  {cv.experiences.map(exp => (
                    <div key={exp.id} className="border-l-4 border-blue-600 pl-4">
                      <h3 className="font-bold text-lg">{exp.job_title}</h3>
                      <p className="text-gray-600 font-medium">{exp.company}</p>
                      {exp.location && <p className="text-sm text-gray-500">{exp.location}</p>}
                      <p className="text-sm text-gray-500 mt-1">
                        {exp.start_date || 'N/A'} - {exp.is_current ? 'Present' : exp.end_date || 'N/A'}
                        {exp.duration_months && ` (${Math.floor(exp.duration_months / 12)}y ${exp.duration_months % 12}m)`}
                      </p>
                      {exp.description && (
                        <p className="mt-2 text-gray-700">{exp.description}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">No experience information</p>
              )}
            </div>
          )}

          {/* Education Tab */}
          {activeTab === 'education' && (
            <div>
              {cv.education && cv.education.length > 0 ? (
                <div className="space-y-6">
                  {cv.education.map(edu => (
                    <div key={edu.id} className="border-l-4 border-green-600 pl-4">
                      <h3 className="font-bold text-lg">{edu.degree}</h3>
                      {edu.field_of_study && (
                        <p className="text-gray-600 font-medium">{edu.field_of_study}</p>
                      )}
                      <p className="text-gray-600">{edu.institution}</p>
                      {edu.location && <p className="text-sm text-gray-500">{edu.location}</p>}
                      <div className="flex gap-4 mt-1 text-sm text-gray-500">
                        {edu.graduation_year && <span>Graduated: {edu.graduation_year}</span>}
                        {edu.gpa && <span>GPA: {edu.gpa}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600">No education information</p>
              )}
            </div>
          )}

          {/* Matches Tab */}
          {activeTab === 'matches' && (
            <div>
              {matches.length > 0 ? (
                <div className="space-y-6">
                  {matches
                    .sort((a, b) => b.overall_score - a.overall_score)
                    .map(match => (
                      <div key={match.id} className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="font-bold text-xl">{match.job_posting.title}</h3>
                            <p className="text-gray-600">{match.job_posting.company}</p>
                            {match.job_posting.location && (
                              <p className="text-sm text-gray-500">{match.job_posting.location}</p>
                            )}
                          </div>
                          <div className="text-right">
                            <div className={`text-3xl font-bold ${getScoreColor(match.overall_score)}`}>
                              {match.overall_score}%
                            </div>
                            <div className="text-sm text-gray-500">Match Score</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4 mb-4">
                          <div>
                            <div className="text-sm text-gray-500">Skills Match</div>
                            <div className={`font-semibold ${getScoreColor(match.skills_match_score)}`}>
                              {match.skills_match_score}%
                            </div>
                          </div>
                          <div>
                            <div className="text-sm text-gray-500">Experience Match</div>
                            <div className={`font-semibold ${getScoreColor(match.experience_match_score)}`}>
                              {match.experience_match_score}%
                            </div>
                          </div>
                          <div>
                            <div className="text-sm text-gray-500">Education Match</div>
                            <div className={`font-semibold ${getScoreColor(match.education_match_score)}`}>
                              {match.education_match_score}%
                            </div>
                          </div>
                        </div>

                        {match.match_summary && (
                          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                            <p className="text-gray-700">{match.match_summary}</p>
                          </div>
                        )}

                        <div className="grid md:grid-cols-2 gap-4">
                          {match.matched_skills.length > 0 && (
                            <div>
                              <h4 className="font-semibold text-green-600 mb-2">Matched Skills</h4>
                              <div className="flex flex-wrap gap-2">
                                {match.matched_skills.map((skill, idx) => (
                                  <span key={idx} className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {match.missing_skills.length > 0 && (
                            <div>
                              <h4 className="font-semibold text-red-600 mb-2">Missing Skills</h4>
                              <div className="flex flex-wrap gap-2">
                                {match.missing_skills.map((skill, idx) => (
                                  <span key={idx} className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>

                        {match.recommendations.length > 0 && (
                          <div className="mt-4">
                            <h4 className="font-semibold mb-2">Recommendations</h4>
                            <ul className="space-y-1">
                              {match.recommendations.map((rec, idx) => (
                                <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                                  <span className="text-blue-600">•</span>
                                  <span>{rec}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Target className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                  <p className="text-gray-600 mb-4">No job matches yet</p>
                  <button
                    onClick={handleMatchCV}
                    disabled={matchingLoading}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
                  >
                    <Target className="h-5 w-5" />
                    {matchingLoading ? 'Matching...' : 'Find Matches'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
