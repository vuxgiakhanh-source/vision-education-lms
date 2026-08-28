import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from 'react-router-dom'
import { changePasswordSchema } from '../schemas/changePasswordSchema'
import { changePasswordService } from '../services/changePasswordService'
import type { ChangePasswordFormData } from '../types/changePasswordTypes'

export function ChangePasswordForm() {
    const [showNewPassword, setShowNewPassword] = useState(false)

    const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false)

    const [successMessage, setSuccessMessage] = useState<string | null>(null)

    const navigate = useNavigate()

    const { register, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<ChangePasswordFormData>({
        resolver: zodResolver(changePasswordSchema)
    })

    async function onSubmit(data: ChangePasswordFormData) {
        try {
            const res = await changePasswordService.changePassword(data)
            setSuccessMessage(res.message)
            setTimeout(() => {
                navigate('/dashboard')
            }, 1500)
        }
        catch (error: any) {
            setError("root", {
                message: error.message
            })
        }
    }
    return (
        <div>
            <h2>Thiết lập mật khẩu mới</h2>
            {successMessage && (
                <p>{successMessage} - Đang chuyển hướng...</p>
            )}
            <form onSubmit={handleSubmit(onSubmit)}>
                <div>
                    <label>Mật khẩu mới</label>
                    <input
                        type={showNewPassword ? "text" : "password"}
                        placeholder="Nhập mật khẩu mới"
                        {...register("newPassword")}
                    />
                    {errors.newPassword && (
                        <p>{errors.newPassword.message}</p>
                    )}
                </div>
                <div>
                    <label>Xác nhận mật khẩu mới</label>
                    <input
                        type={showConfirmNewPassword ? "text" : "password"}
                        placeholder="Xác nhận mật khẩu mới"
                        {...register("confirmNewPassword")}
                    />
                    {errors.confirmNewPassword && (
                        <p>{errors.confirmNewPassword.message}</p>
                    )}
                </div>
                {errors.root && (
                    <p>{errors.root.message}</p>
                )}
                <button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? "Đang xử lí..." : "Cập nhật mật khẩu"}
                </button>
            </form>
        </div>
    )
}