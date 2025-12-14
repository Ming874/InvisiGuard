import React, { useState } from 'react';
import api from '../services/api';

export const VerifyTab = () => {
  const [file, setFile] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setVerificationResult(null);
    }
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
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Blind Verification</h2>
      <p className="text-gray-600 mb-4">Verify a watermark without the original image. Supports rotation and scaling.</p>
      
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Suspect Image</label>
        <input 
          type="file" 
          onChange={handleFileChange} 
          accept="image/*" 
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" 
        />
      </div>
      
      <button 
        onClick={handleVerify} 
        disabled={!file || loading} 
        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 transition-colors"
      >
        {loading ? 'Verifying...' : 'Verify Watermark'}
      </button>
      
      {verificationResult && (
        <div className={`mt-6 p-4 border rounded-lg ${verificationResult.verified ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
          <h3 className={`font-bold text-lg ${verificationResult.verified ? 'text-green-800' : 'text-red-800'}`}>
            {verificationResult.verified ? 'Verified' : 'Not Verified'}
          </h3>
          
          {verificationResult.verified && (
            <div className="mt-2 space-y-2">
              <p><strong>Payload:</strong> {verificationResult.watermark_text}</p>
              <p><strong>Confidence:</strong> {(verificationResult.confidence * 100).toFixed(1)}%</p>
            </div>
          )}
          
          {verificationResult.metadata && (
            <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-600">
              <h4 className="font-semibold mb-1">Geometric Correction:</h4>
              <p>Rotation: {verificationResult.metadata.rotation_detected.toFixed(2)}°</p>
              <p>Scale: {verificationResult.metadata.scale_detected.toFixed(2)}x</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VerifyTab;

