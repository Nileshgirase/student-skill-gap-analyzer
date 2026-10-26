import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listAnalyses, deleteAnalysis } from '../api/analyses';
import { PlusCircle, Search, Trash2, ArrowRight, Building2, Briefcase, Clock, Calendar, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

const Dashboard = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  const fetchAnalyses = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listAnalyses();
      setAnalyses(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load your analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const handleDelete = async (id, e) => {
    e.preventDefault();
    if (!window.confirm('Are you sure you want to delete this analysis? All associated job snapshots, skills, and roadmaps will be removed.')) {
      return;
    }

    setDeletingId(id);
    try {
      await deleteAnalysis(id);
      setAnalyses(analyses.filter((item) => item.id !== id));
    } catch {
      alert('Failed to delete analysis. Please try again.');
    } finally {
      setDeletingId(null);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'analysis_complete':
      case 'verified_jobs_found':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle className="w-3.5 h-3.5" /> Verified Data
          </span>
        );
      case 'archived_jobs_found':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
            <CheckCircle className="w-3.5 h-3.5" /> Archived Data
          </span>
        );
      case 'company_not_verified':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
            <AlertCircle className="w-3.5 h-3.5" /> Private ATS (Action Ready)
          </span>
        );
      case 'no_matching_jobs':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
            <AlertCircle className="w-3.5 h-3.5" /> No Matching Openings
          </span>
        );
      case 'searching':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 animate-pulse">
            Searching Sources...
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
            Pending Search
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">Student Dashboard</h1>
          <p className="text-sm text-slate-600 mt-1">
            Track verified job requirements, skill gaps, and learning roadmaps.
          </p>
        </div>
        <Link
          to="/new-analysis"
          className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2.5 rounded-xl shadow-md shadow-blue-200 transition"
        >
          <PlusCircle className="w-5 h-5" />
          <span>New Job Analysis</span>
        </Link>
      </div>

      {loading && <LoadingState message="Loading your analysis portfolio..." />}
      {error && <ErrorState message={error} onRetry={fetchAnalyses} />}

      {!loading && !error && analyses.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center max-w-xl mx-auto shadow-sm">
          <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600 mx-auto mb-4">
            <Search className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">No Job Analyses Yet</h3>
          <p className="text-sm text-slate-600 mt-2 max-w-md mx-auto">
            Enter a company name and target role to search real job descriptions, verify required skills with text evidence, and build your personalized study roadmap.
          </p>
          <Link
            to="/new-analysis"
            className="mt-6 inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-5 py-2.5 rounded-xl shadow-md shadow-blue-200 transition"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Start Your First Analysis</span>
          </Link>
        </div>
      )}

      {!loading && !error && analyses.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {analyses.map((item) => (
            <div
              key={item.id}
              className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700">
                    <Building2 className="w-4 h-4 text-blue-600" />
                    <span>{item.company_name}</span>
                  </div>
                  <div>{getStatusBadge(item.status)}</div>
                </div>

                <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2 mb-3">
                  <Briefcase className="w-4 h-4 text-slate-400 shrink-0" />
                  <span>{item.target_role}</span>
                </h3>

                <div className="space-y-1.5 text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1 text-slate-500">
                      <Clock className="w-3.5 h-3.5" /> Study commitment:
                    </span>
                    <span className="font-semibold text-slate-800">{item.weekly_hours} hrs/week</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Self-reported skills:</span>
                    <span className="font-semibold text-slate-800">{item.skill_count} skills</span>
                  </div>
                  <div className="flex items-center justify-between pt-1 border-t border-slate-200/60">
                    <span className="flex items-center gap-1 text-slate-400">
                      <Calendar className="w-3 h-3" /> Created:
                    </span>
                    <span className="text-slate-500">
                      {new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between gap-2">
                <button
                  onClick={(e) => handleDelete(item.id, e)}
                  disabled={deletingId === item.id}
                  className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                  title="Delete analysis"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <div className="flex items-center gap-2">
                  {item.status === 'company_not_verified' ? (
                    <Link
                      to={`/analyses/${item.id}`}
                      className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg text-emerald-800 bg-emerald-100 hover:bg-emerald-200 transition"
                      title="This employer uses a private career portal; click to apply verified benchmark or archive"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Resolve Requirements</span>
                    </Link>
                  ) : (
                    <Link
                      to={`/analyses/${item.id}/roadmap`}
                      className="text-xs font-semibold px-3 py-1.5 rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 transition"
                    >
                      Roadmap
                    </Link>
                  )}
                  <Link
                    to={`/analyses/${item.id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition"
                  >
                    <span>View Analysis</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
