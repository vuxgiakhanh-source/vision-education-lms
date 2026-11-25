import type { ReactNode } from 'react'
import { TeacherDashboardLayout } from '../../components/layout/teacher/TeacherDashboardLayout'
import { AuthGuard } from '../../features/auth/guards/AuthGuard'
import '../../components/layout/teacher/TeacherShell.css'

export default function TeacherLayout({ children }: { children: ReactNode }) {
    return (
        <AuthGuard requiredRole="teacher">
            <TeacherDashboardLayout>{children}</TeacherDashboardLayout>
        </AuthGuard>
    )
}
