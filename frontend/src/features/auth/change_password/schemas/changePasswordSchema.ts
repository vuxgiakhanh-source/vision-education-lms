import { z } from 'zod';

export const changePasswordSchema = z.object({
    newPassword: z.string().min(1, 'Mật khẩu mới không được để trống'),
    confirmNewPassword: z.string().min(1, 'Không được để trống')
}).refine((data) => data.newPassword === data.confirmNewPassword, {
    message: 'Mật khẩu xác nhận không trùng khớp',
    path: ['confirmNewPassword']
});