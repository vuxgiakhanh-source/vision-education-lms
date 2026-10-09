import axios from 'axios'
import { env } from '../config/config'

export const api = axios.create({
    baseURL: env.API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
})

// Tự động đính kèm JWT token vào header của mọi request nếu đã đăng nhập
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Xử lý response / bắt lỗi tập trung
api.interceptors.response.use(
    (response) => response,
    (error) => {
        return Promise.reject(error)
    }
)

export default api
