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
    diffLabel: string
  }
  streak: {
    days: number
    note: string
  }
  pendingAssignments: {
    count: number
    isUrgent: boolean
    nearestDeadline: string
  }
}

export interface DashboardTask {
  id: string
  title: string
  subjectTopic: string
  categoryTag: string
  categoryTagColor: 'blue' | 'cyan' | 'pink'
  deadline: string
  remainingDays: number
  isUrgent?: boolean
  isCompleted: boolean
}

export interface DashboardNotification {
  id: string
  type: 'exam' | 'calendar' | 'material' | 'achievement'
  title: string
  description: string
  timeAgo: string
  isUnread: boolean
}

export interface UpcomingClassItem {
  id: string
  dayOfWeek: string
  date: string
  topic: string
  time: string
  room: string
  teacher: string
}

export interface ResourceItem {
  id: string
  title: string
  format: 'PDF' | 'PPT' | 'DOC'
  size: string
  timeAgo: string
  downloadUrl?: string
}
