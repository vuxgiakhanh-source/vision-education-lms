export function getShortName(fullName: string): string {
    const words = fullName.trim().split(/\s+/)
    const lastTwoWords = words.slice(-2)

    return lastTwoWords.join(' ')
}