import api from '@/lib/api';

export interface CodingProblem {
  id: number;
  title: string;
  slug: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  category: string;
  tags: string[];
  input_format: string;
  output_format: string;
  constraints: string;
  examples: Array<{
    input: string;
    output: string;
    explanation?: string;
  }>;
  python_template: string;
  javascript_template: string;
  java_template: string;
  max_score: number;
  time_limit_seconds: number;
  memory_limit_mb: number;
  total_submissions: number;
  accepted_submissions: number;
  acceptance_rate: number;
  sample_test_cases?: TestCase[];
}

export interface TestCase {
  id: number;
  input_data: string;
  expected_output: string;
  is_hidden: boolean;
  is_sample: boolean;
  explanation?: string;
  weight: number;
}

export interface Submission {
  id: number;
  problem: number;
  problem_title: string;
  code: string;
  language: 'python' | 'javascript' | 'java';
  status: 'pending' | 'running' | 'accepted' | 'wrong_answer' | 'time_limit_exceeded' | 'memory_limit_exceeded' | 'runtime_error' | 'compilation_error';
  score: number;
  passed_test_cases: number;
  total_test_cases: number;
  execution_time_ms?: number;
  memory_used_mb?: number;
  error_message?: string;
  test_results?: TestCaseResult[];
  submitted_at: string;
  completed_at?: string;
}

export interface TestCaseResult {
  id: number;
  test_case: TestCase;
  passed: boolean;
  actual_output?: string;
  execution_time_ms?: number;
  memory_used_mb?: number;
  error_message?: string;
}

export interface UserProgress {
  id: number;
  problem: CodingProblem;
  is_solved: boolean;
  is_attempted: boolean;
  best_score: number;
  attempts_count: number;
  first_attempted_at?: string;
  solved_at?: string;
  last_attempted_at?: string;
}

class CodeAssessmentService {
  async getProblems(params?: {
    difficulty?: string;
    category?: string;
    search?: string;
  }): Promise<CodingProblem[]> {
    const response = await api.get('/code-assessment/problems/', { params });
    return response.data;
  }

  async getProblem(id: number): Promise<CodingProblem> {
    const response = await api.get(`/code-assessment/problems/${id}/`);
    return response.data;
  }

  async submitCode(data: {
    problem: number;
    code: string;
    language: 'python' | 'javascript' | 'java';
  }): Promise<Submission> {
    const response = await api.post('/code-assessment/submissions/', data);
    return response.data;
  }

  async getSubmission(id: number): Promise<Submission> {
    const response = await api.get(`/code-assessment/submissions/${id}/`);
    return response.data;
  }

  async getSubmissions(problemId?: number): Promise<Submission[]> {
    const params = problemId ? { problem: problemId } : {};
    const response = await api.get('/code-assessment/submissions/', { params });
    return response.data;
  }

  async getUserProgress(): Promise<UserProgress[]> {
    const response = await api.get('/code-assessment/progress/');
    return response.data;
  }

  async runCode(data: {
    problem: number;
    code: string;
    language: string;
  }): Promise<any> {
    const response = await api.post('/code-assessment/run/', data);
    return response.data;
  }
}

export default new CodeAssessmentService();
