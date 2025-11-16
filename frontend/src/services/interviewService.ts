import api from '@/lib/api';

export interface InterviewTemplate {
  id: number;
  name: string;
  description: string;
  interview_type: 'technical' | 'behavioral' | 'case_study' | 'system_design' | 'cultural_fit' | 'mixed';
  difficulty: 'easy' | 'medium' | 'hard';
  duration_minutes: number;
  total_questions: number;
  is_public: boolean;
}

export interface Question {
  id: number;
  question_type: 'multiple_choice' | 'coding' | 'open_ended' | 'behavioral' | 'system_design';
  difficulty: 'easy' | 'medium' | 'hard';
  topic: string;
  question_text: string;
  options?: string[];
  correct_answer?: string;
  test_cases?: any;
  time_limit_seconds?: number;
  points: number;
}

export interface SessionQuestion {
  id: number;
  question: Question;
  user_answer?: string;
  is_correct?: boolean;
  score: number;
  feedback?: string;
  time_taken_seconds?: number;
  answered_at?: string;
}

export interface InterviewSession {
  id: number;
  template: InterviewTemplate;
  started_at: string;
  completed_at?: string;
  status: 'in_progress' | 'completed' | 'abandoned';
  current_question_index: number;
  total_score: number;
  max_score: number;
  questions?: SessionQuestion[];
}

export interface InterviewFeedback {
  id: number;
  session: number;
  overall_performance: string;
  technical_performance?: string;
  communication_performance?: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  percentile_rank?: number;
  generated_at: string;
}

export interface StartSessionRequest {
  template_id: number;
  job_role?: string;
  experience_level?: string;
}

export interface SubmitAnswerRequest {
  session_id: number;
  question_id: number;
  answer: string;
  time_taken_seconds?: number;
}

class InterviewService {
  async getTemplates(): Promise<InterviewTemplate[]> {
    const response = await api.get('/interviews/templates/');
    return response.data;
  }

  async getTemplate(id: number): Promise<InterviewTemplate> {
    const response = await api.get(`/interviews/templates/${id}/`);
    return response.data;
  }

  async getSessions(): Promise<InterviewSession[]> {
    const response = await api.get('/interviews/sessions/');
    return response.data;
  }

  async getSession(id: number): Promise<InterviewSession> {
    const response = await api.get(`/interviews/sessions/${id}/`);
    return response.data;
  }

  async startSession(data: StartSessionRequest): Promise<InterviewSession> {
    const response = await api.post('/interviews/sessions/', data);
    return response.data;
  }

  async submitAnswer(data: SubmitAnswerRequest): Promise<SessionQuestion> {
    const response = await api.post('/interviews/sessions/submit-answer/', data);
    return response.data;
  }

  async completeSession(sessionId: number): Promise<InterviewSession> {
    const response = await api.post(`/interviews/sessions/${sessionId}/complete/`);
    return response.data;
  }

  async getFeedback(sessionId: number): Promise<InterviewFeedback> {
    const response = await api.get(`/interviews/sessions/${sessionId}/feedback/`);
    return response.data;
  }

  async generateQuestion(data: {
    question_type: string;
    difficulty: string;
    topic: string;
    job_role?: string;
  }): Promise<Question> {
    const response = await api.post('/interviews/questions/generate/', data);
    return response.data;
  }
}

export default new InterviewService();
