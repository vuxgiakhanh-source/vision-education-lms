import { authenticatedApi } from '../../../auth/session/authenticatedApi'
import { toTeacherSessionRecord, type TeachingSessionResponse } from '../../sessions/services/teacherSessionService'
import { toScheduledTeacherSession } from '../services/teacherScheduleSession'
import type { TeacherSession } from '../types/teacherScheduleTypes'

export async function getTeacherUpcomingSession(signal: AbortSignal): Promise<TeacherSession | null> {
    const { data } = await authenticatedApi.get<TeachingSessionResponse | null>('/teacher/schedule/upcoming', { signal })
    return data && toScheduledTeacherSession(toTeacherSessionRecord(data))
}
