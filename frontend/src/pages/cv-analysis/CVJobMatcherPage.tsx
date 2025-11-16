import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Upload, FileText, Target, AlertCircle, TrendingUp, CheckCircle2, XCircle } from 'lucide-react'
import api from '@/lib/api'

interface CVJobMatch {
  id: string
  cv: string
  job_description: string
  match_score: number
  matched_skills: string[]
  missing_skills: string[]
  experience_match: string
  recommendations: string[]
  created_at: string
}

interface UsageData {
  free_matches_used: number
  free_matches_remaining: number
  can_use_free: boolean
}

export default function CVJobMatcherPage() {
  const [selectedCV, setSelectedCV] = useState<File | null>(null)
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [dragActive, setDragActive] = useState(false)
  const [currentMatch, setCurrentMatch] = useState<CVJobMatch | null>(null)
  const queryClient = useQueryClient()

  // Fetch usage stats
  const { data: usage } = useQuery<UsageData>({
    queryKey: ['cv-matcher-usage'],
    queryFn: async () => {
      const response = await api.get('/api/cv-analysis/cv-job-matcher/usage/')
      return response.data
    },
  })

  // Fetch match history
  const { data: history } = useQuery<CVJobMatch[]>({
    queryKey: ['cv-matcher-history'],
    queryFn: async () => {
      const response = await api.get('/api/cv-analysis/cv-job-matcher/history/')
      return response.data
    },
  })

  // Match CV to job mutation
  const matchMutation = useMutation({
    mutationFn: async (data: { cv: File; jobTitle: string; jobDescription: string }) => {
      const formData = new FormData()
      formData.append('cv_file', data.cv)
      formData.append('job_title', data.jobTitle)
      formData.append('job_description', data.jobDescription)
      const response = await api.post('/api/cv-analysis/cv-job-matcher/match/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      setCurrentMatch(data)
      setSelectedCV(null)
      setJobTitle('')
      setJobDescription('')
      queryClient.invalidateQueries({ queryKey: ['cv-matcher-usage'] })
      queryClient.invalidateQueries({ queryKey: ['cv-matcher-history'] })
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

  const handleMatch = () => {
    if (selectedCV && jobTitle.trim() && jobDescription.trim()) {
      matchMutation.mutate({ cv: selectedCV, jobTitle, jobDescription })
    }
  }

  const getMatchColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getMatchDescription = (score: number) => {
    if (score >= 80) return 'Excellent match! You\'re a strong candidate for this role.'
    if (score >= 60) return 'Good match with some skills gaps to address.'
    return 'Limited match. Consider upskilling in key areas.'
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">CV-Job Matcher</h1>
        <p className="text-gray-600">
          See how well your CV matches a specific job description
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Section */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Upload & Match</CardTitle>
              <CardDescription>
                Upload your CV and paste the job description to see your compatibility
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Usage Stats */}
              {usage && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-blue-900">
                      Free Matches Remaining
                    </span>
                    <Badge variant="secondary">
                      {usage.free_matches_remaining} / 3
                    </Badge>
                  </div>
                  <Progress 
                    value={(usage.free_matches_used / 3) * 100} 
                    className="h-2"
                  />
                  {!usage.can_use_free && (
                    <p className="text-xs text-blue-700 mt-2">
                      Upgrade to premium for unlimited matching
                    </p>
                  )}
                </div>
              )}

              {/* CV Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your CV
                </label>
                <div
                  className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                    dragActive
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                >
                  <Upload className="mx-auto h-10 w-10 text-gray-400 mb-3" />
                  <p className="text-sm text-gray-600 mb-2">
                    Drag and drop your CV here
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
                    size="sm"
                    onClick={() => document.getElementById('cv-upload')?.click()}
                    type="button"
                  >
                    Choose File
                  </Button>
                  {selectedCV && (
                    <div className="mt-3 flex items-center justify-center gap-2 text-sm text-gray-700">
                      <FileText className="h-4 w-4" />
                      <span>{selectedCV.name}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Job Title */}
              <div>
                <label htmlFor="job-title" className="block text-sm font-medium text-gray-700 mb-2">
                  Job Title
                </label>
                <input
                  type="text"
                  id="job-title"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g., Senior Software Engineer"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              {/* Job Description */}
              <div>
                <label htmlFor="job-description" className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description
                </label>
                <textarea
                  id="job-description"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the complete job description here..."
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Include requirements, responsibilities, and qualifications for best results
                </p>
              </div>

              <Button
                onClick={handleMatch}
                disabled={!selectedCV || !jobTitle.trim() || !jobDescription.trim() || matchMutation.isPending || (usage && !usage.can_use_free)}
                className="w-full"
                size="lg"
              >
                {matchMutation.isPending ? 'Analyzing Match...' : 'Analyze Match'}
              </Button>

              {matchMutation.error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    {(matchMutation.error as any).response?.data?.error || 'Failed to analyze match'}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Results Section */}
          {currentMatch && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Match Results
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Match Score */}
                <div className="text-center py-6 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg">
                  <div className={`text-6xl font-bold mb-2 ${getMatchColor(currentMatch.match_score)}`}>
                    {currentMatch.match_score}%
                  </div>
                  <p className="text-sm text-gray-600">Job Match Score</p>
                  <p className="text-sm text-gray-700 mt-2 font-medium px-4">
                    {getMatchDescription(currentMatch.match_score)}
                  </p>
                </div>

                {/* Matched Skills */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    Your Matching Skills ({currentMatch.matched_skills.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {currentMatch.matched_skills.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="bg-green-100 text-green-800">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Missing Skills */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <XCircle className="h-5 w-5 text-red-600" />
                    Skills to Develop ({currentMatch.missing_skills.length})
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {currentMatch.missing_skills.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="bg-red-100 text-red-800">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Experience Match */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-2">Experience Level</h3>
                  <p className="text-sm text-gray-700">
                    {currentMatch.experience_match}
                  </p>
                </div>

                {/* Recommendations */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-indigo-600" />
                    Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {currentMatch.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-indigo-600 mt-0.5">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* History Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Recent Matches</CardTitle>
            </CardHeader>
            <CardContent>
              {history && history.length > 0 ? (
                <div className="space-y-3">
                  {history.slice(0, 5).map((match) => (
                    <button
                      key={match.id}
                      onClick={() => setCurrentMatch(match)}
                      className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className={`text-2xl font-bold ${getMatchColor(match.match_score)}`}>
                          {match.match_score}%
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {new Date(match.created_at).toLocaleDateString()}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 truncate">
                        {match.matched_skills.length} skills matched
                      </p>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 text-center py-8">
                  No matches yet. Upload your CV and a job description!
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
