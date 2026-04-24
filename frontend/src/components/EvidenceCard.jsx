import { useState } from 'react'
import { ExternalLink, ChevronDown, ChevronUp, BookOpen } from 'lucide-react'

const STUDY_TYPE_COLORS = {
  'Meta-Analysis':              'bg-purple-100 text-purple-700',
  'Systematic Review':          'bg-violet-100 text-violet-700',
  'Randomized Controlled Trial':'bg-blue-100 text-blue-700',
  'Clinical Trial':             'bg-cyan-100 text-cyan-700',
  'Review':                     'bg-teal-100 text-teal-700',
  'Case Report':                'bg-amber-100 text-amber-700',
  'Observational Study':        'bg-slate-100 text-slate-600',
}

export default function EvidenceCard({ paper, index }) {
  const [expanded, setExpanded] = useState(false)
  const studyTypeClass = STUDY_TYPE_COLORS[paper.study_type] || STUDY_TYPE_COLORS['Observational Study']

  return (
    <div className="bg-white rounded-xl border border-slate-200 hover:border-blue-200 transition-all overflow-hidden">
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Index bubble */}
          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center">
            {index}
          </span>

          <div className="flex-1 min-w-0">
            {/* Title + link */}
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <h3 className="text-sm font-semibold text-slate-800 leading-snug">
                {paper.title}
              </h3>
              <a
                href={paper.url}
                target="_blank"
                rel="noreferrer"
                className="flex-shrink-0 text-blue-500 hover:text-blue-700 transition-colors"
                title="View on PubMed"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            {/* Meta row */}
            <div className="flex flex-wrap items-center gap-2 mb-2">
              {paper.study_type && (
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${studyTypeClass}`}>
                  {paper.study_type}
                </span>
              )}
              {paper.year && paper.year !== 'N/A' && (
                <span className="text-xs text-slate-500">{paper.year}</span>
              )}
              {paper.journal && (
                <span className="text-xs text-slate-400 italic truncate max-w-[180px]">
                  {paper.journal}
                </span>
              )}
            </div>

            {/* Authors */}
            {paper.authors && paper.authors.length > 0 && (
              <p className="text-xs text-slate-500 mb-2">
                <BookOpen className="inline w-3 h-3 mr-1" />
                {paper.authors.join(', ')}
              </p>
            )}

            {/* Abstract toggle */}
            {paper.abstract && paper.abstract !== 'Abstract not available.' && (
              <button
                onClick={() => setExpanded(e => !e)}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-medium transition-colors"
              >
                {expanded ? (
                  <><ChevronUp className="w-3.5 h-3.5" /> Hide abstract</>
                ) : (
                  <><ChevronDown className="w-3.5 h-3.5" /> Show abstract</>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Expandable abstract */}
        {expanded && paper.abstract && (
          <div className="mt-3 ml-9 p-3 bg-slate-50 rounded-lg text-xs text-slate-700 leading-relaxed border border-slate-100">
            {paper.abstract}
          </div>
        )}
      </div>

      {/* PMID footer */}
      <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
        <span className="text-xs text-slate-400">PMID: {paper.pmid}</span>
        <a
          href={paper.url}
          target="_blank"
          rel="noreferrer"
          className="text-xs text-blue-500 hover:text-blue-700 font-medium"
        >
          View on PubMed →
        </a>
      </div>
    </div>
  )
}
