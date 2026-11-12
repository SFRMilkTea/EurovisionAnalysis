import { request, toFormData } from './http'
import type { AdminData, DashboardData, FormValues, User } from '../types'

export const api = {
  me: () => request<User>('/api/me'),
  login: (form: FormData) =>
    request<User>('/api/session/login', { method: 'POST', body: form }),
  logout: () => request('/api/session/logout', { method: 'POST' }),
  dashboard: (eventId?: number | null, signal?: AbortSignal) =>
    request<DashboardData>(
      `/api/dashboard${eventId ? `?event_id=${eventId}` : ''}`,
      { signal },
    ),
  saveOpinionScore: (values: FormValues) =>
    request('/opinions/score', { method: 'POST', body: toFormData(values) }),
  saveOpinionNote: (values: FormValues) =>
    request('/opinions/note', { method: 'POST', body: toFormData(values) }),
  admin: () => request<AdminData>('/api/admin'),
  adminMessage: () =>
    request<{ message: { text: string; kind: string } | null }>(
      '/api/admin/message',
    ),
  adminAction: (url: string, values: FormValues) =>
    request(url, { method: 'POST', body: toFormData(values) }),
}
