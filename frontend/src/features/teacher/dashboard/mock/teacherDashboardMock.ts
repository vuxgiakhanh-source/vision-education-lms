export const teacherMetrics = [
    { label: 'Lớp đang phụ trách', value: '8', tone: 'violet' },
    { label: 'Buổi dạy hôm nay', value: '3', tone: 'sky' },
    { label: 'Học sinh cần chú ý', value: '5', tone: 'amber' },
    { label: 'Tỷ lệ chuyên cần', value: '95%', tone: 'green' },
] as const

export const teachingDate = '2026-11-21'

export const teachingSessions = [
    { name: 'Toán 12A', time: '07:30 – 09:00', shift: 'Ca sáng', tone: 'sky', upcoming: true },
    { name: 'Luyện đề 12', time: '14:00 – 15:30', shift: 'Ca chiều', tone: 'amber', upcoming: false },
    { name: 'Ôn tập Toán 12', time: '18:00 – 20:00', shift: 'Ca tối', tone: 'violet', upcoming: false },
] as const

export const studentsToWatch = [
    { name: 'Nguyễn Minh An', group: 'Toán 12A', reason: 'Vắng 2 buổi liên tiếp' },
    { name: 'Trần Linh Chi', group: 'Toán 12B', reason: 'Vắng 3 buổi trong tháng' },
    { name: 'Lê Hương Giang', group: 'Toán 11C', reason: 'Vắng 3 buổi liên tiếp' },
    { name: 'Phạm Minh Khang', group: 'Toán 12A', reason: 'Vắng 2 buổi trong tháng' },
    { name: 'Vũ Bảo Ngọc', group: 'Toán 12B', reason: 'Vắng 2 buổi liên tiếp' },
]

export const teacherTasks = [
    { id: 'attendance', title: 'Xác nhận điểm danh buổi 4 (12B)', color: '#ffb527' },
    { id: 'resources', title: 'Đăng tài liệu ôn tập học kỳ I (12A, 12B)', color: '#29ba86' },
    { id: 'questions', title: 'Phản hồi câu hỏi của học sinh', color: '#237bd2', badge: '3 câu hỏi' },
]

export const attendanceByClass = {
    all: { present: 258, excused: 8, absent: 6 },
    '12A': { present: 34, excused: 1, absent: 1 },
    '12B': { present: 36, excused: 2, absent: 1 },
    '11C': { present: 30, excused: 1, absent: 2 },
}
