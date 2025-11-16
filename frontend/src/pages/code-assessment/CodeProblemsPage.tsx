import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Code, Filter, Search, CheckCircle, XCircle, Clock } from 'lucide-react';
import codeAssessmentService, { CodingProblem, UserProgress } from '@/services/codeAssessmentService';

export default function CodeProblemsPage() {
  const [problems, setProblems] = useState<CodingProblem[]>([]);
  const [progress, setProgress] = useState<UserProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    difficulty: '',
    category: '',
    search: '',
  });

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [problemsData, progressData] = await Promise.all([
        codeAssessmentService.getProblems(filters),
        codeAssessmentService.getUserProgress(),
      ]);
      setProblems(problemsData);
      setProgress(progressData);
    } catch (err) {
      console.error('Failed to load problems:', err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      easy: 'text-green-600 bg-green-100',
      medium: 'text-yellow-600 bg-yellow-100',
      hard: 'text-red-600 bg-red-100',
    };
    return colors[difficulty as keyof typeof colors] || colors.medium;
  };

  const getProblemStatus = (problemId: number) => {
    const userProgress = progress.find(p => p.problem.id === problemId);
    if (!userProgress) return null;
    if (userProgress.is_solved) return 'solved';
    if (userProgress.is_attempted) return 'attempted';
    return null;
  };

  const getStatusIcon = (problemId: number) => {
    const status = getProblemStatus(problemId);
    if (status === 'solved') return <CheckCircle className="h-5 w-5 text-green-600" />;
    if (status === 'attempted') return <Clock className="h-5 w-5 text-yellow-600" />;
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Code Challenges</h1>
        <p className="text-gray-600">Practice coding problems and improve your skills</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Search className="inline h-4 w-4 mr-1" />
              Search
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              placeholder="Search problems..."
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Filter className="inline h-4 w-4 mr-1" />
              Difficulty
            </label>
            <select
              value={filters.difficulty}
              onChange={(e) => setFilters({ ...filters, difficulty: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="">All</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="">All Categories</option>
              <option value="arrays">Arrays</option>
              <option value="strings">Strings</option>
              <option value="linked_lists">Linked Lists</option>
              <option value="trees">Trees</option>
              <option value="graphs">Graphs</option>
              <option value="dynamic_programming">Dynamic Programming</option>
              <option value="sorting">Sorting</option>
              <option value="searching">Searching</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => setFilters({ difficulty: '', category: '', search: '' })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Problems', value: problems.length, color: 'bg-blue-100 text-blue-800' },
          { label: 'Solved', value: progress.filter(p => p.is_solved).length, color: 'bg-green-100 text-green-800' },
          { label: 'Attempted', value: progress.filter(p => p.is_attempted && !p.is_solved).length, color: 'bg-yellow-100 text-yellow-800' },
          { label: 'Not Started', value: problems.length - progress.length, color: 'bg-gray-100 text-gray-800' },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
            <p className={`text-3xl font-bold ${stat.color.split(' ')[1]}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Problems List */}
      {problems.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Code className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <h2 className="text-xl font-semibold mb-2">No Problems Available</h2>
          <p className="text-gray-600">Check back later for coding challenges</p>
        </div>
      ) : (
        <div className="space-y-4">
          {problems.map((problem) => (
            <Link
              key={problem.id}
              to={`/code-assessment/problems/${problem.id}`}
              className="block bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getStatusIcon(problem.id)}
                    <h3 className="text-xl font-bold text-gray-900">{problem.title}</h3>
                  </div>
                  
                  <p className="text-gray-600 mb-4 line-clamp-2">{problem.description}</p>
                  
                  <div className="flex flex-wrap gap-2 mb-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(problem.difficulty)}`}>
                      {problem.difficulty}
                    </span>
                    <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                      {problem.category.replace('_', ' ')}
                    </span>
                    {problem.tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm">
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex items-center gap-6 text-sm text-gray-600">
                    <span>Acceptance: {problem.acceptance_rate}%</span>
                    <span>Submissions: {problem.total_submissions}</span>
                    <span>Max Score: {problem.max_score}</span>
                  </div>
                </div>
                
                <div className="ml-4">
                  <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    Solve
                  </button>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
