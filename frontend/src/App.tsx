import { LoginPage } from './features/auth/login/pages/LoginPage'
import { BrowserRouter } from 'react-router-dom'

export default function App() {
    return (
        <BrowserRouter>
            <LoginPage />
        </BrowserRouter>
    )
}
