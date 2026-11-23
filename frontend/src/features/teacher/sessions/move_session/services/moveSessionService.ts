import { authenticatedApi } from '../../../../auth/session/authenticatedApi'
import { scheduleSaveTimeout, sessionTimeSnapshot, type TeacherSessionRecord } from '../../services/teacherSessionService'
import type { TeachingSlot } from '../../types/teacherSessionTypes'

export async function moveTeacherSession(session: TeacherSessionRecord, target: TeachingSlot): Promise<void> {
    await authenticatedApi.put(`/teacher/sessions/${session.id}/move`, {
        expected_time: sessionTimeSnapshot(session),
        target_date: target.date,
        target_shift: target.shift,
    }, { timeout: scheduleSaveTimeout })
}
