import { ChevronRight, UserRoundPlus, Users } from 'lucide-react'

export function TeacherExamAudience() {
    return (
        <section className="exam-card exam-fields" aria-labelledby="exam-event-audience-label">
            <div className="exam-audience-section" role="group" aria-labelledby="exam-event-audience-label">
                <header className="exam-card-head">
                    <h2 id="exam-event-audience-label">
                        <Users aria-hidden="true" />
                        Đối tượng tham gia{' '}
                        <span className="exam-required" aria-hidden="true">
                            *
                        </span>
                    </h2>
                </header>
                <div className="exam-wizard-audience">
                    <div>
                        <h3>
                            <Users aria-hidden="true" />
                            Lớp học
                        </h3>
                        <div className="exam-wizard-audience-body">
                            <div className="exam-grade-groups" id="exam-event-groups">
                                {[12, 11, 10].map((grade) => (
                                    <details className="exam-grade-group" key={grade}>
                                        <summary>
                                            <ChevronRight aria-hidden="true" />
                                            Khối {grade}
                                        </summary>
                                        <p className="exam-classes-grid">Chưa nối danh sách lớp.</p>
                                    </details>
                                ))}
                            </div>
                        </div>
                    </div>
                    <div>
                        <h3>
                            <UserRoundPlus aria-hidden="true" />
                            Thêm học sinh
                        </h3>
                        <div className="exam-wizard-audience-body">
                            <input
                                type="search"
                                id="exam-event-student-search"
                                aria-label="Tìm học sinh theo tên"
                                placeholder="Tìm học sinh theo tên…"
                                readOnly
                            />
                            <div className="exam-wizard-results" />
                            <div className="exam-wizard-chips" />
                        </div>
                    </div>
                </div>
                <p className="exam-wizard-selection" id="exam-event-audience-summary" role="status">
                    Chưa chọn lớp hoặc học sinh.
                </p>
            </div>
        </section>
    )
}
