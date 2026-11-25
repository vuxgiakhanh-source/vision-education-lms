import type { UserRole } from '../me/types/meTypes'

export function dashboardPath(role: UserRole | undefined) {
    if (role === 'teacher') return '/teacher-dashboard'
    if (role === 'student') return '/student-dashboard'
}
