import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Upload, FileText, CheckCircle, XCircle, AlertCircle, TrendingUp, Sparkles } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import api from '@/lib/api'

interface ATSAnalysis {
  id: string
  cv: string
  ats_score: number
  keyword_matches: string[]
  missing_keywords: string[]
  quick_suggestions: string[]
  has_detailed_report: boolean
  detailed_report?: string
  created_at: string
}

interface UsageData {
  free_analyses_used: number
  free_analyses_remaining: number
  can_use_free: boolean
}

export default function ATSCheckerPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [currentAnalysis, setCurrentAnalysis] = useState<ATSAnalysis | null>(null)
  const queryClient = useQueryClient()

  // Fetch usage stats
  const { data: usage } = useQuery<UsageData>({
    queryKey: ['ats-usage'],
    queryFn: async () => {
      const response = await api.get('/api/cv-analysis/ats-checker/usage/')
      return response.data
    },
  })

  // Fetch analysis history
  const { data: history } = useQuery<ATSAnalysis[]>({
    queryKey: ['ats-history'],
    queryFn: async () => {
      const response = await api.get('/api/cv-analysis/ats-checker/history/')
      return response.data
    },
  })

  // Analyze CV mutation
  const analyzeMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('cv_file', file)
      const response = await api.post('/api/cv-analysis/ats-checker/analyze/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      setCurrentAnalysis(data)
      setSelectedFile(null)
      queryClient.invalidateQueries({ queryKey: ['ats-usage'] })
      queryClient.invalidateQueries({ queryKey: ['ats-history'] })
    },
  })

  // Request detailed report mutation
  const detailedReportMutation = useMutation({
    mutationFn: async (analysisId: string) => {
      const response = await api.post(`/api/cv-analysis/ats-checker/${analysisId}/detailed_report/`)
      return response.data
    },
    onSuccess: (data) => {
      setCurrentAnalysis(data)
      queryClient.invalidateQueries({ queryKey: ['ats-usage'] })
      queryClient.invalidateQueries({ queryKey: ['ats-history'] })
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
        setSelectedFile(file)
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleAnalyze = () => {
    if (selectedFile) {
      analyzeMutation.mutate(selectedFile)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreDescription = (score: number) => {
    if (score >= 80) return 'Excellent! Your CV is highly optimized for ATS.'
    if (score >= 60) return 'Good, but there\'s room for improvement.'
    return 'Needs improvement to pass ATS filters.'
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">ATS Checker</h1>
        <p className="text-gray-600">
          Check how well your CV performs with Applicant Tracking Systems
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Section */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Upload Your CV</CardTitle>
              <CardDescription>
                Upload your CV in PDF format to get an instant ATS score
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Usage Stats */}
              {usage && (
                <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-blue-900">
                      Free Analyses Remaining
                    </span>
                    <Badge variant="secondary">
                      {usage.free_analyses_remaining} / 3
                    </Badge>
                  </div>
                  <Progress 
                    value={(usage.free_analyses_used / 3) * 100} 
                    className="h-2"
                  />
                  {!usage.can_use_free && (
                    <p className="text-xs text-blue-700 mt-2">
                      Upgrade to premium for unlimited analyses
                    </p>
                  )}
                </div>
              )}

              {/* File Upload */}
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    Drag and drop your CV here, or click to browse
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
                    className="cursor-pointer"
                    onClick={() => document.getElementById('cv-upload')?.click()}
                    type="button"
                  >
                    Choose File
                  </Button>
                </div>
                {selectedFile && (
                  <div className="mt-4 flex items-center justify-center gap-2 text-sm text-gray-700">
                    <FileText className="h-4 w-4" />
                    <span>{selectedFile.name}</span>
                  </div>
                )}
              </div>

              <Button
                onClick={handleAnalyze}
                disabled={!selectedFile || analyzeMutation.isPending || (usage && !usage.can_use_free)}
                className="w-full mt-4"
                size="lg"
              >
                {analyzeMutation.isPending ? 'Analyzing...' : 'Analyze CV'}
              </Button>

              {analyzeMutation.error && (
                <Alert variant="destructive" className="mt-4">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    {(analyzeMutation.error as any).response?.status === 401 
                      ? 'Please log in to use this feature.' 
                      : (analyzeMutation.error as any).response?.data?.error || 'Failed to analyze CV. Please try again.'}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Results Section */}
          {currentAnalysis && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Analysis Results
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* ATS Score */}
                <div className="text-center py-6 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg">
                  <div className={`text-6xl font-bold mb-2 ${getScoreColor(currentAnalysis.ats_score)}`}>
                    {currentAnalysis.ats_score}%
                  </div>
                  <p className="text-sm text-gray-600">ATS Compatibility Score</p>
                  <p className="text-sm text-gray-700 mt-2 font-medium">
                    {getScoreDescription(currentAnalysis.ats_score)}
                  </p>
                </div>

                {/* Keyword Matches */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    Matched Keywords ({currentAnalysis.keyword_matches.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {currentAnalysis.keyword_matches.map((keyword, index) => (
                      <Badge key={index} variant="secondary" className="bg-green-100 text-green-800">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Missing Keywords */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <XCircle className="h-5 w-5 text-red-600" />
                    Missing Keywords ({currentAnalysis.missing_keywords.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {currentAnalysis.missing_keywords.map((keyword, index) => (
                      <Badge key={index} variant="secondary" className="bg-red-100 text-red-800">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Quick Suggestions */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-indigo-600" />
                    Quick Improvements
                  </h3>
                  <ul className="space-y-2">
                    {currentAnalysis.quick_suggestions.map((suggestion, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-indigo-600 mt-0.5">•</span>
                        <span>{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Detailed Report */}
                {!currentAnalysis.has_detailed_report && usage?.can_use_free && (
                  <Button
                    onClick={() => detailedReportMutation.mutate(currentAnalysis.id)}
                    disabled={detailedReportMutation.isPending}
                    variant="outline"
                    className="w-full"
                  >
                    {detailedReportMutation.isPending 
                      ? 'Generating...' 
                      : `Get Detailed Report (${usage.free_analyses_remaining} free remaining)`}
                  </Button>
                )}

                {currentAnalysis.detailed_report && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-2">Detailed Analysis</h3>
                    <p className="text-sm text-gray-700 whitespace-pre-line">
                      {currentAnalysis.detailed_report}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* History Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Recent Analyses</CardTitle>
            </CardHeader>
            <CardContent>
              {history && history.length > 0 ? (
                <div className="space-y-3">
                  {history.slice(0, 5).map((analysis) => (
                    <button
                      key={analysis.id}
                      onClick={() => setCurrentAnalysis(analysis)}
                      className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className={`text-2xl font-bold ${getScoreColor(analysis.ats_score)}`}>
                          {analysis.ats_score}%
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {new Date(analysis.created_at).toLocaleDateString()}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 truncate">
                        {analysis.keyword_matches.length} keywords matched
                      </p>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 text-center py-8">
                  No analyses yet. Upload a CV to get started!
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
