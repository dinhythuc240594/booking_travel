"use client";

import React, { useState } from "react";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import { Button } from "@/components/ui/button";
import { 
  Mail, 
  Phone, 
  MapPin, 
  Clock, 
  Send, 
  CheckCircle2, 
  Building, 
  ChevronDown, 
  Loader2, 
  Sparkles,
  Globe
} from "lucide-react";

// Định nghĩa thông tin chi nhánh
interface Branch {
  id: string;
  name: string;
  address: string;
  phone: string;
  email: string;
  hours: string;
  mapEmbedUrl: string; // Tọa độ giả lập hoặc URL bản đồ
  latLong: string;
}

const branches: Branch[] = [
  {
    id: "hanoi",
    name: "Trụ sở chính Hà Nội",
    address: "Tòa nhà VnTravel, 12 Tràng Thi, Phường Hàng Trống, Quận Hoàn Kiếm, Hà Nội",
    phone: "024 7300 6868",
    email: "hanoi@vitravel.com",
    hours: "8:00 - 18:00 (Tất cả các ngày trong tuần)",
    mapEmbedUrl: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3724.113264426573!2d105.8488349759695!3d21.028148987799587!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135ab9564f2fb9f%3A0xc7fdf705fa97f64!2zMTIgVHLDoG5nIFRoaSwgSMOgbmcgVHLhu5FuZywgSG_DoG4gS2nhur9tLCBIwYAgTuG7mWksIFZpZXRuYW0!5e0!3m2!1svi!2s!4v1700000000000!5m2!1svi!2s",
    latLong: "21.028149, 105.848835"
  },
  {
    id: "danang",
    name: "Chi nhánh Đà Nẵng",
    address: "Tầng 5, Tòa nhà ACB, 218 Bạch Đằng, Phường Phước Ninh, Quận Hải Châu, Đà Nẵng",
    phone: "0236 7300 6868",
    email: "danang@vitravel.com",
    hours: "8:00 - 17:30 (Thứ 2 - Thứ 7)",
    mapEmbedUrl: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3833.916960136262!2d108.22153287586523!3d16.06977278887693!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x314218311d9d713f%3A0x7d6a57500b7bf7e1!2zMjE4IELhuqFjaCDEkOG6sW5nLCBQaMaw4bubYyBOaW5oLCBI4bqjaSBDaMOidSwgxJDDoCBO4bq5bmcsIFZpZXRuYW0!5e0!3m2!1svi!2s!4v1700000000001!5m2!1svi!2s",
    latLong: "16.069773, 108.221533"
  },
  {
    id: "hcm",
    name: "Chi nhánh TP. Hồ Chí Minh",
    address: "Lầu 8, Vietcombank Tower, 5 Công Trường Mê Linh, Bến Nghé, Quận 1, TP. Hồ Chí Minh",
    phone: "028 7300 6868",
    email: "hcm@vitravel.com",
    hours: "8:00 - 18:00 (Tất cả các ngày trong tuần)",
    mapEmbedUrl: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3919.45899980646!2d106.70425337577531!3d10.776101989373243!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x31752f47a9ab57ab%3A0xf6f698305ff4c3b2!2zNSBDw7RuZyBUcsaw4budbmcgTcOqIExpbmgsIELhur_biBOnaMOpLCBRdeG6rW4gMSwgVGjDoG5oIHBo4buRIEjhu5MgQ2jDrSBNaW5oLCBWaWV0bmFt!5e0!3m2!1svi!2s!4v1700000000002!5m2!1svi!2s",
    latLong: "10.776102, 106.704253"
  }
];

// Định nghĩa câu hỏi thường gặp
interface FAQ {
  question: string;
  answer: string;
}

const faqs: FAQ[] = [
  {
    question: "Tôi có thể tự thiết kế lịch trình tour riêng không?",
    answer: "Có, VnTravel cung cấp dịch vụ thiết kế tour riêng (Customized Tour) hoàn hảo cho các gia đình, hội nhóm bạn bè hoặc doanh nghiệp. Bạn chỉ cần chọn chủ đề 'Yêu cầu thiết kế tour riêng' trong form liên hệ và cung cấp các thông tin cơ bản về điểm đến mong muốn, số lượng người và khoảng ngân sách. Đội ngũ chuyên viên thiết kế hành trình của chúng tôi sẽ liên hệ lại để cùng bạn xây dựng một lịch trình cá nhân hóa lý tưởng nhất."
  },
  {
    question: "Thời gian phản hồi sau khi gửi yêu cầu liên hệ là bao lâu?",
    answer: "Chúng tôi cam kết phản hồi tất cả các yêu cầu liên hệ trong giờ làm việc (8:00 - 18:00 hàng ngày) trong vòng tối đa 30 phút. Đối với những yêu cầu được gửi ngoài giờ làm việc hoặc vào các ngày nghỉ lễ lớn, chuyên viên chăm sóc khách hàng của VnTravel sẽ ưu tiên xử lý và liên hệ lại với bạn trước 9:00 sáng ngày làm việc tiếp theo."
  },
  {
    question: "Tôi có thể thanh toán đặt tour bằng các phương thức nào?",
    answer: "VnTravel hỗ trợ đa dạng phương thức thanh toán an toàn, linh hoạt bao gồm: Chuyển khoản ngân hàng trực tuyến nhanh (QR Pay), thẻ ATM nội địa, thẻ quốc tế Visa/Mastercard/JCB qua cổng thanh toán bảo mật, thanh toán qua ví điện tử thông dụng (Momo, VNPAY, ShopeePay), hoặc trả tiền mặt trực tiếp tại các văn phòng chi nhánh của VnTravel trên toàn quốc."
  },
  {
    question: "Chính sách hủy tour và hoàn tiền của VnTravel như thế nào?",
    answer: "Chính sách hủy và hoàn trả tiền sẽ phụ thuộc cụ thể vào từng gói tour và thời điểm hủy trước ngày khởi hành. Thông thường, nếu quý khách thực hiện yêu cầu hủy trước 15 ngày khởi hành, quý khách sẽ được hoàn trả 100% tiền cọc (trừ các chi phí vé máy bay không hoàn hủy nếu có). Các mốc thời gian cụ thể và chi tiết hoàn tiền luôn được ghi rõ ràng, minh bạch trong Hợp đồng Dịch vụ Lữ hành ký kết trước khi thanh toán."
  },
  {
    question: "VnTravel có cung cấp hướng dẫn viên tiếng nước ngoài không?",
    answer: "Có, chúng tôi sở hữu mạng lưới hướng dẫn viên du lịch chuyên nghiệp, giàu kinh nghiệm thực tế và có chứng chỉ hành nghề chuẩn quốc tế với nhiều ngôn ngữ như Tiếng Anh, Tiếng Trung, Tiếng Hàn, Tiếng Nhật, Tiếng Pháp, Tiếng Đức... Vui lòng ghi rõ yêu cầu về ngôn ngữ của hướng dẫn viên trong lời nhắn để chúng tôi chuẩn bị chu đáo nhất cho đoàn của bạn."
  }
];

export default function ContactClient() {
  const [activeBranch, setActiveBranch] = useState<string>("hanoi");
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(null);

  // Form State
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [subject, setSubject] = useState("Đặt tour du lịch");
  const [message, setMessage] = useState("");
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const currentBranch = branches.find(b => b.id === activeBranch) || branches[0];

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    // Validate cơ bản
    if (!fullName.trim() || !email.trim() || !phone.trim() || !message.trim()) {
      setErrorMsg("Vui lòng nhập đầy đủ các trường thông tin bắt buộc.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setErrorMsg("Email không đúng định dạng.");
      return;
    }

    setIsSubmitting(true);

    // Giả lập gửi API
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSuccess(true);
      
      // Lưu tin nhắn vào local storage để mô phỏng hệ thống quản trị nhận tin nhắn
      try {
        const existingMessages = JSON.parse(localStorage.getItem("vitravel-contact-messages") || "[]");
        const newMessage = {
          id: `msg-${Date.now()}`,
          fullName,
          email,
          phone,
          subject,
          message,
          createdAt: new Date().toISOString(),
          status: "unread"
        };
        localStorage.setItem("vitravel-contact-messages", JSON.stringify([newMessage, ...existingMessages]));
      } catch (err) {
        console.error("Lỗi lưu message:", err);
      }
    }, 1500);
  };

  const handleResetForm = () => {
    setFullName("");
    setEmail("");
    setPhone("");
    setSubject("Đặt tour du lịch");
    setMessage("");
    setIsSuccess(false);
  };

  const toggleFaq = (index: number) => {
    setOpenFaqIndex(openFaqIndex === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
      {/* Header trong suốt trên nền Hero */}
      <Header transparent={true} />

      <main className="flex-grow">
        {/* 1. HERO BANNER SECTION */}
        <section className="relative h-[400px] flex items-center justify-center overflow-hidden">
          {/* Background Image */}
          <div className="absolute inset-0 z-0">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1600&auto=format&fit=crop&q=80"
              alt="Contact Us Background"
              className="w-full h-full object-cover brightness-[0.6] scale-105"
            />
            {/* Dark overlay */}
            <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-zinc-50 dark:to-black" />
          </div>

          <div className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white mt-10">
            <span className="inline-flex items-center gap-1 px-3.5 py-1 rounded-full bg-cyan-500/20 backdrop-blur-md text-cyan-300 text-xs font-bold uppercase tracking-wider mb-4 border border-cyan-400/30">
              <Sparkles className="w-3.5 h-3.5" /> Kết nối cùng VnTravel
            </span>
            <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4">
              Liên Hệ Với Chúng Tôi
            </h1>
            <p className="text-sm sm:text-base md:text-lg text-zinc-200/90 max-w-2xl mx-auto">
              Bắt đầu hành trình khám phá thế giới của bạn bằng cách kết nối với các chuyên gia lập lịch trình lữ hành hàng đầu của chúng tôi.
            </p>
          </div>
        </section>

        {/* 2. QUICK CONTACT CARDS */}
        <section className="relative z-20 -mt-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Hotline Card */}
            <div className="bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-6 shadow-xl hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 flex flex-col justify-between group">
              <div>
                <div className="w-12 h-12 bg-cyan-500/10 text-cyan-500 rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
                  <Phone className="w-6 h-6 animate-pulse" />
                </div>
                <h3 className="text-base font-bold text-zinc-900 dark:text-white mb-2">Đường dây nóng 24/7</h3>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4 leading-relaxed">
                  Gọi điện trực tiếp để nhận tư vấn nhanh, phản hồi sự cố hoặc yêu cầu sửa đổi lịch trình khẩn cấp.
                </p>
              </div>
              <div className="space-y-1">
                <a href="tel:19006868" className="block text-lg font-extrabold text-cyan-500 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">
                  1900 6868
                </a>
                <a href="tel:02473006868" className="block text-xs font-semibold text-zinc-400 dark:text-zinc-500">
                  Phòng vé/Hỗ trợ: (024) 7300 6868
                </a>
              </div>
            </div>

            {/* Email Card */}
            <div className="bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-6 shadow-xl hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 flex flex-col justify-between group">
              <div>
                <div className="w-12 h-12 bg-blue-500/10 text-blue-500 rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
                  <Mail className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-zinc-900 dark:text-white mb-2">Hòm thư điện tử</h3>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4 leading-relaxed">
                  Gửi yêu cầu hợp tác doanh nghiệp, báo giá tour đoàn số lượng lớn hoặc gửi phản ánh dịch vụ.
                </p>
              </div>
              <div className="space-y-1">
                <a href="mailto:support@vitravel.com" className="block text-lg font-extrabold text-cyan-500 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors break-all">
                  support@vitravel.com
                </a>
                <a href="mailto:info@vitravel.com" className="block text-xs font-semibold text-zinc-400 dark:text-zinc-500 break-all">
                  Đối tác/Quảng cáo: info@vitravel.com
                </a>
              </div>
            </div>

            {/* Office Card */}
            <div className="bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-6 shadow-xl hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 flex flex-col justify-between group">
              <div>
                <div className="w-12 h-12 bg-emerald-500/10 text-emerald-500 rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300">
                  <Building className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-zinc-900 dark:text-white mb-2">Văn phòng đại diện</h3>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-4 leading-relaxed">
                  Đến văn phòng của chúng tôi để trao đổi trực tiếp, thiết kế lịch trình chuyên biệt hoặc ký kết hợp đồng giấy.
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-bold text-zinc-800 dark:text-zinc-200">
                  Hà Nội, Đà Nẵng, TP. HCM
                </p>
                <p className="text-xs font-semibold text-zinc-400 dark:text-zinc-500">
                  Mở cửa đón khách từ 8:00 đến 18:00
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* 3. CONTACT FORM & INTERACTIVE MAP */}
        <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
            
            {/* COLUMN 1: FORM (7/12) */}
            <div className="lg:col-span-7 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-3xl p-6 sm:p-10 shadow-lg relative overflow-hidden">
              
              {/* Form title */}
              <div className="mb-8">
                <h2 className="text-2xl font-extrabold text-zinc-900 dark:text-white mb-2">
                  Gửi Yêu Cầu Cho Chúng Tôi
                </h2>
                <p className="text-xs sm:text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">
                  Hãy điền đầy đủ các thông tin bên dưới. Chuyên viên tư vấn lữ hành của VnTravel sẽ liên hệ lại trực tiếp qua số điện thoại hoặc email trong vòng tối đa 30 phút.
                </p>
              </div>

              {/* SUCCESS OVERLAY STATE */}
              {isSuccess ? (
                <div className="py-12 px-4 flex flex-col items-center justify-center text-center animate-scale-up">
                  <div className="w-20 h-20 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 rounded-3xl flex items-center justify-center mb-6 animate-bounce">
                    <CheckCircle2 className="w-12 h-12" />
                  </div>
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-[10px] font-bold uppercase tracking-wider mb-3">
                    Gửi tin nhắn thành công
                  </span>
                  <h3 className="text-xl font-extrabold text-zinc-900 dark:text-white mb-2">
                    Cảm ơn {fullName}!
                  </h3>
                  <p className="text-xs sm:text-sm text-zinc-500 dark:text-zinc-400 max-w-md mx-auto mb-8 leading-relaxed">
                    Yêu cầu tư vấn chủ đề <strong className="text-zinc-800 dark:text-zinc-200">&quot;{subject}&quot;</strong> của bạn đã được chuyển tới phòng kinh doanh lữ hành. Chúng tôi sẽ gọi lại cho bạn sớm nhất theo số <strong className="text-cyan-500">{phone}</strong>.
                  </p>
                  <Button 
                    onClick={handleResetForm}
                    className="rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0 shadow-md font-bold px-8 py-5 transition-all"
                  >
                    Gửi yêu cầu mới
                  </Button>
                </div>
              ) : (
                /* ACTUAL FORM */
                <form onSubmit={handleFormSubmit} className="space-y-5">
                  {/* Name field */}
                  <div>
                    <label htmlFor="form-name" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                      Họ và tên <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="form-name"
                      type="text"
                      required
                      placeholder="Nguyễn Văn A"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      disabled={isSubmitting}
                      className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
                    />
                  </div>

                  {/* Email & Phone grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                      <label htmlFor="form-email" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                        Địa chỉ Email <span className="text-red-500">*</span>
                      </label>
                      <input
                        id="form-email"
                        type="email"
                        required
                        placeholder="email@example.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        disabled={isSubmitting}
                        className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
                      />
                    </div>
                    <div>
                      <label htmlFor="form-phone" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                        Số điện thoại <span className="text-red-500">*</span>
                      </label>
                      <input
                        id="form-phone"
                        type="tel"
                        required
                        placeholder="0901234567"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        disabled={isSubmitting}
                        className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
                      />
                    </div>
                  </div>

                  {/* Subject selector */}
                  <div>
                    <label htmlFor="form-subject" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                      Chủ đề cần tư vấn
                    </label>
                    <select
                      id="form-subject"
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                      disabled={isSubmitting}
                      className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 cursor-pointer transition-all disabled:opacity-50"
                    >
                      <option value="Đặt tour du lịch">Đặt tour du lịch có sẵn</option>
                      <option value="Yêu cầu thiết kế tour riêng">Yêu cầu thiết kế tour riêng (Customized Tour)</option>
                      <option value="Hỗ trợ thanh toán/Hoàn tiền">Hỗ trợ thanh toán / Hoàn tiền</option>
                      <option value="Hợp tác đại lý/Doanh nghiệp">Hợp tác đại lý / Doanh nghiệp</option>
                      <option value="Ý kiến đóng góp/Khiếu nại">Ý kiến đóng góp / Khiếu nại</option>
                      <option value="Khác">Khác</option>
                    </select>
                  </div>

                  {/* Message field */}
                  <div>
                    <label htmlFor="form-message" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                      Lời nhắn / Mô tả chi tiết yêu cầu <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      id="form-message"
                      rows={4}
                      required
                      placeholder="Nhập thông tin chi tiết về số lượng người, ngày khởi hành dự kiến, khách sạn yêu cầu hoặc bất kỳ câu hỏi nào bạn đang thắc mắc..."
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      disabled={isSubmitting}
                      className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50 resize-y min-h-[120px]"
                    />
                  </div>

                  {/* Error display */}
                  {errorMsg && (
                    <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-red-500 flex-shrink-0" />
                      <span>{errorMsg}</span>
                    </div>
                  )}

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full py-6 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold border-0 shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" /> Đang gửi yêu cầu...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" /> Gửi thông tin liên hệ
                      </>
                    )}
                  </Button>
                </form>
              )}
            </div>

            {/* COLUMN 2: TABBED BRANCHES & MAP (5/12) */}
            <div className="lg:col-span-5 flex flex-col gap-6">
              
              {/* Branch Selector Tabs */}
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200/60 dark:border-zinc-800/60 rounded-3xl p-2 shadow-sm flex gap-1">
                {branches.map(b => (
                  <button
                    key={b.id}
                    onClick={() => setActiveBranch(b.id)}
                    className={`flex-1 py-3 text-xs font-bold rounded-2xl cursor-pointer transition-all ${
                      activeBranch === b.id 
                        ? "bg-gradient-to-tr from-cyan-500 to-blue-600 text-white shadow-md"
                        : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800"
                    }`}
                  >
                    {b.id === "hanoi" ? "Hà Nội" : b.id === "danang" ? "Đà Nẵng" : "TP. HCM"}
                  </button>
                ))}
              </div>

              {/* Branch Detailed Card & Embed Map */}
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-3xl overflow-hidden shadow-lg flex flex-col flex-grow">
                {/* Embed Map Iframe */}
                <div className="w-full h-[240px] relative bg-zinc-100 dark:bg-zinc-950 border-b border-zinc-200 dark:border-zinc-800">
                  <iframe
                    title={currentBranch.name}
                    src={currentBranch.mapEmbedUrl}
                    width="100%"
                    height="100%"
                    style={{ border: 0 }}
                    allowFullScreen={false}
                    loading="lazy"
                    referrerPolicy="no-referrer-when-downgrade"
                    className="brightness-95 dark:invert dark:hue-rotate-180"
                  />
                  {/* Glowing Radar Anchor point overlay */}
                  <div className="absolute top-4 right-4 bg-zinc-900/80 backdrop-blur-md px-3 py-1 rounded-full border border-zinc-700/50 text-[10px] text-zinc-300 font-mono flex items-center gap-1.5 shadow-md">
                    <Globe className="w-3.5 h-3.5 text-cyan-400 animate-spin-slow" />
                    <span>GPS: {currentBranch.latLong.split(",")[0].trim()}</span>
                  </div>
                </div>

                {/* Branch Info details */}
                <div className="p-6 sm:p-8 space-y-5 text-sm flex-grow flex flex-col justify-between">
                  <div className="space-y-4">
                    <h3 className="font-extrabold text-lg text-zinc-900 dark:text-white flex items-center gap-2">
                      <Building className="w-5 h-5 text-cyan-500" />
                      {currentBranch.name}
                    </h3>
                    
                    <div className="space-y-3.5 text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed">
                      <div className="flex items-start gap-3">
                        <MapPin className="w-4 h-4 text-zinc-400 flex-shrink-0 mt-0.5" />
                        <span>{currentBranch.address}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Phone className="w-4 h-4 text-zinc-400 flex-shrink-0" />
                        <a href={`tel:${currentBranch.phone.replace(/\s/g, "")}`} className="hover:text-cyan-500 transition-colors font-semibold">
                          {currentBranch.phone}
                        </a>
                      </div>
                      <div className="flex items-center gap-3">
                        <Mail className="w-4 h-4 text-zinc-400 flex-shrink-0" />
                        <a href={`mailto:${currentBranch.email}`} className="hover:text-cyan-500 transition-colors font-semibold break-all">
                          {currentBranch.email}
                        </a>
                      </div>
                      <div className="flex items-start gap-3">
                        <Clock className="w-4 h-4 text-zinc-400 flex-shrink-0 mt-0.5" />
                        <span>{currentBranch.hours}</span>
                      </div>
                    </div>
                  </div>

                  <hr className="border-zinc-150 dark:border-zinc-800/80 my-4" />

                  {/* Actions for offices */}
                  <div className="flex gap-3">
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(currentBranch.address)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 py-3 text-center bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 font-bold rounded-xl text-xs transition-all text-zinc-700 dark:text-zinc-300 cursor-pointer"
                    >
                      Xem bản đồ lớn
                    </a>
                    <a
                      href={`tel:${currentBranch.phone.replace(/\s/g, "")}`}
                      className="flex-1 py-3 text-center bg-gradient-to-tr from-cyan-500 to-blue-600 text-white font-bold rounded-xl text-xs transition-all shadow-md hover:shadow-lg flex items-center justify-center gap-1.5 cursor-pointer"
                    >
                      <Phone className="w-3.5 h-3.5" /> Gọi chi nhánh
                    </a>
                  </div>
                </div>

              </div>

            </div>

          </div>
        </section>

        {/* 4. FAQ ACCORDION SECTION */}
        <section className="py-24 bg-zinc-100 dark:bg-zinc-950/40 border-t border-zinc-200/50 dark:border-zinc-800/40">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            {/* Section Header */}
            <div className="text-center mb-16">
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 text-xs font-bold uppercase tracking-wider mb-3">
                Hỗ trợ giải đáp
              </span>
              <h2 className="text-3xl font-extrabold text-zinc-900 dark:text-white">
                Câu Hỏi Thường Gặp
              </h2>
              <p className="text-zinc-500 dark:text-zinc-400 mt-3 text-xs sm:text-sm">
                Tìm kiếm nhanh câu trả lời cho các thắc mắc phổ biến nhất của quý khách trước khi gửi thông tin liên hệ.
              </p>
            </div>

            {/* Accordion container */}
            <div className="space-y-4">
              {faqs.map((faq, index) => {
                const isOpen = openFaqIndex === index;
                return (
                  <div
                    key={index}
                    className="bg-white dark:bg-zinc-900 border border-zinc-200/60 dark:border-zinc-800/60 rounded-2xl overflow-hidden shadow-sm transition-all"
                  >
                    {/* Accordion Header */}
                    <button
                      onClick={() => toggleFaq(index)}
                      className="w-full px-6 py-5 text-left flex justify-between items-center gap-4 hover:bg-zinc-50/50 dark:hover:bg-zinc-950/10 cursor-pointer"
                    >
                      <span className="font-bold text-sm sm:text-base text-zinc-800 dark:text-zinc-200">
                        {faq.question}
                      </span>
                      <div className={`w-8 h-8 rounded-xl bg-zinc-50 dark:bg-zinc-950 border border-zinc-200/80 dark:border-zinc-800/80 flex items-center justify-center flex-shrink-0 text-zinc-500 transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                    </button>

                    {/* Accordion Content */}
                    <div
                      className={`transition-all duration-300 ease-in-out overflow-hidden ${
                        isOpen ? "max-h-[300px] border-t border-zinc-150 dark:border-zinc-850" : "max-h-0"
                      }`}
                    >
                      <div className="px-6 py-5 text-xs sm:text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed bg-zinc-50/20 dark:bg-zinc-950/5">
                        {faq.answer}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

          </div>
        </section>

      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}
