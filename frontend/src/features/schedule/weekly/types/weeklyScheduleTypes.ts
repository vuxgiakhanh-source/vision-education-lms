export type WeeklySessionResponse = {
    id: number
    class_name: string
    teaching_week: number | null
    topic: string
    starts_at: string
    ends_at: string
}

export type WeeklyScheduleResponse = {
    week_start: string
    sessions: WeeklySessionResponse[]
    my_session_ids: number[]
    transferred_session_ids: number[]
}

export type WeeklySession = {
    id: string | number
    date: string
    shift: 'morning' | 'afternoon' | 'evening'
    label?: string
    className?: string
    topic: string
    topicFlags?: {
        hasAlgebra?: boolean
        hasGeometry?: boolean
        isReview?: boolean
    }
    status?: 'mine' | 'transferred'
}

export type WeeklySchedule = {
    weekStart: string
    sessions: WeeklySession[]
}

export type WeeklyPreview = WeeklySchedule & {
    grade: number
}
