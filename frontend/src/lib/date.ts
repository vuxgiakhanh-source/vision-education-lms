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

export function formatLocalDateTimeRange(startsAt: string, endsAt: string): string {
    // The API sends the center's local time. Keep its wall time when formatting the range.
    const startDate = startsAt.slice(0, 10)
    const endDate = endsAt.slice(0, 10)
    const start = `${startDate.split('-').reverse().join('/')} · ${startsAt.slice(11, 16)}`
    const endTime = endsAt.slice(11, 16)
    const end = endDate === startDate ? endTime : `${endDate.split('-').reverse().join('/')} · ${endTime}`
    return `${start} – ${end}`
}
