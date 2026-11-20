import { authenticatedApi } from '../../session/authenticatedApi'
import type { MeResponse } from '../types/meTypes'

export const meService = {
    async getMe(signal?: AbortSignal): Promise<MeResponse> {
        const res = await authenticatedApi.get<MeResponse>('/me', { signal })
        return res.data
    }
}
