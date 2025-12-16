import { useState, useEffect } from 'react'
import api from './services/api'
import Dropzone from './components/Dropzone'
import ConfigPanel from './components/ConfigPanel'
import ComparisonView from './components/ComparisonView'
import VerifyTab from './components/VerifyTab'
import { validateEmbedRequest } from './utils/validation'

// Icons
const ShieldCheckIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <path d="m9 12 2 2 4-4" />
    </svg>
)

const LockIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
)

const SearchIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.3-4.3" />
    </svg>
)

const EyeIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
        <circle cx="12" cy="12" r="3" />
    </svg>
)

const DownloadIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" x2="12" y1="15" y2="3" />
    </svg>
)

function App() {
    const [health, setHealth] = useState(null)
    const [activeTab, setActiveTab] = useState('embed')

    // Embed State
    const [file, setFile] = useState(null)
    const [text, setText] = useState('')
    const [alpha, setAlpha] = useState(1.0)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [originalPreview, setOriginalPreview] = useState(null)

    // Extract State
    const [extractOriginal, setExtractOriginal] = useState(null)
    const [extractSuspect, setExtractSuspect] = useState(null)
    const [extractResult, setExtractResult] = useState(null)
    const [extractOriginalPreview, setExtractOriginalPreview] = useState(null)
    const [extractSuspectPreview, setExtractSuspectPreview] = useState(null)

    const handleExtractOriginalSelect = (selectedFile) => {
        setExtractOriginal(selectedFile)
        setExtractOriginalPreview(URL.createObjectURL(selectedFile))
    }

    const handleExtractSuspectSelect = (selectedFile) => {
        setExtractSuspect(selectedFile)
        setExtractSuspectPreview(URL.createObjectURL(selectedFile))
    }

    useEffect(() => {
        api.get('/health')
            .then(res => setHealth(res.data))
            .catch(err => console.error(err))
    }, [])

    const handleEmbedFileSelect = (selectedFile) => {
        setFile(selectedFile)
        setOriginalPreview(URL.createObjectURL(selectedFile))
        setResult(null)
    }

    const handleEmbed = async () => {
        const validation = validateEmbedRequest(file, text, alpha)
        if (!validation.valid) {
            const errorMessage = validation.errors.join('\n')
            alert(`❌ Validation Error\n\n${errorMessage}`)
            return
        }

        setLoading(true)
        const formData = new FormData()
        formData.append('file', file)
        formData.append('text', text.trim())
        formData.append('alpha', alpha)

        try {
            const res = await api.post('/embed', formData)
            setResult(res.data.data)
        } catch (err) {
            console.error(err)
            if (err.response?.data?.message) {
                const errorData = err.response.data
                const errorMessage = `❌ ${errorData.message}\n\n${errorData.suggestion || 'Please try again.'}`
                alert(errorMessage)
            } else {
                alert('❌ Error embedding watermark. Please check the console for details.')
            }
        } finally {
            setLoading(false)
        }
    }

    const handleExtract = async () => {
        if (!extractOriginal || !extractSuspect) return

        setLoading(true)
        const formData = new FormData()
        formData.append('original_file', extractOriginal)
        formData.append('suspect_file', extractSuspect)

        try {
            const res = await api.post('/extract', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            setExtractResult(res.data.data)
        } catch (err) {
            console.error(err)
            alert('Extraction failed')
        } finally {
            setLoading(false)
        }
    }

    const handleDownloadResult = async () => {
        if (!result || !result.image_url) return

        setLoading(true)
        try {
            const resp = await fetch(result.image_url)
            if (!resp.ok) throw new Error('Download failed')
            const blob = await resp.blob()
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = 'watermarked_image.png'
            document.body.appendChild(a)
            a.click()
            a.remove()
            URL.revokeObjectURL(url)
        } catch (err) {
            console.error(err)
            alert('Download failed')
        } finally {
            setLoading(false)
        }
    }

    const tabs = [
        { id: 'embed', label: 'Embed Watermark', icon: LockIcon },
        { id: 'extract', label: 'Extract (With Original)', icon: EyeIcon },
        { id: 'verify', label: 'Verify (Blind)', icon: SearchIcon },
    ]

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="bg-blue-600 p-2 rounded-lg text-white shadow-lg shadow-blue-600/20">
                            <ShieldCheckIcon className="w-6 h-6" />
                        </div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700">
                            InvisiGuard
                        </span>
                    </div>

                    <div className="flex items-center gap-3">
                         <div className={`w-2 h-2 rounded-full ${health ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500 animate-pulse'}`}></div>
                         <span className="text-sm font-medium text-slate-600 hidden sm:block">
                            {health ? 'System Online' : 'Connecting...'}
                         </span>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
                
                {/* Tabs */}
                <div className="flex justify-center mb-10 px-4">
                    <div className="bg-white p-1.5 rounded-2xl shadow-sm border border-slate-200 grid grid-cols-1 sm:flex gap-1 w-full sm:w-auto">
                        {tabs.map(tab => {
                            const Icon = tab.icon
                            const isActive = activeTab === tab.id
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`
                                        flex items-center justify-center gap-2 px-6 py-3 sm:py-2.5 rounded-xl text-sm font-medium transition-all duration-300 ease-in-out whitespace-nowrap w-full sm:w-auto
                                        ${isActive 
                                            ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20 scale-[1.02] sm:scale-105' 
                                            : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}
                                    `}
                                >
                                    <Icon className="w-4 h-4" />
                                    {tab.label}
                                </button>
                            )
                        })}
                    </div>
                </div>

                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {activeTab === 'embed' && (
                        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                            {/* Left Column: Controls */}
                            <div className="lg:col-span-4 space-y-6">
                                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
                                    <div className="p-6 border-b border-slate-50 bg-slate-50/50">
                                        <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                            <span className="bg-blue-100 text-blue-700 w-6 h-6 rounded-full flex items-center justify-center text-xs">1</span>
                                            Upload Image
                                        </h2>
                                    </div>
                                    <div className="p-6">
                                        <Dropzone onFileSelect={handleEmbedFileSelect} label={file ? file.name : "Choose an image"} />
                                    </div>
                                </div>

                                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
                                    <div className="p-6 border-b border-slate-50 bg-slate-50/50">
                                        <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                                            <span className="bg-blue-100 text-blue-700 w-6 h-6 rounded-full flex items-center justify-center text-xs">2</span>
                                            Configuration
                                        </h2>
                                    </div>
                                    <div className="p-6">
                                        <ConfigPanel
                                            text={text}
                                            setText={setText}
                                            alpha={alpha}
                                            setAlpha={setAlpha}
                                            onEmbed={handleEmbed}
                                            loading={loading}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Right Column: Preview & Results */}
                            <div className="lg:col-span-8 space-y-6">
                                {(!result && !originalPreview) && (
                                    <div className="h-full min-h-[400px] flex flex-col items-center justify-center bg-slate-100/50 rounded-2xl border-2 border-dashed border-slate-200 text-slate-400">
                                        <div className="p-4 bg-white rounded-full shadow-sm mb-4">
                                            <ShieldCheckIcon className="w-10 h-10 text-blue-200" />
                                        </div>
                                        <p className="font-medium">Ready to protect your digital assets</p>
                                        <p className="text-sm text-slate-400 mt-1">Upload an image to get started</p>
                                    </div>
                                )}

                                {originalPreview && !result && (
                                    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden p-2">
                                        <img src={originalPreview} alt="Preview" className="w-full h-full object-contain rounded-xl bg-slate-50" />
                                    </div>
                                )}

                                {result && (
                                    <div className="space-y-6 animate-in fade-in duration-500">
                                        {/* PNG Format Warning */}
                                        <div className="bg-amber-50 rounded-xl border border-amber-200 p-4 flex gap-3">
                                            <div className="shrink-0 mt-0.5">
                                                <svg className="h-5 w-5 text-amber-500" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                                </svg>
                                            </div>
                                            <div>
                                                <h3 className="text-sm font-semibold text-amber-800">Use PNG Format Only</h3>
                                                <div className="mt-1 text-sm text-amber-700/80">
                                                    The watermark is optimized for lossless formats. <strong className="font-semibold text-amber-900">Do not convert to JPG</strong>, as compression will destroy the hidden data.
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                                            <div className="p-6 border-b border-slate-50 bg-slate-50/50 flex justify-between items-center">
                                                <h2 className="text-lg font-bold text-slate-800">Result Analysis</h2>
                                                <button
                                                    onClick={handleDownloadResult}
                                                    disabled={loading}
                                                    className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white text-sm font-medium rounded-lg transition-colors shadow-sm shadow-emerald-600/20"
                                                >
                                                    <DownloadIcon className="w-4 h-4" />
                                                    Download PNG
                                                </button>
                                            </div>
                                            <div className="p-6">
                                                <ComparisonView
                                                    originalUrl={originalPreview}
                                                    processedUrl={result.image_url}
                                                    signalMapUrl={result.signal_map_url ? result.signal_map_url : null}
                                                    metrics={{ psnr: result.psnr, ssim: result.ssim }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === 'extract' && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <div className="space-y-6">
                                {/* Instructions */}
                                <div className="bg-blue-50/50 rounded-2xl border border-blue-100 p-6">
                                    <h3 className="text-blue-900 font-semibold mb-3 flex items-center gap-2">
                                        <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        How it works
                                    </h3>
                                    <ul className="space-y-2 text-sm text-blue-800/80 ml-1">
                                        <li className="flex gap-2">
                                            <span className="font-bold text-blue-600">1.</span>
                                            <span>Upload the <strong>Original Image</strong> (reference).</span>
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="font-bold text-blue-600">2.</span>
                                            <span>Upload the <strong>Suspect Image</strong> (watermarked).</span>
                                        </li>
                                        <li className="flex gap-2">
                                            <span className="font-bold text-blue-600">3.</span>
                                            <span>The system aligns them to extract the hidden message.</span>
                                        </li>
                                    </ul>
                                </div>
                                
                                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
                                    <div className="p-6 border-b border-slate-50 bg-slate-50/50 flex justify-between items-center">
                                        <h2 className="text-lg font-bold text-slate-800">Original Image</h2>
                                        {extractOriginal && <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">Uploaded</span>}
                                    </div>
                                    <div className="p-6">
                                        <Dropzone
                                            onFileSelect={handleExtractOriginalSelect}
                                            label={extractOriginal ? extractOriginal.name : "Upload Reference Image"}
                                        />
                                        {extractOriginalPreview && (
                                            <div className="mt-4 rounded-xl overflow-hidden border border-slate-200">
                                                <img src={extractOriginalPreview} alt="Original preview" className="w-full h-32 object-cover" />
                                            </div>
                                        )}
                                    </div>
                                </div>
                                
                                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
                                    <div className="p-6 border-b border-slate-50 bg-slate-50/50 flex justify-between items-center">
                                        <h2 className="text-lg font-bold text-slate-800">Suspect Image</h2>
                                        {extractSuspect && <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">Uploaded</span>}
                                    </div>
                                    <div className="p-6">
                                        <Dropzone
                                            onFileSelect={handleExtractSuspectSelect}
                                            label={extractSuspect ? extractSuspect.name : "Upload Watermarked Image"}
                                        />
                                        {extractSuspectPreview && (
                                            <div className="mt-4 rounded-xl overflow-hidden border border-slate-200">
                                                <img src={extractSuspectPreview} alt="Suspect preview" className="w-full h-32 object-cover" />
                                            </div>
                                        )}
                                    </div>
                                </div>
                                
                                <button
                                    onClick={handleExtract}
                                    disabled={loading || !extractOriginal || !extractSuspect}
                                    className={`
                                        w-full py-4 rounded-xl font-bold text-lg shadow-lg transition-all duration-300 flex items-center justify-center gap-2
                                        ${(!extractOriginal || !extractSuspect) 
                                            ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none' 
                                            : 'bg-blue-600 text-white hover:bg-blue-700 hover:scale-[1.01] shadow-blue-600/30'}
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
                                            <EyeIcon className="w-5 h-5" />
                                            Extract Watermark
                                        </>
                                    )}
                                </button>
                            </div>

                            <div className="space-y-6">
                                {extractResult ? (
                                    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden h-full flex flex-col animate-in fade-in duration-500">
                                        <div className="p-6 border-b border-slate-50 bg-slate-50/50">
                                            <h2 className="text-lg font-bold text-slate-800">Extraction Results</h2>
                                        </div>
                                        <div className="p-8 flex-1 flex flex-col justify-center space-y-8">
                                            <div className="text-center">
                                                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Decoded Message</label>
                                                <div className="mt-3 text-3xl font-mono font-bold text-blue-600 break-all p-6 bg-blue-50/50 rounded-2xl border border-blue-100">
                                                    {extractResult.decoded_text || "<No text found>"}
                                                </div>
                                            </div>
                                            
                                            <div className="grid grid-cols-2 gap-6">
                                                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 text-center">
                                                    <div className="text-xs text-slate-500 mb-1">Alignment Status</div>
                                                    <div className={`font-bold ${extractResult.debug_info?.status === 'aligned' ? 'text-emerald-600' : 'text-amber-600'}`}>
                                                        {extractResult.debug_info?.status === 'aligned' ? '✅ Aligned' : '⚠️ Failed'}
                                                    </div>
                                                </div>
                                                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 text-center">
                                                    <div className="text-xs text-slate-500 mb-1">Confidence Score</div>
                                                    <div className="font-bold text-slate-700">{(extractResult.confidence * 100).toFixed(0)}%</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="h-full flex flex-col items-center justify-center bg-slate-100/50 rounded-2xl border-2 border-dashed border-slate-200 text-slate-400 p-12 text-center">
                                        <EyeIcon className="w-12 h-12 mb-4 text-slate-300" />
                                        <p className="font-medium">Waiting for images</p>
                                        <p className="text-sm mt-1 text-slate-400">Upload both original and suspect images to start extraction</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === 'verify' && (
                        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                             <VerifyTab />
                        </div>
                    )}
                </div>
            </main>
            
            <footer className="mt-12 py-8 bg-white border-t border-slate-200">
                <div className="max-w-7xl mx-auto px-4 text-center text-slate-400 text-sm">
                    &copy; 2025 InvisiGuard. Protected by Invisible Watermarking Technology.
                </div>
            </footer>
        </div>
    )
}

export default App