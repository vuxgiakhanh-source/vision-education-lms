import { api } from '../../../lib/axios'
import type { LoginFormData, LoginResponse } from '../types/authTypes'

export const authService = {
    async login(data: LoginFormData): Promise<LoginResponse> {
        const res = await api.post<LoginResponse>('/login', {
            phone_number: data.phoneNumber,
            password: data.password
        })
        return res.data
    }
}   