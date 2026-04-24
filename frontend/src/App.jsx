import { useState, useEffect } from 'react'
import Header from './components/Header'
import ClaimInput from './components/ClaimInput'
import ResultCard from './components/ResultCard'
import LoadingState from './components/LoadingState'
import { verifyClaim, getExamples } from './api/client'

export default function App() {
  const [claim, setClaim]         = useState('')
  const [result, setResult]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [examples, setExamples]   = useState([])
  const [history, setHistory]     = useState([])

  useEffect(() => {
    getExamples()
      .then(data => setExamples(data.examples || []))
      .catch(() => {}) // Fail silently
  }, [])

  const handleVerify = async (claimText) => {
    const text = (claimText || claim).trim()
    if (!text) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await verifyClaim(text)
      setResult(data)
      setHistory(prev => [data, ...prev].slice(0, 10))
    } catch (err) {
      const msg = err.response?.data?.error || 'Something went wrong. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    setClaim('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <Header />

      <main className="max-w-4xl mx-auto px-4 py-10">

        {/* Hero */}
        {!result && !loading && (
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold text-slate-800 mb-3">
              Is this medical claim <span className="text-blue-600">evidence-based</span>?
            </h1>
            <p className="text-slate-500 text-lg max-w-2xl mx-auto">
              BioClaim Guard retrieves peer-reviewed PubMed studies and applies the PICO framework
              to classify medical claims as supported, misleading, contradicted, or unverifiable.
            </p>
          </div>
        )}

        {/* Input */}
        <ClaimInput
          claim={claim}
          setClaim={setClaim}
          onVerify={handleVerify}
          onReset={handleReset}
          examples={examples}
          loading={loading}
          hasResult={!!result}
        />

        {/* Error */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Loading */}
        {loading && <LoadingState />}

        {/* Result */}
        {result && !loading && <ResultCard result={result} />}

        {/* History */}
        {history.length > 1 && !loading && (
          <section className="mt-12">
            <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">
              Recent Verifications
            </h2>
            <div className="space-y-2">
              {history.slice(1).map((item, i) => (
                <button
                  key={i}
                  onClick={() => setResult(item)}
                  className="w-full text-left p-3 bg-white rounded-lg border border-slate-200 hover:border-blue-300 hover:shadow-sm transition-all"
                >
                  <div className="flex items-center gap-3">
                    <VerdictDot color={item.verdict_color} />
                    <span className="text-slate-700 text-sm truncate">{item.claim}</span>
                    <span className="ml-auto text-xs text-slate-400 whitespace-nowrap">{item.classification}</span>
                  </div>
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Footer disclaimer */}
        <p className="text-center text-xs text-slate-400 mt-16 pb-8">
          BioClaim Guard is a research tool and does not provide medical advice.
          Always consult a qualified healthcare professional for medical decisions.
        </p>
      </main>
    </div>
  )
}

function VerdictDot({ color }) {
  const colors = {
    green:  'bg-emerald-400',
    yellow: 'bg-amber-400',
    red:    'bg-red-400',
    gray:   'bg-slate-400',
  }
  return <span className={`inline-block w-2.5 h-2.5 rounded-full flex-shrink-0 ${colors[color] || colors.gray}`} />
}
