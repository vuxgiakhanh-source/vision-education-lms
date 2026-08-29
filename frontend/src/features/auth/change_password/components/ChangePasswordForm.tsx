import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from 'react-router-dom'
import { changePasswordSchema } from '../schemas/changePasswordSchema'
import { changePasswordService } from '../services/changePasswordService'
import type { ChangePasswordFormData } from '../types/changePasswordTypes'
import logoImage from '../../../../assets/images/logo.webp'

export function ChangePasswordForm() {
    const [showNewPassword, setShowNewPassword] = useState(false)
    const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false)
    const [successMessage, setSuccessMessage] = useState<string | null>(null)

    const navigate = useNavigate()

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        setError
    } = useForm<ChangePasswordFormData>({
        resolver: zodResolver(changePasswordSchema)
    })

    async function onSubmit(data: ChangePasswordFormData) {
        try {
            const res = await changePasswordService.changePassword(data)
            setSuccessMessage(res.message)
            setTimeout(() => {
                navigate('/dashboard')
            }, 1500)
        } catch (error: any) {
            setError("root", {
                message: error.message
            })
        }
    }

    return (
        <div className="w-full max-w-[430px] bg-white rounded-[32px] p-8 sm:p-9 shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)] flex flex-col items-center border border-white">
            {/* Logo VE */}
            <div className="mb-4">
                <img
                    src={logoImage}
                    alt="Vision Education Logo"
                    className="h-12 w-auto object-contain drop-shadow-sm"
                />
            </div>

            {/* Header */}
            <h2 className="text-[23px] font-bold text-[#1e2329] mb-1.5 text-center tracking-tight">
                Đổi mật khẩu
            </h2>
            <p className="text-[13px] text-[#8b95a5] mb-6 text-center font-normal">
                Vui lòng nhập mật khẩu mới của bạn
            </p>

            {/* Thông báo thành công */}
            {successMessage && (
                <div className="w-full p-3 bg-green-50 border border-green-200 text-green-700 text-xs rounded-[14px] font-medium text-center mb-4">
                    {successMessage} - Đang chuyển hướng...
                </div>
            )}

            {/* Form */}
            <form className="w-full space-y-4" onSubmit={handleSubmit(onSubmit)}>
                {/* Mật khẩu mới */}
                <div className="space-y-1.5">
                    <label className="block text-[12px] font-semibold text-[#374151]">
                        Mật khẩu mới
                    </label>
                    <div className="relative flex items-center">
                        <span className="absolute left-3.5 text-[#9ca3af] pointer-events-none">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </span>
                        <input
                            type={showNewPassword ? "text" : "password"}
                            placeholder="Nhập mật khẩu mới"
                            {...register("newPassword")}
                            className="w-full pl-10 pr-11 py-3.5 text-[13px] bg-[#f8f9fd] border border-[#edf0f7] rounded-[14px] focus:outline-none focus:ring-2 focus:ring-[#6366f1]/40 focus:bg-white transition-all text-[#1f2937] placeholder-[#a0aec0]"
                        />
                        <button
                            type="button"
                            onClick={() => setShowNewPassword(!showNewPassword)}
                            className="absolute right-3.5 text-[#9ca3af] hover:text-[#6b7280] cursor-pointer focus:outline-none p-1"
                        >
                            {showNewPassword ? (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858-5.908a10.025 10.025 0 011.53-.163c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21m-2.122-2.122L3 3" />
                                </svg>
                            ) : (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                            )}
                        </button>
                    </div>
                    {errors.newPassword && (
                        <p className="text-red-500 text-xs mt-1 font-medium">{errors.newPassword.message}</p>
                    )}
                </div>

                {/* Xác nhận mật khẩu mới */}
                <div className="space-y-1.5">
                    <label className="block text-[12px] font-semibold text-[#374151]">
                        Xác nhận mật khẩu mới
                    </label>
                    <div className="relative flex items-center">
                        <span className="absolute left-3.5 text-[#9ca3af] pointer-events-none">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </span>
                        <input
                            type={showConfirmNewPassword ? "text" : "password"}
                            placeholder="Nhập lại mật khẩu mới"
                            {...register("confirmNewPassword")}
                            className="w-full pl-10 pr-11 py-3.5 text-[13px] bg-[#f8f9fd] border border-[#edf0f7] rounded-[14px] focus:outline-none focus:ring-2 focus:ring-[#6366f1]/40 focus:bg-white transition-all text-[#1f2937] placeholder-[#a0aec0]"
                        />
                        <button
                            type="button"
                            onClick={() => setShowConfirmNewPassword(!showConfirmNewPassword)}
                            className="absolute right-3.5 text-[#9ca3af] hover:text-[#6b7280] cursor-pointer focus:outline-none p-1"
                        >
                            {showConfirmNewPassword ? (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858-5.908a10.025 10.025 0 011.53-.163c4.478 0 8.268 2.943 9.542 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21m-2.122-2.122L3 3" />
                                </svg>
                            ) : (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                            )}
                        </button>
                    </div>
                    {errors.confirmNewPassword && (
                        <p className="text-red-500 text-xs mt-1 font-medium">{errors.confirmNewPassword.message}</p>
                    )}
                </div>

                {/* Lỗi server */}
                {errors.root && (
                    <div className="w-full p-3 bg-red-50 border border-red-200 text-red-600 text-xs rounded-[14px] font-medium text-center">
                        {errors.root.message}
                    </div>
                )}

                {/* Nút Đổi mật khẩu */}
                <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full py-3.5 bg-gradient-to-r from-[#5a60ec] to-[#7076f7] hover:from-[#4f55e0] hover:to-[#6369eb] active:scale-[0.99] text-white font-medium text-sm rounded-[14px] transition-all shadow-[0_10px_25px_rgba(90,96,236,0.35)] cursor-pointer mt-2"
                >
                    {isSubmitting ? "Đang xử lí..." : "Đổi mật khẩu"}
                </button>
            </form>

            {/* Quay lại đăng nhập */}
            <div className="mt-6 text-center">
                <Link
                    to="/login"
                    className="inline-flex items-center gap-1.5 text-[13px] text-[#4b5563] hover:text-[#111827] font-medium transition-colors"
                >
                    <span>←</span>
                    <span>Quay lại đăng nhập</span>
                </Link>
            </div>
        </div>
    )
}