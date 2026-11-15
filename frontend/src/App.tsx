import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { LoginPage } from './features/auth/login/pages/LoginPage'
import { ChangePasswordPage } from './features/auth/change_password/pages/ChangePasswordPage'
import { AuthGuard } from './features/auth/guards/AuthGuard'
import { StudentDashboardPage } from './features/dashboard/pages/StudentDashboardPage'
import { SchedulePage } from './features/schedule/pages/SchedulePage'

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                {/* Route xem trước Lịch học không cần đăng nhập để bạn test nhanh giao diện */}
                <Route path="/schedule-preview" element={<SchedulePage />} />
                <Route element={<AuthGuard />}>
                    <Route path="/change-password" element={<ChangePasswordPage />} />
                    <Route path="/dashboard" element={<StudentDashboardPage />} />
                    <Route path="/schedule" element={<SchedulePage />} />
                </Route>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    )
}
