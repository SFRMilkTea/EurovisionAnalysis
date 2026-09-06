import { useEffect, useState } from 'react'
import { api } from './api/client'
import { Admin } from './components/Admin'
import { Dashboard } from './components/Dashboard'
import { Login } from './components/Login'
import { SongEditPage } from './components/SongEditPage'
import type { User } from './types'

export default function App() {
  const [me, setMe] = useState<User | null | undefined>(undefined)
  const [path, setPath] = useState(location.pathname)
  useEffect(() => { void api.me().then(setMe).catch(() => setMe(null)) }, [])
  useEffect(() => { const handlePopState = () => setPath(location.pathname); addEventListener('popstate', handlePopState); return () => removeEventListener('popstate', handlePopState) }, [])
  const navigate = (nextPath: string) => { history.pushState({}, '', nextPath); setPath(nextPath) }
  if (me === undefined) return null
  if (!me) return <Login onLogin={user => { setMe(user); history.replaceState({}, '', '/'); setPath('/') }} />
  const songMatch = path.match(/^\/admin\/songs\/(\d+)$/)
  if (songMatch && me.is_admin) return <SongEditPage songId={Number(songMatch[1])} onBack={() => navigate('/admin')} />
  if (path === '/admin' && me.is_admin) return <Admin onBack={() => navigate('/')} onEditSong={songId => navigate(`/admin/songs/${songId}`)} />
  return <Dashboard me={me} onAdmin={() => navigate('/admin')} onLogout={() => { void api.logout().then(() => { setMe(null); history.replaceState({}, '', '/') }) }} />
}
