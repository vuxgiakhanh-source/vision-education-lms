'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { AuthGuard, useAuthProfile } from '../guards/AuthGuard'
import { dashboardPath } from './dashboardPath'

function DashboardRedirect() {
    const role = useAuthProfile()?.role
    const router = useRouter()

    useEffect(() => {
        const destination = dashboardPath(role)
        if (destination) router.replace(destination)
    }, [role, router])

    return <p role="status" className="p-6 text-center">{role === 'admin' || role === 'teaching_assistant' ? 'Chưa có trang chủ cho vai trò này.' : 'Đang mở trang chủ…'}</p>
}

export function SessionHome() {
    return <AuthGuard><DashboardRedirect /></AuthGuard>
}
