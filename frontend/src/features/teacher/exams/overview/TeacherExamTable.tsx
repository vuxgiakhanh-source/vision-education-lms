'use client'

import { useRef, useState } from 'react'
import { ArrowRight, CalendarDays, FileText, Search } from 'lucide-react'

const statuses = [
    { value: '', label: 'Tất cả' },
    { value: 'open', label: 'Đang diễn ra' },
    { value: 'upcoming', label: 'Sắp tới' },
    { value: 'ended', label: 'Đã kết thúc' },
] as const

type ExamRow = {
    title: string
    audience: string
    groups: string[]
    date: string
    time: string
    state: 'open' | 'upcoming' | 'ended'
    submitted: number
    total: number
}

const previewExams: ExamRow[] = [
    {
        title: 'Thi thử THPTQG – Lần 1',
        audience: 'Khối 12',
        groups: ['12A', '12B', '12C'],
        date: '25/11/2026',
        time: '08:00 – 10:00',
        state: 'open',
        submitted: 18,
        total: 80,
    },
    {
        title: 'Kiểm tra chương Đạo hàm',
        audience: '12A, 12B',
        groups: ['12A', '12B'],
        date: '25/11/2026',
        time: '14:00 – 15:00',
        state: 'open',
        submitted: 11,
        total: 60,
    },
    {
        title: 'Kiểm tra 1 tiết – Hàm số',
        audience: '11A',
        groups: ['11A'],
        date: '23/11/2026',
        time: '09:30 – 10:15',
        state: 'upcoming',
        submitted: 0,
        total: 40,
    },
    {
        title: 'Ôn tập giữa kỳ I',
        audience: '10A, 10B',
        groups: ['10A', '10B'],
        date: '20/11/2026',
        time: '07:30 – 08:30',
        state: 'ended',
        submitted: 40,
        total: 40,
    },
]

function searchText(value: string) {
    return value
        .toLowerCase()
        .normalize('NFD')
        .replace(/\p{Diacritic}/gu, '')
        .replaceAll('đ', 'd')
        .trim()
}

export function TeacherExamTable({ preview, initialQuery }: { preview: boolean; initialQuery: string }) {
    const [selectedStatus, setSelectedStatus] = useState('')
    const [selectedGroup, setSelectedGroup] = useState('')
    const [query, setQuery] = useState(initialQuery)
    const [dialogRow, setDialogRow] = useState<ExamRow | null>(null)
    const dialog = useRef<HTMLDialogElement>(null)
    const rows = preview ? previewExams : []
    const groups = [
        ...new Set(
            rows.flatMap((row) => [row.audience, ...row.groups]).filter((group) => !group.includes(',')),
        ),
    ].sort()
    const normalizedQuery = searchText(query)
    const matches = rows.filter(
        (row) =>
            (!selectedGroup || row.groups.includes(selectedGroup) || row.audience === selectedGroup) &&
            searchText(row.title).includes(normalizedQuery),
    )
    const visible = matches.filter((row) => !selectedStatus || row.state === selectedStatus)

    function openDetails(row: ExamRow | null) {
        setDialogRow(row)
        dialog.current?.showModal()
    }

    return (
        <section className="room-panel" aria-labelledby="exam-rooms-title">
            <header className="room-panel-head">
                <h2 id="exam-rooms-title">
                    <CalendarDays size={32} aria-hidden="true" />
                    Danh sách kỳ thi
                </h2>
                <button
                    type="button"
                    className="room-outline room-calendar"
                    onClick={() => openDetails(null)}
                >
                    Xem lịch thi <ArrowRight size={19} aria-hidden="true" />
                </button>
            </header>
            <div className="room-tabs" role="group" aria-label="Trạng thái kỳ thi">
                {statuses.map(({ value, label }) => (
                    <button
                        type="button"
                        key={value}
                        aria-pressed={selectedStatus === value}
                        onClick={() => setSelectedStatus(value)}
                    >
                        {label} ({matches.filter((row) => !value || row.state === value).length})
                    </button>
                ))}
            </div>
            <div className="room-filters">
                <select
                    aria-label="Lọc kỳ thi theo lớp hoặc khối"
                    value={selectedGroup}
                    onChange={(event) => setSelectedGroup(event.target.value)}
                >
                    <option value="">Tất cả lớp</option>
                    {groups.map((group) => (
                        <option key={group}>{group}</option>
                    ))}
                </select>
                <select
                    aria-label="Lọc kỳ thi theo trạng thái"
                    value={selectedStatus}
                    onChange={(event) => setSelectedStatus(event.target.value)}
                >
                    <option value="">Tất cả trạng thái</option>
                    {statuses.slice(1).map(({ value, label }) => (
                        <option key={value} value={value}>
                            {label}
                        </option>
                    ))}
                </select>
                <label className="room-search">
                    <Search size={21} aria-hidden="true" />
                    <input
                        aria-label="Tìm trong danh sách kỳ thi"
                        type="search"
                        placeholder="Tìm theo tên kỳ thi…"
                        value={query}
                        onChange={(event) => setQuery(event.target.value)}
                    />
                </label>
            </div>
            <div
                className="room-table-wrap"
                tabIndex={0}
                role="region"
                aria-labelledby="exam-rooms-title"
            >
                <table className="room-table" aria-labelledby="exam-rooms-title">
                    <thead>
                        <tr>
                            {[
                                'Tên kỳ thi',
                                'Lớp/Khối',
                                'Thời gian thi',
                                'Đã nộp bài',
                                'Trạng thái',
                            ].map((label) => (
                                <th scope="col" key={label}>
                                    {label}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {visible.map((row) => {
                            const percent = Math.floor((100 * row.submitted) / row.total)
                            const status = statuses.find((item) => item.value === row.state)?.label
                            return (
                                <tr key={row.title}>
                                    <th scope="row">
                                        <button
                                            type="button"
                                            className="room-row-title"
                                            aria-haspopup="dialog"
                                            onClick={() => openDetails(row)}
                                        >
                                            <FileText size={23} aria-hidden="true" />
                                            {row.title}
                                        </button>
                                    </th>
                                    <td>{row.audience}</td>
                                    <td>
                                        <span className="room-time">
                                            <CalendarDays size={20} aria-hidden="true" />
                                            <span>
                                                <span className="room-time-date">{row.date}</span>
                                                <span className="room-time-range">{row.time}</span>
                                            </span>
                                        </span>
                                    </td>
                                    <td>
                                        <div className="room-progress">
                                            <span>
                                                {row.submitted} / {row.total}
                                            </span>
                                            <span className="room-progress-line">
                                                <progress
                                                    value={row.submitted}
                                                    max={row.total}
                                                    aria-label={`Bài đã nộp · ${row.title}`}
                                                />
                                                {percent}%
                                            </span>
                                        </div>
                                    </td>
                                    <td>
                                        <span className="room-status" data-state={row.state}>
                                            {status}
                                        </span>
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>
            {!visible.length && (
                <p className="room-empty">
                    {rows.length
                        ? 'Không tìm thấy kỳ thi phù hợp.'
                        : 'Chưa có dữ liệu kỳ thi để hiển thị.'}
                </p>
            )}
            {preview && <p className="sr-only">Dữ liệu mẫu từ bản thiết kế</p>}
            <dialog ref={dialog} className="room-dialog" aria-labelledby="room-details-title">
                <h2 id="room-details-title">{dialogRow?.title ?? 'Lịch thi'}</h2>
                {dialogRow ? (
                    <p className="mt-4">
                        {dialogRow.audience} · {dialogRow.date}, {dialogRow.time} · {dialogRow.submitted}
                        /{dialogRow.total} bài đã nộp
                    </p>
                ) : rows.length ? (
                    <ul className="mt-4 space-y-2">
                        {rows.map((row) => (
                            <li key={row.title}>
                                {row.date}, {row.time} · {row.title}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="mt-4">Chưa có kỳ thi trong lịch.</p>
                )}
                {preview && <p className="room-preview-note">Xem trước bằng dữ liệu mẫu</p>}
                <form method="dialog" className="mt-5">
                    <button className="room-outline">Đóng</button>
                </form>
            </dialog>
        </section>
    )
}
