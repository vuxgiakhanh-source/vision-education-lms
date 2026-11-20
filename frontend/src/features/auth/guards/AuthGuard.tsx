'use client'

import { createContext, useContext, useEffect, useState, useSyncExternalStore, type ReactNode } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { meService } from '../me/services/meService'
import type { MeResponse } from '../me/types/meTypes'

const AuthProfileContext = createContext<MeResponse | null>(null)

export function useAuthProfile() {
    return useContext(AuthProfileContext)
}

function subscribeToStorage(onChange: () => void) {
    window.addEventListener('storage', onChange)
    return () => window.removeEventListener('storage', onChange)
}

const getAccessToken = () => localStorage.getItem('access_token')
const getServerSnapshot = () => undefined

export function AuthGuard({ children }: { children: ReactNode }) {
    const router = useRouter()
    const pathname = usePathname()
    const token = useSyncExternalStore(subscribeToStorage, getAccessToken, getServerSnapshot)

    useEffect(() => {
        if (token === null || token === '') router.replace('/login')
    }, [router, token])

    if (!token) return null
    if (pathname === '/change-password') return children

    return <PasswordChangeGuard key={token}>{children}</PasswordChangeGuard>
}

function PasswordChangeGuard({ children }: { children: ReactNode }) {
    const router = useRouter()
    const [profileCheck, setProfileCheck] = useState<MeResponse | 'checking' | 'failed'>('checking')

    useEffect(() => {
        if (profileCheck !== 'checking') return
        const controller = new AbortController()

        async function loadProfile() {
            try {
                const profile = await meService.getMe(controller.signal)
                if (controller.signal.aborted) return

                if (profile.must_change_password) {
                    router.replace('/change-password')
                } else {
                    setProfileCheck(profile)
                }
            } catch {
                if (!controller.signal.aborted) setProfileCheck('failed')
            }
        }

        void loadProfile()
        return () => controller.abort()
    }, [profileCheck, router])

    if (profileCheck === 'failed') {
        return (
            <div className="mx-auto max-w-md p-6 text-center">
                <p role="alert">Không thể xác minh tài khoản. Vui lòng thử lại.</p>
                <button
                    type="button"
                    className="mt-3 rounded-md border px-4 py-2"
                    onClick={() => setProfileCheck('checking')}
                >
                    Thử lại
                </button>
            </div>
        )
    }

    if (profileCheck === 'checking') return <p role="status" className="p-6 text-center">Đang xác minh tài khoản…</p>

    return <AuthProfileContext.Provider value={profileCheck}>{children}</AuthProfileContext.Provider>
}
