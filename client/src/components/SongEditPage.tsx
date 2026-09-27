import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { AdminData, FormValues } from '../types'
import { Notification, type NotificationType } from './Notification'
import { SongForm } from './SongForm'

export function SongEditPage({ songId, onBack }: { songId: number; onBack: () => void }) {
  const [data, setData] = useState<AdminData | null>(null)
  const [notice, setNotice] = useState<{ type: NotificationType; text: string } | null>(null)
  useEffect(() => { void api.admin().then(result => { if (result) setData(result) }).catch(error => setNotice({ type: 'error', text: (error as Error).message })) }, [])
  if (!data) return <main className="loading-screen"><span className="loader" />Загружаем песню…{notice && <Notification type={notice.type} message={notice.text} onClose={() => setNotice(null)} />}</main>
  const song = data.songs.find(item => item.id === songId)
  if (!song) return <main className="app-shell"><button className="button-ghost" onClick={onBack}>← Назад</button><section className="empty-state"><span>♫</span><h3>Песня не найдена</h3><p>Возможно, она была удалена.</p></section></main>
  async function save(values: FormValues) {
    try {
      await api.adminAction(`/admin/songs/${songId}/update`, values)
      const result = await api.adminMessage()
      const type: NotificationType = result?.message?.kind === 'error' ? 'error' : result?.message?.kind === 'warning' ? 'warning' : 'success'
      setNotice({ type, text: result?.message?.text ?? 'Песня сохранена' })
      if (result?.message?.kind !== 'error') { const refreshed = await api.admin(); if (refreshed) setData(refreshed) }
    } catch (error) { setNotice({ type: 'error', text: (error as Error).message }) }
  }
  return <main className="app-shell song-edit-page"><header className="topbar"><div className="brand"><button className="back-button" onClick={onBack} aria-label="Вернуться к списку песен">←</button><div><span className="eyebrow">Редактирование песни</span><h1>{song.name}</h1><p>{song.artist} · {song.country}</p></div></div></header>{notice && <Notification type={notice.type} message={notice.text} onClose={() => setNotice(null)} />}<section className="content-card"><SongForm key={JSON.stringify(song)} initial={song as unknown as FormValues} data={data} submitLabel="Сохранить изменения" onSubmit={values => void save(values)} /></section></main>
}
