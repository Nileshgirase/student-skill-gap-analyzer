import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getRoadmap, createRoadmap, updateRoadmapItemStatus } from '../api/roadmap';
import { BookOpen, Calendar, Clock, ExternalLink, CheckCircle2, Circle, Clock3, RotateCcw, ArrowLeft, Sparkles } from 'lucide-react';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

const Roadmap = () => {
  const { analysisId } = useParams();
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  const loadRoadmap = async () => {
    setLoading(true);
    setError('');
    try {
      let data = await getRoadmap(analysisId);
      // If no roadmap items exist yet, generate them automatically
      if (!data.items || data.items.length === 0) {
        data = await createRoadmap(analysisId);
      }
      setRoadmap(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load personalized roadmap.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoadmap();
  }, [analysisId]);

  const handleRegenerate = async () => {
    if (!window.confirm('Re-generating will re-schedule tasks based on the latest verified gaps. Continue?')) {
      return;
    }
    setGenerating(true);
    try {
      const data = await createRoadmap(analysisId);
      setRoadmap(data);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to re-generate roadmap.');
    } finally {
      setGenerating(false);
    }
  };

  const handleStatusChange = async (itemId, newStatus) => {
    setUpdatingId(itemId);
    try {
      const updated = await updateRoadmapItemStatus(itemId, newStatus);
      setRoadmap({
        ...roadmap,
        items: roadmap.items.map((it) => (it.id === itemId ? updated : it)),
      });
    } catch {
      alert('Failed to update task progress. Please try again.');
    } finally {
      setUpdatingId(null);
    }
  };

  if (loading) {
    return <LoadingState message="Synthesizing personalized learning roadmap and verified resources..." />;
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <ErrorState message={error} onRetry={loadRoadmap} />
      </div>
    );
  }

  if (!roadmap) return null;

  // Group items by week number
  const itemsByWeek = (roadmap.items || []).reduce((acc, item) => {
    acc[item.week_number] = acc[item.week_number] || [];
    acc[item.week_number].push(item);
    return acc;
  }, {});

  const sortedWeeks = Object.keys(itemsByWeek).map(Number).sort((a, b) => a - b);
  const completedCount = roadmap.items.filter((it) => it.status === 'completed').length;
  const progressPercent = roadmap.items.length > 0 ? Math.round((completedCount / roadmap.items.length) * 100) : 0;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Link
              to={`/analyses/${analysisId}`}
              className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800 transition"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Analysis</span>
            </Link>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 flex items-center gap-2.5">
            <BookOpen className="w-7 h-7 text-blue-600" />
            <span>Personalized Learning Roadmap</span>
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Targeting <strong>{roadmap.target_role}</strong> at <strong>{roadmap.company_name}</strong> • Budget: <strong>{roadmap.weekly_hours_budget} hrs/week</strong>
          </p>
        </div>

        <button
          onClick={handleRegenerate}
          disabled={generating}
          className="inline-flex items-center gap-1.5 text-xs font-semibold px-4 py-2 rounded-xl text-slate-700 bg-slate-100 hover:bg-slate-200 transition disabled:opacity-50"
        >
          <RotateCcw className={`w-3.5 h-3.5 ${generating ? 'animate-spin' : ''}`} />
          <span>{generating ? 'Re-synthesizing...' : 'Re-generate Plan'}</span>
        </button>
      </div>

      {/* Progress & Overview Metric Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Plan Duration</div>
          <div className="text-2xl font-extrabold text-slate-900 mt-1 flex items-center gap-1.5">
            <Calendar className="w-5 h-5 text-blue-600" />
            <span>{roadmap.total_weeks} Weeks</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Bounded within {roadmap.weekly_hours_budget} hrs/week</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total Effort</div>
          <div className="text-2xl font-extrabold text-slate-900 mt-1 flex items-center gap-1.5">
            <Clock className="w-5 h-5 text-indigo-600" />
            <span>{roadmap.total_estimated_hours} Hours</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Free open courseware resources</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">Completion Progress</div>
          <div className="text-2xl font-extrabold text-emerald-600 mt-1 flex items-center gap-1.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            <span>{progressPercent}%</span>
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-2">
            <div className="bg-emerald-500 h-full transition-all duration-300" style={{ width: `${progressPercent}%` }} />
          </div>
        </div>
      </div>

      {/* Week-by-Week Learning Tasks */}
      {sortedWeeks.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center text-slate-500">
          No learning tasks generated. Either all required skills are already covered or no verified gaps exist.
        </div>
      ) : (
        <div className="space-y-8">
          {sortedWeeks.map((weekNum) => {
            const weekTasks = itemsByWeek[weekNum] || [];
            const weekHours = weekTasks.reduce((sum, t) => sum + t.estimated_hours, 0);

            return (
              <div key={weekNum} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
                  <div className="flex items-center gap-3">
                    <span className="w-8 h-8 rounded-lg bg-blue-600 text-white font-extrabold text-sm flex items-center justify-center shadow-sm shadow-blue-200">
                      W{weekNum}
                    </span>
                    <h2 className="text-lg font-bold text-slate-900">Week {weekNum} Curriculum</h2>
                  </div>
                  <div className="flex items-center gap-1 text-xs font-semibold text-slate-600 bg-slate-100 px-3 py-1 rounded-full">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{weekHours.toFixed(1)} / {roadmap.weekly_hours_budget} hrs planned</span>
                  </div>
                </div>

                <div className="space-y-4">
                  {weekTasks.map((task) => (
                    <div
                      key={task.id}
                      className={`p-4 rounded-xl border transition ${
                        task.status === 'completed'
                          ? 'bg-emerald-50/40 border-emerald-200'
                          : task.status === 'in_progress'
                          ? 'bg-blue-50/40 border-blue-200'
                          : 'bg-slate-50/60 border-slate-200/70 hover:border-slate-300'
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                              {task.skill_name}
                            </span>
                            <span className="text-xs text-slate-500 flex items-center gap-1 font-medium">
                              <Clock className="w-3 h-3" /> ~{task.estimated_hours}h estimated
                            </span>
                          </div>

                          <h3 className="text-base font-bold text-slate-900 mt-1">{task.resource_title}</h3>
                          <p className="text-xs text-slate-600 mt-1 leading-relaxed">{task.learning_goal}</p>

                          <div className="mt-3 flex flex-wrap items-center gap-4 text-xs">
                            <span className="text-slate-500 font-medium">
                              Provider: <strong className="text-slate-700">{task.resource_provider}</strong>
                            </span>
                            {task.resource_url && (
                              <a
                                href={task.resource_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold"
                              >
                                <span>Open Verified Free Resource</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                        </div>

                        {/* Interactive Status Controls */}
                        <div className="shrink-0 flex items-center gap-1.5 pt-2 sm:pt-0">
                          <select
                            disabled={updatingId === task.id}
                            value={task.status}
                            onChange={(e) => handleStatusChange(task.id, e.target.value)}
                            className={`text-xs font-semibold px-2.5 py-1.5 rounded-lg border focus:outline-none transition ${
                              task.status === 'completed'
                                ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                                : task.status === 'in_progress'
                                ? 'bg-blue-100 text-blue-800 border-blue-300'
                                : 'bg-white text-slate-700 border-slate-300'
                            }`}
                          >
                            <option value="not_started">⚪ Not Started</option>
                            <option value="in_progress">🔵 In Progress</option>
                            <option value="completed">🟢 Completed</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Roadmap;
