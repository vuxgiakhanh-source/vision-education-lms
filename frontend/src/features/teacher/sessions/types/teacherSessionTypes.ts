export type TeachingShift = 'morning' | 'afternoon' | 'evening'

export const teachingShiftIds: readonly TeachingShift[] = ['morning', 'afternoon', 'evening']

export const teachingShifts = {
    morning: { label: 'Ca 1 · Sáng', hours: ['07:30', '10:30'] },
    afternoon: { label: 'Ca 2 · Chiều', hours: ['14:00', '17:00'] },
    evening: { label: 'Ca 3 · Tối', hours: ['18:00', '21:00'] },
} as const

export type TeachingSlot = {
    date: string
    shift: TeachingShift
}
