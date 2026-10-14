import type {
  UserProfile,
  KpiStats,
  TaskItem,
  DocumentItem,
  CalendarDayItem,
} from '../types/dashboard.types'

export const mockUserProfile: UserProfile = {
  name: 'Gia Khánh',
  role: 'Học sinh',
}

export const mockKpiStats: KpiStats = {
  averageScore: {
    current: 8.5,
    max: 10,
    diff: 0.3,
    diffLabel: 'Cao hơn tuần trước',
  },
  pendingAssignments: {
    count: 2,
    tag: 'Cần nộp sớm',
    nearestDeadline: 'Trong 3 ngày tới',
  },
  streak: {
    days: 12,
    note: 'Giữ vững phong độ!',
  },
}

export const mockTasks: TaskItem[] = [
  {
    id: 'task-1',
    title: 'Hoàn thành bài tập Chương 1',
    subjectTopic: 'Đại số - Hàm số',
    dueDate: '24 Thg 9, 2024',
    statusType: 'urgent',
    statusLabel: 'Cần nộp sớm',
    isCompleted: false,
  },
  {
    id: 'task-2',
    title: 'Xem lại video: Phương trình bậc hai',
    subjectTopic: 'Đại số - Phương trình',
    dueDate: '26 Thg 9, 2024',
    statusType: 'due',
    statusLabel: 'Đến hạn',
    isCompleted: false,
  },
  {
    id: 'task-3',
    title: 'Làm đề ôn tập số 2',
    subjectTopic: 'Tổng ôn chương 1 + 2',
    dueDate: '28 Thg 9, 2024',
    statusType: 'pending',
    statusLabel: 'Chưa nộp',
    isCompleted: false,
  },
  {
    id: 'task-4',
    title: 'Đọc và tóm tắt lý thuyết tích phân',
    subjectTopic: 'Giải tích - Nguyên hàm, tích phân',
    dueDate: '30 Thg 9, 2024',
    statusType: 'pending',
    statusLabel: 'Chưa nộp',
    isCompleted: false,
  },
]

export const mockDocuments: DocumentItem[] = [
  {
    id: 'doc-1',
    title: 'Tóm tắt lý thuyết - Tích phân (PDF)',
    format: 'PDF',
    size: '2.4 MB',
    date: '24 Thg 9, 2024',
  },
  {
    id: 'doc-2',
    title: 'Bộ đề luyện tập - Hàm số mũ (PDF)',
    format: 'PDF',
    size: '1.8 MB',
    date: '22 Thg 9, 2024',
  },
  {
    id: 'doc-3',
    title: 'Công thức đạo hàm mở rộng (PPT)',
    format: 'PPT',
    size: '3.1 MB',
    date: '20 Thg 9, 2024',
  },
]

export const mockCalendarDays: CalendarDayItem[] = [
  // Tháng 8 (Previous month)
  { day: 26, isCurrentMonth: false },
  { day: 27, isCurrentMonth: false },
  { day: 28, isCurrentMonth: false },
  { day: 29, isCurrentMonth: false },
  { day: 30, isCurrentMonth: false },
  { day: 31, isCurrentMonth: false },
  // Tháng 9 (Current month)
  { day: 1, isCurrentMonth: true },
  { day: 2, isCurrentMonth: true },
  { day: 3, isCurrentMonth: true },
  { day: 4, isCurrentMonth: true },
  { day: 5, isCurrentMonth: true, hasEventDot: true },
  { day: 6, isCurrentMonth: true },
  { day: 7, isCurrentMonth: true },
  { day: 8, isCurrentMonth: true },
  { day: 9, isCurrentMonth: true },
  { day: 10, isCurrentMonth: true },
  { day: 11, isCurrentMonth: true },
  { day: 12, isCurrentMonth: true, isHighlighted: true, hasEventDot: true },
  { day: 13, isCurrentMonth: true, hasEventDot: true },
  { day: 14, isCurrentMonth: true },
  { day: 15, isCurrentMonth: true },
  { day: 16, isCurrentMonth: true },
  { day: 17, isCurrentMonth: true },
  { day: 18, isCurrentMonth: true },
  { day: 19, isCurrentMonth: true },
  { day: 20, isCurrentMonth: true },
  { day: 21, isCurrentMonth: true },
  { day: 22, isCurrentMonth: true },
  { day: 23, isCurrentMonth: true },
  { day: 24, isCurrentMonth: true, isSelected: true },
  { day: 25, isCurrentMonth: true },
  { day: 26, isCurrentMonth: true, hasEventDot: true },
  { day: 27, isCurrentMonth: true },
  { day: 28, isCurrentMonth: true },
  { day: 29, isCurrentMonth: true },
  { day: 30, isCurrentMonth: true },
  // Tháng 10 (Next month)
  { day: 1, isCurrentMonth: false },
  { day: 2, isCurrentMonth: false },
  { day: 3, isCurrentMonth: false },
  { day: 4, isCurrentMonth: false },
  { day: 5, isCurrentMonth: false },
  { day: 6, isCurrentMonth: false },
]
