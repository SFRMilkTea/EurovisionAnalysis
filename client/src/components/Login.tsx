import { useState, type FormEvent } from 'react'
import { api } from '../api/client'
import type { User } from '../types'

export function Login({ onLogin }: { onLogin: (user: User) => void }) {
  const [error, setError] = useState('')
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError('')
    try { const user = await api.login(new FormData(event.currentTarget)); if (user) onLogin(user) } catch (e) { setError((e as Error).message) }
  }
  return <main className="login-page">
    <section className="login-card">
      <div className="brand-mark" aria-hidden="true">E</div>
      <div className="login-heading">
        <span className="eyebrow">Добро пожаловать</span>
        <h1>Еврокомиссия</h1>
        <p>Оценивайте выступления и делитесь впечатлениями.</p>
      </div>
      {error && <p className="alert error" role="alert">{error}</p>}
      <form className="login-form" onSubmit={submit}>
        <label>Почта<input name="email" type="email" autoComplete="email" placeholder="name@example.com" required autoFocus /></label>
        <label>Пароль<input name="password" type="password" autoComplete="current-password" placeholder="Введите пароль" required /></label>
        <button type="submit">Войти</button>
      </form>
    </section>
  </main>
}
