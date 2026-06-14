"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/auth.store";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
// import { mockUsers } from "@/mocks/data/users";
import { UserRole } from "@/constants/enums";
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  Compass,
  Loader2,
  AlertCircle,
  CheckCircle2,
  User as UserIcon,
  Phone
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { User } from "@/types/user";

function RegisterContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isAuthenticated } = useAuthStore();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [data, setData] = useState<{ status: number, message: string, user: User }>();

  // Lấy đường dẫn chuyển hướng từ tham số redirect
  const redirectUrl = searchParams.get("redirect") || "/";

  useEffect(() => {
    if (isAuthenticated) {
      router.push(redirectUrl);
    }
  }, [isAuthenticated, router, redirectUrl]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Kiểm tra đầu vào cơ bản
    if (!name.trim() || !email.trim() || !phoneNumber.trim() || !password || !confirmPassword) {
      setError("Vui lòng điền đầy đủ tất cả các trường.");
      return;
    }

    if (password.length < 6) {
      setError("Mật khẩu phải chứa ít nhất 6 ký tự.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Mật khẩu xác nhận không khớp.");
      return;
    }

    // Kiểm tra định dạng email cơ bản
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError("Địa chỉ email không đúng định dạng.");
      return;
    }

    // Kiểm tra định dạng số điện thoại
    const phoneRegex = /^[0-9]{10,11}$/;
    if (!phoneRegex.test(phoneNumber.trim().replace(/[\s.-]/g, ""))) {
      setError("Số điện thoại không hợp lệ (yêu cầu 10 - 11 số).");
      return;
    }

    setLoading(true);

    const registerUser = async () => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          full_name: name,
          email: email,
          phone: phoneNumber,
          password: password,
          confirm_password: confirmPassword,
        }),
      });
      const data = await response.json();
      return data;
    }

    const data = await registerUser();

    if (data?.message === "success") {
      login(data.user, "mock-jwt-token-xyz");
      setSuccess(true);
      setLoading(false);
      setTimeout(() => {
        router.push(redirectUrl);
      }, 1000);
    }
    else {
      setError(data?.message || "Email hoặc mật khẩu không chính xác.");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full relative">
      {/* Background Decorative Blur Rings */}
      <div className="absolute -top-12 -left-12 w-64 h-64 bg-cyan-400/20 dark:bg-cyan-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />
      <div className="absolute -bottom-12 -right-12 w-64 h-64 bg-blue-400/20 dark:bg-blue-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

      {/* Main Glassmorphic Panel */}
      <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">

        {/* Top Header */}
        <div className="text-center mb-6">
          <Link href="/" className="inline-flex items-center gap-2 group mb-2">
            <div className="p-2 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-xl text-white group-hover:scale-105 transition-transform duration-300">
              <Compass className="w-6 h-6 animate-spin-slow" />
            </div>
            <span className="font-bold text-2xl tracking-tight bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
              VnTravel
            </span>
          </Link>
          <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
            Đăng ký tài khoản
          </h2>
          <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
            Trở thành hội viên để nhận ưu đãi 10% và tích lũy dặm bay du lịch.
          </p>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="mb-5 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs flex items-start gap-2.5 animate-shake">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Success overlay */}
        {success && (
          <div className="absolute inset-0 bg-white/95 dark:bg-zinc-900/95 z-25 flex flex-col items-center justify-center text-center p-6 animate-fade-in">
            <div className="w-16 h-16 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 rounded-2xl flex items-center justify-center mb-4 animate-scale-up">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h3 className="text-lg font-bold text-zinc-900 dark:text-white mb-1">
              Đăng Ký Thành Công!
            </h3>
            <p className="text-xs text-zinc-400 dark:text-zinc-500">
              Hệ thống đang tự động đăng nhập và chuẩn bị hành trình du lịch của bạn...
            </p>
          </div>
        )}

        {/* Register Form */}
        <form onSubmit={handleRegister} className="space-y-4">
          {/* Họ và tên */}
          <div>
            <label htmlFor="name" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-1.5">
              Họ và tên
            </label>
            <div className="relative">
              <span className="absolute left-4 top-3 text-zinc-400">
                <UserIcon className="w-4.5 h-4.5" />
              </span>
              <input
                id="name"
                type="text"
                required
                placeholder="Nguyễn Văn A"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={loading}
                className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-1.5">
              Địa chỉ Email
            </label>
            <div className="relative">
              <span className="absolute left-4 top-3 text-zinc-400">
                <Mail className="w-4.5 h-4.5" />
              </span>
              <input
                id="email"
                type="email"
                required
                placeholder="email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
              />
            </div>
          </div>

          {/* Số điện thoại */}
          <div>
            <label htmlFor="phone" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-1.5">
              Số điện thoại
            </label>
            <div className="relative">
              <span className="absolute left-4 top-3 text-zinc-400">
                <Phone className="w-4.5 h-4.5" />
              </span>
              <input
                id="phone"
                type="tel"
                required
                placeholder="0901234567"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                disabled={loading}
                className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
              />
            </div>
          </div>

          {/* Mật khẩu */}
          <div>
            <label htmlFor="password" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-1.5">
              Mật khẩu (tối thiểu 6 ký tự)
            </label>
            <div className="relative">
              <span className="absolute left-4 top-3 text-zinc-400">
                <Lock className="w-4.5 h-4.5" />
              </span>
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-11 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                className="absolute right-4 top-3 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
              >
                {showPassword ? <EyeOff className="w-4.5 h-4.5" /> : <Eye className="w-4.5 h-4.5" />}
              </button>
            </div>
          </div>

          {/* Xác nhận mật khẩu */}
          <div>
            <label htmlFor="confirmPassword" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-1.5">
              Xác nhận mật khẩu
            </label>
            <div className="relative">
              <span className="absolute left-4 top-3 text-zinc-400">
                <Lock className="w-4.5 h-4.5" />
              </span>
              <input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                required
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-11 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex={-1}
                className="absolute right-4 top-3 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
              >
                {showConfirmPassword ? <EyeOff className="w-4.5 h-4.5" /> : <Eye className="w-4.5 h-4.5" />}
              </button>
            </div>
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full py-6 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold border-0 shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4.5 h-4.5 animate-spin" /> Đang thiết lập tài khoản...
              </>
            ) : (
              "Đăng ký ngay"
            )}
          </Button>
        </form>

        {/* Link to Login */}
        <div className="text-center pt-6 mt-6 border-t border-zinc-150 dark:border-zinc-850 text-xs text-zinc-500">
          Đã có tài khoản thành viên?{" "}
          <Link
            href={`/login?redirect=${encodeURIComponent(redirectUrl)}`}
            className="font-bold text-cyan-500 hover:text-cyan-600 transition-colors"
          >
            Đăng nhập ngay
          </Link>
        </div>

      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
      <Header />

      <main className="flex-grow flex items-center justify-center px-4 pt-28 pb-20 relative">
        <Suspense fallback={
          <div className="flex flex-col items-center justify-center">
            <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
          </div>
        }>
          <RegisterContent />
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}
