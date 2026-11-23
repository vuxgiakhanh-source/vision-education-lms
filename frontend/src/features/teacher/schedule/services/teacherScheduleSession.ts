import { getSessionShift } from '../../../../lib/date'
import type { TeacherSessionRecord } from '../../sessions/services/teacherSessionService'
import type { TeacherSession } from '../types/teacherScheduleTypes'

export function toScheduledTeacherSession(session: TeacherSessionRecord): TeacherSession {
    return {
        ...session,
        shift: getSessionShift(session.startsAt),
    }
}
