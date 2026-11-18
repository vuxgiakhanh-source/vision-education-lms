import { api } from '../../../../lib/axios'
import type { WeeklyScheduleResponse } from '../types/weeklyScheduleTypes'

export const weeklyScheduleService = {
    async getWeeklySchedule(selectedDate: string) {
        const res = await api.get<WeeklyScheduleResponse>('/schedule/weekly', {
            params: { week_start: selectedDate }
        })
        return res.data
    }
}