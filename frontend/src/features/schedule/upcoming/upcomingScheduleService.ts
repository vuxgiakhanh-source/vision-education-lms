import { authenticatedApi } from '../../auth/session/authenticatedApi'

export type UpcomingSession = {
    grade: number
    topic: string
    starts_at: string
    ends_at: string
}

export async function getUpcomingSession(signal: AbortSignal): Promise<UpcomingSession | null> {
    const { data } = await authenticatedApi.get<UpcomingSession | null>('/schedule/upcoming', { signal })
    return data
}
