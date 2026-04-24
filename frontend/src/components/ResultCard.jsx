import { CheckCircle2, AlertTriangle, XCircle, HelpCircle, Clock, Database } from 'lucide-react'
import PICOBreakdown from './PICOBreakdown'
import EvidenceCard from './EvidenceCard'

const VERDICT_CONFIG = {
  'Clinically Supported': {
    icon: CheckCircle2,
    bg: 'bg-emerald-50',
    border: 'border-emerald-300',
    text: 'text-emerald-800',
    badge: 'bg-emerald-100 text-emerald-700',
    iconColor: 'text-emerald-500'
  },
  'Misleading / Overgeneralized': {
    icon: AlertTriangle,
    bg: 'bg-amber-50',
    border: 'border-amber-300',
    text: 'text-amber-800',
    badge: 'bg-amber-100 text-amber-700',
    iconColor: 'text-amber-500'
  },
  'Contradicted': {
    icon: XCircle,
    bg: 'bg-red-50',
    border: 'border-red-300',
    text: 'text-red-800',
    badge: 'bg-red-100 text-red-700',
    iconColor: 'text-red-500'
  },
  'Insufficient Evidence': {
    icon: HelpCircle,
    bg: 'bg-slate-50',
    border: 'border-slate-300',
    text: 'text-slate-700',
    badge: 'bg-slate-100 text-slate-600',
    iconColor: 'text-slate-400'
  }
}

const CONFIDENCE_COLORS = {
  High:     'bg-emerald-100 text-emerald-700',
  Moderate: 'bg-amber-100 text-amber-700',
  Low:      'bg-red-100 text-red-700'
}

export default function ResultCard({ result }) {
  const classification = result.classification || 'Insufficient Evidence'
  const config = VERDICT_CONFIG[classification] || VERDICT_CONFIG['Insufficient Evidence']
  const Icon = config.icon

  return (
    <div className="mt-6 space-y-5">

      {/* ── Main verdict ───────────────────────────────────────────────── */}
      <div className={`rounded-2xl border-2 p-6 ${config.bg} ${config.border}`}>

        {/* Top row */}
        <div className="flex items-start gap-4">
          <Icon className={`w-8 h-8 flex-shrink-0 mt-0.5 ${config.iconColor}`} />
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className={`text-lg font-bold ${config.text}`}>{classification}</span>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${CONFIDENCE_COLORS[result.confidence] || CONFIDENCE_COLORS.Low}`}>
                {result.confidence || 'Low'} confidence
              </span>
              {result.evidence_quality && (
                <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">
                  {result.evidence_quality}
                </span>
              )}
            </div>
            <p className={`text-sm leading-relaxed ${config.text}`}>{result.explanation}</p>
          </div>
        </div>

        {/* Key issues */}
        {result.key_issues && result.key_issues.length > 0 && (
          <div className="mt-4 space-y-1.5">
            <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide">Issues detected</p>
            {result.key_issues.map((issue, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-slate-700">
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-slate-400 flex-shrink-0" />
                {issue}
              </div>
            ))}
          </div>
        )}

        {/* Recommendation */}
        {result.recommendation && (
          <div className="mt-4 p-3 bg-white/60 rounded-lg border border-white/80">
            <p className="text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1">Recommendation</p>
            <p className="text-sm text-slate-700">{result.recommendation}</p>
          </div>
        )}

        {/* Flags */}
        <div className="flex gap-3 mt-4 flex-wrap">
          <FlagBadge
            label="Population match"
            value={result.population_match}
            trueColor="emerald"
            falseColor="red"
          />
          <FlagBadge
            label="Effect exaggerated"
            value={result.effect_exaggerated}
            trueColor="red"
            falseColor="emerald"
            invert
          />
        </div>

        {/* Meta */}
        <div className="mt-4 pt-4 border-t border-white/50 flex gap-4 text-xs text-slate-500">
          {result.processing_time_ms && (
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {result.processing_time_ms}ms
            </span>
          )}
          {result.total_papers_retrieved !== undefined && (
            <span className="flex items-center gap-1">
              <Database className="w-3 h-3" />
              {result.total_papers_retrieved} papers retrieved
            </span>
          )}
          {result.query_used && (
            <span className="truncate max-w-xs">
              Query: "{result.query_used}"
            </span>
          )}
        </div>
      </div>

      {/* ── PICO breakdown ─────────────────────────────────────────────── */}
      {result.pico && <PICOBreakdown pico={result.pico} />}

      {/* ── Evidence cards ─────────────────────────────────────────────── */}
      {result.evidence && result.evidence.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Supporting Evidence ({result.evidence.length} studies)
          </h2>
          <div className="space-y-3">
            {result.evidence.map((paper, i) => (
              <EvidenceCard key={paper.pmid || i} paper={paper} index={i + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function FlagBadge({ label, value, trueColor, falseColor }) {
  const isTrue = !!value
  const color = isTrue ? trueColor : falseColor
  const colorMap = {
    emerald: 'bg-emerald-100 text-emerald-700',
    red:     'bg-red-100 text-red-700',
    amber:   'bg-amber-100 text-amber-700',
    slate:   'bg-slate-100 text-slate-600'
  }
  return (
    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${colorMap[color] || colorMap.slate}`}>
      {isTrue ? '✓' : '✗'} {label}
    </span>
  )
}
