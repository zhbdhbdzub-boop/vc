import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Video, Mic, MicOff, Volume2, VolumeX, Play, Square, MessageSquare, Loader2, Trophy, Target, MessageCircle, Zap, AlertCircle } from 'lucide-react'
import interviewSimulatorService from '@/services/interviewSimulatorService'

interface Message {
  id: string
  role: 'interviewer' | 'candidate'
  content: string
  timestamp: number
  sentiment?: string
  confidence_score?: number
}

interface InterviewReport {
  scores: {
    overall_score: number
    technical_score: number
    communication_score: number
    confidence_score: number
  }
  feedback: string
}

export default function InterviewSimulatorPage() {
  const [isSessionActive, setIsSessionActive] = useState(false)
  const [jobRole, setJobRole] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [currentResponse, setCurrentResponse] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [autoSpeak, setAutoSpeak] = useState(true)
  const [showReportDialog, setShowReportDialog] = useState(false)
  const [interviewReport, setInterviewReport] = useState<InterviewReport | null>(null)
  const [showErrorDialog, setShowErrorDialog] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  
  // Speech Recognition & Synthesis
  const recognitionRef = useRef<any>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Initialize Speech Synthesis
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis
    }

    // Initialize Speech Recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setCurrentResponse(prev => prev + ' ' + transcript)
      }

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsRecording(false)
      }

      recognitionRef.current.onend = () => {
        setIsRecording(false)
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (synthRef.current) {
        synthRef.current.cancel()
      }
    }
  }, [])

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const speakText = (text: string) => {
    if (!synthRef.current) return

    // Cancel any ongoing speech
    synthRef.current.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    
    // Get available voices and select a natural-sounding one
    const voices = synthRef.current.getVoices()
    
    // Try to find a high-quality English voice (prefer female voices for professional tone)
    const preferredVoice = voices.find(voice => 
      (voice.name.includes('Google') || voice.name.includes('Microsoft') || voice.name.includes('Samantha')) &&
      voice.lang.startsWith('en') &&
      (voice.name.toLowerCase().includes('female') || voice.name.toLowerCase().includes('woman'))
    ) || voices.find(voice => 
      voice.lang.startsWith('en') && voice.name.includes('Female')
    ) || voices.find(voice => 
      voice.lang.startsWith('en-US') || voice.lang.startsWith('en-GB')
    )
    
    if (preferredVoice) {
      utterance.voice = preferredVoice
    }
    
    // Natural speech settings
    utterance.rate = 0.95  // Slightly slower for clarity
    utterance.pitch = 1.05  // Slightly higher for friendliness
    utterance.volume = 0.9
    
    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    synthRef.current.speak(utterance)
  }

  const toggleSpeechRecognition = () => {
    if (!recognitionRef.current) {
      setErrorMessage('Speech recognition is not supported in this browser. Please use Chrome or Edge.')
      setShowErrorDialog(true)
      return
    }

    if (isRecording) {
      recognitionRef.current.stop()
      setIsRecording(false)
    } else {
      recognitionRef.current.start()
      setIsRecording(true)
    }
  }

  const handleStartSession = async () => {
    if (!jobRole) {
      setErrorMessage('Please enter a job role to start the interview.')
      setShowErrorDialog(true)
      return
    }

    setIsLoading(true)
    try {
      const result = await interviewSimulatorService.startSession({
        title: `${jobRole} Interview${companyName ? ` at ${companyName}` : ''}`,
        job_role: jobRole,
        company_name: companyName,
        mode: 'simulation'
      })

      setSessionId(result.session_id)
      setIsSessionActive(true)

      const initialMessage: Message = {
        id: Date.now().toString(),
        role: 'interviewer',
        content: result.opening_message,
        timestamp: Date.now()
      }
      setMessages([initialMessage])

      // Speak the opening message
      if (autoSpeak) {
        speakText(result.opening_message)
      }
    } catch (error: any) {
      console.error('Failed to start session:', error)
      setErrorMessage(error.response?.data?.error || 'Failed to start interview session. Please try again.')
      setShowErrorDialog(true)
    } finally {
      setIsLoading(false)
    }
  }

  const handleEndSession = async () => {
    if (!sessionId) return

    setIsLoading(true)
    try {
      const result = await interviewSimulatorService.endSession(sessionId)
      
      // Show feedback in dialog
      setInterviewReport(result)
      setShowReportDialog(true)
      
      setIsSessionActive(false)
      setSessionId(null)
      setMessages([])
      setJobRole('')
      setCompanyName('')
    } catch (error: any) {
      console.error('Failed to end session:', error)
      setErrorMessage('Failed to end session. Please try again.')
      setShowErrorDialog(true)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmitResponse = async () => {
    if (!currentResponse.trim() || !sessionId) return

    const candidateMsg: Message = {
      id: Date.now().toString(),
      role: 'candidate',
      content: currentResponse,
      timestamp: Date.now()
    }
    setMessages(prev => [...prev, candidateMsg])
    setCurrentResponse('')

    setIsLoading(true)
    try {
      const result = await interviewSimulatorService.submitResponse(sessionId, {
        response_text: currentResponse,
        timestamp: Date.now() / 1000
      })

      const aiResponse: Message = {
        id: result.message_id,
        role: 'interviewer',
        content: result.next_question,
        timestamp: Date.now(),
        sentiment: result.analysis.sentiment,
        confidence_score: result.analysis.confidence_score
      }
      setMessages(prev => [...prev, aiResponse])

      // Speak the AI response
      if (autoSpeak) {
        speakText(result.next_question)
      }
    } catch (error: any) {
      console.error('Failed to submit response:', error)
      setErrorMessage('Failed to submit response. Please try again.')
      setShowErrorDialog(true)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isSessionActive) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Simulator</h1>
          <p className="text-gray-600">Practice interviews with AI in real-time</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Start New Interview Session</CardTitle>
            <CardDescription>
              Practice your interview skills with our AI interviewer
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="jobRole">Job Role *</Label>
              <Input
                id="jobRole"
                placeholder="e.g., Senior Software Engineer"
                value={jobRole}
                onChange={(e) => setJobRole(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="company">Company Name (Optional)</Label>
              <Input
                id="company"
                placeholder="e.g., TechCorp"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
              />
            </div>
            <Button 
              onClick={handleStartSession} 
              className="w-full"
              size="lg"
              disabled={isLoading}
            >
              {isLoading ? (
                <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Starting...</>
              ) : (
                <><Play className="w-5 h-5 mr-2" /> Start Interview</>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Features */}
        <div className="grid md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">What You'll Get</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">✓</span>
                  Real-time AI conversation
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">✓</span>
                  Performance scoring (technical, communication, confidence)
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">✓</span>
                  Detailed feedback report
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">✓</span>
                  Response time analytics
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Pricing</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-4">
                <div className="text-3xl font-bold text-gray-900">24.99 TND</div>
                <div className="text-sm text-gray-600 mt-1">per session</div>
                <div className="mt-4 text-sm text-green-600 font-medium">
                  🎁 1 FREE session included
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      <div className="bg-white border-b p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              {jobRole} Interview
              {companyName && <span className="text-gray-600"> at {companyName}</span>}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {isSpeaking && <span className="text-green-600">🔊 AI is speaking...</span>}
            </p>
          </div>
          <div className="flex gap-2">
            <Button 
              onClick={() => {
                if (isSpeaking && synthRef.current) {
                  synthRef.current.cancel()
                  setIsSpeaking(false)
                } else {
                  setAutoSpeak(!autoSpeak)
                }
              }} 
              variant="outline"
              size="sm"
            >
              {autoSpeak ? (
                <><Volume2 className="w-4 h-4 mr-2" /> Audio On</>
              ) : (
                <><VolumeX className="w-4 h-4 mr-2" /> Audio Off</>
              )}
            </Button>
            <Button onClick={handleEndSession} variant="destructive" disabled={isLoading}>
              <Square className="w-4 h-4 mr-2" />
              End Interview
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Video/Avatar Section */}
        <div className="w-1/3 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-600/10"></div>
          <div className="text-center text-white relative z-10">
            <div className="relative inline-block">
              <img 
                src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop&crop=face"
                alt="AI Interviewer"
                className="w-40 h-40 rounded-full object-cover border-4 border-indigo-500 shadow-2xl mb-4"
                onError={(e) => {
                  // Fallback to another professional avatar if image fails to load
                  e.currentTarget.src = 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=400&fit=crop&crop=face'
                }}
              />
              {isSpeaking && (
                <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
                  <div className="flex gap-1">
                    <div className="w-1 h-4 bg-green-400 rounded-full animate-pulse"></div>
                    <div className="w-1 h-6 bg-green-400 rounded-full animate-pulse" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-1 h-4 bg-green-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              )}
            </div>
            <p className="text-lg font-semibold text-white mb-1">Sarah Anderson</p>
            <p className="text-sm text-gray-400">AI Interview Specialist</p>
            {isSpeaking && (
              <p className="text-xs text-green-400 mt-2 animate-pulse">Speaking...</p>
            )}
          </div>
        </div>

        {/* Chat Section */}
        <div className="flex-1 flex flex-col bg-gray-50">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'candidate' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-4 ${
                    msg.role === 'interviewer'
                      ? 'bg-white border border-gray-200'
                      : 'bg-indigo-600 text-white'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center">
                      {msg.role === 'interviewer' ? (
                        <MessageSquare className="w-4 h-4 mr-2 text-indigo-600" />
                      ) : (
                        <div className="w-4 h-4 mr-2 bg-white/20 rounded-full" />
                      )}
                      <span className="text-xs font-medium">
                        {msg.role === 'interviewer' ? 'AI Interviewer' : 'You'}
                      </span>
                    </div>
                    {msg.role === 'interviewer' && (
                      <button
                        onClick={() => speakText(msg.content)}
                        className="ml-2 p-1 hover:bg-gray-100 rounded"
                        title="Play audio"
                      >
                        <Volume2 className="w-3 h-3 text-gray-600" />
                      </button>
                    )}
                  </div>
                  <p className="text-sm">{msg.content}</p>
                  {msg.confidence_score && (
                    <div className="mt-2 text-xs opacity-70">
                      Confidence: {Math.round(msg.confidence_score * 100)}%
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center text-gray-600">
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    <span className="text-sm">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t bg-white p-4">
            <div className="max-w-4xl mx-auto space-y-3">
              <Textarea
                placeholder="Type your response here..."
                value={currentResponse}
                onChange={(e) => setCurrentResponse(e.target.value)}
                rows={3}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmitResponse()
                  }
                }}
              />
              <div className="flex justify-between items-center">
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={toggleSpeechRecognition}
                    disabled={isLoading}
                    className={isRecording ? 'bg-red-50 border-red-300' : ''}
                  >
                    {isRecording ? (
                      <><MicOff className="w-4 h-4 mr-2 text-red-600" /> Stop Recording</>
                    ) : (
                      <><Mic className="w-4 h-4 mr-2" /> Record Answer</>
                    )}
                  </Button>
                  {isRecording && (
                    <span className="text-sm text-red-600 flex items-center">
                      <span className="animate-pulse mr-2">●</span> Listening...
                    </span>
                  )}
                </div>
                <Button 
                  onClick={handleSubmitResponse}
                  disabled={isLoading || !currentResponse.trim()}
                >
                  {isLoading ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Sending...</>
                  ) : (
                    'Send Response'
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Interview Report Dialog */}
      <Dialog open={showReportDialog} onOpenChange={setShowReportDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-2xl">
              <Trophy className="w-6 h-6 text-yellow-500" />
              Interview Completed!
            </DialogTitle>
            <DialogDescription>
              Here's your performance summary
            </DialogDescription>
          </DialogHeader>
          
          {interviewReport && (
            <div className="space-y-6">
              {/* Scores Grid */}
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Target className="w-5 h-5 text-blue-600" />
                        <span className="text-sm font-medium text-gray-600">Overall</span>
                      </div>
                      <span className="text-2xl font-bold text-blue-600">
                        {interviewReport.scores.overall_score}%
                      </span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Zap className="w-5 h-5 text-purple-600" />
                        <span className="text-sm font-medium text-gray-600">Technical</span>
                      </div>
                      <span className="text-2xl font-bold text-purple-600">
                        {interviewReport.scores.technical_score}%
                      </span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <MessageCircle className="w-5 h-5 text-green-600" />
                        <span className="text-sm font-medium text-gray-600">Communication</span>
                      </div>
                      <span className="text-2xl font-bold text-green-600">
                        {interviewReport.scores.communication_score}%
                      </span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Trophy className="w-5 h-5 text-orange-600" />
                        <span className="text-sm font-medium text-gray-600">Confidence</span>
                      </div>
                      <span className="text-2xl font-bold text-orange-600">
                        {interviewReport.scores.confidence_score}%
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Feedback Section */}
              <div>
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-indigo-600" />
                  Detailed Feedback
                </h3>
                <Card>
                  <CardContent className="pt-6">
                    <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {interviewReport.feedback}
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button onClick={() => setShowReportDialog(false)} className="w-full">
              Close Report
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Error Dialog */}
      <Dialog open={showErrorDialog} onOpenChange={setShowErrorDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              Error
            </DialogTitle>
            <DialogDescription className="text-base">
              {errorMessage}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={() => setShowErrorDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
