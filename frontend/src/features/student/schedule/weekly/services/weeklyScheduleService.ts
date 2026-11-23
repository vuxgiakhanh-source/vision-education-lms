import { authenticatedApi } from '../../../../auth/session/authenticatedApi'
import { getSessionShift } from '../../../../../lib/date'
import type { WeeklySchedule, WeeklyScheduleResponse } from '../types/weeklyScheduleTypes'

export const weeklyScheduleService = {
    async getWeeklySchedule(selectedDate: string, signal: AbortSignal): Promise<WeeklySchedule> {
        const { data } = await authenticatedApi.get<WeeklyScheduleResponse>('/schedule/weekly', {
            params: { week_start: selectedDate },
            signal,
        })
        const mine = new Set(data.my_session_ids)
        const transferred = new Set(data.transferred_session_ids)

        return {
            weekStart: data.week_start,
            sessions: data.sessions.map(session => ({
                id: session.id,
                date: session.starts_at.slice(0, 10),
                shift: getSessionShift(session.starts_at),
                label: session.teaching_week == null ? undefined : `Tuần ${session.teaching_week}`,
                className: session.class_name,
                topic: session.topic.trim() || 'Buổi học',
                status: transferred.has(session.id) ? 'transferred' : mine.has(session.id) ? 'mine' : undefined,
            })),
        }
    }
}
