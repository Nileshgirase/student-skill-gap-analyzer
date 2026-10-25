import React from 'react';
import { ExternalLink, MapPin, Calendar, CheckCircle, AlertTriangle } from 'lucide-react';

const JobSourceCard = ({ job }) => {
  const formattedDate = job.fetched_at
    ? new Date(job.fetched_at).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : 'Recently';

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
              {job.source_name}
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
              {job.employer_name}
            </span>
            {job.is_stale && (
              <span className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded bg-amber-100 text-amber-800">
                <AlertTriangle className="w-3 h-3" /> Stale Posting
              </span>
            )}
          </div>
          <h3 className="text-lg font-bold text-slate-900">{job.job_title}</h3>
        </div>

        <a
          href={job.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition"
        >
          <span>View Original Source</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>

      <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 mt-3 pt-3 border-t border-slate-100">
        {job.location && (
          <div className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <span>{job.location}</span>
          </div>
        )}
        <div className="flex items-center gap-1">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <span>Fetched {formattedDate}</span>
        </div>
        <div className="flex items-center gap-1 text-emerald-600 font-medium">
          <CheckCircle className="w-3.5 h-3.5" />
          <span>Employer Relevance Verified</span>
        </div>
      </div>

      {job.verification_notes && (
        <div className="mt-2.5 text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
          <span className="font-semibold text-slate-700">Audit notes:</span> {job.verification_notes}
        </div>
      )}
    </div>
  );
};

export default JobSourceCard;
