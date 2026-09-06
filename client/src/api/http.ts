import type { FormValues } from '../types'

export async function request<T>(url: string, options: RequestInit = {}): Promise<T | null> {
  const response = await fetch(url, { credentials: 'same-origin', ...options })
  if (!response.ok) {
    const payload = await response.json().catch(() => ({})) as { detail?: string }
    throw new Error(payload.detail ?? 'Не удалось выполнить запрос')
  }
  return response.headers.get('content-type')?.includes('application/json') ? response.json() as Promise<T> : null
}

export function toFormData(values: FormValues): FormData {
  const data = new FormData()
  Object.entries(values).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '' || value === false) return
    if (Array.isArray(value)) value.forEach(item => data.append(key, String(item)))
    else data.append(key, String(value))
  })
  return data
}
