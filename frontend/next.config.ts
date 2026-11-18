import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  devIndicators: false,
  turbopack: { root: __dirname },
  async redirects() {
    return [{
      source: '/dashboard-preview',
      destination: '/dashboard-preview/index.html',
      permanent: false,
    }]
  },
}

export default nextConfig
