import type { Metadata } from 'next'
import { StudentDashboardPage } from '../../../features/dashboard/pages/StudentDashboardPage'
import { WelcomeBanner } from '../../../features/dashboard/components/WelcomeBanner'

export const metadata: Metadata = { title: 'Vision Education · Preview banner' }

export default async function DashboardPreviewFrame({
  searchParams,
}: {
  searchParams: Promise<{ view?: string }>
}) {
  const { view } = await searchParams

  return view === 'banner' ? (
    <main style={{ padding: 16 }}>
      <WelcomeBanner userName="Gia Khánh" taskCount={4} />
    </main>
  ) : (
    <StudentDashboardPage preview />
  )
}
