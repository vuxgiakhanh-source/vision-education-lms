import axios from 'axios'
import { env } from '../config/config'

export const api = axios.create({
    baseURL: env.API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
})

export default api
