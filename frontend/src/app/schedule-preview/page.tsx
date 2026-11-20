import { SchedulePage } from '../../features/schedule/pages/SchedulePage'
import { weeklyPreview } from '../../features/schedule/weekly/mock/schedule.mock'

export default function SchedulePreviewRoute() {
  return <SchedulePage preview={weeklyPreview} />
}
