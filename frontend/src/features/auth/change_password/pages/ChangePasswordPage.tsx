import bgImage from '../../../../assets/images/background.webp'
import { ChangePasswordForm } from '../components/ChangePasswordForm'

export function ChangePasswordPage() {
    return (
        <main
            className="min-h-screen w-full bg-[length:100%_100%] bg-no-repeat bg-center flex items-center justify-center p-4 sm:p-6 lg:p-8 relative overflow-hidden"
            style={{ backgroundImage: `url(${bgImage})` }}
        >
            <div className="w-full max-w-[430px] flex items-center justify-center relative z-10">
                <ChangePasswordForm />
            </div>
        </main>
    )
}
