export const MIN_NEW_PASSWORD_CHARACTERS = 8
export const MAX_PASSWORD_BYTES = 72
export const passwordTooLongMessage = `Mật khẩu không được vượt quá ${MAX_PASSWORD_BYTES} byte UTF-8.`

export function passwordFitsByteLimit(password: string): boolean {
    return new TextEncoder().encode(password).length <= MAX_PASSWORD_BYTES
}
