const PICO_FIELDS = [
  {
    key: 'population',
    label: 'P — Population',
    description: 'Who is the claim about?',
    color: 'bg-violet-50 border-violet-200 text-violet-700',
    dot: 'bg-violet-400'
  },
  {
    key: 'intervention',
    label: 'I — Intervention',
    description: 'What treatment or exposure?',
    color: 'bg-blue-50 border-blue-200 text-blue-700',
    dot: 'bg-blue-400'
  },
  {
    key: 'comparison',
    label: 'C — Comparison',
    description: 'Compared to what?',
    color: 'bg-cyan-50 border-cyan-200 text-cyan-700',
    dot: 'bg-cyan-400'
  },
  {
    key: 'outcome',
    label: 'O — Outcome',
    description: 'What health effect is claimed?',
    color: 'bg-teal-50 border-teal-200 text-teal-700',
    dot: 'bg-teal-400'
  }
]

export default function PICOBreakdown({ pico }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-slate-700">PICO Framework Analysis</h2>
        {pico.claim_type && (
          <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full capitalize">
            {pico.claim_type}
          </span>
        )}
        {pico.scope && (
          <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${
            pico.scope === 'universal' ? 'bg-red-100 text-red-600' :
            pico.scope === 'general'   ? 'bg-amber-100 text-amber-600' :
                                         'bg-green-100 text-green-600'
          }`}>
            {pico.scope} scope
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {PICO_FIELDS.map(({ key, label, description, color, dot }) => (
          <div key={key} className={`p-3 rounded-xl border ${color}`}>
            <div className="flex items-center gap-2 mb-1">
              <span className={`w-2 h-2 rounded-full flex-shrink-0 ${dot}`} />
              <span className="text-xs font-semibold">{label}</span>
            </div>
            <p className="text-sm font-medium ml-4">
              {pico[key] || 'Not stated'}
            </p>
            <p className="text-xs opacity-60 ml-4 mt-0.5">{description}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
