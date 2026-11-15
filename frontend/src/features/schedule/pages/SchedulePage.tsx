import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { DashboardLayout } from '../../dashboard/components/DashboardLayout'
import { meService } from '../../auth/me/services/meService'
import { getShortName } from '../../../utils/getShortName'
import type { MeResponse } from '../../auth/me/types/meTypes'
import { ScheduleOptionA } from '../components/ScheduleOptionA'
import { ScheduleOptionB } from '../components/ScheduleOptionB'
import { ScheduleOptionC } from '../components/ScheduleOptionC'

export const SchedulePage: React.FC<{ initialVariant?: 'A' | 'B' | 'C' }> = ({
  initialVariant = 'A',
}) => {
  const [searchParams, setSearchParams] = useSearchParams()
  const queryVariant = searchParams.get('variant')?.toUpperCase()
  const validVariant: 'A' | 'B' | 'C' =
    queryVariant === 'A' || queryVariant === 'B' || queryVariant === 'C'
      ? queryVariant
      : initialVariant

  const [user, setUser] = useState<MeResponse | null>(null)
  const [activeVariant, setActiveVariant] = useState<'A' | 'B' | 'C'>(validVariant)

  useEffect(() => {
    if (queryVariant === 'A' || queryVariant === 'B' || queryVariant === 'C') {
      setActiveVariant(queryVariant)
    }
  }, [queryVariant])

  useEffect(() => {
    async function loadUser() {
      try {
        const profile = await meService.getMe()
        setUser(profile)
      } catch (error) {
        // Fallback khi xem preview
      }
    }

    loadUser()
  }, [])

  const handleSelectVariant = (variant: 'A' | 'B' | 'C') => {
    setActiveVariant(variant)
    setSearchParams({ variant: variant.toLowerCase() })
  }

  const displayName = user ? getShortName(user.full_name) : 'Gia Khánh'

  return (
    <DashboardLayout user={{ name: displayName }}>
      <div className="flex-1 flex flex-col w-full pb-8">
        {/* Nội dung trang: Mặc định hiển thị Bản A chuẩn mockup */}
        {activeVariant === 'A' && <ScheduleOptionA />}
        {activeVariant === 'B' && <ScheduleOptionB />}
        {activeVariant === 'C' && <ScheduleOptionC />}

        {/* Thanh chuyển đổi nhỏ gọn, tinh tế ở góc dưới để không làm rối mắt */}
        <div className="mt-8 pt-4 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-400">
          <span>Xem các biến thể thiết kế khác:</span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => handleSelectVariant('A')}
              className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${
                activeVariant === 'A'
                  ? 'bg-[#272288] text-white font-semibold'
                  : 'hover:text-slate-700 bg-slate-100'
              }`}
            >
              Bản A (Chuẩn Mockup)
            </button>
            <button
              type="button"
              onClick={() => handleSelectVariant('B')}
              className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${
                activeVariant === 'B'
                  ? 'bg-[#272288] text-white font-semibold'
                  : 'hover:text-slate-700 bg-slate-100'
              }`}
            >
              Bản B (Mobile Adaptive)
            </button>
            <button
              type="button"
              onClick={() => handleSelectVariant('C')}
              className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer ${
                activeVariant === 'C'
                  ? 'bg-[#272288] text-white font-semibold'
                  : 'hover:text-slate-700 bg-slate-100'
              }`}
            >
              Bản C (Interactive Modal)
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
