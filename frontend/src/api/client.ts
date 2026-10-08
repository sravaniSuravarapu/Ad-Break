import { ApiError } from './errors'

const TOKEN_KEY = 'adbreak_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(`/api/v1${path}`, { ...options, headers })
  if (response.status === 204) return undefined as T
  const body: unknown = await response.json().catch(() => ({}))
  if (!response.ok) throw new ApiError(response.status, body)
  return body as T
}
