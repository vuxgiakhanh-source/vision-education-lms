import React, { useState } from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import type { UserProfile } from '../types/dashboard.types'

interface DashboardLayoutProps {
  user: UserProfile
  children: React.ReactNode
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  user,
  children,
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="h-screen w-full bg-[#F8FAFD] flex font-sans antialiased text-[#1E293B] overflow-hidden selection:bg-[#EEF0FD] selection:text-[#5553E6]">
      {/* 1. Sidebar cố định bên trái */}
      <Sidebar
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* 2. Khung Viewport chính kéo dãn toàn bộ màn hình */}
      <div className="flex-1 min-w-0 flex flex-col h-screen overflow-y-auto overflow-x-hidden">
        {/* Header trên cùng cố định với backdrop blur tinh tế */}
        <div
          className="w-full bg-[#F8FAFD]/90 backdrop-blur-md px-3 sm:px-6 xl:px-7 sticky top-0 z-20 shrink-0 transition-all"
          style={{ paddingTop: 'var(--header-pt)', paddingBottom: 'var(--header-pb)' }}
        >
          <div className="w-full min-w-0">
            <Header
              user={user}
              onOpenMobileMenu={() => setIsMobileMenuOpen(true)}
            />
          </div>
        </div>

        {/* Nội dung trang */}
        <main
          className="flex-1 min-w-0 flex flex-col px-3 sm:px-6 xl:px-7 overflow-x-hidden"
          style={{ paddingTop: 'var(--main-pt)', paddingBottom: 'var(--main-pb)' }}
        >
          <div className="flex-1 min-w-0 flex flex-col w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
