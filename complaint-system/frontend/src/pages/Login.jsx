import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(form.email, form.password)
      if (user.role === 'admin' || user.role === 'employee') {
        navigate('/admin')
      } else {
        navigate('/dashboard')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">


      <div
        className="hidden lg:flex lg:w-1/2 relative overflow-hidden flex-col items-center justify-center p-12"
        style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #312e81 100%)' }}
      >

        <div style={{
          position: 'absolute', top: '-80px', left: '-80px',
          width: '400px', height: '400px', borderRadius: '50%',
          background: 'rgba(99,102,241,0.25)', filter: 'blur(80px)',
        }} />
        <div style={{
          position: 'absolute', bottom: '-60px', right: '-60px',
          width: '350px', height: '350px', borderRadius: '50%',
          background: 'rgba(59,130,246,0.2)', filter: 'blur(80px)',
        }} />
        <div style={{
          position: 'absolute', top: '45%', left: '55%',
          width: '200px', height: '200px', borderRadius: '50%',
          background: 'rgba(139,92,246,0.15)', filter: 'blur(60px)',
        }} />


        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.07) 1px, transparent 1px)',
          backgroundSize: '28px 28px',
        }} />


        <div className="relative z-10 text-center text-white max-w-sm">
          <div className="text-7xl mb-6 drop-shadow-lg">🎯</div>
          <h1 className="text-4xl font-bold mb-4 leading-tight">
            Smart Complaint System
          </h1>
          <p className="text-blue-200 text-lg leading-relaxed mb-10">
            AI-powered complaint management that classifies, prioritises, and resolves issues faster.
          </p>


          <div className="flex flex-col gap-3 text-sm text-left">
            {[
              { icon: '🤖', text: 'Auto-classify complaints with AI' },
              { icon: '⚡', text: 'Priority-based routing to agents' },
              { icon: '📧', text: 'Real-time email notifications' },
              { icon: '📊', text: 'Analytics & performance tracking' },
            ].map((f) => (
              <div key={f.text}
                className="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-xl px-4 py-3 border border-white/10">
                <span className="text-xl">{f.icon}</span>
                <span className="text-blue-100">{f.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>


      <div className="flex-1 flex items-center justify-center px-6 py-12
                      bg-gray-50 dark:bg-gray-950">
        <div className="w-full max-w-md">


          <div className="lg:hidden text-center mb-8">
            <div className="text-5xl mb-3">🎯</div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Smart Complaint System</h1>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl
                          dark:shadow-black/40 border border-gray-100
                          dark:border-gray-700 p-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Welcome back</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-7">Sign in to your account to continue</p>

            {error && (
              <div className="bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800
                              text-red-700 dark:text-red-400 px-4 py-3 rounded-xl mb-5 text-sm flex items-center gap-2">
                <span>⚠️</span> {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
                  Email address
                </label>
                <input
                  type="email"
                  className="input-field"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  className="input-field"
                  placeholder="••••••••"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl font-semibold text-white transition-all
                           bg-gradient-to-r from-blue-600 to-indigo-600
                           hover:from-blue-700 hover:to-indigo-700
                           disabled:opacity-50 disabled:cursor-not-allowed shadow-md
                           hover:shadow-blue-500/25 hover:shadow-lg"
              >
                {loading ? 'Signing in…' : 'Sign In →'}
              </button>
            </form>

            <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-7">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-600 dark:text-blue-400 font-semibold hover:underline">
                Create one
              </Link>
            </p>
          </div>

          <p className="text-center text-xs text-gray-400 dark:text-gray-600 mt-5">
            Demo · admin@demo.com / admin123
          </p>
        </div>
      </div>
    </div>
  )
}
