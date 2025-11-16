import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Upload, FileText, MapPin, Briefcase, Building2, 
  ExternalLink, AlertCircle, Loader2, Globe, TrendingUp
} from 'lucide-react'
import api from '@/lib/api'

interface PossibleJob {
  title: string
  domain: string
  seniority: string
  confidence: number
}

interface JobPosting {
  title: string
  company: string
  location: string
  via: string
  posted: string
  short_description: string
  full_description: string | null
  apply_link: string | null
  google_job_url: string | null
  query_used: string
  source_title: string
  source_domain: string
  source_seniority: string
  source_confidence: number
}

interface JobMatchResults {
  possible_jobs: PossibleJob[]
  job_postings: JobPosting[]
  summary: {
    total_possible_jobs: number
    jobs_scraped: number
    total_postings_found: number
    country: string
    min_confidence: number
  }
}

interface CV {
  id: string
  filename: string
  file_type: string
  uploaded_at: string
}

const COUNTRIES = [
  { value: 'Tunisia', label: '🇹🇳 Tunisia', region: 'North Africa' },
  { value: 'Morocco', label: '🇲🇦 Morocco', region: 'North Africa' },
  { value: 'Algeria', label: '🇩🇿 Algeria', region: 'North Africa' },
  { value: 'France', label: '🇫🇷 France', region: 'Europe' },
  { value: 'Germany', label: '🇩🇪 Germany', region: 'Europe' },
  { value: 'Spain', label: '🇪🇸 Spain', region: 'Europe' },
  { value: 'Italy', label: '🇮🇹 Italy', region: 'Europe' },
  { value: 'Belgium', label: '🇧🇪 Belgium', region: 'Europe' },
  { value: 'Switzerland', label: '🇨🇭 Switzerland', region: 'Europe' },
  { value: 'United Kingdom', label: '🇬🇧 United Kingdom', region: 'Europe' },
  { value: 'Canada', label: '🇨🇦 Canada', region: 'North America' },
  { value: 'United States', label: '🇺🇸 United States', region: 'North America' },
  { value: 'Qatar', label: '🇶🇦 Qatar', region: 'Middle East' },
  { value: 'UAE', label: '🇦🇪 UAE', region: 'Middle East' },
  { value: 'Saudi Arabia', label: '🇸🇦 Saudi Arabia', region: 'Middle East' },
]

export default function RealJobMatcherPage() {
  const [selectedCV, setSelectedCV] = useState<CV | null>(null)
  const [selectedCountry, setSelectedCountry] = useState('Tunisia')
  const [minConfidence, setMinConfidence] = useState(70)
  const [results, setResults] = useState<JobMatchResults | null>(null)
  const [selectedJob, setSelectedJob] = useState<JobPosting | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const queryClient = useQueryClient()

  // Fetch user's CVs
  const { data: cvList } = useQuery<CV[]>({
    queryKey: ['cvs'],
    queryFn: async () => {
      const response = await api.get('/api/cv-analysis/cvs/')
      return response.data.results || response.data
    },
  })

  // Upload CV mutation
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await api.post('/api/cv-analysis/cvs/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: (data) => {
      setSelectedCV(data)
      setSelectedFile(null)
      queryClient.invalidateQueries({ queryKey: ['cvs'] })
    },
  })

  // Find jobs mutation
  const findJobsMutation = useMutation({
    mutationFn: async (data: { cvId: string; country: string; min_confidence: number }) => {
      const response = await api.post(`/api/cv-analysis/cvs/${data.cvId}/find_jobs/`, {
        country: data.country,
        min_confidence: data.min_confidence,
        max_jobs_per_title: 5
      })
      return response.data
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const handleFindJobs = () => {
    if (selectedCV) {
      findJobsMutation.mutate({
        cvId: selectedCV.id,
        country: selectedCountry,
        min_confidence: minConfidence
      })
    }
  }

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
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf') || 
          file.name.endsWith('.docx') || file.name.endsWith('.txt')) {
        setSelectedFile(file)
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile)
    }
  }

  const groupByRegion = () => {
    const grouped: Record<string, typeof COUNTRIES> = {}
    COUNTRIES.forEach(country => {
      if (!grouped[country.region]) {
        grouped[country.region] = []
      }
      grouped[country.region].push(country)
    })
    return grouped
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <Globe className="h-8 w-8 text-indigo-600" />
          CV-Job Matcher
        </h1>
        <p className="text-gray-600">
          Find real job postings that match your CV in your target country
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Section */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Search Settings</CardTitle>
              <CardDescription>
                Select your CV and target country
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* CV Upload/Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your CV
                </label>
                
                {!selectedCV ? (
                  <>
                    {/* Upload Area */}
                    <div
                      onDragEnter={handleDrag}
                      onDragLeave={handleDrag}
                      onDragOver={handleDrag}
                      onDrop={handleDrop}
                      className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                        dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'
                      }`}
                    >
                      <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                      <p className="text-sm text-gray-600 mb-1">
                        {selectedFile ? selectedFile.name : 'Drag and drop your CV here'}
                      </p>
                      <p className="text-xs text-gray-500 mb-3">or</p>
                      <label className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer">
                        <Upload className="mr-2 h-4 w-4" />
                        Browse Files
                        <input
                          type="file"
                          className="hidden"
                          accept=".pdf,.docx,.txt"
                          onChange={handleFileChange}
                        />
                      </label>
                      <p className="text-xs text-gray-500 mt-2">PDF, DOCX, or TXT (max 10MB)</p>
                    </div>

                    {selectedFile && (
                      <Button
                        onClick={handleUpload}
                        disabled={uploadMutation.isPending}
                        className="w-full mt-3"
                      >
                        {uploadMutation.isPending ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Uploading...
                          </>
                        ) : (
                          <>
                            <Upload className="mr-2 h-4 w-4" />
                            Upload CV
                          </>
                        )}
                      </Button>
                    )}

                    {uploadMutation.error && (
                      <Alert variant="destructive" className="mt-3">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          {(uploadMutation.error as any).response?.data?.error || 'Failed to upload CV'}
                        </AlertDescription>
                      </Alert>
                    )}

=
                  </>
                ) : (
                  <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FileText className="h-5 w-5 text-indigo-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{selectedCV.filename}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(selectedCV.uploaded_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedCV(null)}
                      >
                        Change
                      </Button>
                    </div>
                  </div>
                )}
              </div>

              {/* Country Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="inline h-4 w-4 mr-1" />
                  Target Country
                </label>
                <select
                  value={selectedCountry}
                  onChange={(e) => setSelectedCountry(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {Object.entries(groupByRegion()).map(([region, countries]) => (
                    <optgroup key={region} label={region}>
                      {countries.map((country) => (
                        <option key={country.value} value={country.value}>
                          {country.label}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </div>

              {/* Confidence Slider */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Matching rate: {minConfidence}%
                </label>
                <input
                  type="range"
                  min="50"
                  max="90"
                  step="5"
                  value={minConfidence}
                  onChange={(e) => setMinConfidence(parseInt(e.target.value))}
                  className="w-full"
                />
                <p className="text-xs text-gray-500 mt-1">
                  The match rate of your CV with the jobs found
                </p>
              </div>

              <Button
                onClick={handleFindJobs}
                disabled={!selectedCV || findJobsMutation.isPending}
                className="w-full"
                size="lg"
              >
                {findJobsMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Searching Jobs...
                  </>
                ) : (
                  <>
                    <Briefcase className="mr-2 h-4 w-4" />
                    Find Real Jobs
                  </>
                )}
              </Button>

              {findJobsMutation.error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    {(findJobsMutation.error as any).response?.data?.error || 'Failed to find jobs'}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Possible Jobs from CV */}
          {results && results.possible_jobs.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Detected Job Roles</CardTitle>
                <CardDescription>
                  AI analyzed your CV and identified {results.possible_jobs.length} possible roles
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {results.possible_jobs.map((job, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-start justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">{job.title}</span>
                      <Badge variant="secondary" className="text-xs">
                        {job.confidence}%
                      </Badge>
                    </div>
                    <div className="text-xs text-gray-600">
                      {job.domain} • {job.seniority}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2 space-y-6">
          {results ? (
            <>
              {/* Summary Card */}
              <Card className="bg-gradient-to-br from-indigo-50 to-blue-50">
                <CardContent className="pt-6">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-3xl font-bold text-indigo-600">
                        {results.summary.total_possible_jobs}
                      </div>
                      <div className="text-sm text-gray-600">Roles Found</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-indigo-600">
                        {results.summary.total_postings_found}
                      </div>
                      <div className="text-sm text-gray-600">Job Postings</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-indigo-600">
                        {results.summary.country}
                      </div>
                      <div className="text-sm text-gray-600">Location</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Job Postings */}
              {results.job_postings.length > 0 ? (
                <div className="space-y-4">
                  {results.job_postings.map((job, index) => (
                    <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedJob(job)}>
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {job.title}
                            </h3>
                            <div className="flex items-center gap-3 text-sm text-gray-600 mb-2">
                              <span className="flex items-center gap-1">
                                <Building2 className="h-4 w-4" />
                                {job.company}
                              </span>
                              <span className="flex items-center gap-1">
                                <MapPin className="h-4 w-4" />
                                {job.location}
                              </span>
                            </div>
                          </div>
                          <Badge className="bg-indigo-100 text-indigo-800">
                            {job.source_confidence}% match
                          </Badge>
                        </div>

                        <p className="text-sm text-gray-700 mb-3 line-clamp-2">
                          {job.short_description}
                        </p>

                        <div className="flex flex-wrap gap-2 mb-3">
                          <Badge variant="outline" className="text-xs">
                            {job.source_domain}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {job.source_seniority}
                          </Badge>
                          {job.posted && (
                            <Badge variant="outline" className="text-xs">
                              Posted {job.posted}
                            </Badge>
                          )}
                        </div>

                        <div className="flex gap-2">
                          {job.apply_link && (
                            <a href={job.apply_link} target="_blank" rel="noopener noreferrer">
                              <Button size="sm">
                                <ExternalLink className="mr-2 h-3 w-3" />
                                Apply Now
                              </Button>
                            </a>
                          )}
                        </div>

                        {job.via && (
                          <p className="text-xs text-gray-500 mt-2">
                            Via {job.via}
                          </p>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card>
                  <CardContent className="py-12 text-center">
                    <Briefcase className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No jobs found
                    </h3>
                    <p className="text-gray-600">
                      Try lowering the confidence threshold or selecting a different country.
                    </p>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <Globe className="mx-auto h-16 w-16 text-gray-300 mb-4" />
                <h3 className="text-xl font-medium text-gray-900 mb-2">
                  Ready to find your next opportunity?
                </h3>
                <p className="text-gray-600 mb-4 max-w-md mx-auto">
                  Select your CV and target country, then click "Find Real Jobs" to discover
                  positions that match your skills and experience.
                </p>
                <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <TrendingUp className="h-4 w-4" />
                    AI-powered matching
                  </div>
                  <div className="flex items-center gap-1">
                    <Globe className="h-4 w-4" />
                    Global opportunities
                  </div>
                  <div className="flex items-center gap-1">
                    <ExternalLink className="h-4 w-4" />
                    Direct apply links
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Job Detail Modal */}
      {selectedJob && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedJob(null)}
        >
          <Card className="max-w-3xl w-full max-h-[90vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <CardHeader>
              <CardTitle>{selectedJob.title}</CardTitle>
              <CardDescription>
                {selectedJob.company} • {selectedJob.location}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {selectedJob.full_description ? (
                <div className="prose prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700">
                    {selectedJob.full_description}
                  </pre>
                </div>
              ) : (
                <p className="text-gray-700">{selectedJob.short_description}</p>
              )}

              <div className="flex gap-2 pt-4 border-t">
                {selectedJob.apply_link && (
                  <a href={selectedJob.apply_link} target="_blank" rel="noopener noreferrer" className="flex-1">
                    <Button className="w-full">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Apply for this Job
                    </Button>
                  </a>
                )}
                <Button variant="outline" onClick={() => setSelectedJob(null)}>
                  Close
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
