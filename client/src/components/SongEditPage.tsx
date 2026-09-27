import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { AdminData, FormValues } from '../types'
import { SongForm } from './SongForm'

export function SongEditPage({ songId, onBack }: { songId: number; onBack: () => void }) {
  const [data, setData] = useState<AdminData | null>(null)
  const [notice, setNotice] = useState('')
  useEffect(() => { void api.admin().then(result => { if (result) setData(result) }).catch(error => setNotice((error as Error).message)) }, [])
  if (!data) return <main className="loading-screen"><span className="loader" />Загружаем песню…{notice && <p className="alert error">{notice}</p>}</main>
  const song = data.songs.find(item => item.id === songId)
  if (!song) return <main className="app-shell"><button className="button-ghost" onClick={onBack}>← Назад</button><section className="empty-state"><span>♫</span><h3>Песня не найдена</h3><p>Возможно, она была удалена.</p></section></main>
  async function save(values: FormValues) {
    try {
      await api.adminAction(`/admin/songs/${songId}/update`, values)
      const result = await api.adminMessage()
      setNotice(result?.message?.text ?? 'Песня сохранена')
      if (result?.message?.kind !== 'error') { const refreshed = await api.admin(); if (refreshed) setData(refreshed) }
    } catch (error) { setNotice((error as Error).message) }
  }
  return <main className="app-shell song-edit-page"><header className="topbar"><div className="brand"><button className="back-button" onClick={onBack} aria-label="Вернуться к списку песен">←</button><div><span className="eyebrow">Редактирование песни</span><h1>{song.name}</h1><p>{song.artist} · {song.country}</p></div></div></header>{notice && <p className={`alert ${notice.toLowerCase().includes('сохран') ? 'success' : 'error'}`}>{notice}</p>}<section className="content-card"><SongForm key={JSON.stringify(song)} initial={song as unknown as FormValues} data={data} submitLabel="Сохранить изменения" onSubmit={values => void save(values)} /></section></main>
}
