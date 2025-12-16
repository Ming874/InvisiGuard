import React from 'react'

const MagicWandIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
        <polyline points="14 2 14 8 20 8" />
        <path d="m9 15 2 2 4-4" />
    </svg>
)

export default function ConfigPanel({ text, setText, alpha, setAlpha, onEmbed, loading }) {
    return (
        <div className="space-y-6">
            <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Watermark Text
                </label>
                <div className="relative">
                    <input
                        type="text"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        maxLength={32}
                        className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder-slate-400 text-slate-700"
                        placeholder="e.g., Copyright 2025"
                    />
                    <div className="absolute right-3 top-3 text-xs text-slate-400 font-medium bg-slate-100 px-2 py-0.5 rounded">
                        {text.length}/32
                    </div>
                </div>
            </div>

            <div>
                <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-semibold text-slate-700">
                        Strength (Alpha)
                    </label>
                    <span className="text-sm font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                        {alpha.toFixed(1)}
                    </span>
                </div>
                <input
                    type="range"
                    min="0.1"
                    max="5.0"
                    step="0.1"
                    value={alpha}
                    onChange={(e) => setAlpha(parseFloat(e.target.value))}
                    className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs font-medium text-slate-400 mt-2">
                    <span>Invisible (High Quality)</span>
                    <span>Robust (Resistant)</span>
                </div>
            </div>

            <button
                onClick={onEmbed}
                disabled={loading || !text}
                className={`
                    w-full py-3.5 px-4 rounded-xl font-bold text-lg shadow-lg transition-all duration-300 flex items-center justify-center gap-2
                    ${loading || !text
                        ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'
                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 hover:scale-[1.01] shadow-blue-600/30'}
                `}
            >
                {loading ? (
                    <>
                        <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Processing...
                    </>
                ) : (
                    <>
                        <MagicWandIcon className="w-5 h-5" />
                        Embed Watermark
                    </>
                )}
            </button>
        </div>
    )
}