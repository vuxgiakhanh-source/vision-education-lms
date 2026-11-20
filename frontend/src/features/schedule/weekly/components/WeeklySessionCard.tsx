import { useLayoutEffect, useRef } from 'react'
import { ArrowLeftRight, BookOpen, Check, RotateCcw, Sigma, Triangle } from 'lucide-react'
import type { WeeklySession } from '../types/weeklyScheduleTypes'

const SESSION_TOPICS = [
    { flag: 'hasAlgebra', label: 'Đại số', shortLabel: 'Đại', Icon: Sigma },
    { flag: 'hasGeometry', label: 'Hình học', shortLabel: 'Hình', Icon: Triangle },
    { flag: 'isReview', label: 'Ôn tập', shortLabel: 'Ôn', Icon: RotateCcw },
] as const

const SESSION_COLORS = {
    mine: {
        card: 'border-[#DCEDE3] border-l-[#2EAA58] bg-[#F2FAF4]',
        icon: 'bg-[#DEF2E4] text-[#187139]',
        badge: 'bg-[#D8F0DF] text-[#166534]',
    },
    other: {
        card: 'border-[#F3DEE6] border-l-[#EE4E75] bg-[#FFF2F6]',
        icon: 'bg-[#FBDDE6] text-[#B92C51]',
        badge: 'bg-[#FBD7E2] text-[#9D2247]',
    },
}

function SessionTopicIndicators({ flags }: { flags: NonNullable<WeeklySession['topicFlags']> }) {
    return (
        <ul role="list" aria-label="Phân loại nội dung" className="grid w-full max-w-24 grid-cols-3 gap-0.5">
            {SESSION_TOPICS.map(({ flag, label, shortLabel, Icon }) => {
                const active = flags[flag]
                const description = `${label}: ${active ? 'Có' : 'Không'}`

                return (
                    <li key={flag} title={description} className="flex min-w-0 flex-col items-center gap-1">
                        <span className={`relative flex size-5 items-center justify-center rounded-md ${active ? 'bg-white/85 text-slate-800' : 'text-slate-500/65'}`}>
                            <Icon aria-hidden="true" className="size-3.5" />
                            {active && (
                                <Check aria-hidden="true" className="absolute -end-0.5 -top-0.5 size-2.5 rounded-full bg-slate-700 p-px text-white" strokeWidth={3} />
                            )}
                        </span>
                        <span aria-hidden="true" className="text-[9px] leading-none font-medium text-slate-600">{shortLabel}</span>
                        <span className="sr-only">{description}</span>
                    </li>
                )
            })}
        </ul>
    )
}

export function WeeklySessionCard({ session }: { session: WeeklySession }) {
    const { label, className, topic, topicFlags, status } = session
    const colors = status === 'mine' ? SESSION_COLORS.mine : SESSION_COLORS.other
    const statusLabel = status === 'transferred' ? 'Đã chuyển ca' : 'Ca của bạn'
    const StatusIcon = status === 'transferred' ? ArrowLeftRight : Check
    const viewportRef = useRef<HTMLDivElement>(null)
    const textRef = useRef<HTMLDivElement>(null)

    useLayoutEffect(() => {
        const viewport = viewportRef.current
        const text = textRef.current
        if (!viewport || !text) return

        const fitText = () => {
            text.style.removeProperty('font-size')
            let overflows = text.scrollHeight > viewport.clientHeight
            if (overflows) {
                const normalSize = parseFloat(getComputedStyle(text).fontSize)
                const minSize = normalSize * 0.85
                let size = normalSize
                while (overflows && size > minSize) {
                    size = Math.max(minSize, size - 0.5)
                    text.style.fontSize = `${size}px`
                    overflows = text.scrollHeight > viewport.clientHeight
                }
            }
            if (overflows) viewport.tabIndex = 0
            else viewport.removeAttribute('tabindex')
        }

        fitText()
        const observer = new ResizeObserver(fitText)
        observer.observe(viewport, { box: 'border-box' })
        document.fonts.addEventListener('loadingdone', fitText)
        return () => {
            observer.disconnect()
            document.fonts.removeEventListener('loadingdone', fitText)
        }
    }, [className, label, status, topic, topicFlags])

    return (
        <article className={`@container flex min-w-0 flex-[1_0_4rem] flex-col overflow-hidden rounded-[15px] border border-l-4 px-1.5 py-2 text-left shadow-[0_1px_4px_rgba(45,54,88,0.1)] sm:px-2.5 ${colors.card}`}>
            <div ref={viewportRef} role="group" aria-label="Nội dung buổi học" className="flex min-h-0 min-w-0 flex-1 flex-col overflow-y-auto">
                <div ref={textRef} className="flex min-w-0 shrink-0 flex-col items-start gap-[0.45em] text-xs leading-tight supports-[font-size:1cqi]:text-[clamp(0.75rem,10cqi,0.875rem)]">
                    <header className="flex max-w-full items-center gap-[0.4em]">
                        <span className={`grid size-[1.65em] shrink-0 place-items-center rounded-md ${colors.icon}`}>
                            <BookOpen aria-hidden="true" className="size-[1.05em]" />
                        </span>
                        {label && <p className="text-[0.85em] font-semibold text-slate-700">{label}</p>}
                    </header>
                    {className && <h2 className="max-w-full text-[1.05em] leading-snug font-bold wrap-anywhere text-slate-950">{className}</h2>}
                    {topic && (
                        <p className="max-w-full leading-snug font-medium wrap-anywhere text-slate-700">
                            {topic}
                        </p>
                    )}
                    {topicFlags && <SessionTopicIndicators flags={topicFlags} />}
                </div>
            </div>
            {status && (
                <footer className="mt-1.5 shrink-0">
                    <p className={`inline-flex max-w-full items-center gap-0.5 rounded-full px-1 py-1 text-[0.625rem] leading-none font-semibold @min-[6rem]:gap-1 @min-[6rem]:px-1.5 @min-[7rem]:text-[0.6875rem] ${colors.badge}`}>
                        <StatusIcon aria-hidden="true" className="hidden size-3 shrink-0 @min-[6rem]:block" />
                        <span className="min-w-0 wrap-anywhere">{statusLabel}</span>
                    </p>
                </footer>
            )}
        </article>
    )
}
