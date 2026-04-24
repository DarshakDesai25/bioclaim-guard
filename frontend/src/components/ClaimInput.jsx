import { Search, RotateCcw, Lightbulb, ChevronRight } from 'lucide-react'

export default function ClaimInput({ claim, setClaim, onVerify, onReset, examples, loading, hasResult }) {

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      onVerify()
    }
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
      <label className="block text-sm font-semibold text-slate-700 mb-2">
        Enter a medical claim to verify
      </label>

      <textarea
        value={claim}
        onChange={e => setClaim(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder='e.g. "Aspirin prevents heart attacks in all adults."'
        rows={3}
        disabled={loading}
        className="w-full border border-slate-200 rounded-xl px-4 py-3 text-slate-800 placeholder-slate-400
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                   resize-none text-sm disabled:opacity-50 disabled:bg-slate-50"
      />

      <div className="flex items-center justify-between mt-3 gap-3">
        <span className="text-xs text-slate-400">
          {claim.length}/1000 · Ctrl+Enter to submit
        </span>
        <div className="flex gap-2">
          {hasResult && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              New claim
            </button>
          )}
          <button
            onClick={() => onVerify()}
            disabled={loading || !claim.trim()}
            className="flex items-center gap-1.5 px-5 py-2 bg-blue-600 text-white text-sm font-medium
                       rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
                       transition-colors shadow-sm"
          >
            <Search className="w-3.5 h-3.5" />
            Verify Claim
          </button>
        </div>
      </div>

      {/* Example claims */}
      {examples.length > 0 && !hasResult && (
        <div className="mt-5 border-t border-slate-100 pt-4">
          <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500 mb-2.5">
            <Lightbulb className="w-3.5 h-3.5" />
            Try an example
          </div>
          <div className="flex flex-col gap-1.5">
            {examples.map((ex, i) => (
              <button
                key={i}
                onClick={() => onVerify(ex.claim)}
                className="flex items-center justify-between text-left px-3 py-2 rounded-lg
                           bg-slate-50 hover:bg-blue-50 hover:text-blue-700 border border-transparent
                           hover:border-blue-200 transition-all group"
              >
                <span className="text-xs text-slate-600 group-hover:text-blue-700">{ex.claim}</span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 ml-2 group-hover:text-blue-500" />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
