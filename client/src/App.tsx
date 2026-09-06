import { useEffect, useState } from 'react'
import { api } from './api/client'
import { Admin } from './components/Admin'
import { Dashboard } from './components/Dashboard'
import { Login } from './components/Login'
import type { User } from './types'

export default function App() {
  const [me, setMe] = useState<User | null | undefined>(undefined)
  const [view, setView] = useState<'dashboard' | 'admin'>(location.pathname === '/admin' ? 'admin' : 'dashboard')
  useEffect(() => { void api.me().then(setMe).catch(() => setMe(null)) }, [])
  if (me === undefined) return null
  if (!me) return <Login onLogin={user => { setMe(user); setView('dashboard'); history.replaceState({}, '', '/') }} />
  if (view === 'admin' && me.is_admin) return <Admin onBack={() => { setView('dashboard'); history.pushState({}, '', '/') }} />
  return <Dashboard me={me} onAdmin={() => { setView('admin'); history.pushState({}, '', '/admin') }} onLogout={() => { void api.logout().then(() => setMe(null)) }} />
}
