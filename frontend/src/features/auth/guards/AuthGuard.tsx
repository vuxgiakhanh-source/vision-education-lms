import { Navigate, Outlet } from 'react-router-dom'

export function AuthGuard() {
    const token = localStorage.getItem('access_token')
    if (!token) {
        return <Navigate to="/login" replace />
    }
    else {
        return <Outlet />
    }
}