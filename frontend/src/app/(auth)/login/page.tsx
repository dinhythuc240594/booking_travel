"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/auth.store";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import { mockUsers } from "@/mocks/data/users";
import { User } from "@/types/user";
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
  ShieldAlert,
} from "lucide-react";
import { Button } from "@/components/ui/button";

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isAuthenticated } = useAuthStore();
  const [user, setUser] = useState(null);
  const [data, setData] = useState<{ status: number, message: string, user: User }>();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [demoLoginType, setDemoLoginType] = useState<string | null>(null);

  // Lấy đường dẫn chuyển hướng từ tham số redirect
  const redirectUrl = searchParams.get("redirect") || "/";

  useEffect(() => {
    if (isAuthenticated) {
      router.push(redirectUrl);
    }
  }, [isAuthenticated, router, redirectUrl]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email.trim() || !password.trim()) {
      setError("Vui lòng nhập đầy đủ email và mật khẩu.");
      return;
    }

    setLoading(true);

    const fetchUser = async () => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/signin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
        credentials: "include",
      });
      const data = await response.json();
      return data;
    }

    const data = await fetchUser();

    if (data?.status == true) {
      login(data.user, "mock-jwt-token-xyz");
      setSuccess(true);
      setLoading(false);
      setTimeout(() => {
        router.push(redirectUrl);
      }, 1000);
    }
    else {
      setError(data.message);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full relative">
      {/* Background Decorative Blur Rings */}
      <div className="absolute -top-12 -left-12 w-64 h-64 bg-cyan-400/20 dark:bg-cyan-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />
      <div className="absolute -bottom-12 -right-12 w-64 h-64 bg-blue-400/20 dark:bg-blue-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

      {/* Main Glassmorphic Login Box */}
      <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">

        {/* Top Branding / Welcome */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 group mb-3">
            <div className="p-2 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-xl text-white group-hover:scale-105 transition-transform duration-300">
              <Compass className="w-6 h-6 animate-spin-slow" />
            </div>
            <span className="font-bold text-2xl tracking-tight bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
              VnTravel
            </span>
          </Link>
          <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
            Chào mừng trở lại!
          </h2>
          <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
            Đăng nhập để quản lý lịch trình và hành trình du lịch của bạn.
          </p>
        </div>

        {/* Error notification */}
        {error && (
          <div className="mb-5 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs flex items-start gap-2.5 animate-shake">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Success animation overlay */}
        {success && (
          <div className="absolute inset-0 bg-white/95 dark:bg-zinc-900/95 z-25 flex flex-col items-center justify-center text-center p-6 animate-fade-in">
            <div className="w-16 h-16 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 rounded-2xl flex items-center justify-center mb-4 animate-scale-up">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h3 className="text-lg font-bold text-zinc-900 dark:text-white mb-1">
              Đăng Nhập Thành Công!
            </h3>
            <p className="text-xs text-zinc-400 dark:text-zinc-500">
              Đang chuyển hướng về trang đích của bạn...
            </p>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
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

          <div>
            <div className="flex justify-between items-center mb-2">
              <label htmlFor="password" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
                Mật khẩu
              </label>
              <Link
                href="/forgot-password"
                className="text-xs font-semibold text-cyan-500 hover:text-cyan-600 transition-colors"
              >
                Quên mật khẩu?
              </Link>
            </div>
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

          <Button
            type="submit"
            disabled={loading}
            className="w-full py-6 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold border-0 shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50"
          >
            {loading && !demoLoginType ? (
              <>
                <Loader2 className="w-4.5 h-4.5 animate-spin" /> Đang kiểm tra...
              </>
            ) : (
              "Đăng nhập"
            )}
          </Button>
        </form>

        {/* Divider */}
        {/* <div className="my-6 flex items-center gap-3">
          <div className="h-px bg-zinc-200 dark:bg-zinc-800 flex-grow" />
          <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">Hoặc sử dụng demo</span>
          <div className="h-px bg-zinc-200 dark:bg-zinc-800 flex-grow" />
        </div> */}

        {/* Quick Demo Login Panels */}
        {/* <div className="space-y-2 mb-6">
          <div className="grid grid-cols-3 gap-2">
            {[
              { role: "customer", label: "Khách hàng", icon: Users, color: "text-emerald-500 bg-emerald-500/10 hover:bg-emerald-500/20" },
              { role: "admin", label: "Quản trị viên", icon: ShieldAlert, color: "text-amber-500 bg-amber-500/10 hover:bg-amber-500/20" },
              { role: "user", label: "Nhân viên", icon: UserIcon, color: "text-cyan-500 bg-cyan-500/10 hover:bg-cyan-500/20" }
            ].map((demo) => (
              <button
                key={demo.role}
                type="button"
                disabled={loading}
                onClick={() => handleQuickLogin(demo.role as "customer" | "admin" | "user")}
                className={`py-2 px-2.5 rounded-xl border-0 flex flex-col items-center justify-center gap-1 text-[10px] font-bold cursor-pointer transition-all ${demo.color} disabled:opacity-40`}
              >
                {loading && demoLoginType === demo.role ? (
                  <Loader2 className="w-4.5 h-4.5 animate-spin" />
                ) : (
                  <demo.icon className="w-4.5 h-4.5" />
                )}
                <span>{demo.label}</span>
              </button>
            ))}
          </div>
          <p className="text-[10px] text-center text-zinc-400 dark:text-zinc-500">
            *Nhấp để đăng nhập nhanh tức thì bằng tài khoản mẫu hệ thống
          </p>
        </div> */}

        {/* Link to Register */}
        <div className="text-center pt-2.5 border-t border-zinc-150 dark:border-zinc-850 text-xs text-zinc-500">
          Chưa có tài khoản?{" "}
          <Link
            href={`/register?redirect=${encodeURIComponent(redirectUrl)}`}
            className="font-bold text-cyan-500 hover:text-cyan-600 transition-colors"
          >
            Đăng ký tài khoản mới
          </Link>
        </div>

      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
      <Header />

      <main className="flex-grow flex items-center justify-center px-4 pt-28 pb-20 relative">
        <Suspense fallback={
          <div className="flex flex-col items-center justify-center">
            <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
          </div>
        }>
          <LoginContent />
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}
