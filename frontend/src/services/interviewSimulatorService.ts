import api from '../lib/api'

export interface StartSessionRequest {
  title: string
  job_role: string
  company_name?: string
  mode?: 'practice' | 'simulation'
}

export interface StartSessionResponse {
  session_id: string
  status: string
  opening_message: string
  session: any
}

export interface RespondRequest {
  response_text: string
  audio_url?: string
  timestamp?: number
}

export interface RespondResponse {
  next_question: string
  analysis: {
    sentiment: string
    confidence_score: number
    keywords: string[]
  }
  message_id: string
}

export interface EndSessionResponse {
  session: any
  feedback: string
  scores: {
    overall_score: number
    technical_score: number
    communication_score: number
    confidence_score: number
    problem_solving_score: number
  }
}

export interface Message {
  id: string
  role: 'interviewer' | 'candidate'
  content: string
  timestamp: number
  sentiment?: string
  confidence_score?: number
}

class InterviewSimulatorService {
  async startSession(data: StartSessionRequest): Promise<StartSessionResponse> {
    const response = await api.post('/api/interviews/simulator/start/', data)
    return response.data
  }

  async submitResponse(sessionId: string, data: RespondRequest): Promise<RespondResponse> {
    const response = await api.post(`/api/interviews/simulator/${sessionId}/respond/`, data)
    return response.data
  }

  async endSession(sessionId: string): Promise<EndSessionResponse> {
    const response = await api.post(`/api/interviews/simulator/${sessionId}/end/`)
    return response.data
  }

  async getTranscript(sessionId: string): Promise<any> {
    const response = await api.get(`/api/interviews/simulator/${sessionId}/transcript/`)
    return response.data
  }

  async getMessages(sessionId: string): Promise<{ messages: Message[] }> {
    const response = await api.get(`/api/interviews/simulator/${sessionId}/messages/`)
    return response.data
  }

  async getHistory(): Promise<any> {
    const response = await api.get('/api/interviews/simulator/history/')
    return response.data
  }
}

export default new InterviewSimulatorService()
