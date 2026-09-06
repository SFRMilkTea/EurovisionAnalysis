import { useState, type FormEvent } from 'react'
import { api } from '../api/client'
import type { User } from '../types'

export function Login({ onLogin }: { onLogin: (user: User) => void }) {
  const [error, setError] = useState('')
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('')
    try { const user = await api.login(new FormData(event.currentTarget)); if (user) onLogin(user) } catch (e) { setError((e as Error).message) }
  }
  return <main className="login"><article><h1>Еврокомиссия</h1><p>Войдите, чтобы посмотреть и заполнить оценки.</p>{error && <p className="error">{error}</p>}<form onSubmit={submit}><label>Почта<input name="email" type="email" required autoFocus /></label><label>Пароль<input name="password" type="password" required /></label><button>Войти</button></form></article></main>
}
