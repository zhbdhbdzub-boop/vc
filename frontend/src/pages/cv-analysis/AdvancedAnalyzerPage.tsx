import { useState, useRef, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { 
  Upload, 
  FileText, 
  AlertCircle, 
  Sparkles, 
  Send,
  Bot,
  User as UserIcon,
  Loader2
} from 'lucide-react'
import api from '@/lib/api'

interface AdvancedAnalysis {
  id: string
  cv: string
  full_analysis: string
  strengths: string[]
  weaknesses: string[]
  improvement_suggestions: string[]
  career_recommendations: string[]
  created_at: string
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export default function AdvancedAnalyzerPage() {
  const [selectedCV, setSelectedCV] = useState<File | null>(null)
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [currentAnalysis, setCurrentAnalysis] = useState<AdvancedAnalysis | null>(null)
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatInput, setChatInput] = useState('')
  const chatEndRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  // Analyze CV mutation
  const analyzeMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('cv_file', file)
      const response = await api.post('/api/cv-analysis/advanced-cv-analyzer/analyze/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      setCurrentAnalysis(data)
      setSelectedCV(null)
      setChatMessages([])
      queryClient.invalidateQueries({ queryKey: ['advanced-analysis-history'] })
    },
  })

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: async (data: { analysisId: string; message: string }) => {
      const response = await api.post(
        `/api/cv-analysis/advanced-cv-analyzer/${data.analysisId}/chat/`,
        { message: data.message }
      )
      return response.data
    },
    onSuccess: (data) => {
      setChatMessages(prev => [...prev, data])
      setChatInput('')
    },
  })

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        setSelectedCV(file)
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedCV(e.target.files[0])
    }
  }

  const handleAnalyze = () => {
    if (selectedCV) {
      analyzeMutation.mutate(selectedCV)
    }
  }

  const handleSendMessage = () => {
    if (chatInput.trim() && currentAnalysis) {
      // Add user message immediately
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: chatInput,
        created_at: new Date().toISOString(),
      }
      setChatMessages(prev => [...prev, userMessage])
      
      // Send to API
      chatMutation.mutate({
        analysisId: currentAnalysis.id,
        message: chatInput,
      })
    }
  }

  // Auto scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  return (
    <div className="container mx-auto px-4 py-8 max-w-[1600px]">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <h1 className="text-3xl font-bold text-gray-900">Advanced CV Analyzer</h1>
          <Badge className="bg-gradient-to-r from-purple-600 to-indigo-600">Premium</Badge>
        </div>
        <p className="text-gray-600">
          Get comprehensive AI-powered CV analysis with personalized career insights powered by Llama 3.1
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-250px)]">
        {/* Left Side - Input Section */}
        <div className="flex flex-col gap-6 h-full">
          {/* Job Details Section */}
          <Card className="flex-shrink-0">
            <CardHeader>
              <CardTitle>Job Details</CardTitle>
              <CardDescription>
                Enter the target position details for better analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="job-title">Job Title</Label>
                <Input
                  id="job-title"
                  placeholder="e.g., Senior Software Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="job-description">Job Description</Label>
                <Textarea
                  id="job-description"
                  placeholder="Paste the job description here..."
                  value={jobDescription}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setJobDescription(e.target.value)}
                  rows={4}
                  className="resize-none"
                />
              </div>
            </CardContent>
          </Card>

          {/* CV Upload Section */}
          <Card className="flex-1 flex flex-col">
            <CardHeader>
              <CardTitle>Upload Your CV</CardTitle>
              <CardDescription>
                Upload your CV in PDF format
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              <div
                className={`border-2 border-dashed rounded-lg flex-1 flex flex-col items-center justify-center transition-colors ${
                  dragActive
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <Upload className="h-12 w-12 text-gray-400 mb-3" />
                <p className="text-base text-gray-700 mb-1">
                  Drag and drop your CV here
                </p>
                <p className="text-sm text-gray-500 mb-3">
                  or click to browse files
                </p>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                  id="cv-upload"
                />
                <Button 
                  variant="outline"
                  onClick={() => document.getElementById('cv-upload')?.click()}
                  type="button"
                >
                  Choose File
                </Button>
                {selectedCV && (
                  <div className="mt-4 flex items-center gap-2 text-sm text-gray-700">
                    <FileText className="h-5 w-5 text-indigo-600" />
                    <span className="font-medium">{selectedCV.name}</span>
                  </div>
                )}
              </div>

              <Button
                onClick={handleAnalyze}
                disabled={!selectedCV || analyzeMutation.isPending}
                className="w-full mt-4"
                size="lg"
              >
                {analyzeMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing with AI...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Analyze CV
                  </>
                )}
              </Button>

              {analyzeMutation.error && (
                <Alert variant="destructive" className="mt-4">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    {(analyzeMutation.error as any).response?.data?.error || 'Failed to analyze CV'}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Side - Chat Section */}
        <Card className="flex flex-col h-full">
          <CardHeader className="flex-shrink-0">
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-indigo-600" />
              Chat with Llama 3.1 AI
            </CardTitle>
            <CardDescription>
              {currentAnalysis 
                ? 'Ask questions about your CV analysis' 
                : 'Upload and analyze your CV to start chatting'}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col min-h-0">
            {/* Chat Messages */}
            <div className="flex-1 bg-gray-50 rounded-lg p-4 mb-4 overflow-y-auto">
              {!currentAnalysis ? (
                <div className="h-full flex items-center justify-center text-center">
                  <div>
                    <Bot className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-base text-gray-500 font-medium mb-2">
                      Waiting for CV analysis...
                    </p>
                    <p className="text-sm text-gray-400">
                      Upload your CV and click "Analyze CV" to start
                    </p>
                  </div>
                </div>
              ) : chatMessages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-center">
                  <div>
                    <Bot className="h-16 w-16 text-indigo-300 mx-auto mb-4" />
                    <p className="text-base text-gray-700 font-medium mb-2">
                      Hi! I'm your AI CV consultant 👋
                    </p>
                    <p className="text-sm text-gray-500 mb-4">
                      Ask me anything about your CV!
                    </p>
                    <div className="space-y-2 text-left bg-white p-4 rounded-lg max-w-md mx-auto">
                      <p className="text-xs text-gray-600 font-medium">Example questions:</p>
                      <ul className="text-xs text-gray-500 space-y-1">
                        <li>• How can I improve my technical skills section?</li>
                        <li>• What are my biggest weaknesses?</li>
                        <li>• Should I add more quantifiable achievements?</li>
                        <li>• How can I make my CV stand out?</li>
                      </ul>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {message.role === 'assistant' && (
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center">
                            <Bot className="h-5 w-5 text-white" />
                          </div>
                        </div>
                      )}
                      <div
                        className={`rounded-lg px-4 py-3 max-w-[85%] ${
                          message.role === 'user'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-line leading-relaxed">{message.content}</p>
                        <p className="text-xs mt-2 opacity-70">
                          {new Date(message.created_at).toLocaleTimeString()}
                        </p>
                      </div>
                      {message.role === 'user' && (
                        <div className="flex-shrink-0">
                          <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                            <UserIcon className="h-5 w-5 text-gray-600" />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  {chatMutation.isPending && (
                    <div className="flex gap-3">
                      <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                      <div className="bg-white rounded-lg px-4 py-3 border border-gray-200">
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin text-indigo-600" />
                          <span className="text-sm text-gray-500">Thinking...</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="flex gap-2 flex-shrink-0">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                placeholder={currentAnalysis ? "Ask a question..." : "Analyze CV first..."}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                disabled={!currentAnalysis || chatMutation.isPending}
              />
              <Button
                onClick={handleSendMessage}
                disabled={!currentAnalysis || !chatInput.trim() || chatMutation.isPending}
                size="lg"
                className="px-6"
              >
                <Send className="h-5 w-5" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analysis Results Modal/Section - Show below when analysis is done */}
      {currentAnalysis && (
        <div className="mt-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-indigo-600" />
                  Analysis Results
                </CardTitle>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    setCurrentAnalysis(null)
                    setChatMessages([])
                    setSelectedCV(null)
                    setJobTitle('')
                    setJobDescription('')
                  }}
                >
                  New Analysis
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Full Analysis */}
                <div className="md:col-span-2 bg-gradient-to-br from-indigo-50 to-blue-50 p-6 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-3 text-lg">📋 Executive Summary</h3>
                  <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                    {currentAnalysis.full_analysis}
                  </p>
                </div>

                {/* Strengths */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 text-lg">💪 Key Strengths</h3>
                  <div className="space-y-2">
                    {currentAnalysis.strengths.map((strength, index) => (
                      <div key={index} className="flex items-start gap-2 bg-green-50 p-3 rounded-lg border border-green-100">
                        <span className="text-green-600 mt-0.5 font-bold">✓</span>
                        <span className="text-sm text-gray-700">{strength}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Weaknesses */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 text-lg">⚠️ Areas for Improvement</h3>
                  <div className="space-y-2">
                    {currentAnalysis.weaknesses.map((weakness, index) => (
                      <div key={index} className="flex items-start gap-2 bg-yellow-50 p-3 rounded-lg border border-yellow-100">
                        <span className="text-yellow-600 mt-0.5 font-bold">!</span>
                        <span className="text-sm text-gray-700">{weakness}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Improvement Suggestions */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 text-lg">🎯 Action Items</h3>
                  <ul className="space-y-2">
                    {currentAnalysis.improvement_suggestions.map((suggestion, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start gap-2 bg-blue-50 p-3 rounded-lg border border-blue-100">
                        <span className="text-blue-600 mt-0.5 font-bold">→</span>
                        <span>{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Career Recommendations */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 text-lg">🚀 Career Insights</h3>
                  <div className="space-y-2">
                    {currentAnalysis.career_recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start gap-2 bg-purple-50 p-3 rounded-lg border border-purple-100">
                        <span className="text-purple-600 mt-0.5 font-bold">★</span>
                        <span className="text-sm text-gray-700">{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
