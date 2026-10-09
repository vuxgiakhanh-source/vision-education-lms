import React from 'react'
import {
  BarChart2,
  Flame,
  FileText,
  ChevronRight,
  TrendingUp,
  Target,
  CalendarCheck2,
} from 'lucide-react'
import type { KpiStats } from '../types/dashboard.types'

interface KpiStatCardsProps {
  stats: KpiStats
}

export const KpiStatCards: React.FC<KpiStatCardsProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 select-none">
      {/* Card 1: Điểm trung bình */}
      <div className="bg-white rounded-[26px] p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)] flex flex-col justify-between">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-[#EEF2FF] text-[#4F46E5] flex items-center justify-center shrink-0">
              <BarChart2 className="w-6 h-6" strokeWidth={2.5} />
            </div>
            <div>
              <span className="text-[12.5px] font-medium text-slate-500 block mb-1">
                Điểm trung bình
              </span>
              <div className="flex items-baseline gap-2">
                <div className="flex items-baseline">
                  <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
                    {stats.averageScore.current}
                  </span>
                  <span className="text-lg font-bold text-slate-400">
                    /{stats.averageScore.max}
                  </span>
                </div>
                {/* Trend Badge */}
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#ECFDF5] text-[#10B981]">
                  <TrendingUp className="w-3 h-3" strokeWidth={2.5} />
                  +{stats.averageScore.diff}
                </span>
              </div>
            </div>
          </div>
          <button
            type="button"
            aria-label="Chi tiết điểm"
            className="text-slate-400 hover:text-slate-600 p-1"
          >
            <ChevronRight className="w-4 h-4" strokeWidth={2.5} />
          </button>
        </div>

        {/* Footer info */}
        <div className="mt-3.5 pt-1 flex items-center gap-1.5 text-xs text-slate-500">
          <TrendingUp className="w-3.5 h-3.5 text-[#4F46E5]" strokeWidth={2} />
          <span>{stats.averageScore.diffLabel}</span>
        </div>
      </div>

      {/* Card 2: Chuỗi học tập */}
      <div className="bg-white rounded-[26px] p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)] flex flex-col justify-between">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-[#FFF7ED] text-[#F97316] flex items-center justify-center shrink-0">
              <Flame className="w-6 h-6 fill-[#F97316]/20" strokeWidth={2.2} />
            </div>
            <div>
              <span className="text-[12.5px] font-medium text-slate-500 block mb-1">
                Chuỗi học tập
              </span>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
                  {stats.streak.days} ngày
                </span>
              </div>
            </div>
          </div>
          <button
            type="button"
            aria-label="Chi tiết chuỗi"
            className="text-slate-400 hover:text-slate-600 p-1"
          >
            <ChevronRight className="w-4 h-4" strokeWidth={2.5} />
          </button>
        </div>

        {/* Footer info */}
        <div className="mt-3.5 pt-1 flex items-center gap-1.5 text-xs text-slate-500">
          <Target className="w-3.5 h-3.5 text-slate-400" strokeWidth={2} />
          <span>{stats.streak.note}</span>
        </div>
      </div>

      {/* Card 3: Bài tập cần nộp */}
      <div className="bg-white rounded-[26px] p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)] flex flex-col justify-between">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-[#F5F3FF] text-[#7C3AED] flex items-center justify-center shrink-0">
              <FileText className="w-6 h-6" strokeWidth={2.2} />
            </div>
            <div>
              <span className="text-[12.5px] font-medium text-slate-500 block mb-1">
                Bài tập cần nộp
              </span>
              <div className="flex items-center gap-2.5">
                <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
                  {stats.pendingAssignments.count} bài
                </span>
                {stats.pendingAssignments.isUrgent && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#FEE2E2] text-[#EF4444]">
                    <span className="w-3.5 h-3.5 rounded-full bg-[#EF4444] text-white text-[10px] font-bold flex items-center justify-center leading-none">!</span>
                    Cần nộp sớm
                  </span>
                )}
              </div>
            </div>
          </div>
          <button
            type="button"
            aria-label="Chi tiết bài tập"
            className="text-slate-400 hover:text-slate-600 p-1"
          >
            <ChevronRight className="w-4 h-4" strokeWidth={2.5} />
          </button>
        </div>

        {/* Footer info */}
        <div className="mt-3.5 pt-1 flex items-center gap-1.5 text-xs text-slate-500">
          <CalendarCheck2 className="w-3.5 h-3.5 text-slate-400" strokeWidth={2} />
          <span>Hạn gần nhất: {stats.pendingAssignments.nearestDeadline}</span>
        </div>
      </div>
    </div>
  )
}
