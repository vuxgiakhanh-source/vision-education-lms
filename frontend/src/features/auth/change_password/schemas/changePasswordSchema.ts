import { z } from 'zod';
import { MIN_NEW_PASSWORD_CHARACTERS, passwordFitsByteLimit, passwordTooLongMessage } from '../../passwordPolicy'

export const changePasswordSchema = z.object({
    newPassword: z.string().min(1, 'Mật khẩu mới không được để trống')
        .refine(password => Array.from(password).length >= MIN_NEW_PASSWORD_CHARACTERS,
            `Mật khẩu mới phải có ít nhất ${MIN_NEW_PASSWORD_CHARACTERS} ký tự.`)
        .refine(passwordFitsByteLimit, passwordTooLongMessage),
    confirmNewPassword: z.string().min(1, 'Không được để trống')
}).refine((data) => data.newPassword === data.confirmNewPassword, {
    message: 'Mật khẩu xác nhận không trùng khớp',
    path: ['confirmNewPassword']
});
