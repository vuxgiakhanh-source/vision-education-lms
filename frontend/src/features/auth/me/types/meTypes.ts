export type UserRole = 'admin' | 'teacher' | 'teaching_assistant' | 'student'

export type MeResponse = {
    id: number
    full_name: string
    phone_number: string
    role: UserRole
    must_change_password: boolean
    is_active: boolean
}  
