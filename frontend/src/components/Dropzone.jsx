import React, { useCallback, useRef, useState } from 'react'

const UploadIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" x2="12" y1="3" y2="15" />
    </svg>
)

export default function Dropzone({ onFileSelect, label = "Upload Image" }) {
  const fileInputRef = useRef(null)
  const [isDragActive, setIsDragActive] = useState(false)
  
  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0])
    }
  }, [onFileSelect])

  const handleDragOver = (e) => {
      e.preventDefault()
      setIsDragActive(true)
  }

  const handleDragLeave = (e) => {
      e.preventDefault()
      setIsDragActive(false)
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0])
    }
  }

  const handleClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  return (
    <div 
      className={`
        relative group cursor-pointer transition-all duration-300 ease-in-out
        border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center
        ${isDragActive 
            ? 'border-blue-500 bg-blue-50 scale-[1.02]' 
            : 'border-slate-300 hover:border-blue-400 hover:bg-slate-50'}
      `}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={handleClick}
    >
      <input 
        type="file" 
        ref={fileInputRef}
        className="hidden" 
        accept="image/*" 
        onChange={handleChange} 
      />
      
      <div className={`
        p-4 rounded-full mb-3 transition-colors duration-300
        ${isDragActive ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-400 group-hover:text-blue-500 group-hover:bg-blue-50'}
      `}>
        <UploadIcon className="w-8 h-8" />
      </div>
      
      <p className={`font-medium transition-colors duration-300 ${isDragActive ? 'text-blue-700' : 'text-slate-700'}`}>
        {label}
      </p>
      <p className="text-sm text-slate-400 mt-1">
        Drag & drop or click to select
      </p>
    </div>
  )
}