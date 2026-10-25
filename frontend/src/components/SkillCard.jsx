import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Sparkles, HelpCircle, ChevronDown, ChevronUp, Quote } from 'lucide-react';

const SkillCard = ({ skill }) => {
  const [showEvidence, setShowEvidence] = useState(false);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'self_reported_covered':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" /> Covered
          </span>
        );
      case 'needs_improvement':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="w-3.5 h-3.5" /> Needs Practice
          </span>
        );
      case 'missing':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <XCircle className="w-3.5 h-3.5" /> Missing
          </span>
        );
      case 'additional_skill':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <Sparkles className="w-3.5 h-3.5" /> Additional Skill
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-50 text-slate-700 border border-slate-200">
            <HelpCircle className="w-3.5 h-3.5" /> Uncertain
          </span>
        );
    }
  };

  const getRequirementBadge = (type) => {
    switch (type) {
      case 'required':
        return <span className="text-[11px] font-bold uppercase tracking-wider text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-100">Strictly Required</span>;
      case 'preferred':
        return <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">Preferred / Plus</span>;
      default:
        return <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600 bg-slate-100 px-2 py-0.5 rounded">Mentioned</span>;
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:border-slate-300 transition">
      <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
        <div>
          <h4 className="text-base font-bold text-slate-900">{skill.display_name}</h4>
          {skill.requirement_type && <div className="mt-1">{getRequirementBadge(skill.requirement_type)}</div>}
        </div>
        <div>{getStatusBadge(skill.status)}</div>
      </div>

      <p className="text-sm text-slate-600 mt-2">{skill.explanation}</p>

      {skill.student_proficiency && skill.student_proficiency !== 'none' && (
        <div className="mt-3 text-xs text-slate-500 flex items-center gap-1.5">
          <span className="font-semibold text-slate-700">Self-reported:</span>
          <span className="capitalize px-1.5 py-0.5 bg-slate-100 rounded text-slate-800">{skill.student_proficiency}</span>
        </div>
      )}

      {skill.evidence_text && (
        <div className="mt-3 pt-3 border-t border-slate-100">
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition"
          >
            <Quote className="w-3.5 h-3.5" />
            <span>{showEvidence ? 'Hide Source Evidence' : 'View Job Description Evidence'}</span>
            {showEvidence ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showEvidence && (
            <div className="mt-2 p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 italic leading-relaxed">
              "{skill.evidence_text}"
              {skill.source_employer && (
                <div className="not-italic text-[11px] font-semibold text-slate-500 mt-1.5 text-right">
                  — Verified from {skill.source_employer} Posting
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SkillCard;
