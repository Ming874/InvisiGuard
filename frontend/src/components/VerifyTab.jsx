import React, { useState } from 'react';
import api from '../services/api';
import Dropzone from './Dropzone';

const SearchIcon = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.3-4.3" />
    </svg>
)

export const VerifyTab = () => {
  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
    setFilePreview(URL.createObjectURL(selectedFile));
    setVerificationResult(null);
  };

  const handleVerify = async () => {
    if (!file) return;
    setLoading(true);
    
    const formData = new FormData();
    formData.append('image', file);

    try {
      const res = await api.post('/verify', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setVerificationResult(res.data.data);
    } catch (err) {
      console.error(err);
      alert('Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 p-6">
        {/* Left Column: Input */}
        <div className="lg:col-span-5 space-y-6">
            <div className="bg-blue-50/50 rounded-2xl border border-blue-100 p-6">
                <h3 className="text-blue-900 font-semibold mb-3 flex items-center gap-2">
                    <SearchIcon className="w-5 h-5 text-blue-600" />
                    Blind Verification
                </h3>
                <p className="text-sm text-blue-800/80 leading-relaxed">
                    This mode detects watermarks without the original image. It uses synchronization templates to correct for rotation and scaling attacks automatically.
                </p>
            </div>

            <div className="bg-white">
                <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center justify-between">
                    <span>Suspect Image</span>
                    {file && <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">Selected</span>}
                </h2>
                <Dropzone onFileSelect={handleFileSelect} label={file ? file.name : "Upload Image to Verify"} />
            </div>

            {filePreview && (
                <div className="rounded-xl overflow-hidden border border-slate-200 shadow-sm">
                    <img src={filePreview} alt="Preview" className="w-full h-48 object-cover bg-slate-50" />
                </div>
            )}

            <button 
                onClick={handleVerify} 
                disabled={!file || loading} 
                className={`
                    w-full py-4 rounded-xl font-bold text-lg shadow-lg transition-all duration-300 flex items-center justify-center gap-2
                    ${!file 
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
                        Verifying...
                    </>
                ) : (
                    <>
                        <SearchIcon className="w-5 h-5" />
                        Verify Watermark
                    </>
                )}
            </button>
        </div>

        {/* Right Column: Results */}
        <div className="lg:col-span-7">
            {verificationResult ? (
                <div className="bg-white h-full flex flex-col animate-in fade-in duration-500">
                    <div className="p-6 bg-slate-50 rounded-xl border border-slate-100 mb-6 text-center">
                        <div className="text-sm font-medium text-slate-500 mb-2">Verification Status</div>
                        {verificationResult.verified ? (
                            <div className="inline-flex items-center gap-2 px-6 py-2 bg-emerald-100 text-emerald-800 rounded-full font-bold text-lg">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                                Watermark Detected
                            </div>
                        ) : (
                            <div className="inline-flex items-center gap-2 px-6 py-2 bg-red-100 text-red-800 rounded-full font-bold text-lg">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                                No Watermark Found
                            </div>
                        )}
                    </div>

                    {verificationResult.verified && (
                        <div className="space-y-6">
                            <div className="text-center">
                                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Payload Message</label>
                                <div className="mt-2 text-2xl font-mono font-bold text-blue-600 break-all p-4 bg-white rounded-xl border border-blue-100 shadow-sm">
                                    {verificationResult.watermark_text}
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                    <div className="text-xs text-slate-500 mb-1">Confidence Score</div>
                                    <div className="font-bold text-slate-700 text-lg">
                                        {(verificationResult.confidence * 100).toFixed(1)}%
                                    </div>
                                </div>
                                
                                {verificationResult.metadata && (
                                    <>
                                        <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                            <div className="text-xs text-slate-500 mb-1">Rotation Detected</div>
                                            <div className="font-bold text-slate-700 text-lg">
                                                {verificationResult.metadata.rotation_detected.toFixed(1)}°
                                            </div>
                                        </div>
                                        <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                            <div className="text-xs text-slate-500 mb-1">Scale Detected</div>
                                            <div className="font-bold text-slate-700 text-lg">
                                                {verificationResult.metadata.scale_detected.toFixed(2)}x
                                            </div>
                                        </div>
                                        <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                            <div className="text-xs text-slate-500 mb-1">Sync Peak Quality</div>
                                            <div className="font-bold text-slate-700 text-lg">
                                                {verificationResult.metadata.peak_quality ? verificationResult.metadata.peak_quality.toFixed(3) : 'N/A'}
                                            </div>
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                <div className="h-full flex flex-col items-center justify-center bg-slate-100/50 rounded-2xl border-2 border-dashed border-slate-200 text-slate-400 p-12 text-center min-h-[300px]">
                    <SearchIcon className="w-12 h-12 mb-4 text-slate-300" />
                    <p className="font-medium">Ready to verify</p>
                    <p className="text-sm mt-1 text-slate-400">Upload a suspect image to check for watermarks</p>
                </div>
            )}
        </div>
    </div>
  );
};

export default VerifyTab;