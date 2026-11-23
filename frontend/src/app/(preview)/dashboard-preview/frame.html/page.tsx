import type { Metadata } from 'next'
import { StudentDashboardPreview } from '../../../../features/student/dashboard/pages/StudentDashboardPage'
import { StudentWelcomeBanner } from '../../../../features/student/dashboard/components/StudentWelcomeBanner'

export const metadata: Metadata = { title: 'Vision Education · Preview banner' }

export default async function DashboardPreviewFrame({
  searchParams,
}: {
  searchParams: Promise<{ view?: string }>
}) {
  const { view } = await searchParams

  return view === 'banner' ? (
    <main style={{ padding: 16 }}>
      <StudentWelcomeBanner userName="Gia Khánh" taskCount={4} />
    </main>
  ) : (
    <StudentDashboardPreview />
  )
}
