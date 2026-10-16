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
    <div className="dashboard-layout h-dvh w-full wide:max-w-[2000px] ultrawide:max-w-none ultrawide:border-x-0 wide:mx-auto wide:border-x wide:border-[#EAEFF5] bg-[#F8FAFD] flex font-sans antialiased text-[#1E293B] overflow-hidden selection:bg-[#EEF0FD] selection:text-[#5553E6]">
      {/* 1. Sidebar cố định bên trái */}
      <Sidebar
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* 2. Khung Viewport chính kéo dãn toàn bộ màn hình */}
      <div className="flex-1 min-w-0 flex flex-col h-dvh overflow-y-auto overflow-x-hidden">
        {/* Header trên cùng cố định với backdrop blur tinh tế */}
        <div
          className="w-full bg-[#F8FAFD]/90 backdrop-blur-md px-4 sm:px-6 xl:px-[26px] wide:max-w-[1752px] ultrawide:max-w-none wide:mx-auto wide:px-8 ultrawide:px-[clamp(32px,2vw,64px)] sticky top-0 z-20 shrink-0"
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
          className="flex-1 min-w-0 flex flex-col px-4 sm:px-6 xl:px-[26px] wide:w-full wide:max-w-[1752px] ultrawide:max-w-none wide:mx-auto wide:px-8 ultrawide:px-[clamp(32px,2vw,64px)]"
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
