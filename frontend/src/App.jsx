import { useState, useEffect } from 'react'
import api from './services/api'
import Dropzone from './components/Dropzone'
import ConfigPanel from './components/ConfigPanel'
import ComparisonView from './components/ComparisonView'
import AttackSimulator from './components/AttackSimulator'
import VerifyTab from './components/VerifyTab'

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

    useEffect(() => {
        api.get('/health')
            .then(res => setHealth(res.data))
            .catch(err => console.error(err))
    }, [])

    const handleEmbedFileSelect = (selectedFile) => {
        setFile(selectedFile)
        setOriginalPreview(URL.createObjectURL(selectedFile))
        setResult(null)
        // Removed auto-set of extractOriginal to prevent state conflict
    }

    const handleEmbed = async () => {
        if (!file || !text) return

        setLoading(true)
        const formData = new FormData()
        formData.append('file', file)
        formData.append('text', text)
        formData.append('alpha', alpha)

        try {
            const res = await api.post('/embed', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            setResult(res.data.data)
        } catch (err) {
            console.error(err)
            alert('Error embedding watermark')
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

    return (
        <div className="min-h-screen bg-gray-100 p-8">
            <div className="max-w-6xl mx-auto space-y-8">
                <header className="flex justify-between items-center">
                    <h1 className="text-3xl font-bold text-gray-900">InvisiGuard</h1>
                    <div className="flex items-center gap-4">
                        <div className="space-x-2">
                            <button
                                onClick={() => setActiveTab('embed')}
                                className={`px-4 py-2 rounded ${activeTab === 'embed' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Embed Watermark
                            </button>
                            <button
                                onClick={() => setActiveTab('extract')}
                                className={`px-4 py-2 rounded ${activeTab === 'extract' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Extract (With Original)
                            </button>
                            <button
                                onClick={() => setActiveTab('verify')}
                                className={`px-4 py-2 rounded ${activeTab === 'verify' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Verify (Blind)
                            </button>
                        </div>
                        <div className="text-sm">
                            {health ? (
                                <span className="text-green-600 font-medium">● System Online</span>
                            ) : (
                                <span className="text-red-500">● Connecting...</span>
                            )}
                        </div>
                    </div>
                </header>

                {activeTab === 'embed' && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Left Column: Controls */}
                        <div className="space-y-6">
                            <section className="bg-white p-6 rounded-lg shadow-md">
                                <h2 className="text-xl font-semibold mb-4">1. Upload Image</h2>
                                <Dropzone onFileSelect={handleEmbedFileSelect} label={file ? file.name : "Upload Image"} />
                            </section>

                            <section>
                                <ConfigPanel
                                    text={text}
                                    setText={setText}
                                    alpha={alpha}
                                    setAlpha={setAlpha}
                                    onEmbed={handleEmbed}
                                    loading={loading}
                                />
                            </section>
                        </div>

                        {/* Right Column: Preview & Results */}
                        <div className="lg:col-span-2 space-y-6">
                            {originalPreview && !result && (
                                <div className="bg-white p-6 rounded-lg shadow-md">
                                    <h2 className="text-xl font-semibold mb-4">Preview</h2>
                                    <img src={originalPreview} alt="Preview" className="max-h-[500px] mx-auto rounded" />
                                </div>
                            )}

                            {result && (
                                <div className="space-y-6">
                                    <div className="bg-white p-6 rounded-lg shadow-md">
                                        <h2 className="text-xl font-semibold mb-4">Result Analysis</h2>
                                        <ComparisonView
                                            originalUrl={originalPreview}
                                            processedUrl={result.image_url}
                                            signalMapUrl={result.signal_map_url ? result.signal_map_url : null}
                                            metrics={{ psnr: result.psnr, ssim: result.ssim }}
                                        />
                                        <div className="mt-4 flex justify-end">
                                            <button
                                                onClick={handleDownloadResult}
                                                disabled={loading}
                                                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 inline-flex items-center gap-2 disabled:opacity-50"
                                            >
                                                <span>Download Image</span>
                                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                                </svg>
                                            </button>
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
                            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-blue-800 text-sm">
                                <strong>Note:</strong> Use this tab if you have the original image. It provides higher accuracy than Blind Verify.
                            </div>
                            <section className="bg-white p-6 rounded-lg shadow-md">
                                <h2 className="text-xl font-semibold mb-4">1. Original Image</h2>
                                <Dropzone
                                    onFileSelect={setExtractOriginal}
                                    label={extractOriginal ? extractOriginal.name : "Upload Original"}
                                />
                            </section>
                            <section className="bg-white p-6 rounded-lg shadow-md">
                                <h2 className="text-xl font-semibold mb-4">2. Suspect Image</h2>
                                <Dropzone
                                    onFileSelect={setExtractSuspect}
                                    label={extractSuspect ? extractSuspect.name : "Upload Suspect"}
                                />
                            </section>
                            <button
                                onClick={handleExtract}
                                disabled={loading || !extractOriginal || !extractSuspect}
                                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                            >
                                {loading ? "Extracting..." : "Extract Watermark"}
                            </button>
                        </div>

                        <div className="space-y-6">
                            {extractResult && (
                                <div className="bg-white p-6 rounded-lg shadow-md">
                                    <h2 className="text-xl font-semibold mb-4">Extraction Result</h2>
                                    <div className="space-y-4">
                                        <div className="p-4 bg-gray-50 rounded border">
                                            <div className="text-sm text-gray-500">Decoded Text</div>
                                            <div className="text-2xl font-mono font-bold text-blue-600 break-all">
                                                {extractResult.decoded_text || "<No text found>"}
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="p-3 bg-gray-50 rounded border">
                                                <div className="text-xs text-gray-500">Status</div>
                                                <div className="font-medium">
                                                    {extractResult.debug_info?.status === 'aligned' ? '✅ Aligned' : '⚠️ Alignment Failed'}
                                                </div>
                                            </div>
                                            <div className="p-3 bg-gray-50 rounded border">
                                                <div className="text-xs text-gray-500">Confidence</div>
                                                <div className="font-medium">{(extractResult.confidence * 100).toFixed(0)}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
                {activeTab === 'verify' && <VerifyTab />}
            </div>
        </div>
    )
}

export default App
