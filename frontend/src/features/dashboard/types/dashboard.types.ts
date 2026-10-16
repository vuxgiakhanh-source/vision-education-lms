export interface UserProfile {
  name: string
  avatarUrl?: string
  role?: string
}

export interface KpiStats {
  averageScore: {
    current: number
    max: number
    diff: number
    diffLabel?: string
  }
  pendingAssignments: {
    count: number
    tag: string
    isUrgent?: boolean
    nearestDeadline?: string
  }
  streak: {
    days: number
    note?: string
  }
}

export interface TaskItem {
  id: string
  title: string
  subjectTopic: string
  dueDate: string
  statusType: 'urgent' | 'due' | 'pending'
  statusLabel: string
  isCompleted: boolean
  actionLabel?: string
}

export interface DocumentItem {
  id: string
  title: string
  format: 'PDF' | 'PPT' | 'DOC'
  size: string
  date: string
}

export interface CalendarDayItem {
  day: number
  isCurrentMonth: boolean
  isSelected?: boolean
  isHighlighted?: boolean
  hasEventDot?: boolean
}


