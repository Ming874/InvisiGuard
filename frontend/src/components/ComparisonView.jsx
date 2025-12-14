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
      const ctx = canvas.getContext('2d')
      
      // Set dimensions
      canvas.width = img1.width
      canvas.height = img1.height
      
      // Draw images to offscreen canvases to get data
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
    <div className="space-y-6">
      <div className="flex justify-center space-x-4 mb-4">
        <button 
          onClick={() => setViewMode('processed')}
          className={`px-3 py-1 rounded ${viewMode === 'processed' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          Watermarked
        </button>
        <button 
          onClick={() => setViewMode('diff')}
          className={`px-3 py-1 rounded ${viewMode === 'diff' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          Diff Map
        </button>
        {signalMapUrl && (
          <button 
            onClick={() => setViewMode('signal')}
            className={`px-3 py-1 rounded ${viewMode === 'signal' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            Signal Map
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <h4 className="font-medium text-gray-700">Original</h4>
          <img src={originalUrl} alt="Original" className="w-full rounded shadow" />
        </div>
        <div className="space-y-2">
          <h4 className="font-medium text-gray-700">
            {viewMode === 'processed' ? 'Watermarked' : viewMode === 'diff' ? 'Difference Map' : 'Signal Map'}
          </h4>
          {viewMode === 'processed' && (
            <img src={processedUrl} alt="Watermarked" className="w-full rounded shadow" />
          )}
          {viewMode === 'diff' && (
            <canvas ref={canvasRef} className="w-full rounded shadow border bg-black" />
          )}
          {viewMode === 'signal' && (
            <img src={signalMapUrl} alt="Signal Map" className="w-full rounded shadow" />
          )}
        </div>
      </div>

      {metrics && (
        <div className="bg-gray-50 p-4 rounded border">
          <h4 className="font-medium mb-2">Quality Metrics</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>PSNR: <span className="font-mono font-bold">{metrics.psnr} dB</span></div>
            <div>SSIM: <span className="font-mono font-bold">{metrics.ssim}</span></div>
          </div>
        </div>
      )}
    </div>
  )
}
