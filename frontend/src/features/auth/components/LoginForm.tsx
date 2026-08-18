import { useForm } from 'react-hook-form'
import type { LoginFormData } from '../types/authTypes' 
import { zodResolver } from '@hookform/resolvers/zod'
import { loginSchema } from '../schemas/authSchema'
 

export function LoginForm() {
    const {register, handleSubmit} = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema)
    })
    function onSubmit(data: LoginFormData) {
        console.log(data)
    }
    return (
        <form onSubmit={handleSubmit(onSubmit)}>
            <input placeholder="Nhập số điện thoại" type="tel" {...register("phoneNumber")} />
            <input placeholder ="Nhập mật khẩu" type="password" {...register("password")} />
            <button type="submit">Đăng nhập</button>
        </form>
    )
}
