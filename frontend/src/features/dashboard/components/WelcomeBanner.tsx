import React from 'react'

interface WelcomeBannerProps {
  userName: string
  taskCount: number
}

export const WelcomeBanner: React.FC<WelcomeBannerProps> = ({
  userName,
  taskCount,
}) => {
  return (
    <div className="space-y-1 select-none">
      <h1 className="text-3xl sm:text-[32px] font-extrabold tracking-tight text-slate-900">
        Chào <span className="text-[#4338CA]">{userName}!</span>
      </h1>
      <p className="text-[14.5px] text-slate-500 font-normal flex items-center gap-1.5">
        <span>Bạn có {taskCount} nhiệm vụ cần hoàn thành hôm nay. Cố gắng lên nhé!</span>
        <span className="text-amber-400">✨</span>
      </p>
    </div>
  )
}
