import React from 'react'
import bannerUnified from '../../../assets/images/banner_unified_pristine.png'

interface WelcomeBannerProps {
  userName: string
  taskCount: number
}

export const WelcomeBanner: React.FC<WelcomeBannerProps> = ({
  userName,
  taskCount,
}) => {
  return (
    <div
      className="relative w-full rounded-[20px] sm:rounded-[24px] overflow-hidden shadow-[0_8px_28px_rgba(23,26,78,0.12)] flex items-center select-none bg-gradient-to-r from-[#1B1E4E] via-[#22275E] to-[#2B308C] transition-all"
      style={{ minHeight: 'var(--banner-h)' }}
    >
      {/* 100% Unified Authentic Background Artwork - Seamless across full width */}
      <div className="absolute right-0 top-0 bottom-0 pointer-events-none flex items-center justify-end h-full w-full">
        <img
          src={bannerUnified}
          alt=""
          className="h-full w-full object-cover object-right select-none pointer-events-none opacity-50 sm:opacity-100"
        />
      </div>

      {/* Dynamic Typography - Sắc nét, phân cấp rõ ràng theo chuẩn thiết kế */}
      <div
        className="relative z-10 space-y-1 sm:space-y-2 max-w-[85%] sm:max-w-[62%] xl:max-w-[58%]"
        style={{
          paddingLeft: 'var(--banner-pad-x)',
          paddingRight: 'var(--banner-pad-x)',
          paddingTop: 'var(--banner-pad-y)',
          paddingBottom: 'var(--banner-pad-y)',
        }}
      >
        <p
          className="text-[#A5B4FC] font-semibold tracking-wide"
          style={{ fontSize: 'var(--banner-sub-size)' }}
        >
          Chào {userName}!
        </p>

        <h1
          className="font-extrabold text-white leading-[1.28] tracking-tight"
          style={{ fontSize: 'var(--banner-title-size)' }}
        >
          Bạn có <span className="text-[#C7D2FE] font-black">{taskCount} nhiệm vụ</span> <br className="hidden sm:inline" />{' '}
          cần hoàn thành hôm nay
        </h1>

        <p
          className="text-[#CBD5E1] font-medium pt-0.5"
          style={{ fontSize: 'var(--banner-sub-size)' }}
        >
          Cố gắng lên nhé!
        </p>
      </div>
    </div>
  )
}
