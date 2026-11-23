import type { ReactNode } from 'react'
import { StudentDashboardLayout } from '../../components/layout/StudentDashboardLayout'
import { AuthGuard } from '../../features/auth/guards/AuthGuard'

export default function StudentLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard requiredRole="student">
      <StudentDashboardLayout>{children}</StudentDashboardLayout>
    </AuthGuard>
  )
}
