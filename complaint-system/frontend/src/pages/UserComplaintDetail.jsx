import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import ChatPanel from '../components/ChatPanel'

const PRIORITY_COLORS = {
  High:     'bg-orange-100 text-orange-700 border-orange-200',
  Medium:   'bg-yellow-100 text-yellow-700 border-yellow-200',
  Low:      'bg-green-100 text-green-700 border-green-200',
}


const STATUS_STEPS = [
  {
    key:   'Open',
    label: 'Submitted',
    icon:  '📝',
    desc:  'Your complaint has been received',
    color: 'blue',
  },
  {
    key:   'In Progress',
    label: 'Under Review',
    icon:  '🔍',
    desc:  'Our team is investigating your issue',
    color: 'purple',
  },
  {
    key:   'Escalated',
    label: 'Escalated',
    icon:  '🚨',
    desc:  'Escalated to senior team for priority resolution',
    color: 'red',
  },
  {
    key:   'Resolved',
    label: 'Resolved',
    icon:  '✅',
    desc:  'Your complaint has been resolved',
    color: 'green',
  },
]

const COLOR_MAP = {
  blue:   { ring: 'ring-blue-400',   bg: 'bg-blue-600',   text: 'text-blue-600',   light: 'bg-blue-50',   border: 'border-blue-200' },
  purple: { ring: 'ring-purple-400', bg: 'bg-purple-600', text: 'text-purple-600', light: 'bg-purple-50', border: 'border-purple-200' },
  red:    { ring: 'ring-red-400',    bg: 'bg-red-600',    text: 'text-red-600',    light: 'bg-red-50',    border: 'border-red-200' },
  green:  { ring: 'ring-green-400',  bg: 'bg-green-600',  text: 'text-green-600',  light: 'bg-green-50',  border: 'border-green-200' },
}

function StatusTracker({ complaint, history }) {

  const statusTime = {}
  history.forEach((h) => {
    if (!statusTime[h.status]) statusTime[h.status] = h.created_at
  })

  const currentStatus = complaint.status
  const isEscalated   = history.some((h) => h.status === 'Escalated')


  const steps = isEscalated
    ? STATUS_STEPS
    : STATUS_STEPS.filter((s) => s.key !== 'Escalated')

  const currentIdx = steps.findIndex((s) => s.key === currentStatus)

  const formatTime = (iso) => {
    if (!iso) return null
    const d = new Date(iso)
    return {
      date: d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }),
      time: d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
    }
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
      <h3 className="text-sm font-bold text-gray-700 mb-6">📦 Complaint Status Tracker</h3>


      <div className="relative">

        <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-gray-100 z-0" />

        <div className="space-y-6 relative z-10">
          {steps.map((step, idx) => {
            const isDone    = idx <= currentIdx
            const isCurrent = idx === currentIdx
            const isPending = idx > currentIdx
            const c         = COLOR_MAP[step.color]
            const ts        = formatTime(statusTime[step.key])

            return (
              <div key={step.key} className="flex items-start gap-4">

                <div className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 border-2 transition-all duration-500 ${
                  isCurrent
                    ? `${c.bg} border-transparent ring-4 ${c.ring} ring-opacity-30 shadow-lg`
                    : isDone
                    ? `${c.bg} border-transparent`
                    : 'bg-gray-50 border-gray-200'
                }`}>
                  <span className={`text-lg ${isPending ? 'opacity-30 grayscale' : ''}`}>
                    {isDone ? (isCurrent ? step.icon : '✓') : step.icon}
                  </span>
                </div>


                <div className={`flex-1 rounded-xl p-3 transition-all duration-300 ${
                  isCurrent ? `${c.light} border ${c.border}` : 'bg-transparent'
                }`}>
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <span className={`font-semibold text-sm ${
                      isCurrent ? c.text : isDone ? 'text-gray-700' : 'text-gray-300'
                    }`}>
                      {step.label}
                      {isCurrent && (
                        <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${c.bg} text-white font-bold`}>
                          Current
                        </span>
                      )}
                    </span>
                    {ts && isDone && (
                      <span className="text-xs text-gray-400 whitespace-nowrap">
                        {ts.date} · {ts.time}
                      </span>
                    )}
                    {!ts && !isPending && (
                      <span className="text-xs text-gray-400">—</span>
                    )}
                  </div>
                  <p className={`text-xs mt-0.5 ${
                    isCurrent ? c.text + ' opacity-80' : isDone ? 'text-gray-400' : 'text-gray-200'
                  }`}>
                    {step.desc}
                  </p>


                  {step.key === 'Resolved' && isDone && complaint.resolution_note && (
                    <div className="mt-2 pt-2 border-t border-green-200">
                      <p className="text-xs text-green-700 leading-relaxed">
                        {complaint.resolution_note}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>


      {currentStatus !== 'Resolved' && (
        <div className="mt-5 pt-4 border-t border-gray-100 flex items-center gap-2 text-xs text-gray-400">
          <span>⏱️</span>
          <span>
            Typical resolution time: <strong className="text-gray-600">
              {complaint.priority === 'High'     ? '24 hours' :
               complaint.priority === 'Medium'   ? '2–3 days' : '5 business days'}
            </strong> for {complaint.priority} priority complaints.
          </span>
        </div>
      )}
    </div>
  )
}

export default function UserComplaintDetail() {
  const { complaintId } = useParams()
  const navigate        = useNavigate()
  const { user }        = useAuth()

  const [complaint, setComplaint] = useState(null)
  const [history,   setHistory]   = useState([])
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    Promise.all([
      api.get(`/api/complaints/${complaintId}`),
      api.get(`/api/complaints/${complaintId}/history`),
    ])
      .then(([compRes, histRes]) => {
        setComplaint(compRes.data)
        setHistory(histRes.data || [])
      })
      .catch(() => navigate('/my-complaints'))
      .finally(() => setLoading(false))
  }, [complaintId])

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-gray-400">
      <div className="text-center">
        <div className="text-4xl mb-2 animate-bounce">📦</div>
        <p>Loading your complaint…</p>
      </div>
    </div>
  )

  if (!complaint) return null

  const date = complaint.created_at
    ? new Date(complaint.created_at).toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
      })
    : '—'

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">


      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/my-complaints')}
          className="text-gray-400 hover:text-gray-600 text-xl transition-colors">←</button>
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-sm text-gray-500">{complaint.complaint_id}</span>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${PRIORITY_COLORS[complaint.priority]}`}>
              {complaint.priority}
            </span>
            {complaint.sla_breached && (
              <span className="text-xs font-bold bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
                ⚠️ SLA Breached
              </span>
            )}
          </div>
          <p className="text-xs text-gray-400 mt-0.5">Submitted {date}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">


        <div className="space-y-4">


          <StatusTracker complaint={complaint} history={history} />


          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Your Complaint</h3>
            <p className="text-gray-800 leading-relaxed whitespace-pre-wrap text-sm">{complaint.complaint_text}</p>
            {complaint.category && (
              <span className="inline-block mt-3 bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full font-medium">
                {complaint.category}
              </span>
            )}
          </div>


          {complaint.image_path && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Attached Photo</h3>
              <img
                src={`http://localhost:8001/uploads/${complaint.image_path}`}
                alt="Complaint attachment"
                className="rounded-xl max-h-48 object-cover cursor-pointer hover:opacity-90 transition-opacity shadow-sm"
                onClick={() => window.open(`http://localhost:8001/uploads/${complaint.image_path}`, '_blank')}
              />
            </div>
          )}
        </div>


        <div>
          <ChatPanel complaintId={complaintId} currentUser={user} />
        </div>
      </div>
    </div>
  )
}
