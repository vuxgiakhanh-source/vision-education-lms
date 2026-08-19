import { LoginPage } from './features/auth/pages/LoginPage'
import { BrowserRouter } from 'react-router-dom'

export default function App() {
    return (
        <BrowserRouter>
            <LoginPage />
        </BrowserRouter>
    )
}
