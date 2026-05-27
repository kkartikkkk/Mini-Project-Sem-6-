import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/axios'

const CHANNELS = ['Web Form', 'Email', 'Phone', 'Chat', 'Social Media']

const EXAMPLES = [
  "My account was hacked and I see unauthorized purchases!",
  "The shipment tracking has not updated in several days.",
  "I received a wrong item that doesn't match my order.",
  "The product I received is completely broken and damaged.",
  "I need a refund for an order I cancelled last week.",
  "The support agent was very rude and unhelpful.",
]


const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
const SPEECH_SUPPORTED  = !!SpeechRecognition

export default function SubmitComplaint() {
  const navigate     = useNavigate()
  const fileRef      = useRef(null)
  const cameraRef    = useRef(null)
  const recognizerRef = useRef(null)

  const [text,        setText]        = useState('')
  const [channel,     setChannel]     = useState('Web Form')
  const [image,       setImage]       = useState(null)
  const [preview,     setPreview]     = useState(null)
  const [loading,     setLoading]     = useState(false)
  const [result,      setResult]      = useState(null)
  const [error,       setError]       = useState('')


  const [listening,   setListening]   = useState(false)
  const [voiceInterim, setVoiceInterim] = useState('') 


  const startListening = () => {
    if (!SPEECH_SUPPORTED) {
      setError('Voice input is not supported in this browser. Please use Chrome or Edge.')
      return
    }
    const recognition = new SpeechRecognition()
    recognition.continuous      = true   
    recognition.interimResults  = true   
    recognition.lang            = 'en-IN' 

    recognition.onstart = () => {
      setListening(true)
      setError('')
    }

    recognition.onresult = (event) => {
      let finalText  = ''
      let interimText = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalText += transcript + ' '
        } else {
          interimText += transcript
        }
      }
      if (finalText) {
        setText((prev) => (prev + finalText).trimStart())
      }
      setVoiceInterim(interimText)
    }

    recognition.onerror = (event) => {
      if (event.error !== 'aborted') {
        setError(`Microphone error: ${event.error}. Please allow microphone access.`)
      }
      setListening(false)
      setVoiceInterim('')
    }

    recognition.onend = () => {
      setListening(false)
      setVoiceInterim('')
    }

    recognizerRef.current = recognition
    recognition.start()
  }

  const stopListening = () => {
    recognizerRef.current?.stop()
    setListening(false)
    setVoiceInterim('')
  }


  useEffect(() => () => recognizerRef.current?.abort(), [])


  const handleImageChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.size > 5 * 1024 * 1024) {
      setError('Image must be under 5MB.')
      return
    }
    setImage(file)
    setError('')
    const reader = new FileReader()
    reader.onload = (ev) => setPreview(ev.target.result)
    reader.readAsDataURL(file)
  }

  const removeImage = () => {
    setImage(null)
    setPreview(null)
    if (fileRef.current)   fileRef.current.value   = ''
    if (cameraRef.current) cameraRef.current.value = ''
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!text.trim() || text.trim().length < 10) {
      setError('Please describe your complaint in at least 10 characters.')
      return
    }
    setError('')
    setLoading(true)
    try {

      const formData = new FormData()
      formData.append('complaint_text', text)
      formData.append('channel', channel)
      if (image) formData.append('image', image)

      const res = await api.post('/api/complaints/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit complaint.')
    } finally {
      setLoading(false)
    }
  }


  if (result) {
    const priorityBadge = {
      High:   'bg-red-100 text-red-700 border border-red-200',
      Medium: 'bg-yellow-100 text-yellow-700 border border-yellow-200',
      Low:    'bg-green-100 text-green-700 border border-green-200',
    }

    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <div className="rounded-2xl border-2 border-green-400 bg-green-50 p-8 text-center">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Complaint Submitted!</h2>
          <p className="text-gray-500 mb-6">Our AI has classified your complaint</p>

          <div className="bg-white rounded-xl p-6 text-left space-y-3 mb-6 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Complaint ID</span>
              <button
                onClick={() => navigate(`/complaint/${result.complaint_id}`)}
                className="text-sm font-mono font-semibold text-blue-600 hover:text-blue-800 hover:underline"
              >
                {result.complaint_id} ↗
              </button>
            </div>
            <Row label="Category" value={result.category} />
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Priority</span>
              <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${priorityBadge[result.priority] || priorityBadge.Medium}`}>
                {result.priority}
              </span>
            </div>
            <Row label="Status" value={result.status} />
          </div>


          {result.image_path && (
            <div className="mb-6">
              <p className="text-xs text-gray-400 mb-2">Attached photo</p>
              <img
                src={`http://localhost:8001/uploads/${result.image_path}`}
                alt="Complaint attachment"
                className="rounded-xl max-h-48 mx-auto object-cover shadow"
              />
            </div>
          )}

          {result.resolution_note && (
            <div className="bg-white rounded-xl p-4 text-left mb-6 shadow-sm">
              <p className="text-sm font-semibold text-gray-700 mb-1">Resolution Plan:</p>
              <p className="text-sm text-gray-600">{result.resolution_note}</p>
            </div>
          )}


          {result.assigned_to && (
            <div className="flex items-center justify-center gap-2 bg-teal-50 border border-teal-100 rounded-xl px-4 py-3 mb-4">
              <span className="text-teal-600 text-lg">👤</span>
              <p className="text-sm text-teal-800">
                Assigned to <span className="font-semibold">{result.assigned_to.name}</span>
              </p>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => navigate(`/complaint/${result.complaint_id}`)}
              className="btn-primary flex items-center justify-center gap-2 px-6"
            >
              📍 Track This Complaint
            </button>
            <button onClick={() => navigate('/my-complaints')} className="btn-secondary">
              All My Complaints
            </button>
            <button onClick={() => { setResult(null); setText(''); removeImage() }} className="btn-secondary">
              Submit Another
            </button>
          </div>
        </div>
      </div>
    )
  }


  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Submit a Complaint</h1>
      <p className="text-gray-500 text-sm mb-6">
        Our AI will automatically categorize your complaint and assign priority
      </p>

      <div className="card mb-6">
        <form onSubmit={handleSubmit} className="space-y-5">


          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-sm font-medium text-gray-700">
                Describe your complaint <span className="text-red-500">*</span>
              </label>


              {SPEECH_SUPPORTED && (
                <button
                  type="button"
                  onClick={listening ? stopListening : startListening}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    listening
                      ? 'bg-red-500 text-white animate-pulse shadow-lg shadow-red-200'
                      : 'bg-gray-100 text-gray-600 hover:bg-blue-50 hover:text-blue-600'
                  }`}
                  title={listening ? 'Click to stop recording' : 'Click to speak your complaint'}
                >
                  {listening ? (
                    <>
                      <span className="w-2 h-2 rounded-full bg-white animate-ping inline-block" />
                      Stop Recording
                    </>
                  ) : (
                    <>🎤 Speak Complaint</>
                  )}
                </button>
              )}
            </div>


            {listening && (
              <div className="mb-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
                <span className="flex gap-0.5">
                  {[1,2,3,4,5].map((i) => (
                    <span
                      key={i}
                      className="w-1 bg-red-400 rounded-full animate-bounce"
                      style={{ height: `${8 + (i % 3) * 6}px`, animationDelay: `${i * 0.1}s` }}
                    />
                  ))}
                </span>
                <p className="text-xs text-red-600 font-medium flex-1 truncate">
                  {voiceInterim || 'Listening… speak clearly'}
                </p>
              </div>
            )}

            <textarea
              className={`input-field resize-none transition-all ${
                listening ? 'border-red-300 ring-2 ring-red-100' : ''
              }`}
              rows={6}
              placeholder={listening ? 'Your words will appear here as you speak…' : 'Please describe your issue in detail…  or click 🎤 Speak Complaint above'}
              value={text}
              onChange={(e) => setText(e.target.value)}
              required
            />
            <div className="flex justify-between mt-1">
              {error && <p className="text-red-500 text-xs">{error}</p>}
              <p className="text-xs text-gray-400 ml-auto">{text.length} characters</p>
            </div>
          </div>


          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Attach a Photo <span className="text-gray-400 font-normal">(optional — JPG/PNG, max 5MB)</span>
            </label>


            {preview ? (
              <div className="relative inline-block mb-3">
                <img
                  src={preview}
                  alt="Preview"
                  className="rounded-xl max-h-48 object-cover border border-gray-200 shadow-sm"
                />
                <button
                  type="button"
                  onClick={removeImage}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shadow hover:bg-red-600"
                >
                  ✕
                </button>
              </div>
            ) : (
              <div className="flex gap-3">

                <button
                  type="button"
                  onClick={() => fileRef.current?.click()}
                  className="flex items-center gap-2 px-4 py-2.5 border-2 border-dashed border-gray-300 rounded-xl text-sm text-gray-500 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50 transition-all"
                >
                  🖼️ Choose from Gallery
                </button>


                <button
                  type="button"
                  onClick={() => cameraRef.current?.click()}
                  className="flex items-center gap-2 px-4 py-2.5 border-2 border-dashed border-gray-300 rounded-xl text-sm text-gray-500 hover:border-green-400 hover:text-green-600 hover:bg-green-50 transition-all"
                >
                  📷 Take Photo
                </button>
              </div>
            )}


            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleImageChange}
            />
            <input
              ref={cameraRef}
              type="file"
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={handleImageChange}
            />
          </div>


          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Preferred Contact Channel
            </label>
            <select className="input-field" value={channel} onChange={(e) => setChannel(e.target.value)}>
              {CHANNELS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full py-3">
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Analyzing & Submitting...
              </span>
            ) : '🚀 Submit Complaint'}
          </button>
        </form>
      </div>


      <div>
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Try an example:</p>
        <div className="space-y-2">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => setText(ex)}
              className="w-full text-left text-sm bg-white border border-gray-200 rounded-lg px-3 py-2 hover:bg-blue-50 hover:border-blue-300 transition-colors text-gray-600"
            >
              {ex}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

function Row({ label, value, mono, className = '' }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-500">{label}</span>
      <span className={`text-sm font-medium ${mono ? 'font-mono' : ''} ${className}`}>{value}</span>
    </div>
  )
}
