export type Stage = 'FIRST' | 'FINAL'
export type Id = number | string

export interface User { id: number; username: string; email?: string | null; is_admin: boolean; is_active?: boolean }
export interface Event { id: number; name: string; year: number; host_id?: number; host?: string; is_current: boolean; first_stage_open: boolean; final_stage_open: boolean }
export interface Song { id: number; country_id?: number; country: string; event_id?: number | null; event?: string | null; year?: number; name: string; artist: string; vocal?: string; bpm?: number | null; key?: string | null; energy?: number | null; danceability?: number | null; happiness?: number | null; url?: string | null; genre_ids?: number[]; language_ids?: number[] }
export interface Opinion { song_id: number; user_id: number; stage: Stage; score: number; note: string | null }
export interface CatalogItem { id: number; name: string }
export interface DashboardData { events: Event[]; selected_event_id: number | null; songs: Song[]; users: User[]; opinions: Opinion[]; current_user: User }
export interface AdminData { countries: CatalogItem[]; genres: CatalogItem[]; languages: CatalogItem[]; events: Event[]; users: User[]; songs: Song[]; vocals: string[] }
export type FormValues = Record<string, string | number | boolean | null | undefined | Array<string | number>>
