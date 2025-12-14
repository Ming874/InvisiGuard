import React, { useState, useRef, useEffect } from 'react'

export default function AttackSimulator({ imageUrl, onExport }) {
  const [rotation, setRotation] = useState(0)
  const [scale, setScale] = useState(1)
  const canvasRef = useRef(null)

  useEffect(() => {
    if (!imageUrl || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    const img = new Image()
    
    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height
      
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Center pivot
      ctx.translate(canvas.width / 2, canvas.height / 2)
      ctx.rotate((rotation * Math.PI) / 180)
      ctx.scale(scale, scale)
      ctx.drawImage(img, -img.width / 2, -img.height / 2)
      ctx.setTransform(1, 0, 0, 1, 0, 0) // Reset
    }
    
    img.src = imageUrl
    img.crossOrigin = "Anonymous"
    
  }, [imageUrl, rotation, scale])

  const handleExport = () => {
    if (canvasRef.current) {
      canvasRef.current.toBlob(blob => {
        const file = new File([blob], "attacked.png", { type: "image/png" })
        onExport(file)
      })
    }
  }

  return (
    <div className="space-y-4 bg-white p-4 rounded shadow">
      <h3 className="font-semibold text-lg">Attack Simulator</h3>
      <div className="flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium">Rotation ({rotation}°)</label>
          <input 
            type="range" min="-45" max="45" value={rotation} 
            onChange={e => setRotation(Number(e.target.value))}
            className="w-full"
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium">Scale ({scale}x)</label>
          <input 
            type="range" min="0.5" max="1.5" step="0.1" value={scale} 
            onChange={e => setScale(Number(e.target.value))}
            className="w-full"
          />
        </div>
      </div>
      
      <div className="border rounded overflow-hidden bg-gray-100 flex justify-center">
        <canvas ref={canvasRef} className="max-w-full max-h-[400px]" />
      </div>
      
      <button 
        onClick={handleExport}
        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 w-full font-medium"
      >
        Use as Suspect Image
      </button>
    </div>
  )
}
