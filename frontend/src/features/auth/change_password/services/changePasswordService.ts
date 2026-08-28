import { api } from '../../../../lib/axios'
import type { ChangePasswordFormData, ChangePasswordResponse } from '../types/changePasswordTypes'

export const changePasswordService = {
    async changePassword(data: ChangePasswordFormData): Promise<ChangePasswordResponse> {
        const res = await api.put<ChangePasswordResponse>('/change-password', {
            new_password: data.newPassword,
        })
        return res.data
    }
}