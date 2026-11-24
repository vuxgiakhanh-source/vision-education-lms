import axios from 'axios'
import { env } from './config'

// Không có timeout thì mạng yếu làm request treo vô hạn. Phòng thi dựa vào quy tắc
// "mỗi lần chỉ một request lưu đang chạy", nên một request treo sẽ chặn mọi lần lưu sau đó.
export const REQUEST_TIMEOUT_MS = 15_000

export const api = axios.create({
    baseURL: env.API_URL,
    timeout: REQUEST_TIMEOUT_MS,
    headers: {
        'Content-Type': 'application/json',
    },
})

export default api
