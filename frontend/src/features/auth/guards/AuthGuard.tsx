'use client'

import { useEffect, useSyncExternalStore, type ReactNode } from 'react'
import { useRouter } from 'next/navigation'

function subscribeToStorage(onChange: () => void) {
    window.addEventListener('storage', onChange)
    return () => window.removeEventListener('storage', onChange)
}

function getAccessToken() {
    return localStorage.getItem('access_token')
}

function getServerSnapshot() {
    return undefined
}

export function AuthGuard({ children }: { children: ReactNode }) {
    const router = useRouter()
    const token = useSyncExternalStore(subscribeToStorage, getAccessToken, getServerSnapshot)

    useEffect(() => {
        if (token === null || token === '') router.replace('/login')
    }, [router, token])

    return token ? children : null
}
