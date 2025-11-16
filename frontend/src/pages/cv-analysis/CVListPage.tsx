import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Upload, Trash2, RefreshCw, Clock, CheckCircle, XCircle, Loader } from 'lucide-react';
import cvAnalysisService, { CV } from '@/services/cvAnalysisService';

export default function CVListPage() {
  const [cvs, setCvs] = useState<CV[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  useEffect(() => {
    loadCVs();
  }, []);

  const loadCVs = async () => {
    try {
      setLoading(true);
      const data = await cvAnalysisService.getCVs();
      setCvs(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load CVs');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this CV?')) return;

    try {
      setDeletingId(id);
      await cvAnalysisService.deleteCV(id);
      setCvs(cvs.filter(cv => cv.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete CV');
    } finally {
      setDeletingId(null);
    }
  };

  const handleReprocess = async (id: number) => {
    try {
      await cvAnalysisService.reprocessCV(id);
      loadCVs();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reprocess CV');
    }
  };

  const getStatusBadge = (status: CV['status']) => {
    const badges = {
      pending: { icon: Clock, class: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
      processing: { icon: Loader, class: 'bg-blue-100 text-blue-800', label: 'Processing' },
      completed: { icon: CheckCircle, class: 'bg-green-100 text-green-800', label: 'Completed' },
      failed: { icon: XCircle, class: 'bg-red-100 text-red-800', label: 'Failed' },
    };
    const badge = badges[status];
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${badge.class}`}>
        <Icon className="h-4 w-4" />
        {badge.label}
      </span>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">My CVs</h1>
          <p className="text-gray-600">Manage and analyze your uploaded resumes</p>
        </div>
        <Link
          to="/cv-analysis/upload"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Upload className="h-5 w-5" />
          Upload New CV
        </Link>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {cvs.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <h2 className="text-xl font-semibold mb-2">No CVs uploaded yet</h2>
          <p className="text-gray-600 mb-6">
            Upload your first CV to get started with AI-powered analysis
          </p>
          <Link
            to="/cv-analysis/upload"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Upload className="h-5 w-5" />
            Upload CV
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {cvs.map(cv => (
            <div key={cv.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <FileText className="h-10 w-10 text-blue-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-lg mb-1 truncate" title={cv.file_name}>
                      {cv.file_name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {formatFileSize(cv.file_size)} • {cv.file_type.toUpperCase()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="mb-4">{getStatusBadge(cv.status)}</div>

              <div className="text-sm text-gray-600 mb-4">
                <p>Uploaded: {formatDate(cv.uploaded_at)}</p>
                {cv.processed_at && (
                  <p>Processed: {formatDate(cv.processed_at)}</p>
                )}
              </div>

              {cv.error_message && (
                <div className="mb-4 p-2 bg-red-50 rounded text-sm text-red-600">
                  {cv.error_message}
                </div>
              )}

              <div className="flex gap-2">
                {cv.status === 'completed' && (
                  <Link
                    to={`/cv-analysis/cvs/${cv.id}`}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center text-sm font-medium"
                  >
                    View Analysis
                  </Link>
                )}
                
                {cv.status === 'failed' && (
                  <button
                    onClick={() => handleReprocess(cv.id)}
                    className="flex-1 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-center text-sm font-medium flex items-center justify-center gap-2"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Retry
                  </button>
                )}

                {(cv.status === 'pending' || cv.status === 'processing') && (
                  <div className="flex-1 px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-center text-sm font-medium">
                    Processing...
                  </div>
                )}

                <button
                  onClick={() => handleDelete(cv.id)}
                  disabled={deletingId === cv.id}
                  className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
                  title="Delete CV"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
