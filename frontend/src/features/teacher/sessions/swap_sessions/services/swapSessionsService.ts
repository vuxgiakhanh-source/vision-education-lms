import { authenticatedApi } from '../../../../auth/session/authenticatedApi'
import { scheduleSaveTimeout, sessionTimeSnapshot, type TeacherSessionRecord } from '../../services/teacherSessionService'

export async function swapTeacherSessions(session: TeacherSessionRecord, other: TeacherSessionRecord): Promise<void> {
    await authenticatedApi.put(`/teacher/sessions/${session.id}/swap`, {
        other_session_id: other.id,
        expected_time: sessionTimeSnapshot(session),
        expected_other_time: sessionTimeSnapshot(other),
    }, { timeout: scheduleSaveTimeout })
}
