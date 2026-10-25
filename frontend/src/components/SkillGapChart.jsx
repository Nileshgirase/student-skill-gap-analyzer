import React from 'react';
import { Target, CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

const SkillGapChart = ({ gapResult }) => {
  const coverage = gapResult.coverage_percentage;
  const total = gapResult.unique_required_count || 0;
  const covered = gapResult.covered_required_count || 0;
  const needsImprovement = gapResult.needs_improvement_count || 0;
  const missing = gapResult.missing_required_count || 0;

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm mb-8">
      <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-6">
          {/* Circular progress visual */}
          <div className="relative w-28 h-28 flex items-center justify-center shrink-0">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-slate-100"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className={coverage !== null && coverage >= 70 ? 'text-emerald-500' : coverage !== null && coverage >= 40 ? 'text-blue-500' : 'text-amber-500'}
                strokeDasharray={`${coverage !== null ? coverage : 0}, 100`}
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-2xl font-extrabold text-slate-900">
                {coverage !== null ? `${Math.round(coverage)}%` : 'N/A'}
              </span>
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Coverage</span>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-600" />
              <span>Verified Skill Coverage</span>
            </h3>
            <p className="text-sm text-slate-600 max-w-xl mt-1 leading-relaxed">
              {gapResult.coverage_explanation}
            </p>
          </div>
        </div>

        {/* Breakdown counters */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full lg:w-auto">
          <div className="bg-slate-50 border border-slate-200/60 rounded-xl p-3 text-center">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Required</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{total}</div>
          </div>
          <div className="bg-emerald-50/60 border border-emerald-200/60 rounded-xl p-3 text-center">
            <div className="flex items-center justify-center gap-1 text-xs font-semibold text-emerald-700 uppercase tracking-wider">
              <CheckCircle2 className="w-3.5 h-3.5" /> Covered
            </div>
            <div className="text-2xl font-bold text-emerald-700 mt-1">{covered}</div>
          </div>
          <div className="bg-amber-50/60 border border-amber-200/60 rounded-xl p-3 text-center">
            <div className="flex items-center justify-center gap-1 text-xs font-semibold text-amber-700 uppercase tracking-wider">
              <AlertTriangle className="w-3.5 h-3.5" /> Practice
            </div>
            <div className="text-2xl font-bold text-amber-700 mt-1">{needsImprovement}</div>
          </div>
          <div className="bg-rose-50/60 border border-rose-200/60 rounded-xl p-3 text-center">
            <div className="flex items-center justify-center gap-1 text-xs font-semibold text-rose-700 uppercase tracking-wider">
              <XCircle className="w-3.5 h-3.5" /> Missing
            </div>
            <div className="text-2xl font-bold text-rose-700 mt-1">{missing}</div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2 text-xs text-slate-500">
        <Info className="w-4 h-4 text-slate-400 shrink-0" />
        <span>
          <strong>Non-negotiable principle:</strong> Coverage is an explanatory estimate based on student self-assessment and extracted job description evidence, not a hiring probability or employment guarantee.
        </span>
      </div>
    </div>
  );
};

export default SkillGapChart;
