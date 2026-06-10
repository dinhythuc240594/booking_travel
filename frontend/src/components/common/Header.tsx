"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/store/auth.store";
import { useWishlistStore } from "@/store/wishlist.store";
import { Menu, X, Compass, User as UserIcon, LogOut, LayoutDashboard, Heart, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  transparent?: boolean;
}

export default function Header({ transparent = false }: HeaderProps) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuthStore();
  const { wishlistedIds } = useWishlistStore();
  const wishlistCount = wishlistedIds.length;

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsMounted(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Kiểm tra xem header hiện tại có nên dùng nền trong suốt không
  const isTransparent = transparent && !isScrolled;

  const navigation = [
    { name: "Trang Chủ", href: "/" },
    { name: "Khám Phá Tours", href: "/tours" },
    { name: "Liên Hệ", href: "/contact" },
  ];

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        isTransparent
          ? "bg-transparent text-white"
          : "bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md border-b border-zinc-200/50 dark:border-zinc-800/50 shadow-sm text-zinc-900 dark:text-zinc-50"
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 sm:h-20">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="p-2 bg-gradient-to-tr from-cyan-500 to-blue-600 rounded-xl text-white group-hover:scale-105 transition-transform duration-300">
                <Compass className="w-6 h-6 animate-spin-slow" />
              </div>
              <span className="font-sans font-bold text-xl sm:text-2xl tracking-tight bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
                VnTravel
              </span>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex space-x-8">
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "text-sm font-medium transition-colors hover:text-cyan-500 relative py-2",
                    isActive
                      ? "text-cyan-500 font-semibold"
                      : isTransparent ? "text-white/90" : "text-zinc-600 dark:text-zinc-300"
                  )}
                >
                  {item.name}
                  {isActive && (
                    <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-500 rounded-full" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Desktop Auth / User Controls */}
          <div className="hidden md:flex items-center gap-4">
            {isMounted && isAuthenticated && user ? (
              <div className="flex items-center gap-4">
                <Link style={{ display: "none" }}
                  href="/wishlist"
                  className={cn(
                    "p-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors relative",
                    isTransparent ? "hover:bg-white/10" : ""
                  )}
                  title="Danh sách yêu thích"
                >
                  <Heart className="w-5 h-5 text-red-500 fill-red-500" />
                  {isMounted && wishlistCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white rounded-full flex items-center justify-center text-[9px] font-bold animate-pulse">
                      {wishlistCount}
                    </span>
                  )}
                </Link>
                <div className="flex items-center gap-3 pl-2 border-l border-zinc-200 dark:border-zinc-800">
                  <div className="text-right">
                    <p className="text-xs text-zinc-400">Xin chào,</p>
                    <p className="text-sm font-semibold">{user.name || "Tài khoản"}</p>
                  </div>
                  {/* Avatar đơn giản */}
                  <div className="relative group">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-400 to-blue-500 flex items-center justify-center text-white font-bold cursor-pointer hover:ring-2 hover:ring-cyan-400 transition-all">
                      {user.avatarUrl ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={user.avatarUrl} alt={user.name || "User"} className="w-full h-full rounded-full object-cover" />
                      ) : (
                        (user.name || "U").charAt(0).toUpperCase()
                      )}
                    </div>
                    {/* Dropdown Menu nhỏ */}
                    <div className="absolute right-0 top-full pt-2 w-48 hidden group-hover:block z-50">
                      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-xl py-2 text-zinc-700 dark:text-zinc-200">
                        <Link href="/profile" className="flex items-center gap-2 px-4 py-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-sm">
                          <UserIcon className="w-4 h-4" /> Thông tin cá nhân
                        </Link>
                        <Link href="/bookings" className="flex items-center gap-2 px-4 py-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-sm">
                          <Calendar className="w-4 h-4" /> Lịch sử đặt tour
                        </Link>
                        {/* <Link href="/admin/dashboard" className="flex items-center gap-2 px-4 py-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-sm">
                          <LayoutDashboard className="w-4 h-4" /> Trang quản trị
                        </Link> */}
                        <hr className="my-1 border-zinc-200 dark:border-zinc-800" />
                        <button
                          onClick={logout}
                          className="flex items-center gap-2 w-full text-left px-4 py-2 hover:bg-red-50 dark:hover:bg-red-950/20 text-red-600 dark:text-red-400 text-sm"
                        >
                          <LogOut className="w-4 h-4" /> Đăng xuất
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <>
                <Link href="/login" className={cn("text-sm font-medium hover:text-cyan-500 transition-colors", isTransparent ? "text-white" : "text-zinc-600 dark:text-zinc-300")}>
                  Đăng nhập
                </Link>
                <Link href="/register">
                  <Button className="rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0 shadow-md hover:shadow-lg transition-all duration-300">
                    Đăng ký
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center gap-3">
            {isMounted && isAuthenticated && user && (
              <Link
                href="/wishlist"
                className={cn(
                  "p-2 rounded-full",
                  isTransparent ? "text-white" : "text-zinc-700 dark:text-zinc-300"
                )}
              >
                <Heart className="w-5 h-5 text-red-500 fill-red-500" />
              </Link>
            )}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className={cn(
                "p-2 rounded-xl transition-colors",
                isTransparent ? "text-white hover:bg-white/10" : "text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800"
              )}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white dark:bg-zinc-950 border-b border-zinc-200 dark:border-zinc-850 px-4 pt-2 pb-6 space-y-3 animate-fade-in text-zinc-900 dark:text-zinc-50 shadow-lg">
          <div className="space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className="block px-3 py-2.5 rounded-lg text-base font-medium hover:bg-zinc-100 dark:hover:bg-zinc-900 transition-colors"
              >
                {item.name}
              </Link>
            ))}
          </div>

          <hr className="border-zinc-200 dark:border-zinc-800 my-2" />

          {isMounted && isAuthenticated && user ? (
            <div className="space-y-2">
              <div className="px-3 py-2 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-400 to-blue-500 flex items-center justify-center text-white font-bold">
                  {(user.name || "U").charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="text-sm font-semibold">{user.name || "Tài khoản"}</p>
                  <p className="text-xs text-zinc-500">{user.email || ""}</p>
                </div>
              </div>
              <Link
                href="/profile"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-base hover:bg-zinc-100 dark:hover:bg-zinc-900"
              >
                <UserIcon className="w-5 h-5 text-zinc-400" /> Thông tin cá nhân
              </Link>
              <Link
                href="/bookings"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-base hover:bg-zinc-100 dark:hover:bg-zinc-900"
              >
                <Calendar className="w-5 h-5 text-zinc-400" /> Lịch sử đặt tour
              </Link>
              <Link
                href="/admin/dashboard"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-base hover:bg-zinc-100 dark:hover:bg-zinc-900"
              >
                <LayoutDashboard className="w-5 h-5 text-zinc-400" /> Trang quản trị
              </Link>
              <button
                onClick={() => {
                  logout();
                  setIsMobileMenuOpen(false);
                }}
                className="flex items-center gap-2 w-full text-left px-3 py-2.5 rounded-lg text-base text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
              >
                <LogOut className="w-5 h-5" /> Đăng xuất
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-2 pt-2 px-3">
              <Link href="/login" onClick={() => setIsMobileMenuOpen(false)}>
                <Button variant="outline" className="w-full rounded-full border-zinc-300 dark:border-zinc-700">
                  Đăng nhập
                </Button>
              </Link>
              <Link href="/register" onClick={() => setIsMobileMenuOpen(false)}>
                <Button className="w-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0 shadow-md">
                  Đăng ký
                </Button>
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
