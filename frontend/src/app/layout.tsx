import type { Metadata } from 'next'
import { Plus_Jakarta_Sans } from 'next/font/google'
import type { ReactNode } from 'react'
import '../index.css'

// next/font tải phông lúc build rồi phục vụ từ chính máy chủ của mình, không gọi tới Google
// khi học sinh mở trang. Bộ 'vietnamese' bắt buộc phải có, thiếu thì dấu tiếng Việt rơi về phông hệ thống.
const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ['latin', 'latin-ext', 'vietnamese'],
  display: 'swap',
  variable: '--font-plus-jakarta-sans',
})

export const metadata: Metadata = {
  title: 'Vision Education - LMS Dashboard',
  icons: { icon: '/favicon.svg' },
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="vi" className={plusJakartaSans.variable}>
      <body>{children}</body>
    </html>
  )
}
