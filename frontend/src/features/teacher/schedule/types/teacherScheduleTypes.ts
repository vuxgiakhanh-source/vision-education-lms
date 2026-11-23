import type { TeacherSessionRecord } from '../../sessions/services/teacherSessionService'
import type { TeachingShift } from '../../sessions/types/teacherSessionTypes'

export type TeacherSession = TeacherSessionRecord & {
    shift: TeachingShift
}


