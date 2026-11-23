import type { NextConfig } from 'next'

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
    ]
  },
}

export default nextConfig
