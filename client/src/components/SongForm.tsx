import { useState, type FormEvent } from 'react'
import type { AdminData, CatalogItem, FormValues } from '../types'

interface SongFormProps {
  initial: FormValues
  data: AdminData
  submitLabel: string
  onSubmit: (values: FormValues) => void
}

function ComboList({ label, options, initial, onChange }: { label: string; options: CatalogItem[]; initial: Array<number | string>; onChange: (values: string[]) => void }) {
  const [items, setItems] = useState<string[]>(initial.length ? initial.map(String) : [''])
  const selected = items.filter(Boolean)
  const update = (index: number, value: string) => {
    const next = [...items]
    next[index] = value
    setItems(next)
    onChange(next.filter(Boolean))
  }
  const add = () => { if (selected.length < options.length && items.every(Boolean)) setItems(current => [...current, '']) }
  const remove = (index: number) => {
    const next = items.length === 1 ? [''] : items.filter((_, itemIndex) => itemIndex !== index)
    setItems(next)
    onChange(next.filter(Boolean))
  }
  return <div className="combo-list"><span className="combo-label">{label}</span>{items.map((value, index) => <div className="combo-row" key={index}><select value={value} onChange={event => update(index, event.target.value)}><option value="">Выберите значение</option>{options.filter(option => option.id.toString() === value || !selected.includes(option.id.toString())).map(option => <option key={option.id} value={option.id}>{option.name}</option>)}</select><button type="button" className="combo-remove secondary outline" onClick={() => remove(index)} aria-label={`Удалить поле «${label}»`}>×</button></div>)}<button type="button" className="combo-add secondary outline" onClick={add} disabled={selected.length >= options.length || items.some(item => !item)}>+ Добавить</button></div>
}

export function SongForm({ initial, data, submitLabel, onSubmit }: SongFormProps) {
  const [value, setValue] = useState<FormValues>(initial)
  const set = (key: string, item: FormValues[string]) => setValue(current => ({ ...current, [key]: item }))
  const submit = (event: FormEvent) => { event.preventDefault(); onSubmit(value) }

  return <form className="song-form" onSubmit={submit}>
    <fieldset><legend>Основная информация</legend><div className="form-grid">
      <label>Название<input value={String(value.name ?? '')} onChange={event => set('name', event.target.value)} required /></label>
      <label>Исполнитель<input value={String(value.artist ?? '')} onChange={event => set('artist', event.target.value)} required /></label>
      <label>Год<input type="number" value={String(value.year ?? '')} onChange={event => set('year', event.target.value)} required /></label>
      <label>Вокал<select value={String(value.vocal ?? '')} onChange={event => set('vocal', event.target.value)}>{data.vocals.map(item => <option key={item}>{item}</option>)}</select></label>
      <label>Страна<select value={String(value.country_id ?? '')} onChange={event => set('country_id', event.target.value)} required>{data.countries.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
      <label>Мероприятие<select value={String(value.event_id ?? '')} onChange={event => set('event_id', event.target.value)}><option value="">Без мероприятия</option>{data.events.map(item => <option key={item.id} value={item.id}>{item.name} {item.year}</option>)}</select></label>
      <label className="span-2">Ссылка<input type="url" value={String(value.url ?? '')} onChange={event => set('url', event.target.value)} placeholder="https://…" /></label>
    </div></fieldset>
    <fieldset><legend>Музыкальные характеристики</legend><div className="form-grid metrics">
      <label>BPM<input type="number" min="0" value={String(value.bpm ?? '')} onChange={event => set('bpm', event.target.value)} /></label>
      <label>Тональность<input value={String(value.key ?? '')} onChange={event => set('key', event.target.value)} /></label>
      {([['Энергия','energy'],['Танцевальность','danceability'],['Позитивность','happiness']] as const).map(([label,key]) => <label key={key}>{label}<input type="number" min="0" max="100" value={String(value[key] ?? '')} onChange={event => set(key, event.target.value)} /></label>)}
    </div></fieldset>
    <fieldset><legend>Классификация</legend><div className="form-grid">
      <ComboList label="Жанры" options={data.genres} initial={(value.genre_ids as Array<number | string>) ?? []} onChange={items => set('genre_ids', items)} />
      <ComboList label="Языки" options={data.languages} initial={(value.language_ids as Array<number | string>) ?? []} onChange={items => set('language_ids', items)} />
    </div></fieldset>
    <div className="form-actions"><button type="submit">{submitLabel}</button></div>
  </form>
}
