import type { Metadata } from "next";
import ContactClient from "./contact-client";

export const metadata: Metadata = {
  title: "Liên Hệ Với Chúng Tôi | ViTravel",
  description: "Liên hệ với ViTravel để nhận hỗ trợ giải đáp thắc mắc, tư vấn thiết kế tour du lịch riêng và các dịch vụ hành trình tối ưu nhất.",
};

export default function ContactPage() {
  return <ContactClient />;
}
