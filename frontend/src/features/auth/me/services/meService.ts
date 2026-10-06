import { api } from '../../../../lib/axios'
import type { MeResponse } from '../types/meTypes'

export const meService = {
    async getMe(): Promise<MeResponse> {
        const res = await api.get<MeResponse>('/me')
        return res.data
    }
}