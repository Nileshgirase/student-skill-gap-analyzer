import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getAnalysis, runGapAnalysis, searchJobs } from '../api/analyses';
import { Building2, Briefcase, RefreshCw, MapPin, ExternalLink, Calendar, AlertTriangle, ArrowRight, BookOpen, Layers } from 'lucide-react';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import JobSourceCard from '../components/JobSourceCard';
import SkillCard from '../components/SkillCard';
import SkillGapChart from '../components/SkillGapChart';

const AnalysisResult = () => {
  const { analysisId } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [gapResult, setGapResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState('');
  const [error, setError] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getAnalysis(analysisId);
      setAnalysis(data);

      // If verified jobs are present, run/fetch the gap analysis
      if (data.job_snapshots && data.job_snapshots.length > 0) {
        try {
          const gap = await runGapAnalysis(analysisId);
          setGapResult(gap);
        } catch (gapErr) {
          console.warn('Gap analysis could not be auto-run:', gapErr);
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load analysis results.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [analysisId]);

  const handleRefreshJobs = async () => {
    setActionLoading('Re-querying verified source feeds...');
    try {
      await searchJobs(analysisId);
      await loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to refresh job postings.');
    } finally {
      setActionLoading('');
    }
  };

  if (loading) {
    return <LoadingState message="Fetching verified job snapshots and requirements..." />;
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <ErrorState message={error} onRetry={loadData} />
      </div>
    );
  }

  if (!analysis) return null;

  const hasJobs = analysis.job_snapshots && analysis.job_snapshots.length > 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Info Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            <Building2 className="w-4 h-4 text-blue-600" />
            <span>Target Employer & Role</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 flex items-center gap-2">
            <span>{analysis.target_role}</span>
            <span className="text-slate-400 font-normal">at</span>
            <span className="text-blue-600">{analysis.company_name}</span>
          </h1>
          <p className="text-xs text-slate-500 mt-2">
            Study budget: <strong>{analysis.weekly_hours} hrs/week</strong> • Verified postings analyzed: <strong>{analysis.job_snapshots?.length || 0}</strong>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleRefreshJobs}
            disabled={!!actionLoading}
            className="inline-flex items-center gap-1.5 text-xs font-semibold px-3.5 py-2 rounded-xl text-slate-700 bg-slate-100 hover:bg-slate-200 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${actionLoading ? 'animate-spin' : ''}`} />
            <span>{actionLoading ? 'Refreshing...' : 'Refresh Sources'}</span>
          </button>

          {hasJobs && (
            <Link
              to={`/analyses/${analysisId}/roadmap`}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-xl shadow-md shadow-blue-200 transition"
            >
              <BookOpen className="w-4 h-4" />
              <span>Personalized Roadmap</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>
      </div>

      {/* Honest Empty / Error States */}
      {!hasJobs && (
        <div className="bg-white border border-amber-200 rounded-2xl p-8 sm:p-12 text-center max-w-2xl mx-auto shadow-sm">
          <div className="w-16 h-16 bg-amber-50 rounded-2xl flex items-center justify-center text-amber-600 mx-auto mb-4">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">
            {analysis.status === 'company_not_verified'
              ? `No Verified Job Board Found for '${analysis.company_name}'`
              : analysis.status === 'no_matching_jobs'
              ? `No Postings Matched '${analysis.target_role}' at ${analysis.company_name}`
              : `Job Sources Currently Unavailable`}
          </h2>
          <p className="text-sm text-slate-600 mt-2 max-w-lg mx-auto leading-relaxed">
            {analysis.status === 'company_not_verified' &&
              `We queried permitted public job feeds (Greenhouse and Lever), but no accessible board could be verified for '${analysis.company_name}'. In accordance with system principles, we never invent or fabricate job requirements.`}
            {analysis.status === 'no_matching_jobs' &&
              `The public job board was verified, but no open postings sufficiently matched the target role '${analysis.target_role}'. Try broadening the role title.`}
            {analysis.status === 'source_unavailable' &&
              `The upstream career feeds timed out or were temporarily unreachable. Please retry shortly.`}
          </p>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={handleRefreshJobs}
              className="inline-flex items-center gap-1.5 text-xs font-semibold px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-sm transition"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry Search</span>
            </button>
            <Link
              to="/new-analysis"
              className="inline-flex items-center gap-1.5 text-xs font-semibold px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition"
            >
              <span>Adjust Company / Role</span>
            </Link>
          </div>
        </div>
      )}

      {/* Verified Jobs and Skill Gaps Results */}
      {hasJobs && (
        <>
          {/* Skill Coverage Metric Chart */}
          {gapResult && <SkillGapChart gapResult={gapResult} />}

          {/* Tabular / Card Layout for Gaps & Postings */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left 2 Cols: Extracted Skills & Gap Comparison */}
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                    <Layers className="w-5 h-5 text-blue-600" />
                    <span>Evidence-Backed Skill Comparison</span>
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Every requirement is extracted with its supporting quote from the verified job description.
                  </p>
                </div>
              </div>

              {gapResult?.skill_gaps && gapResult.skill_gaps.length > 0 ? (
                <div className="grid grid-cols-1 gap-4">
                  {gapResult.skill_gaps.map((skill, idx) => (
                    <SkillCard key={idx} skill={skill} />
                  ))}
                </div>
              ) : (
                <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-sm text-slate-500">
                  No verified technical skills could be extracted with high confidence from the fetched descriptions.
                </div>
              )}

              {/* Additional Student Skills Not Found in Requirements */}
              {gapResult?.additional_skills && gapResult.additional_skills.length > 0 && (
                <div className="mt-8 pt-6 border-t border-slate-200">
                  <h3 className="text-sm font-bold text-slate-800 mb-2">Additional Skills You Reported</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {gapResult.additional_skills.map((add, idx) => (
                      <SkillCard key={idx} skill={add} />
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right 1 Col: Verified Source Job Postings */}
            <div className="space-y-4">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Verified Job Postings ({analysis.job_snapshots.length})</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Sources verified through official public ATS feeds.
                </p>
              </div>

              <div className="space-y-4">
                {analysis.job_snapshots.map((job) => (
                  <JobSourceCard key={job.id} job={job} />
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AnalysisResult;
