import { joinSchedule, splitSchedule, toDraftFields, type ExamDraftFields } from './draftService'

const fieldLabels = {
    title: 'Tên kỳ thi',
    description: 'Mô tả',
    paper_id: 'Đề thi',
    duration_minutes: 'Thời lượng làm bài',
    opens_date: 'Ngày mở',
    opens_time: 'Giờ mở',
    closes_date: 'Ngày đóng',
    closes_time: 'Giờ đóng',
}

function splitFields(fields: ExamDraftFields) {
    const { opens_at, closes_at, ...rest } = toDraftFields(fields)
    const [opens_date, opens_time] = splitSchedule(opens_at)
    const [closes_date, closes_time] = splitSchedule(closes_at)
    return { ...rest, opens_date, opens_time, closes_date, closes_time }
}

export function mergeDraftEdits(
    base: ExamDraftFields | undefined,
    local: ExamDraftFields,
    remote: ExamDraftFields,
    resolution?: 'local' | 'server',
) {
    const before = base && splitFields(base)
    const mine = splitFields(local)
    const theirs = splitFields(remote)
    const conflicts: string[] = []

    function merge<Key extends keyof typeof mine>(key: Key) {
        if (mine[key] === theirs[key] || mine[key] === before?.[key]) return theirs[key]
        if (before && theirs[key] === before[key]) return mine[key]
        conflicts.push(fieldLabels[key])
        return resolution === 'server' ? theirs[key] : mine[key]
    }

    const fields: ExamDraftFields = {
        paper_id: merge('paper_id'),
        title: merge('title'),
        description: merge('description'),
        opens_at: joinSchedule(merge('opens_date'), merge('opens_time')),
        closes_at: joinSchedule(merge('closes_date'), merge('closes_time')),
        duration_minutes: merge('duration_minutes'),
    }
    return { fields, conflicts }
}

export function sameDraftFields(first: ExamDraftFields, second: ExamDraftFields) {
    return (Object.keys(first) as (keyof ExamDraftFields)[]).every((key) => first[key] === second[key])
}
