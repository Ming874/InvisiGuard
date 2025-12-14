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

    const handleFileSelect = (selectedFile) => {
        setFile(selectedFile)
        setOriginalPreview(URL.createObjectURL(selectedFile))
        setResult(null)
        // Auto-set as extract original too for convenience
        setExtractOriginal(selectedFile)
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
                                Embed
                            </button>
                            <button
                                onClick={() => setActiveTab('extract')}
                                className={`px-4 py-2 rounded ${activeTab === 'extract' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Extract
                            </button>
                            <button
                                onClick={() => setActiveTab('verify')}
                                className={`px-4 py-2 rounded ${activeTab === 'verify' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
                            >
                                Verify
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
                                <Dropzone onFileSelect={handleFileSelect} label={file ? file.name : "Upload Image"} />
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
                                            processedUrl={`http://localhost:8000${result.image_url}`}
                                            signalMapUrl={result.signal_map_url ? `http://localhost:8000${result.signal_map_url}` : null}
                                            metrics={{ psnr: result.psnr, ssim: result.ssim }}
                                        />
                                    </div>

                                    <AttackSimulator
                                        imageUrl={`http://localhost:8000${result.image_url}`}
                                        onExport={(file) => {
                                            setExtractSuspect(file)
                                            setActiveTab('extract')
                                            alert("Attacked image set as suspect for extraction!")
                                        }}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                )}
                {activeTab === 'extract' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div className="space-y-6">
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
