import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'

const statConfig = [
  { key: 'Open', label: 'Open', color: 'bg-blue-50 border-blue-200 text-blue-700', icon: '📂' },
  { key: 'In Progress', label: 'In Progress', color: 'bg-purple-50 border-purple-200 text-purple-700', icon: '⚙️' },
  { key: 'Escalated', label: 'Escalated', color: 'bg-red-50 border-red-200 text-red-700', icon: '🚨' },
  { key: 'Resolved', label: 'Resolved', color: 'bg-green-50 border-green-200 text-green-700', icon: '✅' },
]

export default function Dashboard() {
  const { user } = useAuth()
  const [complaints, setComplaints] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/complaints/my?limit=100')
      .then((r) => setComplaints(r.data.items || []))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const counts = statConfig.reduce((acc, s) => {
    acc[s.key] = complaints.filter((c) => c.status === s.key).length
    return acc
  }, {})

  const recent = complaints.slice(0, 5)

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.name?.split(' ')[0]}! 👋
        </h1>
        <p className="text-gray-500 text-sm mt-1">Here's an overview of your complaints</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {statConfig.map((s) => (
          <div key={s.key} className={`rounded-xl border p-4 ${s.color}`}>
            <div className="text-2xl mb-1">{s.icon}</div>
            <div className="text-2xl font-bold">{counts[s.key] || 0}</div>
            <div className="text-sm font-medium">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <Link
          to="/submit"
          className="card flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer border-2 border-dashed border-blue-200 hover:border-blue-400"
        >
          <span className="text-3xl">✍️</span>
          <div>
            <div className="font-semibold text-gray-900">Submit New Complaint</div>
            <div className="text-sm text-gray-500">Our AI will categorize it instantly</div>
          </div>
        </Link>
        <Link
          to="/my-complaints"
          className="card flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer"
        >
          <span className="text-3xl">📋</span>
          <div>
            <div className="font-semibold text-gray-900">View All Complaints</div>
            <div className="text-sm text-gray-500">{complaints.length} total complaints</div>
          </div>
        </Link>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-4">Recent Complaints</h2>
        {loading ? (
          <div className="text-center py-10 text-gray-400">Loading...</div>
        ) : recent.length === 0 ? (
          <div className="card text-center py-10 text-gray-400">
            <div className="text-4xl mb-3">📭</div>
            <p>No complaints yet. <Link to="/submit" className="text-blue-600 hover:underline">Submit one now</Link></p>
          </div>
        ) : (
          <div className="space-y-3">
            {recent.map((c) => (
              <RecentRow key={c.id} complaint={c} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function RecentRow({ complaint }) {
  const priorityColors = {
    High: 'text-orange-600 bg-orange-50',
    Medium: 'text-yellow-700 bg-yellow-50',
    Low: 'text-green-700 bg-green-50',
  }
  return (
    <div className="card flex items-center justify-between gap-4">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-mono text-gray-400">{complaint.complaint_id}</span>
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${priorityColors[complaint.priority] || ''}`}>
            {complaint.priority}
          </span>
        </div>
        <p className="text-sm text-gray-700 truncate">{complaint.complaint_text}</p>
        {complaint.category && (
          <span className="text-xs text-indigo-600 font-medium">{complaint.category}</span>
        )}
      </div>
      <div className="shrink-0">
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
          complaint.status === 'Resolved' ? 'bg-green-100 text-green-800' :
          complaint.status === 'Escalated' ? 'bg-red-100 text-red-800' :
          complaint.status === 'In Progress' ? 'bg-purple-100 text-purple-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          {complaint.status}
        </span>
      </div>
    </div>
  )
}
