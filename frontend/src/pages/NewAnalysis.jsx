import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createAnalysis, searchJobs, pasteJobDescription, useCachedPosting, useIndustryBenchmark } from '../api/analyses';
import { Building2, Briefcase, Clock, Plus, Trash2, ArrowRight, AlertCircle, Info, Sparkles, FileText } from 'lucide-react';

const NewAnalysis = () => {
  const [companyName, setCompanyName] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [weeklyHours, setWeeklyHours] = useState(10);
  const [skills, setSkills] = useState([
    { name: 'Python', proficiency: 'intermediate' },
    { name: 'SQL', proficiency: 'beginner' },
  ]);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillProficiency, setNewSkillProficiency] = useState('beginner');
  const [jobDescription, setJobDescription] = useState('');
  const [jobSourceUrl, setJobSourceUrl] = useState('');
  const [showPasteOption, setShowPasteOption] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [progressStep, setProgressStep] = useState('');

  const navigate = useNavigate();

  const handleAddSkill = (e) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;

    // Avoid duplicate names in state
    if (skills.some((s) => s.name.toLowerCase() === newSkillName.trim().toLowerCase())) {
      setError(`Skill '${newSkillName.trim()}' is already added.`);
      return;
    }

    setSkills([...skills, { name: newSkillName.trim(), proficiency: newSkillProficiency }]);
    setNewSkillName('');
    setNewSkillProficiency('beginner');
    setError('');
  };

  const handleRemoveSkill = (indexToRemove) => {
    setSkills(skills.filter((_, idx) => idx !== indexToRemove));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!companyName.trim()) {
      setError('Please provide a target company name.');
      return;
    }
    if (!targetRole.trim()) {
      setError('Please provide a target job role.');
      return;
    }
    if (weeklyHours < 1 || weeklyHours > 100) {
      setError('Weekly study hours must be between 1 and 100 hours.');
      return;
    }

    setSubmitting(true);
    try {
      setProgressStep('Saving student parameters & self-reported skills...');
      const created = await createAnalysis({
        company_name: companyName.trim(),
        target_role: targetRole.trim(),
        weekly_hours: Number(weeklyHours),
        student_skills: skills,
      });

      if (jobDescription.trim().length >= 20) {
        setProgressStep(`Extracting evidence-backed requirements from provided ${companyName.trim()} description...`);
        await pasteJobDescription(created.id, {
          description_text: jobDescription.trim(),
          source_url: jobSourceUrl.trim() || undefined,
          job_title: targetRole.trim(),
        });
      } else {
        setProgressStep(`Searching live ATS sources (Greenhouse & Lever) for verified ${companyName.trim()} postings...`);
        const searchRes = await searchJobs(created.id);
        if (searchRes.status === 'company_not_verified') {
          if (searchRes.has_cached_snapshots) {
            setProgressStep(`Attaching verified ${companyName.trim()} archive posting...`);
            await useCachedPosting(created.id);
          } else if (searchRes.has_industry_benchmark) {
            setProgressStep(`Attaching standard industry competency framework for ${targetRole.trim()}...`);
            await useIndustryBenchmark(created.id);
          }
        }
      }

      navigate(`/analyses/${created.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initiate job search. Please try again.');
      setSubmitting(false);
      setProgressStep('');
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 sm:p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-extrabold text-slate-900">Start Job Skill Gap Analysis</h1>
          <p className="text-sm text-slate-600 mt-1">
            We query live, permitted source feeds to extract real requirements and compare with your current skills.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-start gap-3 text-xs text-rose-700">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {submitting && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-center gap-3 text-xs text-blue-800 animate-pulse">
            <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
            <span>{progressStep}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Target Company (Free text) */}
          <div>
            <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
              Target Company Name (Free Text)
            </label>
            <div className="relative">
              <Building2 className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="text"
                required
                disabled={submitting}
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g. Stripe, GitLab, Netflix, Cloudflare, TCS..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition"
              />
            </div>
            <p className="text-[11px] text-slate-500 mt-1.5 flex items-center gap-1">
              <Info className="w-3.5 h-3.5" />
              Never restricted to predefined company lists. We query live career feeds for the name you provide.
            </p>
          </div>

          {/* Target Role (Free text) */}
          <div>
            <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
              Target Job Role (Free Text)
            </label>
            <div className="relative">
              <Briefcase className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="text"
                required
                disabled={submitting}
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g. Backend Engineer, Data Analyst, Cloud DevOps..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition"
              />
            </div>
            <p className="text-[11px] text-slate-500 mt-1.5 flex items-center gap-1">
              <Info className="w-3.5 h-3.5" />
              No fixed dropdowns. Roles are matched against live job titles using explainable relevance rules.
            </p>
          </div>

          {/* Optional Direct Job Description Paste */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5">
            <button
              type="button"
              onClick={() => setShowPasteOption(!showPasteOption)}
              className="w-full flex items-center justify-between text-left text-xs font-bold text-blue-700 hover:text-blue-900 transition"
            >
              <div className="flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-blue-600" />
                <span>Have the job description from {companyName.trim() || 'the employer'}? (Optional: Paste it here)</span>
              </div>
              <span className="text-slate-400 font-normal">{showPasteOption ? '▲ Hide' : '▼ Show'}</span>
            </button>

            {showPasteOption && (
              <div className="mt-3 space-y-3 pt-3 border-t border-slate-200/60">
                <p className="text-[11px] text-slate-500">
                  Recommended for companies that don't host public feeds on Greenhouse or Lever (e.g. HCLTech, TCS, Infosys, Wipro, Accenture). Paste the description directly from their career page or LinkedIn.
                </p>
                <div>
                  <textarea
                    rows={4}
                    disabled={submitting}
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    placeholder="Paste job description or qualification requirements here..."
                    className="w-full p-2.5 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition"
                  />
                </div>
                <div>
                  <input
                    type="url"
                    disabled={submitting}
                    value={jobSourceUrl}
                    onChange={(e) => setJobSourceUrl(e.target.value)}
                    placeholder="Optional posting link (e.g. https://www.hcltech.com/careers/...)"
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Weekly Hours Study Budget */}
          <div>
            <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
              Weekly Study Availability (Hours/Week)
            </label>
            <div className="relative">
              <Clock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="number"
                min={1}
                max={100}
                required
                disabled={submitting}
                value={weeklyHours}
                onChange={(e) => setWeeklyHours(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition"
              />
            </div>
            <p className="text-[11px] text-slate-500 mt-1.5">
              Your personalized learning roadmap will strictly schedule within this weekly study limit.
            </p>
          </div>

          {/* Current Skills (Self-reported) */}
          <div className="pt-4 border-t border-slate-200">
            <h3 className="text-sm font-bold text-slate-900 mb-1">Your Current Skills & Self-Reported Proficiency</h3>
            <p className="text-xs text-slate-500 mb-4">
              Add the tools, languages, or frameworks you already know. We compare them against verified requirements.
            </p>

            <div className="flex flex-col sm:flex-row gap-2 mb-4">
              <input
                type="text"
                disabled={submitting}
                value={newSkillName}
                onChange={(e) => setNewSkillName(e.target.value)}
                placeholder="Skill name (e.g. React, PostgreSQL, Docker)"
                className="flex-1 px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition"
              />
              <select
                disabled={submitting}
                value={newSkillProficiency}
                onChange={(e) => setNewSkillProficiency(e.target.value)}
                className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition text-slate-700"
              >
                <option value="beginner">Beginner (Basic concept)</option>
                <option value="intermediate">Intermediate (Built projects)</option>
                <option value="advanced">Advanced (Production experience)</option>
              </select>
              <button
                type="button"
                onClick={handleAddSkill}
                disabled={submitting}
                className="inline-flex items-center justify-center gap-1.5 bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold px-4 py-2 rounded-xl transition"
              >
                <Plus className="w-4 h-4" />
                <span>Add Skill</span>
              </button>
            </div>

            {skills.length > 0 ? (
              <div className="space-y-2">
                {skills.map((s, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200/80 rounded-xl text-sm"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-800">{s.name}</span>
                      <span className="text-xs font-medium px-2 py-0.5 rounded-full capitalize bg-blue-50 text-blue-700 border border-blue-100">
                        {s.proficiency}
                      </span>
                    </div>
                    <button
                      type="button"
                      disabled={submitting}
                      onClick={() => handleRemoveSkill(idx)}
                      className="p-1 text-slate-400 hover:text-rose-600 transition"
                      title="Remove skill"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">No current skills added yet. You can still proceed.</p>
            )}
          </div>

          <div className="pt-6 border-t border-slate-200 flex justify-end">
            <button
              type="submit"
              disabled={submitting}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-xl shadow-md shadow-blue-200 transition disabled:opacity-50"
            >
              <span>{submitting ? 'Searching verified jobs...' : 'Search Jobs & Analyze Skill Gaps'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NewAnalysis;
