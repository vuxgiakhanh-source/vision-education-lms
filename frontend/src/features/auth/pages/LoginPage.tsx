import bgImage from '../../../assets/images/background.webp'
import laptopImage from '../../../assets/images/laptop.webp'
import notebookImage from '../../../assets/images/notebook.webp'
import { LoginForm } from "../components/LoginForm"

export function LoginPage() {
    return (
        <main
            className="min-h-screen w-full bg-[length:100%_100%] bg-no-repeat bg-center flex items-center justify-center p-4 sm:p-6 lg:p-8 relative overflow-hidden"
            style={{ backgroundImage: `url(${bgImage})` }}
        >
            {/* Khung chứa trung tâm, căn chỉnh khoảng cách hài hòa giữa 2 khối */}
            <div className="w-full max-w-[1240px] mx-auto flex flex-col lg:flex-row items-center justify-center gap-8 lg:gap-14 xl:gap-20 relative z-10 px-4 sm:px-6">

                {/* --- CỘT TRÁI: LAPTOP VÀ CUỐN SỔ ĐẶT PHÍA TRƯỚC --- */}
                <div className="w-full lg:flex-1 max-w-[620px] xl:max-w-[680px] hidden lg:flex justify-center items-center">
                    <div className="relative w-full">
                        {/* Ảnh Laptop */}
                        <img
                            src={laptopImage}
                            alt="Vision LMS Preview"
                            className="w-full h-auto object-contain pointer-events-none drop-shadow-[0_20px_40px_rgba(0,0,0,0.08)]"
                        />
                        {/* Ảnh Cuốn sổ đặt ở góc dưới phía trước máy tính, không che màn hình */}
                        <img
                            src={notebookImage}
                            alt="Vision LMS Notebook"
                            className="absolute -bottom-[8%] left-[26%] w-[48%] h-auto object-contain pointer-events-none drop-shadow-[0_15px_30px_rgba(0,0,0,0.12)]"
                        />
                    </div>
                </div>

                {/* --- CỘT PHẢI: FORM ĐĂNG NHẬP (ĐƯỢC DỊCH VỀ GẦN TRUNG TÂM) --- */}
                <div className="w-full lg:w-auto flex justify-center items-center">
                    <LoginForm />
                </div>

            </div>
        </main>
    )
}


