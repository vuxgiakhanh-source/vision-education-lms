import type { NextConfig } from 'next'

// Các trang xem thử và mockup HTML chỉ dành cho lúc phát triển. Thư mục public/ được Next phục vụ
// nguyên trạng nên ở production phải chủ động chuyển hướng, không để học sinh mở được.
const isProduction = process.env.NODE_ENV === 'production'
const developmentOnlyPages = [
  '/:file(schedule-mockup.*)',
  '/dashboard-preview/:path*',
  '/schedule-preview',
]

const nextConfig: NextConfig = {
  devIndicators: false,
  turbopack: { root: __dirname },
  async redirects() {
    return [
      {
        source: '/schedule',
        destination: '/student-schedule',
        permanent: false,
      },
      {
        source: '/dashboard',
        destination: '/student-dashboard',
        permanent: false,
      },
      {
        source: '/teacher/dashboard',
        destination: '/teacher-dashboard',
        permanent: false,
      },
      {
        source: '/dashboard-preview',
        destination: '/dashboard-preview/index.html',
        permanent: false,
      },
      ...(isProduction
        ? developmentOnlyPages.map(source => ({ source, destination: '/', permanent: false }))
        : []),
    ]
  },
}

export default nextConfig
