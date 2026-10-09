import type {
  UserProfile,
  KpiStats,
  DashboardTask,
  DashboardNotification,
  UpcomingClassItem,
  ResourceItem,
} from '../types/dashboard.types'

export const mockUserProfile: UserProfile = {
  name: 'Gia Khánh',
  role: 'Học sinh',
}

export const mockKpiStats: KpiStats = {
  averageScore: {
    current: 10,
    max: 10,
    diff: 0.3,
    diffLabel: 'Cao hơn lần trước',
  },
  streak: {
    days: 12,
    note: 'Giữ vững phong độ!',
  },
  pendingAssignments: {
    count: 2,
    isUrgent: true,
    nearestDeadline: '24/09',
  },
}

export const mockDashboardTasks: DashboardTask[] = [
  {
    id: 't-1',
    title: 'Hoàn thành bài tập Chương 1',
    subjectTopic: 'Đại số - Hàm số',
    categoryTag: 'Đại số',
    categoryTagColor: 'blue',
    deadline: '24/09',
    remainingDays: 1,
    isUrgent: true,
    isCompleted: false,
  },
  {
    id: 't-2',
    title: 'Xem lại video: Phương trình bậc hai',
    subjectTopic: 'Đại số - Phương trình',
    categoryTag: 'Đại số',
    categoryTagColor: 'blue',
    deadline: '26/09',
    remainingDays: 3,
    isUrgent: false,
    isCompleted: false,
  },
  {
    id: 't-3',
    title: 'Làm đề ôn tập số 2',
    subjectTopic: 'Tổng ôn chương 1 + 2',
    categoryTag: 'Tổng ôn',
    categoryTagColor: 'cyan',
    deadline: '28/09',
    remainingDays: 5,
    isUrgent: false,
    isCompleted: false,
  },
  {
    id: 't-4',
    title: 'Đọc và tóm tắt lý thuyết tích phân',
    subjectTopic: 'Giải tích - Nguyên hàm, tích phân',
    categoryTag: 'Giải tích',
    categoryTagColor: 'pink',
    deadline: '30/09',
    remainingDays: 7,
    isUrgent: false,
    isCompleted: false,
  },
]

export const mockDashboardNotifications: DashboardNotification[] = [
  {
    id: 'n-1',
    type: 'exam',
    title: 'Có 3 đề luyện mới trong chủ đề Hàm số',
    description: 'Bộ đề bám sát cấu trúc đề thi, có lời giải chi tiết.',
    timeAgo: '2 giờ trước',
    isUnread: true,
  },
  {
    id: 'n-2',
    type: 'calendar',
    title: 'Lịch thi thử tháng 10 đã mở đăng ký',
    description: 'Đăng ký ngay để kiểm tra năng lực và nhận đánh giá.',
    timeAgo: '5 giờ trước',
    isUnread: true,
  },
  {
    id: 'n-3',
    type: 'material',
    title: 'Giáo viên đã đăng thêm tài liệu chương 2',
    description: 'Bao gồm tóm tắt lý thuyết, công thức và bài tập mẫu.',
    timeAgo: '1 ngày trước',
    isUnread: false,
  },
  {
    id: 'n-4',
    type: 'achievement',
    title: 'Bạn đạt 80% ở đề: Đạo hàm cơ bản',
    description: 'Xem chi tiết kết quả và phân tích lỗi sai.',
    timeAgo: '1 ngày trước',
    isUnread: false,
  },
]

export const mockUpcomingClasses: UpcomingClassItem[] = [
  {
    id: 'c-1',
    dayOfWeek: 'Th 3',
    date: '24/09',
    topic: 'Ôn tập Hàm số bậc hai',
    time: '19:00 - 20:30',
    room: 'Phòng học: A1',
    teacher: 'GV. Nguyễn Minh',
  },
  {
    id: 'c-2',
    dayOfWeek: 'Th 5',
    date: '26/09',
    topic: 'Luyện đề Tổng hợp chương 1',
    time: '14:00 - 15:30',
    room: 'Phòng học: B2',
    teacher: 'GV. Trần Thu Hà',
  },
]

export const mockResources: ResourceItem[] = [
  {
    id: 'r-1',
    title: 'Tóm tắt lý thuyết - Tích phân (PDF)',
    format: 'PDF',
    size: '2.4 MB',
    timeAgo: '2 giờ trước',
  },
  {
    id: 'r-2',
    title: 'Bộ đề luyện tập - Hàm số mũ (PDF)',
    format: 'PDF',
    size: '3.1 MB',
    timeAgo: '1 ngày trước',
  },
  {
    id: 'r-3',
    title: 'Công thức đạo hàm mở rộng (PPT)',
    format: 'PPT',
    size: '5.2 MB',
    timeAgo: '2 ngày trước',
  },
  {
    id: 'r-4',
    title: 'Sơ đồ tư duy chương 2 (PDF)',
    format: 'PDF',
    size: '1.8 MB',
    timeAgo: '3 ngày trước',
  },
]
