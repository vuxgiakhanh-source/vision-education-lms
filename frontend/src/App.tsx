import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { LoginPage } from './features/auth/login/pages/LoginPage'
import { ChangePasswordPage } from './features/auth/change_password/pages/ChangePasswordPage'
import { AuthGuard } from './features/auth/guards/AuthGuard'
import { StudentDashboardPage } from './features/dashboard/pages/StudentDashboardPage'

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/dashboard" element={<StudentDashboardPage />} />
                <Route element={<AuthGuard />}>
                    <Route path="/change-password" element={<ChangePasswordPage />} />
                </Route>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    )
}
