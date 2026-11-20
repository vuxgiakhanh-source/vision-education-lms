import { isAxiosError } from 'axios'
import { api } from '../../../lib/axios'

export const authenticatedApi = api.create()

authenticatedApi.interceptors.request.use(config => {
    if (typeof window === 'undefined') return config

    const token = localStorage.getItem('access_token')
    if (token) config.headers.set('Authorization', `Bearer ${token}`)
    return config
})

authenticatedApi.interceptors.response.use(undefined, (error: unknown) => {
    if (typeof window === 'undefined' || !isAxiosError<{ detail?: { code?: string } }>(error)) {
        return Promise.reject(error)
    }

    const { response } = error
    const accountLocked = response?.status === 403 && response.data?.detail?.code === 'ACCOUNT_LOCKED'
    if (response?.status !== 401 && !accountLocked) return Promise.reject(error)

    const sentAuthorization = error.config?.headers.get('Authorization')
    const currentToken = localStorage.getItem('access_token')
    if (currentToken && sentAuthorization === `Bearer ${currentToken}`) {
        localStorage.removeItem('access_token')
        if (window.location.pathname !== '/login') window.location.href = '/login'
    }

    return Promise.reject(error)
})
