import { TeacherExamOverview } from '../../../features/teacher/exams/overview/TeacherExamOverview'
import '../../../features/teacher/exams/overview/TeacherExamOverview.css'

export default async function TeacherExamsPage({
    searchParams,
}: {
    searchParams: Promise<{ preview?: string; q?: string }>
}) {
    const { preview, q } = await searchParams
    const showPreview =
        preview === '1' || (preview === undefined && process.env.NODE_ENV === 'development')
    return <TeacherExamOverview preview={showPreview} query={typeof q === 'string' ? q : ''} />
}
