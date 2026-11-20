import { authenticatedApi } from '../../session/authenticatedApi'
import type { ChangePasswordFormData, ChangePasswordResponse } from '../types/changePasswordTypes'

export const changePasswordService = {
    async changePassword(data: ChangePasswordFormData): Promise<ChangePasswordResponse> {
        const res = await authenticatedApi.put<ChangePasswordResponse>('/change-password', {
            new_password: data.newPassword,
        })
        return res.data
    }
}
