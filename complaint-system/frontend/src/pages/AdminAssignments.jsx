import { useState, useEffect } from 'react'
import api from '../api/axios'

const CATEGORY_ICONS = {
  'Delivery Issue':   '🚚',
  'Payment Issue':    '💳',
  'Product Issue':    '📦',
  'Account Issue':    '🔐',
  'Refund Request':   '💰',
  'Customer Service': '🎧',
  'Product Inquiry':  '🔍',
}


export default function AdminAssignments() {
  const [assignments, setAssignments] = useState([])
  const [agents,      setAgents]      = useState([])
  const [loading,     setLoading]     = useState(true)
  const [saving,      setSaving]      = useState({})   
  const [saved,       setSaved]       = useState({})   

  useEffect(() => {
    Promise.all([
      api.get('/api/admin/assignments'),
      api.get('/api/admin/agents'),
    ]).then(([aRes, gRes]) => {
      setAssignments(aRes.data)
      setAgents(gRes.data)
    }).finally(() => setLoading(false))
  }, [])

  const handleAssign = async (category, userId) => {
    setSaving((s) => ({ ...s, [category]: true }))
    setSaved((s) => ({ ...s, [category]: false }))
    try {
      const res = await api.put(
        `/api/admin/assignments/${encodeURIComponent(category)}`,
        { user_id: userId ? parseInt(userId) : null }
      )
      setAssignments((prev) =>
        prev.map((a) => (a.category === category ? res.data : a))
      )
      setSaved((s) => ({ ...s, [category]: true }))
      setTimeout(() => setSaved((s) => ({ ...s, [category]: false })), 2500)
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to save assignment')
    } finally {
      setSaving((s) => ({ ...s, [category]: false }))
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-gray-400">
      <div className="text-center">
        <div className="text-3xl animate-spin inline-block mb-2">⚙️</div>
        <p>Loading assignments...</p>
      </div>
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">


      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Category → Agent Assignment</h1>
        <p className="text-sm text-gray-500 mt-1">
          Set which agent handles each complaint category. New complaints are auto-assigned on submission.
        </p>
      </div>


      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 mb-6 flex items-start gap-3">
        <span className="text-blue-400 text-lg mt-0.5">ℹ️</span>
        <div>
          <p className="text-sm text-blue-800 font-medium">How it works</p>
          <p className="text-xs text-blue-600 mt-0.5">
            When a user submits a complaint, the system classifies it into a category and instantly assigns it
            to the agent you've set here. Admins can always manually reassign from the complaint detail page.
          </p>
        </div>
      </div>

      {agents.length === 0 ? (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
          <p className="text-sm text-amber-800 font-medium">⚠️ No agents available</p>
          <p className="text-xs text-amber-600 mt-1">
            Go to <strong>User Management</strong> and change a user's role to <strong>Employee</strong> or <strong>Admin</strong> to make them available as an agent.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 mb-6">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Available Agents ({agents.length})</p>
          <div className="flex flex-wrap gap-2">
            {agents.map((a) => (
              <span
                key={a.id}
                className="inline-flex items-center gap-1.5 bg-teal-50 text-teal-700 text-xs px-3 py-1 rounded-full border border-teal-100 font-medium"
              >
                <span className="w-5 h-5 rounded-full bg-teal-200 text-teal-800 flex items-center justify-center text-xs font-bold">
                  {a.name[0].toUpperCase()}
                </span>
                {a.name}
                <span className="text-teal-400 capitalize">· {a.role}</span>
              </span>
            ))}
          </div>
        </div>
      )}


      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              <th className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide px-6 py-3">Category</th>
              <th className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide px-6 py-3">Assigned Agent</th>
              <th className="w-24 px-6 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {assignments.map((a) => (
              <AssignmentRow
                key={a.category}
                assignment={a}
                agents={agents}
                saving={!!saving[a.category]}
                saved={!!saved[a.category]}
                onAssign={handleAssign}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


function AssignmentRow({ assignment, agents, saving, saved, onAssign }) {
  const [selected, setSelected] = useState(assignment.assigned_user_id || '')


  useEffect(() => {
    setSelected(assignment.assigned_user_id || '')
  }, [assignment.assigned_user_id])

  const icon        = CATEGORY_ICONS[assignment.category] || '📋'
  const isDirty     = String(selected) !== String(assignment.assigned_user_id || '')
  const agentName   = agents.find((a) => a.id === (assignment.assigned_user_id))?.name

  return (
    <tr className="hover:bg-gray-50 transition-colors">

      <td className="px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="text-lg">{icon}</span>
          <span className="font-medium text-gray-800 text-sm">{assignment.category}</span>
        </div>
      </td>


      <td className="px-6 py-4">
        <select
          className="input-field text-sm py-1.5 pr-8 min-w-[200px]"
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
        >
          <option value="">— Unassigned —</option>
          {agents.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name} ({a.role})
            </option>
          ))}
        </select>
        {agentName && !isDirty && (
          <p className="text-xs text-teal-600 mt-1 ml-1">Currently: {agentName}</p>
        )}
      </td>


      <td className="px-6 py-4 text-right">
        {saved ? (
          <span className="text-green-600 text-xs font-medium">✅ Saved</span>
        ) : (
          <button
            onClick={() => onAssign(assignment.category, selected || null)}
            disabled={saving || !isDirty}
            className={`text-xs font-semibold px-3 py-1.5 rounded-lg transition-all ${
              isDirty
                ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            {saving ? '⏳' : 'Save'}
          </button>
        )}
      </td>
    </tr>
  )
}
