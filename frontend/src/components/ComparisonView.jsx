import React, { useEffect, useRef, useState } from 'react'

export default function ComparisonView({ originalUrl, processedUrl, signalMapUrl, metrics }) {
  const [viewMode, setViewMode] = useState('processed')
  const canvasRef = useRef(null)

  useEffect(() => {
    if (viewMode !== 'diff' || !originalUrl || !processedUrl || !canvasRef.current) return

    const img1 = new Image()
    const img2 = new Image()
    let loaded = 0

    const drawDiff = () => {
      const canvas = canvasRef.current
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      
      canvas.width = img1.width
      canvas.height = img1.height
      
      const c1 = document.createElement('canvas')
      const c2 = document.createElement('canvas')
      c1.width = c2.width = img1.width
      c1.height = c2.height = img1.height
      
      const ctx1 = c1.getContext('2d')
      const ctx2 = c2.getContext('2d')
      
      ctx1.drawImage(img1, 0, 0)
      ctx2.drawImage(img2, 0, 0)
      
      const d1 = ctx1.getImageData(0, 0, img1.width, img1.height)
      const d2 = ctx2.getImageData(0, 0, img1.width, img1.height)
      const diff = ctx.createImageData(img1.width, img1.height)
      
      // Calculate absolute difference amplified by 10x
      for (let i = 0; i < d1.data.length; i += 4) {
        diff.data[i] = Math.abs(d1.data[i] - d2.data[i]) * 10
        diff.data[i+1] = Math.abs(d1.data[i+1] - d2.data[i+1]) * 10
        diff.data[i+2] = Math.abs(d1.data[i+2] - d2.data[i+2]) * 10
        diff.data[i+3] = 255 // Alpha
      }
      
      ctx.putImageData(diff, 0, 0)
    }

    img1.onload = () => { loaded++; if(loaded === 2) drawDiff() }
    img2.onload = () => { loaded++; if(loaded === 2) drawDiff() }
    
    img1.crossOrigin = "Anonymous"
    img2.crossOrigin = "Anonymous"
    
    img1.src = originalUrl
    img2.src = processedUrl

  }, [originalUrl, processedUrl, viewMode])

  return (
    <div className="space-y-8">
      <div className="flex justify-center">
          <div className="bg-slate-100 p-1 rounded-xl flex">
            {['processed', 'diff', 'signal'].map(mode => {
                if (mode === 'signal' && !signalMapUrl) return null
                return (
                    <button
                        key={mode}
                        onClick={() => setViewMode(mode)}
                        className={`
                            px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 capitalize
                            ${viewMode === mode 
                                ? 'bg-white text-blue-600 shadow-sm' 
                                : 'text-slate-500 hover:text-slate-700'}
                        `}
                    >
                        {mode === 'processed' ? 'Watermarked Result' : mode === 'diff' ? 'Difference Map' : 'Signal Map'}
                    </button>
                )
            })}
          </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-3">
          <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider text-center">Original</h4>
          <div className="rounded-2xl overflow-hidden border border-slate-200 shadow-sm bg-slate-50 aspect-auto relative group">
              <img src={originalUrl} alt="Original" className="w-full h-full object-contain" />
          </div>
        </div>
        
        <div className="space-y-3">
          <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider text-center">
            {viewMode === 'processed' ? 'Watermarked' : viewMode === 'diff' ? 'Difference Analysis' : 'HVS Signal Map'}
          </h4>
          <div className="rounded-2xl overflow-hidden border border-slate-200 shadow-sm bg-slate-50 aspect-auto relative group">
              {viewMode === 'processed' && (
                <img src={processedUrl} alt="Watermarked" className="w-full h-full object-contain" />
              )}
              {viewMode === 'diff' && (
                <canvas ref={canvasRef} className="w-full h-full object-contain bg-black/90" />
              )}
              {viewMode === 'signal' && (
                <img src={signalMapUrl} alt="Signal Map" className="w-full h-full object-contain" />
              )}
          </div>
        </div>
      </div>

      {metrics && (
        <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
          <h4 className="text-sm font-bold text-slate-700 mb-4 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
            </svg>
            Quality Metrics
          </h4>
          <div className="grid grid-cols-2 gap-8">
            <div className="relative pl-4 border-l-2 border-blue-500">
                <div className="text-xs text-slate-500 font-medium">PSNR (Peak Signal-to-Noise Ratio)</div>
                <div className="text-2xl font-mono font-bold text-slate-800 mt-1">{metrics.psnr} <span className="text-sm text-slate-400 font-normal">dB</span></div>
                <div className="text-xs text-slate-400 mt-1">Higher is better (&gt;30dB is good)</div>
            </div>
            <div className="relative pl-4 border-l-2 border-emerald-500">
                <div className="text-xs text-slate-500 font-medium">SSIM (Structural Similarity)</div>
                <div className="text-2xl font-mono font-bold text-slate-800 mt-1">{metrics.ssim}</div>
                <div className="text-xs text-slate-400 mt-1">Max 1.0 (1.0 = identical)</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}