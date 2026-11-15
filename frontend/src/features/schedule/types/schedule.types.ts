export type ShiftType = 'morning' | 'afternoon' | 'evening'

export interface ShiftDefinition {
  id: ShiftType
  name: string
  label: string
  timeRange: string
  bgLight: string
  badgeColor: string
  textColor: string
  borderColor: string
}

export interface DayColumn {
  dayOfWeek: string // e.g., 'T2', 'T3', ...
  dateStr: string   // e.g., '09/11'
  fullDate: string  // e.g., '2026-11-10'
  isHighlighted?: boolean
}

export type SessionTagType = 'user' | 'same_lesson' | 'empty'

export interface ScheduleSessionItem {
  id: string
  dayOfWeek: string // 'T2', 'T3', etc.
  shiftId: ShiftType
  tagType: SessionTagType
  tagLabel?: string
  topic: string
  grade?: number
  subject?: string
  room?: string
  timeRange?: string
  dateDisplay?: string
}

export interface UpcomingSessionInfo {
  subject: string
  grade: number
  dateDisplay: string
  timeRange: string
  room: string
}
