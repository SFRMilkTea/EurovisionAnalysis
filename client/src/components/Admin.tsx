import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import { api } from '../api/client'
import type { AdminData, CatalogItem, FormValues } from '../types'
import { SongForm } from './SongForm'

type Tab = 'songs' | 'events' | 'users' | 'countries' | 'genres' | 'languages'
const tabs: Array<[Tab, string]> = [['songs', 'Песни'], ['events', 'Мероприятия'], ['users', 'Пользователи'], ['countries', 'Страны'], ['genres', 'Жанры'], ['languages', 'Языки']]
const Field = ({ label, children }: { label: string; children: ReactNode }) => <label>{label}{children}</label>

function Select({ value, onChange, options, blank = false, multiple = false }: { value: string | number | readonly string[] | undefined | null; onChange: (value: string | string[]) => void; options: Array<CatalogItem | string>; blank?: boolean; multiple?: boolean }) {
  return <select value={value ?? (multiple ? [] : '')} multiple={multiple} onChange={event => onChange(multiple ? [...event.target.selectedOptions].map(option => option.value) : event.target.value)}>{blank && <option value="">—</option>}{options.map(option => <option key={typeof option === 'string' ? option : option.id} value={typeof option === 'string' ? option : option.id}>{typeof option === 'string' ? option : option.name}</option>)}</select>
}

function Editor({ initial, render, submit }: { initial: FormValues; render: (value: FormValues, set: (key: string, item: FormValues[string]) => void) => ReactNode; submit: (value: FormValues) => void }) {
  const [value, setValue] = useState<FormValues>(initial)
  return <form className="editor" onSubmit={event => { event.preventDefault(); submit(value); setValue(initial) }}>{render(value, (key, item) => setValue({ ...value, [key]: item }))}<button type="submit">Добавить</button></form>
}

function SectionHeading({ title, count, children }: { title: string; count?: number; children?: ReactNode }) {
  return <div className="section-heading"><div><h2>{title}</h2>{children && <p>{children}</p>}</div>{count !== undefined && <span className="count-badge">{count}</span>}</div>
}

export function Admin({ onBack, onEditSong }: { onBack: () => void; onEditSong: (songId: number) => void }) {
  const [data, setData] = useState<AdminData | null>(null), [tab, setTab] = useState<Tab>('songs'), [notice, setNotice] = useState('')
  const load = () => void api.admin().then(result => { if (result) setData(result) }).catch(error => setNotice((error as Error).message))
  useEffect(load, [])
  async function action(url: string, values: FormValues, question?: string) { if (question && !window.confirm(question)) return; try { await api.adminAction(url, values); const result = await api.adminMessage(); const message = result?.message; setNotice(message?.text ?? 'Сохранено'); if (message?.kind !== 'error') load() } catch (error) { setNotice((error as Error).message) } }
  if (!data) return <main className="loading-screen"><span className="loader" />Загружаем данные…{notice && <p className="alert error">{notice}</p>}</main>

  const Catalog = ({ type, title }: { type: 'countries' | 'genres' | 'languages'; title: string }) => <section className="content-card">
    <SectionHeading title={title} count={data[type].length}>Добавляйте новые значения или изменяйте существующие прямо в таблице.</SectionHeading>
    <form className="inline add-row" onSubmit={(event: FormEvent<HTMLFormElement>) => { event.preventDefault(); void action(type === 'countries' ? '/admin/countries' : `/admin/catalog/${type}`, { name: new FormData(event.currentTarget).get('name') as string }); event.currentTarget.reset() }}><input name="name" placeholder="Новое название" aria-label="Новое название" required /><button type="submit">Добавить</button></form>
    <div className="table admin-table compact-table"><table><tbody>{data[type].map(item => <tr key={item.id}><td><input aria-label={`Название: ${item.name}`} defaultValue={item.name} onBlur={event => void action(`/admin/${type}/${item.id}/update`, { name: event.target.value })} /></td><td className="action-cell"><button type="button" className="danger button-small" onClick={() => void action(`/admin/${type}/${item.id}/delete`, {}, 'Удалить запись?')}>Удалить</button></td></tr>)}</tbody></table></div>
  </section>

  return <main className="app-shell admin-page">
    <header className="topbar"><div className="brand"><span className="brand-mark small" aria-hidden="true">E</span><div><span className="eyebrow">Панель управления</span><h1>Администрирование</h1></div></div><button type="button" className="button-ghost" onClick={onBack}>← К оценкам</button></header>
    {notice && <p className={`alert ${notice === 'Сохранено' || notice.toLowerCase().includes('сохран') ? 'success' : 'error'}`} role="status">{notice}</p>}
    <nav className="tabs admin-tabs" aria-label="Разделы администрирования">{tabs.map(([id, title]) => <button type="button" key={id} onClick={() => setTab(id)} className={tab === id ? 'active' : ''} aria-pressed={tab === id}>{title}</button>)}</nav>
    {tab === 'countries' && <Catalog type="countries" title="Страны" />}
    {tab === 'genres' && <Catalog type="genres" title="Жанры" />}
    {tab === 'languages' && <Catalog type="languages" title="Языки" />}
    {tab === 'events' && <Events data={data} action={action} />}
    {tab === 'users' && <Users data={data} action={action} />}
    {tab === 'songs' && <Songs data={data} action={action} onEditSong={onEditSong} />}
  </main>
}

function Events({ data, action }: { data: AdminData; action: (url: string, values: FormValues, question?: string) => void }) {
  const blank = { name: '', year: new Date().getFullYear(), host_id: data.countries[0]?.id }
  return <section className="content-card"><SectionHeading title="Мероприятия" count={data.events.length}>Управляйте сезонами и доступностью этапов голосования.</SectionHeading>
    <Editor initial={blank} submit={value => action('/admin/events', value)} render={(value, set) => <><Field label="Название"><input value={String(value.name)} onChange={event => set('name', event.target.value)} required /></Field><Field label="Год"><input type="number" value={Number(value.year)} onChange={event => set('year', event.target.value)} required /></Field><Field label="Страна-хозяин"><Select value={value.host_id as number} onChange={item => set('host_id', item)} options={data.countries} /></Field></>} />
    <div className="table admin-table"><table><thead><tr><th>Название</th><th>Год</th><th>Страна-хозяин</th><th>Этапы</th><th /></tr></thead><tbody>{data.events.map(item => <tr key={item.id}><td><input aria-label="Название мероприятия" defaultValue={item.name} onBlur={event => action(`/admin/events/${item.id}/update`, { ...item, name: event.target.value })} /></td><td><input aria-label="Год мероприятия" type="number" defaultValue={item.year} onBlur={event => action(`/admin/events/${item.id}/update`, { ...item, year: event.target.value })} /></td><td><Select value={item.host_id} onChange={value => action(`/admin/events/${item.id}/update`, { ...item, host_id: value })} options={data.countries} /></td><td><div className="switch-list">{([['is_current', 'Текущее'], ['first_stage_open', 'Первый этап'], ['final_stage_open', 'Финал']] as const).map(([key, label]) => <label key={key}><input type="checkbox" role="switch" defaultChecked={item[key]} onChange={event => action(`/admin/events/${item.id}/settings`, { is_current: key === 'is_current' ? event.target.checked : item.is_current, first_stage_open: key === 'first_stage_open' ? event.target.checked : item.first_stage_open, final_stage_open: key === 'final_stage_open' ? event.target.checked : item.final_stage_open })} />{label}</label>)}</div></td><td className="action-cell"><button type="button" className="danger button-small" onClick={() => action(`/admin/events/${item.id}/delete`, {}, 'Удалить мероприятие?')}>Удалить</button></td></tr>)}</tbody></table></div>
  </section>
}

function Users({ data, action }: { data: AdminData; action: (url: string, values: FormValues, question?: string) => void }) {
  return <section className="content-card"><SectionHeading title="Пользователи" count={data.users.length}>Добавляйте участников и настраивайте их доступ.</SectionHeading>
    <Editor initial={{ username: '', email: '', password: '', is_admin: false }} submit={value => action('/admin/users', value)} render={(value, set) => <><Field label="Имя"><input value={String(value.username)} onChange={event => set('username', event.target.value)} required /></Field><Field label="Почта"><input type="email" value={String(value.email)} onChange={event => set('email', event.target.value)} required /></Field><Field label="Пароль"><input type="password" value={String(value.password)} onChange={event => set('password', event.target.value)} required /></Field><label className="checkbox-field"><input type="checkbox" checked={Boolean(value.is_admin)} onChange={event => set('is_admin', event.target.checked)} />Администратор</label></>} />
    <div className="table admin-table"><table><thead><tr><th>Пользователь</th><th>Почта</th><th>Администратор</th><th>Активен</th><th /></tr></thead><tbody>{data.users.map(item => <tr key={item.id}><td><input aria-label="Имя пользователя" defaultValue={item.username} onBlur={event => action(`/admin/users/${item.id}/update`, { ...item, username: event.target.value })} /></td><td>{item.email}</td><td><input aria-label="Права администратора" type="checkbox" role="switch" defaultChecked={item.is_admin} onChange={event => action(`/admin/users/${item.id}/update`, { ...item, is_admin: event.target.checked })} /></td><td><input aria-label="Пользователь активен" type="checkbox" role="switch" defaultChecked={item.is_active} onChange={event => action(`/admin/users/${item.id}/update`, { ...item, is_active: event.target.checked })} /></td><td className="action-cell"><button type="button" className="danger button-small" onClick={() => action(`/admin/users/${item.id}/delete`, {}, 'Удалить пользователя?')}>Удалить</button></td></tr>)}</tbody></table></div>
  </section>
}

function Songs({ data, action, onEditSong }: { data: AdminData; action: (url: string, values: FormValues, question?: string) => void; onEditSong: (songId: number) => void }) {
  const blank: FormValues = { name: '', artist: '', year: new Date().getFullYear(), vocal: data.vocals[0], country_id: data.countries[0]?.id, event_id: '', bpm: '', key: '', energy: '', danceability: '', happiness: '', url: '', genre_ids: [], language_ids: [] }
  return <section className="content-card"><SectionHeading title="Песни" count={data.songs.length}>Добавляйте участников и редактируйте музыкальные характеристики.</SectionHeading>
    <details className="create-panel"><summary>Добавить новую песню</summary><SongForm initial={blank} data={data} submitLabel="Добавить песню" onSubmit={value => action('/admin/songs', value)} /></details>
    <div className="table admin-table songs-table"><table><thead><tr><th>Песня</th><th>Год и вокал</th><th>Страна и мероприятие</th><th>Характеристики</th><th /></tr></thead><tbody>{data.songs.map(song => <tr key={song.id}><td className="song-title"><strong>{song.name}</strong><small>{song.artist}</small></td><td>{song.year}<br /><span className="muted">{song.vocal}</span></td><td>{song.country}<br /><span className="muted">{song.event || 'Без мероприятия'}</span></td><td className="metrics-summary"><span>BPM <b>{song.bpm ?? '—'}</b></span><span>Энергия <b>{song.energy ?? '—'}</b></span><span>Танцы <b>{song.danceability ?? '—'}</b></span><span>Позитив <b>{song.happiness ?? '—'}</b></span></td><td><div className="song-actions"><button type="button" className="button-small" onClick={() => onEditSong(song.id)}>Изменить</button><button type="button" className="danger button-small" onClick={() => action(`/admin/songs/${song.id}/delete`, {}, 'Удалить песню?')}>Удалить</button></div></td></tr>)}</tbody></table></div>
  </section>
}
