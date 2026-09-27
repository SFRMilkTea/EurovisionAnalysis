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
  if (!data) return <main className="loading-screen"><span className="loader" />Загружаем оценки…{error && <p className="alert error">{error}</p>}</main>
  const Cell = ({ song, user, stage, open }: { song: Song; user: User; stage: Stage; open: boolean }) => { const opinion = opinions.get(`${song.id}:${user.id}:${stage}`), editable = user.id === me.id && open; if (!editable) return <><td className="score-cell">{opinion?.score ?? '–'}</td><td className="note opinion-cell">{opinion?.note || <span className="muted">Нет мнения</span>}</td></>; return <><td className="mine score-cell"><select aria-label={`Оценка для ${song.name}`} value={opinion?.score ?? 0} onChange={event => void save(song.id, stage, event.target.value, opinion?.note || '')}>{SCORES.map(score => <option key={score}>{score}</option>)}</select></td><td className="mine note opinion-cell"><AutoGrowComment value={opinion?.note || ''} onSave={note => void save(song.id, stage, opinion?.score ?? 0, note)} /></td></> }
  const average = (song: Song, stage: Stage) => { const scores = data.users.map(user => opinions.get(`${song.id}:${user.id}:${stage}`)?.score).filter((score): score is number => score !== undefined); return scores.length ? (scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(1) : '–' }
  const event = data.events.find(item => item.id === eventId)
  return <main className="app-shell dashboard-page">
    <header className="topbar">
      <div className="brand"><span className="brand-mark small" aria-hidden="true">?</span><div><span className="eyebrow">Надо придумать название</span><h1>Надо придумать название</h1></div></div>
      <div className="user-menu"><span className="user-chip"><span className="avatar">{me.username.slice(0, 1).toUpperCase()}</span><span><small>Вы вошли как</small><b>{me.username}</b></span></span>{me.is_admin && <button type="button" className="button-quiet" onClick={onAdmin}>Администрирование</button>}<button type="button" className="button-ghost" onClick={onLogout}>Выйти</button></div>
    </header>
    <section className="page-intro"><div><span className="eyebrow">Общие оценки</span><h2>{event ? `${event.name} ${event.year}` : 'Выберите мероприятие'}</h2><p>Кто найдет больше всех багов, тому дадим эксклюзивный смайлик в имя</p></div>{event && <div className="stage-status"><span className={event.first_stage_open ? 'status open' : 'status'}>Первый этап · {event.first_stage_open ? 'открыт' : 'закрыт'}</span><span className={event.final_stage_open ? 'status open' : 'status'}>Финал · {event.final_stage_open ? 'открыт' : 'закрыт'}</span></div>}</section>
    {error && <p className="alert error" role="alert">{error}</p>}
    <nav className="tabs event-tabs" aria-label="Мероприятия">{data.events.map(item => <button type="button" aria-pressed={item.id === eventId} className={item.id === eventId ? 'active' : ''} onClick={() => void load(item.id)} key={item.id}><span>{item.name}</span><small>{item.year}</small></button>)}</nav>
    {data.events.length === 0 ? <section className="empty-state"><span>♫</span><h3>Мероприятий пока нет</h3><p>Как только администратор добавит мероприятие, оно появится здесь.</p></section> : <section className="data-panel"><div className="table dashboard-table"><table><thead><tr className="stage-row"><th rowSpan={3} className="sticky">Участник</th><th colSpan={data.users.length * 2 + 1}>Первое прослушивание</th><th colSpan={data.users.length * 2 + 1}>Финальное прослушивание</th></tr><tr className="people-row">{data.users.map(user => <th colSpan={2} className={user.id === me.id ? 'mine' : ''} key={`first-${user.id}`}>{user.username}{user.id === me.id && <small>Вы</small>}</th>)}<th rowSpan={2}>Средняя</th>{data.users.map(user => <th colSpan={2} className={user.id === me.id ? 'mine' : ''} key={`final-${user.id}`}>{user.username}{user.id === me.id && <small>Вы</small>}</th>)}<th rowSpan={2}>Средняя</th></tr><tr className="labels-row">{[...data.users, ...data.users].flatMap((user, index) => [<th key={`score-${user.id}-${index}`}>Оценка</th>, <th key={`note-${user.id}-${index}`}>Мнение</th>])}</tr></thead><tbody>{data.songs.map(song => <tr key={song.id}><td className="sticky song-cell"><span className="country">{song.country}</span>{song.url ? <a href={song.url} target="_blank" rel="noreferrer">{song.name}<span aria-hidden="true"> ↗</span></a> : <strong>{song.name}</strong>}<small>{song.artist}</small></td>{data.users.map(user => <Cell key={`first-${user.id}`} song={song} user={user} stage="FIRST" open={Boolean(event?.first_stage_open)} />)}<td className="average">{average(song, 'FIRST')}</td>{data.users.map(user => <Cell key={`final-${user.id}`} song={song} user={user} stage="FINAL" open={Boolean(event?.final_stage_open)} />)}<td className="average">{average(song, 'FINAL')}</td></tr>)}</tbody></table></div></section>}
  </main>
}
