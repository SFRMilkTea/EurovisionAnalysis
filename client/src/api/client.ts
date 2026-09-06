import { request, toFormData } from './http'
import type { AdminData, DashboardData, FormValues, User } from '../types'

export const api = {
  me: () => request<User>('/api/me'),
  login: (form: FormData) => request<User>('/api/session/login', { method: 'POST', body: form }),
  logout: () => request('/api/session/logout', { method: 'POST' }),
  dashboard: (eventId?: number | null) => request<DashboardData>(`/api/dashboard${eventId ? `?event_id=${eventId}` : ''}`),
  saveOpinion: (values: FormValues) => request('/opinions/save', { method: 'POST', body: toFormData(values) }),
  admin: () => request<AdminData>('/api/admin'),
  adminMessage: () => request<{ message: { text: string; kind: string } | null }>('/api/admin/message'),
  adminAction: (url: string, values: FormValues) => request(url, { method: 'POST', body: toFormData(values) }),
}
