const centerDateFormat = new Intl.DateTimeFormat('sv-SE', {
    timeZone: 'Asia/Ho_Chi_Minh',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
})

export function formatCenterDate(date: Date): string {
    return centerDateFormat.format(date)
}

export function formatLocalDate(date: Date): string {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
}

export function addCalendarDays(date: string, days: number): string {
    const [year, month, day] = date.split('-').map(Number)
    const shiftedDate = new Date(year, month - 1, day + days)
    return formatLocalDate(shiftedDate)
}

export function formatWeekLabel(weekStart: string): string {
    const weekEnd = addCalendarDays(weekStart, 6)
    const [startYear, startMonth, startDay] = weekStart.split('-')
    const [endYear, endMonth, endDay] = weekEnd.split('-')
    if (startYear !== endYear) return `${startDay}/${startMonth}/${startYear} - ${endDay}/${endMonth}/${endYear}`
    if (startMonth !== endMonth) return `${startDay}/${startMonth} - ${endDay}/${endMonth}/${endYear}`
    return `${startDay} - ${endDay}/${endMonth}/${endYear}`
}

export function formatDayMonth(date: string): string {
    const [, month, day] = date.split('-')
    return `${day}/${month}`
}

export function formatDayMonthYear(date: string): string {
    return date.split('-').reverse().join('/')
}

export function formatLocalDateTimeRange(startsAt: string, endsAt: string): string {
    return `${formatDayMonthYear(startsAt.slice(0, 10))} · ${formatLocalTimeRange(startsAt, endsAt)}`
}

export function formatLocalTimeRange(startsAt: string, endsAt: string): string {
    // The API sends the center's local time. Keep its wall time when formatting the range.
    const startDate = startsAt.slice(0, 10)
    const endDate = endsAt.slice(0, 10)
    const start = startsAt.slice(11, 16)
    const endTime = endsAt.slice(11, 16)
    const end = endDate === startDate ? endTime : `${formatDayMonthYear(endDate)} · ${endTime}`
    return `${start} – ${end}`
}

export function getSessionShift(startsAt: string): 'morning' | 'afternoon' | 'evening' {
    // The schedule API sends the center's wall time without a UTC offset.
    const hour = Number(startsAt.slice(11, 13))
    if (hour < 12) return 'morning'
    if (hour < 18) return 'afternoon'
    return 'evening'
}
