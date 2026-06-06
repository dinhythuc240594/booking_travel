"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Compass, Mail, Phone, MapPin, Send } from "lucide-react";

export default function Footer() {
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim()) {
      setSubscribed(true);
      setEmail("");
      setTimeout(() => setSubscribed(false), 5000);
    }
  };

  return (
    <footer className="bg-zinc-900 text-zinc-300 border-t border-zinc-800 pt-16 pb-8 font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">

          {/* Cột 1: Thông tin thương hiệu */}
          <div className="space-y-6">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="p-2 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-xl text-white">
                <Compass className="w-6 h-6" />
              </div>
              <span className="font-bold text-xl text-white tracking-tight">
                VnTravel
              </span>
            </Link>
            <p className="text-sm text-zinc-400 leading-6">
              VnTravel tự hào mang đến những hành trình du lịch hoàn hảo, kết nối bạn với những kỳ quan thiên nhiên và trải nghiệm văn hóa tuyệt vời nhất trên khắp thế giới.
            </p>
            <div className="flex space-x-4">
              <Link href="#" className="p-2 bg-zinc-800 hover:bg-cyan-500 hover:text-white rounded-lg transition-colors duration-300">
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12c0 4.84 3.44 8.87 8 9.8V15H8v-3h2V9.5C10 7.57 11.57 6 13.5 6H16v3h-2c-.55 0-1 .45-1 1v2h3v3h-3v6.95c4.56-.93 8-4.96 8-9.75z" />
                </svg>
              </Link>
              <Link href="#" className="p-2 bg-zinc-800 hover:bg-cyan-500 hover:text-white rounded-lg transition-colors duration-300">
                <svg className="w-4 h-4 fill-none stroke-current stroke-2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
                  <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
                  <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>
                </svg>
              </Link>
              <Link href="#" className="p-2 bg-zinc-800 hover:bg-cyan-500 hover:text-white rounded-lg transition-colors duration-300">
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z" />
                </svg>
              </Link>
            </div>
          </div>

          {/* Cột 2: Khám phá */}
          <div>
            <h3 className="text-white font-semibold text-base mb-6 tracking-wide uppercase">Khám Phá</h3>
            <ul className="space-y-4 text-sm">
              <li>
                <Link href="/tours" className="hover:text-cyan-400 transition-colors">Tất Cả Tours</Link>
              </li>
              <li>
                <Link href="/tours?category=beach" className="hover:text-cyan-400 transition-colors">Du Lịch Biển Đảo</Link>
              </li>
              <li>
                <Link href="/tours?category=mountain" className="hover:text-cyan-400 transition-colors">Chinh Phục Núi Rừng</Link>
              </li>
              {/* <li>
                <Link href="/tours?category=international" className="hover:text-cyan-400 transition-colors">Tours Quốc Tế</Link>
              </li> */}
            </ul>
          </div>

          {/* Cột 3: Liên hệ & Hỗ trợ */}
          <div className="space-y-4">
            <h3 className="text-white font-semibold text-base mb-6 tracking-wide uppercase">Liên Hệ & Hỗ Trợ</h3>
            <ul className="space-y-4 text-sm text-zinc-400">
              <li className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-cyan-500 flex-shrink-0 mt-0.5" />
                <span>12A Đường Lê Lợi, Quận 1, TP. Hồ Chí Minh, Việt Nam</span>
              </li>
              <li className="flex items-center gap-3">
                <Phone className="w-5 h-5 text-cyan-500 flex-shrink-0" />
                <span>+84 (28) 3939 7979</span>
              </li>
              <li className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-cyan-500 flex-shrink-0" />
                <span>support@vitravel.example.com</span>
              </li>
            </ul>
          </div>

          {/* Cột 4: Đăng ký nhận bản tin */}
          <div>
            <h3 className="text-white font-semibold text-base mb-6 tracking-wide uppercase">Nhận Ưu Đãi Ngay</h3>
            <p className="text-sm text-zinc-400 mb-4 leading-6">
              Nhập email để nhận thông tin về các tour khuyến mãi mới nhất và voucher giảm giá 10% ngay hôm nay!
            </p>
            <form onSubmit={handleSubscribe} className="space-y-3">
              <div className="relative">
                <input
                  type="email"
                  required
                  placeholder="Địa chỉ email của bạn"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-zinc-800 text-zinc-100 placeholder-zinc-500 rounded-xl px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-cyan-500 border border-zinc-700 text-sm transition-all"
                />
                <button
                  type="submit"
                  className="absolute right-2 top-2 p-1.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 rounded-lg text-white transition-all shadow-md"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              {subscribed && (
                <p className="text-xs text-emerald-400 animate-fade-in">
                  ✓ Đăng ký thành công! Hãy kiểm tra email để nhận quà tặng.
                </p>
              )}
            </form>
          </div>

        </div>

        {/* Bản quyền */}
        <div className="border-t border-zinc-800 mt-16 pt-8 flex flex-col sm:flex-row justify-between items-center text-xs text-zinc-500 gap-4">
          <p>© {new Date().getFullYear()} VnTravel Inc. Bảo lưu mọi quyền.</p>
          <div className="flex space-x-6">
            <Link href="#" className="hover:text-zinc-400 transition-colors">Điều khoản dịch vụ</Link>
            <Link href="#" className="hover:text-zinc-400 transition-colors">Chính sách bảo mật</Link>
            <Link href="#" className="hover:text-zinc-400 transition-colors">Cookie</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
