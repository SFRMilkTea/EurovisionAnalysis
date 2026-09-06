import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { AdminData, FormValues } from '../types'
import { SongForm } from './SongForm'

export function SongEditPage({ songId, onBack }: { songId: number; onBack: () => void }) {
  const [data, setData] = useState<AdminData | null>(null)
  const [notice, setNotice] = useState('')
  useEffect(() => { void api.admin().then(result => { if (result) setData(result) }).catch(error => setNotice((error as Error).message)) }, [])
  if (!data) return <main className="container">Загрузка… {notice && <p className="error">{notice}</p>}</main>
  const song = data.songs.find(item => item.id === songId)
  if (!song) return <main className="container"><button className="secondary" onClick={onBack}>← Назад</button><p className="error">Песня не найдена.</p></main>
  async function save(values: FormValues) {
    try {
      await api.adminAction(`/admin/songs/${songId}/update`, values)
      const result = await api.adminMessage()
      setNotice(result?.message?.text ?? 'Песня сохранена')
      if (result?.message?.kind !== 'error') { const refreshed = await api.admin(); if (refreshed) setData(refreshed) }
    } catch (error) { setNotice((error as Error).message) }
  }
  return <main className="container song-edit-page"><header><div><button className="secondary" onClick={onBack}>← К списку песен</button><div><small>Редактирование песни</small><h1>{song.name}</h1><p>{song.artist}, {song.country}</p></div></div></header>{notice && <p className={notice.includes('сохран') ? 'notice' : 'error'}>{notice}</p>}<SongForm key={JSON.stringify(song)} initial={song as unknown as FormValues} data={data} submitLabel="Сохранить изменения" onSubmit={values => void save(values)} /></main>
}
