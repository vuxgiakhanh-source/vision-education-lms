import { createRoot } from 'react-dom/client'
import { MemoryRouter } from 'react-router-dom'
import '../src/index.css'
import { StudentDashboardPage } from '../src/features/dashboard/pages/StudentDashboardPage'
import { WelcomeBanner } from '../src/features/dashboard/components/WelcomeBanner'

// Keep previously shared preview URLs pointing to the applied dashboard.
const bannerOnly = new URLSearchParams(window.location.search).get('view') === 'banner'
createRoot(document.getElementById('root')!).render(
  <MemoryRouter>
    {bannerOnly ? <main style={{ padding: 16 }}><WelcomeBanner userName="Gia Khánh" taskCount={4} /></main> : <StudentDashboardPage />}
  </MemoryRouter>,
)
