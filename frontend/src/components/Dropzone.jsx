import React, { useCallback } from 'react'

export default function Dropzone({ onFileSelect, label = "Upload Image" }) {
  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0])
    }
  }, [onFileSelect])

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0])
    }
  }

  return (
    <div 
      className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors cursor-pointer"
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      onClick={() => document.getElementById('fileInput').click()}
    >
      <input 
        type="file" 
        id="fileInput" 
        className="hidden" 
        accept="image/*" 
        onChange={handleChange} 
      />
      <p className="text-gray-600">{label}</p>
      <p className="text-sm text-gray-400 mt-2">Drag & drop or click to select</p>
    </div>
  )
}
