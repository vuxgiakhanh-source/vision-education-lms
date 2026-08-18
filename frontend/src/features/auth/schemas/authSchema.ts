import { z } from 'zod';

export const loginSchema = z.object({
    phoneNumber: z.string().length(10, 'Số điện thoại phải có 10 chữ số').regex(/^\d+$/, 'Số điện thoại chỉ được chứa chữ số'),
    password: z.string().min(1, 'Mật khẩu không được để trống')
})