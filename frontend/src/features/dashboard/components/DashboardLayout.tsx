import React from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import type { UserProfile } from '../types/dashboard.types'
import dashboardBg from '../../../assets/images/dashboard-bg.png'

interface DashboardLayoutProps {
  user: UserProfile
  children: React.ReactNode
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  user,
  children,
}) => {
  return (
    <div
      className="h-screen w-screen relative overflow-hidden flex p-3.5 gap-4 font-sans antialiased text-slate-800 selection:bg-indigo-100 selection:text-indigo-800 bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: `url(${dashboardBg})` }}
    >
      {/* 1. Floating Sidebar Card on Left */}
      <Sidebar />

      {/* 2. Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative z-10">
        {/* Top Header */}
        <div className="pt-1 pb-3 shrink-0">
          <Header user={user} />
        </div>

        {/* Scrollable Viewport */}
        <main className="flex-1 overflow-y-auto space-y-4 pr-1 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
          <div className="max-w-[1360px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
