import React from 'react'
import {
  Download,
  ArrowRight,
  FolderOpen,
} from 'lucide-react'
import type { ResourceItem } from '../types/dashboard.types'

interface ResourceListCardProps {
  resources: ResourceItem[]
}

export const ResourceListCard: React.FC<ResourceListCardProps> = ({
  resources,
}) => {
  return (
    <div className="bg-white rounded-[26px] p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)] flex flex-col justify-between select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <FolderOpen className="w-5 h-5 text-[#4F46E5]" strokeWidth={2.2} />
          <h2 className="text-[15px] font-bold text-slate-900">Tài liệu mới</h2>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-[#EEF2FF] text-[#4F46E5]">
            {resources.length}
          </span>
        </div>
        <button
          type="button"
          className="text-xs font-semibold text-[#4F46E5] hover:text-[#4338CA] flex items-center gap-1 transition-colors"
        >
          <span>Xem tất cả</span>
          <ArrowRight className="w-3.5 h-3.5" strokeWidth={2.2} />
        </button>
      </div>

      {/* Resource Items */}
      <div className="space-y-3 pt-1">
        {resources.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between py-1 px-1 rounded-2xl hover:bg-slate-50/60 transition-all group"
          >
            {/* Left: File Badge + Title */}
            <div className="flex items-center gap-3 min-w-0 pr-2">
              {item.format === 'PDF' ? (
                <div className="w-8 h-8 rounded-lg bg-[#FEF2F2] text-[#EF4444] flex items-center justify-center shrink-0">
                  <span className="text-[10px] font-extrabold uppercase">PDF</span>
                </div>
              ) : (
                <div className="w-8 h-8 rounded-lg bg-[#FFFBEB] text-[#D97706] flex items-center justify-center shrink-0">
                  <span className="text-[10px] font-extrabold uppercase">PPT</span>
                </div>
              )}

              <p className="text-[13px] font-bold text-slate-900 truncate group-hover:text-[#4F46E5] transition-colors cursor-pointer">
                {item.title}
              </p>
            </div>

            {/* Right: File Size, Time, Download */}
            <div className="flex items-center gap-4 shrink-0">
              <span className="text-[11px] text-slate-400 whitespace-nowrap">
                {item.size}
              </span>
              <span className="text-[11px] text-slate-400 whitespace-nowrap hidden sm:inline">
                {item.timeAgo}
              </span>
              <button
                type="button"
                aria-label={`Tải xuống ${item.title}`}
                className="w-8 h-8 rounded-xl flex items-center justify-center text-[#4F46E5] hover:bg-[#EEF2FF] transition-colors"
              >
                <Download className="w-4 h-4" strokeWidth={2.2} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
