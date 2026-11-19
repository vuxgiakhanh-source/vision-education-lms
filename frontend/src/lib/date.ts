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