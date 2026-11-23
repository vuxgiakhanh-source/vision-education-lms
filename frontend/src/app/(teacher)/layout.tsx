import type { ReactNode } from 'react'
import { TeacherDashboardLayout } from '../../components/layout/TeacherDashboardLayout'
import { AuthGuard } from '../../features/auth/guards/AuthGuard'

export default function TeacherLayout({ children }: { children: ReactNode }) {
    return (
        <AuthGuard requiredRole="teacher">
            <TeacherDashboardLayout>{children}</TeacherDashboardLayout>
        </AuthGuard>
    )
}
