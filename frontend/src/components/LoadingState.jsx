import { useState, useEffect } from 'react'
import { Search, Brain, FlaskConical, CheckCheck } from 'lucide-react'

const STEPS = [
  { icon: Brain,       label: 'Extracting PICO components…',        delay: 0    },
  { icon: Search,      label: 'Querying PubMed for evidence…',       delay: 2000 },
  { icon: FlaskConical,label: 'Retrieving peer-reviewed studies…',   delay: 5000 },
  { icon: CheckCheck,  label: 'Verifying claim against evidence…',   delay: 9000 },
]

export default function LoadingState() {
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    const timers = STEPS.slice(1).map((step, i) =>
      setTimeout(() => setActiveStep(i + 1), step.delay)
    )
    return () => timers.forEach(clearTimeout)
  }, [])

  return (
    <div className="mt-6 bg-white rounded-2xl border border-slate-200 p-8">
      <div className="flex flex-col items-center text-center mb-8">
        <div className="relative mb-4">
          <div className="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center">
            <div className="w-10 h-10 rounded-full border-4 border-blue-600 border-t-transparent animate-spin" />
          </div>
        </div>
        <h2 className="text-slate-800 font-semibold text-lg">Analyzing claim…</h2>
        <p className="text-slate-400 text-sm mt-1">This may take 15–30 seconds</p>
      </div>

      <div className="max-w-sm mx-auto space-y-3">
        {STEPS.map((step, i) => {
          const Icon = step.icon
          const isDone    = i < activeStep
          const isActive  = i === activeStep
          const isPending = i > activeStep

          return (
            <div
              key={i}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-500 ${
                isActive  ? 'bg-blue-50 border border-blue-200' :
                isDone    ? 'opacity-60' :
                            'opacity-30'
              }`}
            >
              <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                isDone   ? 'bg-emerald-100' :
                isActive ? 'bg-blue-100' :
                           'bg-slate-100'
              }`}>
                {isDone ? (
                  <span className="text-emerald-600 text-xs font-bold">✓</span>
                ) : (
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                )}
              </div>
              <span className={`text-sm ${
                isActive ? 'text-blue-700 font-medium' :
                isDone   ? 'text-slate-500' :
                           'text-slate-400'
              }`}>
                {step.label}
              </span>
              {isActive && (
                <div className="ml-auto flex gap-0.5">
                  {[0,1,2].map(j => (
                    <span
                      key={j}
                      className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce"
                      style={{ animationDelay: `${j * 0.15}s` }}
                    />
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
