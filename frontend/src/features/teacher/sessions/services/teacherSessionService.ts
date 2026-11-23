import { formatLocalTimeRange } from '../../../../lib/date'
import { authenticatedApi } from '../../../auth/session/authenticatedApi'

export type TeacherSessionDetails = {
    className: string
    date: string
    timeRange: string
    teachingWeek?: number
    topic: string
    outline?: string[]
    materials?: { kind: string; name: string; size: string }[]
}

export type TeacherSessionRecord = TeacherSessionDetails & {
    id: number
    startsAt: string
    endsAt: string
}

export type TeachingSessionResponse = {
    id: number
    class_name: string
    topic: string
    teaching_week: number | null
    starts_at: string
    ends_at: string
}

export function toTeacherSessionRecord(session: TeachingSessionResponse): TeacherSessionRecord {
    return {
        id: session.id,
        className: session.class_name,
        topic: session.topic.trim() || 'Buổi học',
        teachingWeek: session.teaching_week ?? undefined,
        date: session.starts_at.slice(0, 10),
        startsAt: session.starts_at,
        endsAt: session.ends_at,
        timeRange: formatLocalTimeRange(session.starts_at, session.ends_at),
    }
}

export async function getTeacherSession(id: number, signal: AbortSignal): Promise<TeacherSessionRecord> {
    const { data } = await authenticatedApi.get<TeachingSessionResponse>(`/teacher/sessions/${id}`, { signal })
    return toTeacherSessionRecord(data)
}

export const scheduleSaveTimeout = 15_000

export function sessionTimeSnapshot(session: TeacherSessionRecord) {
    return { starts_at: session.startsAt, ends_at: session.endsAt }
}
