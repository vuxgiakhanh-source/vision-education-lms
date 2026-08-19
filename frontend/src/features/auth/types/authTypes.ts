export type LoginFormData = {
    phoneNumber: string
    password: string
}

export type LoginResponse = {
    access_token: string
    token_type: string
}