import { ShieldCheck } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="bg-blue-600 p-1.5 rounded-lg">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-slate-800 text-lg leading-none">BioClaim</span>
            <span className="font-bold text-blue-600 text-lg leading-none"> Guard</span>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm text-slate-500">
          <a
            href="https://github.com/darshakdesai/bioclaim-guard"
            target="_blank"
            rel="noreferrer"
            className="hover:text-blue-600 transition-colors"
          >
            GitHub
          </a>
          <span className="hidden sm:inline px-2 py-0.5 bg-blue-50 text-blue-700 text-xs font-medium rounded-full">
            RAG + PICO + Claude
          </span>
        </div>
      </div>
    </header>
  )
}
