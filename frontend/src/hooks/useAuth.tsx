import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api, getToken, setToken } from '../api/client'
import { ApiError } from '../api/errors'
import type { TokenResponse, User } from '../api/types'

interface AuthValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, role: User['role']) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [token, setTokenState] = useState<string | null>(() => getToken())
  const me = useQuery({
    queryKey: ['me', token],
    queryFn: () => api<User>('/auth/me'),
    enabled: Boolean(token),
    retry: false,
  })

  useEffect(() => {
    if (me.error instanceof ApiError && me.error.status === 401) {
      setToken(null)
      setTokenState(null)
    }
  }, [me.error])

  const value = useMemo<AuthValue>(() => {
    const adopt = async (path: string, body: unknown) => {
      const result = await api<TokenResponse>(path, { method: 'POST', body: JSON.stringify(body) })
      setToken(result.access_token)
      setTokenState(result.access_token)
      queryClient.setQueryData(['me', result.access_token], result.user)
    }
    return {
      user: token ? me.data ?? null : null,
      loading: Boolean(token) && me.isLoading,
      login: (email, password) => adopt('/auth/login', { email, password }),
      signup: (email, password, role) => adopt('/auth/signup', { email, password, role }),
      logout: () => {
        setToken(null)
        setTokenState(null)
        queryClient.clear()
      },
    }
  }, [me.data, me.isLoading, queryClient, token])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext)
  if (!value) throw new Error('AuthProvider is missing')
  return value
}
