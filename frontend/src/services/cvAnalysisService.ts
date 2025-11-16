import api from '@/lib/api';

export interface CV {
  id: number;
  file_name: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  processed_at?: string;
  extracted_text?: string;
  error_message?: string;
}

export interface CVAnalysis {
  id: number;
  cv: number;
  full_name?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  github_url?: string;
  total_experience_years: number;
  experience_score: number;
  education_score: number;
  skills_score: number;
  formatting_score: number;
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  analyzed_at: string;
}

export interface Skill {
  id: number;
  name: string;
  category: 'technical' | 'soft' | 'language' | 'certification' | 'tool' | 'other';
  synonyms: string[];
  description?: string;
}

export interface CVSkill {
  id: number;
  cv: number;
  skill: Skill;
  proficiency_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  years_of_experience?: number;
  confidence_score: number;
}

export interface Experience {
  id: number;
  cv: number;
  job_title: string;
  company: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  duration_months?: number;
  description?: string;
}

export interface Education {
  id: number;
  cv: number;
  degree: string;
  field_of_study?: string;
  institution: string;
  location?: string;
  graduation_year?: number;
  gpa?: string;
}

export interface JobMatch {
  id: number;
  cv: number;
  job_posting: {
    id: number;
    title: string;
    company: string;
    location?: string;
    description?: string;
    requirements?: string;
  };
  overall_score: number;
  skills_match_score: number;
  experience_match_score: number;
  education_match_score: number;
  match_summary: string;
  recommendations: string[];
  matched_skills: string[];
  missing_skills: string[];
  matched_at: string;
}

export interface CVDetail extends CV {
  analysis?: CVAnalysis;
  skills?: CVSkill[];
  experiences?: Experience[];
  education?: Education[];
  matches?: JobMatch[];
}

export interface CVStatistics {
  total_cvs: number;
  processed_cvs: number;
  pending_cvs: number;
  failed_cvs: number;
  average_processing_time: number;
  average_overall_score: number;
  total_skills_extracted: number;
  top_skills: Array<{ skill: string; count: number }>;
}

class CVAnalysisService {
  async uploadCV(file: File): Promise<CV> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/cv-analysis/cvs/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getCVs(): Promise<CV[]> {
    const response = await api.get('/api/cv-analysis/cvs/');
    return response.data;
  }

  async getCVDetail(id: number): Promise<CVDetail> {
    const response = await api.get(`/api/cv-analysis/cvs/${id}/`);
    return response.data;
  }

  async deleteCV(id: number): Promise<void> {
    await api.delete(`/api/cv-analysis/cvs/${id}/`);
  }

  async reprocessCV(id: number): Promise<CV> {
    const response = await api.post(`/api/cv-analysis/cvs/${id}/reprocess/`);
    return response.data;
  }

  async getAnalysis(cvId: number): Promise<CVAnalysis> {
    const response = await api.get(`/api/cv-analysis/cvs/${cvId}/analysis/`);
    return response.data;
  }

  async getMatches(cvId: number): Promise<JobMatch[]> {
    const response = await api.get(`/api/cv-analysis/cvs/${cvId}/matches/`);
    return response.data;
  }

  async matchCV(cvId: number): Promise<JobMatch[]> {
    const response = await api.post('/api/cv-analysis/match/', { cv_id: cvId });
    return response.data;
  }

  async getSkills(params?: {
    category?: string;
    search?: string;
  }): Promise<Skill[]> {
    const response = await api.get('/cv-analysis/skills/', { params });
    return response.data;
  }

  async getTrendingSkills(): Promise<Array<{ skill: Skill; count: number }>> {
    const response = await api.get('/cv-analysis/skills/trending/');
    return response.data;
  }

  async getStatistics(): Promise<CVStatistics> {
    const response = await api.get('/cv-analysis/statistics/cvs/');
    return response.data;
  }
}

export default new CVAnalysisService();
