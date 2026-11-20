import type { WeeklyPreview } from '../types/weeklyScheduleTypes'

export const weeklyPreview: WeeklyPreview = {
    weekStart: '2026-11-23',
    grade: 12,
    sessions: [
        {
            id: 'tuesday-morning',
            date: '2026-11-24',
            shift: 'morning',
            label: 'Buổi 5',
            topic: 'Ứng dụng đạo hàm',
            topicFlags: { hasAlgebra: true },
            status: 'mine',
        },
        {
            id: 'thursday-evening',
            date: '2026-11-26',
            shift: 'evening',
            label: 'Buổi 5',
            topic: '',
            topicFlags: { hasGeometry: true, isReview: true },
        },
        {
            id: 'saturday-afternoon',
            date: '2026-11-28',
            shift: 'afternoon',
            label: 'Buổi 6',
            topic: 'Kiểm tra',
            topicFlags: {},
        },
        {
            id: 'sunday-morning',
            date: '2026-11-29',
            shift: 'morning',
            label: 'Buổi 7',
            topic: '',
            topicFlags: { hasAlgebra: true },
        },
    ],
}
