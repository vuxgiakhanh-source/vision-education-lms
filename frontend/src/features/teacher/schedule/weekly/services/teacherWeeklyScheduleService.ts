import { authenticatedApi } from '../../../../auth/session/authenticatedApi'
import { toTeacherSessionRecord, type TeachingSessionResponse } from '../../../sessions/services/teacherSessionService'
import { toScheduledTeacherSession } from '../../services/teacherScheduleSession'
import type { TeacherSession } from '../../types/teacherScheduleTypes'

export type TeacherWeeklySchedule = {
    weekStart: string
    sessions: TeacherSession[]
}

type TeacherWeeklyScheduleResponse = {
    week_start: string
    sessions: TeachingSessionResponse[]
}

export async function getTeacherWeeklySchedule(weekStart: string, signal: AbortSignal): Promise<TeacherWeeklySchedule> {
    const { data } = await authenticatedApi.get<TeacherWeeklyScheduleResponse>('/teacher/schedule/weekly', {
        params: { week_start: weekStart },
        signal,
    })
    return {
        weekStart: data.week_start,
        sessions: data.sessions.map(session => toScheduledTeacherSession(toTeacherSessionRecord(session))),
    }
}
