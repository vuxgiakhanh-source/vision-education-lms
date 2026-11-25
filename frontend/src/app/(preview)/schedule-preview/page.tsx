import { StudentDashboardLayout } from '../../../components/layout/student/StudentDashboardLayout'
import { StudentSchedulePage } from '../../../features/student/schedule/pages/StudentSchedulePage'
import { weeklyPreview } from '../../../features/student/schedule/weekly/mock/schedule.mock'

export default function SchedulePreviewRoute() {
  return <StudentDashboardLayout><StudentSchedulePage preview={weeklyPreview} /></StudentDashboardLayout>
}
