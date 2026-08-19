import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link } from 'react-router-dom'
import { loginSchema } from '../schemas/authSchema'
import { authService } from '../services/authService'
import type { LoginFormData } from '../types/authTypes'

export function LoginForm() {
    const [showPassword, setShowPassword] = useState(false)

    const { register, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema)
    })

    async function onSubmit(data: LoginFormData) {
        try {
            const res = await authService.login(data)
            localStorage.setItem('access_token', res.access_token)
            console.log('Đăng nhập thành công! Token: ', res.access_token)
        } catch (error: any) {
            console.log('Đăng nhập thất bại: ', error)
            setError("root", {
                message: error.message
            })
        }
    }

    return (
        <div className="w-full max-w-[430px] bg-white rounded-[32px] p-8 sm:p-9 shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)] flex flex-col items-center border border-white">
            {/* Logo VE Ribbon Gradient */}
            <div className="mb-4">
                <svg className="w-16 h-12" viewBox="0 0 100 70" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="ve-grad-v" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#1E40AF" />
                            <stop offset="50%" stopColor="#3B82F6" />
                            <stop offset="100%" stopColor="#6366F1" />
                        </linearGradient>
                        <linearGradient id="ve-grad-e" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#3B82F6" />
                            <stop offset="50%" stopColor="#6366F1" />
                            <stop offset="100%" stopColor="#A855F7" />
                        </linearGradient>
                    </defs>
                    <path d="M12 18L36 58L56 18H44L36 38L24 18H12Z" fill="url(#ve-grad-v)" />
                    <path d="M48 18H84C88 18 90 20 90 23V27C90 30 88 32 84 32H62V36H80C84 36 86 38 86 41V45C86 48 84 50 80 50H62V54H84C88 54 90 56 90 59V63H48V18Z" fill="url(#ve-grad-e)" />
                </svg>
            </div>

            {/* Header */}
            <h2 className="text-[23px] font-bold text-[#1e2329] mb-1 text-center tracking-tight">
                Chào mừng trở lại!
            </h2>
            <p className="text-[12px] text-[#8b95a5] mb-6 text-center font-normal">
                Đăng nhập để tiếp tục hành trình học tập
            </p>

            {/* Form */}
            <form className="w-full space-y-4" onSubmit={handleSubmit(onSubmit)}>
                {/* Input Số điện thoại */}
                <div className="space-y-1.5">
                    <label className="block text-[12px] font-semibold text-[#374151]">
                        Số điện thoại
                    </label>
                    <div className="relative flex items-center">
                        <span className="absolute left-3.5 text-[#9ca3af] pointer-events-none">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                            </svg>
                        </span>
                        <input
                            type="tel"
                            placeholder="Nhập số điện thoại"
                            {...register("phoneNumber")}
                            className="w-full pl-10 pr-4 py-3.5 text-[13px] bg-[#f8f9fd] border border-[#edf0f7] rounded-[14px] focus:outline-none focus:ring-2 focus:ring-[#6366f1]/40 focus:bg-white transition-all text-[#1f2937] placeholder-[#a0aec0]"
                        />
                    </div>
                    {errors.phoneNumber && (
                        <p className="text-red-500 text-xs mt-1 font-medium">{errors.phoneNumber.message}</p>
                    )}
                </div>

                {/* Input Mật khẩu */}
                <div className="space-y-1.5">
                    <label className="block text-[12px] font-semibold text-[#374151]">
                        Mật khẩu
                    </label>
                    <div className="relative flex items-center">
                        <span className="absolute left-3.5 text-[#9ca3af] pointer-events-none">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </span>
                        <input
                            type={showPassword ? "text" : "password"}
                            placeholder="Nhập mật khẩu"
                            {...register("password")}
                            className="w-full pl-10 pr-11 py-3.5 text-[13px] bg-[#f8f9fd] border border-[#edf0f7] rounded-[14px] focus:outline-none focus:ring-2 focus:ring-[#6366f1]/40 focus:bg-white transition-all text-[#1f2937] placeholder-[#a0aec0]"
                        />
                        {/* Nút mắt */}
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3.5 text-[#9ca3af] hover:text-[#6b7280] cursor-pointer focus:outline-none p-1"
                        >
                            {showPassword ? (
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
                    {errors.password && (
                        <p className="text-red-500 text-xs mt-1 font-medium">{errors.password.message}</p>
                    )}
                    <div className="text-right pt-0.5">
                        <Link to="/forgot-password" className="text-[12px] text-[#5850ec] hover:underline font-medium">
                            Quên mật khẩu?
                        </Link>
                    </div>
                </div>

                {/* Hiển thị lỗi từ server */}
                {errors.root && (
                    <div className="w-full p-3 bg-red-50 border border-red-200 text-red-600 text-xs rounded-[14px] font-medium text-center">
                        {errors.root.message}
                    </div>
                )}

                {/* Nút Đăng nhập Gradient xanh tím */}
                <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full py-3.5 bg-gradient-to-r from-[#5a60ec] to-[#7076f7] hover:from-[#4f55e0] hover:to-[#6369eb] active:scale-[0.99] text-white font-medium text-sm rounded-[14px] transition-all shadow-[0_10px_25px_rgba(90,96,236,0.35)] cursor-pointer mt-1"
                >
                    {isSubmitting ? "Đang đăng nhập..." : "Đăng nhập"}
                </button>
            </form>

            {/* Phân cách 'hoặc' */}
            <div className="w-full flex items-center my-4">
                <div className="flex-grow border-t border-[#f0f2f5]"></div>
                <span className="flex-shrink mx-3 text-[11px] text-[#9ca3af]">hoặc</span>
                <div className="flex-grow border-t border-[#f0f2f5]"></div>
            </div>

            {/* Hộp thông báo màu tím pastel */}
            <div className="p-3.5 bg-[#f4f2ff] border border-[#e8e4ff] rounded-[18px] w-full flex items-start space-x-3">
                <div className="w-6 h-6 rounded-full bg-[#e8e4ff] flex items-center justify-center flex-shrink-0 mt-0.5 text-[#5a60ec]">
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                </div>
                <p className="text-[11px] text-[#6b7280] leading-relaxed text-left">
                    <strong className="text-[#374151] font-semibold">Tài khoản do quản trị viên cung cấp.</strong> Vui lòng liên hệ giáo viên hoặc quản trị viên nếu bạn cần hỗ trợ.
                </p>
            </div>
        </div>
    )
}
