import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { api } from '../api/client'
import type { DashboardData, Opinion, Song, Stage, User } from '../types'

const SCORES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12]

function AutoGrowComment({ value, onSave }: { value: string; onSave: (value: string) => void }) {
  const ref = useRef<HTMLTextAreaElement>(null)
  const resize = (element: HTMLTextAreaElement) => {
    element.style.height = 'auto'
    element.style.height = `${element.scrollHeight}px`
  }
  useLayoutEffect(() => { if (ref.current) resize(ref.current) }, [value])
  return <textarea ref={ref} rows={1} defaultValue={value} onInput={event => resize(event.currentTarget)} onBlur={event => onSave(event.currentTarget.value)} placeholder="Напишите мнение…" />
}

export function Dashboard({ me, onLogout, onAdmin }: { me: User; onLogout: () => void; onAdmin: () => void }) {
  const [data, setData] = useState<DashboardData | null>(null), [eventId, setEventId] = useState<number | null>(null), [error, setError] = useState('')
  const load = async (id: number | null = eventId) => { try { const result = await api.dashboard(id); if (result) { setData(result); setEventId(result.selected_event_id) } } catch (e) { setError((e as Error).message) } }
  useEffect(() => { void load() }, [])
  const opinions = useMemo(() => new Map<string, Opinion>((data?.opinions ?? []).map(item => [`${item.song_id}:${item.user_id}:${item.stage}`, item])), [data])
  async function save(songId: number, stage: Stage, score: number | string, note: string) { try { await api.saveOpinion({ song_id: songId, event_id: eventId, stage, score: Number(score), note }); await load() } catch (e) { setError((e as Error).message) } }
  if (!data) return <main className="container">Загрузка… {error && <p className="error">{error}</p>}</main>
  const Cell = ({ song, user, stage, open }: { song: Song; user: User; stage: Stage; open: boolean }) => { const opinion = opinions.get(`${song.id}:${user.id}:${stage}`), editable = user.id === me.id && open; if (!editable) return <><td>{opinion?.score ?? '–'}</td><td className="note">{opinion?.note || '–'}</td></>; return <><td className="mine"><select value={opinion?.score ?? 0} onChange={event => void save(song.id, stage, event.target.value, opinion?.note || '')}>{SCORES.map(score => <option key={score}>{score}</option>)}</select></td><td className="mine note"><AutoGrowComment value={opinion?.note || ''} onSave={note => void save(song.id, stage, opinion?.score ?? 0, note)} /></td></> }
  const average = (song: Song, stage: Stage) => { const scores = data.users.map(user => opinions.get(`${song.id}:${user.id}:${stage}`)?.score).filter((score): score is number => score !== undefined); return scores.length ? (scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(1) : '–' }
  const event = data.events.find(item => item.id === eventId)
  return <main className="container wide"><header><h1>🎵 Еврокомиссия</h1><div>Вы вошли как <b>{me.username}</b>{me.is_admin && <button className="secondary" onClick={onAdmin}>Администрирование</button>}<button className="secondary" onClick={onLogout}>Выйти</button></div></header><p><small>Кто найдет больше багов, тому дадим эксклюзивный смайлик в имя</small></p>{error && <p className="error">{error}</p>}<nav className="tabs">{data.events.map(item => <button className={item.id === eventId ? 'active' : ''} onClick={() => void load(item.id)} key={item.id}>{item.name} {item.year}</button>)}</nav>{data.events.length === 0 ? <p>Мероприятия пока не добавлены.</p> : <div className="table"><table><thead><tr><th rowSpan={3} className="sticky">Страна / песня</th><th colSpan={data.users.length * 2 + 1}>Первое прослушивание</th><th colSpan={data.users.length * 2 + 1}>Финальное прослушивание</th></tr><tr>{data.users.map(user => <th colSpan={2} className={user.id === me.id ? 'mine' : ''} key={`first-${user.id}`}>{user.username}</th>)}<th rowSpan={2}>Средняя</th>{data.users.map(user => <th colSpan={2} className={user.id === me.id ? 'mine' : ''} key={`final-${user.id}`}>{user.username}</th>)}<th rowSpan={2}>Средняя</th></tr><tr>{[...data.users, ...data.users].map((_, index) => <><th key={`score-${index}`}>Оценка</th><th key={`note-${index}`}>Мнение</th></>)}</tr></thead><tbody>{data.songs.map(song => <tr key={song.id}><td className="sticky"><b>{song.country}</b><br />{song.url ? <a href={song.url} target="_blank" rel="noreferrer">{song.name}</a> : song.name}<br /><small>{song.artist}</small></td>{data.users.map(user => <Cell key={`first-${user.id}`} song={song} user={user} stage="FIRST" open={Boolean(event?.first_stage_open)} />)}<td className="average">{average(song, 'FIRST')}</td>{data.users.map(user => <Cell key={`final-${user.id}`} song={song} user={user} stage="FINAL" open={Boolean(event?.final_stage_open)} />)}<td className="average">{average(song, 'FINAL')}</td></tr>)}</tbody></table></div>}</main>
}
