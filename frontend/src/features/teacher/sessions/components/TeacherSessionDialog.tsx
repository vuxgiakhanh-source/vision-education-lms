import { CalendarDays, CircleCheck, Clock3, FileText, Folder, PencilLine, Plus, Users, X } from 'lucide-react'
import { useEffect, useRef, type ReactNode, type Ref } from 'react'
import type { TeacherSessionDetails } from '../services/teacherSessionService'
import styles from './TeacherSessionDialog.module.css'

type Props = {
    session: TeacherSessionDetails
    onClose: () => void
    actions?: ReactNode
    children?: ReactNode
    headingRef?: Ref<HTMLHeadingElement>
    saving?: boolean
}

const vietnameseDate = new Intl.DateTimeFormat('vi-VN', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'Asia/Ho_Chi_Minh' })

export function formatLessonDate(date: string) {
    return vietnameseDate.format(new Date(`${date}T00:00:00+07:00`))
}

export function formatClassTitle(className: string) {
    return `Lớp ${className.replace(/^Toán\s+/, '')}`
}

export function TeacherSessionDialog({ session, onClose, actions, children, headingRef, saving = false }: Props) {
    const dialog = useRef<HTMLDialogElement>(null)
    const materials = session.materials ?? []
    const panelClass = styles['dialog-section']
    const buttonClass = styles['dialog-button']
    const footerClass = styles['dialog-footer']

    useEffect(() => {
        if (dialog.current && !dialog.current.open) dialog.current.showModal()
    }, [])

    return (
        <dialog
            ref={dialog}
            className={styles.dialog}
            aria-labelledby="teacher-session-dialog-title"
            onCancel={event => { if (saving) event.preventDefault() }}
            onClose={onClose}
        >
            <header className={styles['dialog-head']}>
                <span className={styles['dialog-avatar']}><Users aria-hidden="true" /></span>
                <div>
                    <h2 id="teacher-session-dialog-title" ref={headingRef} tabIndex={-1}>{formatClassTitle(session.className)}</h2>
                    <div className={styles['dialog-meta']}>
                        <span><CalendarDays aria-hidden="true" /><time dateTime={session.date}>{formatLessonDate(session.date)}</time></span>
                        <span><Clock3 aria-hidden="true" />{session.timeRange}</span>
                        {session.teachingWeek !== undefined && <span>Tuần {session.teachingWeek}</span>}
                    </div>
                </div>
                <form method="dialog">
                    <button type="submit" aria-label="Đóng chi tiết buổi dạy" autoFocus disabled={saving} className={styles['dialog-close']}><X aria-hidden="true" /></button>
                </form>
            </header>

            {children ?? (
                <>
                    <div className={styles['dialog-body']}>
                        <section className={panelClass}>
                            <div className={styles['dialog-section-head']}>
                                <h3><FileText aria-hidden="true" />Nội dung bài học</h3>
                                <span className={styles['dialog-status']}><CircleCheck aria-hidden="true" />Đã cập nhật</span>
                                <button className={buttonClass} type="button" disabled><PencilLine aria-hidden="true" />Chỉnh sửa</button>
                            </div>
                            <div className={styles['dialog-note']}>
                                <strong>{session.topic}</strong>
                                {session.outline && <ul>{session.outline.map(item => <li key={item}>{item}</li>)}</ul>}
                            </div>
                        </section>
                        <section className={panelClass}>
                            <div className={styles['dialog-section-head']}>
                                <h3><Folder aria-hidden="true" />Tài liệu buổi học</h3>
                                {materials.length > 0 && <span className={styles['dialog-status']}>Đã có ({materials.length})</span>}
                                <button className={buttonClass} type="button" disabled><Plus aria-hidden="true" />Thêm</button>
                            </div>
                            {materials.length ? (
                                <ul className={styles['dialog-files']}>
                                    {materials.map(({ kind, name, size }) => (
                                        <li key={name} className={styles['dialog-file']}><span>{kind}</span><strong>{name}</strong><span className={styles['dialog-file-size']}>{size}</span></li>
                                    ))}
                                </ul>
                            ) : <p className={styles['dialog-empty']}>Chưa có tài liệu cho buổi này.</p>}
                        </section>
                        {actions}
                    </div>
                    <footer className={footerClass}><form method="dialog"><button className={buttonClass} type="submit">Đóng</button></form></footer>
                </>
            )}

        </dialog>
    )
}
