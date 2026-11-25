import { CalendarDays } from 'lucide-react'
import { joinSchedule, splitSchedule, type ScheduleField } from '../drafts/draftService'
import type { useExamDraft } from './useExamDraft'

export function TeacherExamSchedule({
    fields,
    edit,
}: Pick<ReturnType<typeof useExamDraft>, 'fields' | 'edit'>) {
    const [date, time] = splitSchedule(fields.opens_at)
    const [closeDate, closeTime] = splitSchedule(fields.closes_at)
    const { duration_minutes: duration } = fields
    const windowMinutes =
        date && time && closeDate && closeTime
            ? (Date.parse(fields.closes_at + '+07:00') - Date.parse(fields.opens_at + '+07:00')) / 60_000
            : NaN

    function updateDateTime(field: ScheduleField, nextDate: string, nextTime: string) {
        edit(field, joinSchedule(nextDate, nextTime))
    }

    return (
        <section className="exam-card exam-fields" aria-labelledby="exam-event-schedule-title">
            <header className="exam-card-head">
                <h2 id="exam-event-schedule-title">
                    <CalendarDays aria-hidden="true" />
                    Thời gian thi
                </h2>
            </header>
            <fieldset className="exam-timing-window">
                <legend>Khung giờ mở kỳ thi</legend>
                <div className="exam-timing-row">
                    <label>
                        Ngày mở
                        <input
                            name="date"
                            type="date"
                            required
                            value={date}
                            onChange={(event) => {
                                updateDateTime('opens_at', event.target.value, time)
                            }}
                        />
                    </label>
                    <label>
                        Giờ mở
                        <input
                            name="time"
                            type="time"
                            required
                            value={time}
                            onChange={(event) => {
                                updateDateTime('opens_at', date, event.target.value)
                            }}
                        />
                    </label>
                </div>
                <div className="exam-timing-row">
                    <label>
                        Ngày đóng
                        <input
                            name="closeDate"
                            type="date"
                            required
                            value={closeDate}
                            onChange={(event) => {
                                updateDateTime('closes_at', event.target.value, closeTime)
                            }}
                        />
                    </label>
                    <label>
                        Giờ đóng
                        <input
                            name="closeTime"
                            type="time"
                            required
                            value={closeTime}
                            onChange={(event) => {
                                updateDateTime('closes_at', closeDate, event.target.value)
                            }}
                        />
                    </label>
                </div>
            </fieldset>
            <label>
                Thời lượng làm bài mỗi học sinh (phút)
                <input
                    name="duration"
                    type="number"
                    min={1}
                    required
                    value={duration ?? ''}
                    onChange={(event) =>
                        edit(
                            'duration_minutes',
                            Number.isFinite(event.target.valueAsNumber)
                                ? event.target.valueAsNumber
                                : null,
                        )
                    }
                />
            </label>
            <p
                className="exam-wizard-selection exam-timing-summary"
                id="exam-event-end-time"
                role="status"
            >
                {!Number.isFinite(windowMinutes) || !duration ? (
                    'Nhập giờ mở, giờ đóng và thời lượng làm bài.'
                ) : windowMinutes <= 0 ? (
                    'Giờ đóng phải sau giờ mở.'
                ) : (
                    <>
                        <span>
                            Mở {windowMinutes} phút · Làm bài {duration} phút/em
                        </span>
                        <span>
                            {windowMinutes >= duration
                                ? `Khoảng dư: ${windowMinutes - duration} phút`
                                : `Khung giờ mở thiếu ${duration - windowMinutes} phút.`}
                        </span>
                    </>
                )}
            </p>
        </section>
    )
}
