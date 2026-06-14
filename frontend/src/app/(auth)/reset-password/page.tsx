"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import {
  Lock,
  Eye,
  EyeOff,
  Compass,
  Loader2,
  AlertCircle,
  CheckCircle2,
  ArrowLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";

function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!token) {
      setError("Mã xác thực không tìm thấy. Vui lòng sử dụng liên kết từ email của bạn.");
    }
  }, [token]);

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!token) {
      setError("Mã xác thực không hợp lệ. Vui lòng yêu cầu một liên kết mới.");
      return;
    }

    if (!password || !confirmPassword) {
      setError("Vui lòng điền đầy đủ các trường.");
      return;
    }

    if (password.length < 6) {
      setError("Mật khẩu mới phải chứa ít nhất 6 ký tự.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Mật khẩu xác nhận không khớp.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/reset_password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token,
          password,
          confirm_password: confirmPassword,
        }),
      });

      const data = await response.json();

      if (data?.status === true) {
        setSuccess(true);
        setTimeout(() => {
          router.push("/login");
        }, 3000);
      } else {
        setError(data?.message || "Đặt lại mật khẩu thất bại.");
      }
    } catch (err) {
      setError("Không thể kết nối đến máy chủ. Vui lòng thử lại sau.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full relative animate-fade-in">
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
            Đặt lại mật khẩu
          </h2>
          <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
            Vui lòng nhập mật khẩu mới và xác nhận mật khẩu của bạn.
          </p>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="mb-5 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs flex items-start gap-2.5 animate-shake">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Success Overlay */}
        {success && (
          <div className="absolute inset-0 bg-white/95 dark:bg-zinc-900/95 z-25 flex flex-col items-center justify-center text-center p-6 animate-fade-in">
            <div className="w-16 h-16 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 rounded-2xl flex items-center justify-center mb-4 animate-scale-up">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h3 className="text-lg font-bold text-zinc-900 dark:text-white mb-2">
              Đặt lại mật khẩu thành công!
            </h3>
            <p className="text-xs text-zinc-400 dark:text-zinc-500 max-w-xs mx-auto">
              Mật khẩu của bạn đã được cập nhật thành công. Đang tự động chuyển hướng về trang Đăng nhập...
            </p>
          </div>
        )}

        {/* Reset Password Form */}
        <form onSubmit={handleResetPassword} className="space-y-4">
          {/* Mật khẩu mới */}
          <div>
            <label htmlFor="password" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-1.5">
              Mật khẩu mới (tối thiểu 6 ký tự)
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
                disabled={loading || !token}
                className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-11 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                disabled={!token}
                className="absolute right-4 top-3 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors disabled:opacity-50"
              >
                {showPassword ? <EyeOff className="w-4.5 h-4.5" /> : <Eye className="w-4.5 h-4.5" />}
              </button>
            </div>
          </div>

          {/* Xác nhận mật khẩu mới */}
          <div>
            <label htmlFor="confirmPassword" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-1.5">
              Xác nhận mật khẩu mới
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
                disabled={loading || !token}
                className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-11 pr-11 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 transition-all disabled:opacity-50"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex={-1}
                disabled={!token}
                className="absolute right-4 top-3 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors disabled:opacity-50"
              >
                {showConfirmPassword ? <EyeOff className="w-4.5 h-4.5" /> : <Eye className="w-4.5 h-4.5" />}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={loading || !token}
            className="w-full py-6 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold border-0 shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4.5 h-4.5 animate-spin" /> Đang cập nhật mật khẩu...
              </>
            ) : (
              "Xác nhận mật khẩu mới"
            )}
          </Button>
        </form>

        {/* Link back to login */}
        <div className="text-center pt-6 mt-6 border-t border-zinc-150 dark:border-zinc-850 text-xs">
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 font-bold text-zinc-500 hover:text-cyan-500 dark:hover:text-cyan-400 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Quay lại đăng nhập
          </Link>
        </div>

      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
      <Header />

      <main className="flex-grow flex items-center justify-center px-4 pt-28 pb-20 relative">
        <Suspense fallback={
          <div className="flex flex-col items-center justify-center">
            <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
          </div>
        }>
          <ResetPasswordContent />
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}
