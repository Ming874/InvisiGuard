import React from 'react'

export default function ConfigPanel({ text, setText, alpha, setAlpha, onEmbed, loading }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
      <h3 className="text-lg font-semibold">Configuration</h3>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Watermark Text
        </label>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          maxLength={32}
          className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
          placeholder="Enter text..."
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Strength (Alpha): {alpha}
        </label>
        <input
          type="range"
          min="0.1"
          max="5.0"
          step="0.1"
          value={alpha}
          onChange={(e) => setAlpha(parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>Invisible (0.1)</span>
          <span>Robust (5.0)</span>
        </div>
      </div>

      <button
        onClick={onEmbed}
        disabled={loading || !text}
        className={`w-full py-2 px-4 rounded text-white font-medium transition-colors ${
          loading || !text 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-blue-600 hover:bg-blue-700'
        }`}
      >
        {loading ? 'Processing...' : 'Embed Watermark'}
      </button>
    </div>
  )
}
