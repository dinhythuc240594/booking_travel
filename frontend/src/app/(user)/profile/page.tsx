"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/auth.store";
import { useWishlistStore } from "@/store/wishlist.store";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import {
  User as UserIcon,
  Mail,
  Phone,
  Calendar,
  MapPin,
  Shield,
  Heart,
  Star,
  Edit2,
  Save,
  X,
  CheckCircle2,
  Loader2,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ProfilePage() {
  const [isMounted, setIsMounted] = useState(false);
  const { user, isAuthenticated, updateUser } = useAuthStore();
  const { wishlistedIds, setWishlist } = useWishlistStore();

  // Form state
  const [email, setEmail] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [gender, setGender] = useState("male");
  const [dob, setDob] = useState("");

  // Stats state
  const [stats, setStats] = useState({ bookings: 0, wishlist: 0, reviews: 0 });
  const [loadingStats, setLoadingStats] = useState(true);

  // Status state
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Initialize wishlist items based on database sample data on first mount if not loaded
  useEffect(() => {
    if (isMounted && isAuthenticated && user) {
      const isUser3 = String(user.id) === "3";
      const isUser4 = String(user.id) === "4";
      if (wishlistedIds.length === 0) {
        if (isUser3) {
          setWishlist(["2"]); // Tour Săn Mây Cầu Đất
        } else if (isUser4) {
          setWishlist(["1"]); // Tour Sơn Trà
        }
      }
    }
  }, [isMounted, isAuthenticated, user, wishlistedIds.length, setWishlist]);

  useEffect(() => {
    if (user) {
      setFullName(user.name || "");
      setPhone(user.phoneNumber || (user as any).phoneNumber || "");
      setAddress((user as any).address || "");
      setGender((user as any).gender || "male");
      setDob((user as any).dateOfBirth || "");
      setEmail(user.email || "");

      // Fetch user stats from APIs
      const fetchStats = async () => {
        try {
          setLoadingStats(true);
          // 1. Fetch bookings count
          const bookingsRes = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/bookings?email=${user.email}`, {
            credentials: "include"
          });
          let bookingsCount = 0;
          if (bookingsRes.ok) {
            const bookingsData = await bookingsRes.json();
            bookingsCount = Array.isArray(bookingsData) ? bookingsData.length : 0;
          }

          // 2. Wishlist count (read from Zustand wishlist store)
          const wishlistCount = wishlistedIds.length;

          // 3. Reviews count (simulate or read from database reviews count)
          const isUser3 = String(user.id) === "3";
          const reviewsCount = isUser3 ? 1 : 0; // customer_01 commented on tour 1 in database sample

          setStats({
            bookings: bookingsCount,
            wishlist: wishlistCount,
            reviews: reviewsCount
          });
        } catch (err) {
          console.error("Failed to load user stats:", err);
        } finally {
          setLoadingStats(false);
        }
      };

      fetchStats();
    }
  }, [user, wishlistedIds.length]);

  if (!isMounted) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
        <Header />
        <main className="flex-grow flex items-center justify-center pt-24 pb-16">
          <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
        </main>
        <Footer />
      </div>
    );
  }

  // Not Authenticated
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
        <Header />
        <main className="flex-grow flex items-center justify-center px-4 pt-28 pb-20">
          <div className="max-w-md w-full text-center bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-8 shadow-xl">
            <div className="w-16 h-16 bg-amber-50 dark:bg-amber-950/20 text-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-extrabold text-zinc-900 dark:text-white mb-3">
              Yêu Cầu Đăng Nhập
            </h2>
            <p className="text-zinc-500 dark:text-zinc-400 text-sm mb-8 leading-relaxed">
              Vui lòng đăng nhập tài khoản của bạn để quản lý thông tin cá nhân và xem các hành trình đã đặt.
            </p>
            <div className="space-y-3">
              <Link href={`/login?redirect=/profile`} className="block">
                <Button className="w-full py-6 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold border-0 shadow-md hover:shadow-lg transition-all duration-300">
                  Đăng nhập ngay
                </Button>
              </Link>
              <Link href="/" className="block">
                <Button variant="outline" className="w-full py-6 rounded-xl border-zinc-200 dark:border-zinc-850 hover:bg-zinc-50 dark:hover:bg-zinc-800 font-bold transition-all">
                  Quay lại trang chủ
                </Button>
              </Link>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {

      // 1. save profile

      const saveProfileRes = async () => {
        const response = await fetch(`${process.env.NEXT_PUBLIC_ADMIN_BASE_URL}/profile_user`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action: "update_info",
            email: email,
            full_name: fullName,
            phone_number: phone,
            address: address,
            gender: gender,
            date_of_birth: dob
          }),
          credentials: "include"
        });
        const data = await response.json();
        return data;
      }

      const data = await saveProfileRes();

      if (data?.status == true) {
        const userData = data.user;
        updateUser({
          name: userData.full_name,
          phoneNumber: userData.phone_number,
          email: userData.email,
          address: userData.address,
          gender: userData.gender,
          dateOfBirth: userData.date_of_birth
        });
        setMessage({ type: "success", text: "Cập nhật thông tin cá nhân thành công!" });
        setIsEditing(false);
      } else {
        setMessage({ type: "error", text: data?.message || "Có lỗi xảy ra, vui lòng thử lại sau." });
      }
    } catch (err) {
      setMessage({ type: "error", text: "Có lỗi xảy ra, vui lòng thử lại sau." });
    } finally {
      setSaving(false);
    }
  };

  const dashboardNav = [
    { name: "Thông tin cá nhân", href: "/profile", icon: UserIcon, active: true },
    { name: "Lịch sử đặt tour", href: "/bookings", icon: Calendar, active: false },
    // { name: "Danh sách yêu thích", href: "/wishlist", icon: Heart, active: false },
    // { name: "Đánh giá của tôi", href: "/reviews", icon: Star, active: false },
  ];

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
      <Header />

      <main className="flex-grow pt-28 sm:pt-36 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

            {/* Sidebar Navigation */}
            <div className="lg:col-span-1 space-y-6">
              {/* Profile Brief Card */}
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-6 text-center shadow-sm">
                <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-cyan-400 to-blue-500 flex items-center justify-center text-white text-3xl font-bold mx-auto mb-4 shadow-md overflow-hidden">
                  {user.avatarUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={user.avatarUrl} alt={user.name} className="w-full h-full object-cover" />
                  ) : (
                    (user.name || "U").charAt(0).toUpperCase()
                  )}
                </div>
                <h2 className="text-xl font-bold text-zinc-900 dark:text-white line-clamp-1">{user.name || "Khách hàng"}</h2>
                <p className="text-xs text-zinc-450 dark:text-zinc-500 mt-1 line-clamp-1">{user.email}</p>
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-500 text-[10px] font-bold uppercase tracking-wider mt-4">
                  <Shield className="w-3.5 h-3.5" /> Customer
                </div>
              </div>

              {/* Navigation list */}
              <nav className="flex lg:flex-col overflow-x-auto lg:overflow-x-visible gap-2 pb-2 lg:pb-0 border-b lg:border-b-0 border-zinc-150 dark:border-zinc-850">
                {dashboardNav.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center gap-3 px-5 py-3.5 rounded-2xl text-sm font-semibold transition-all whitespace-nowrap ${item.active
                      ? "bg-cyan-500 text-white shadow-md shadow-cyan-500/10"
                      : "text-zinc-650 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-805 hover:text-zinc-900 dark:hover:text-zinc-100"
                      }`}
                  >
                    <item.icon className="w-4 h-4 flex-shrink-0" />
                    <span>{item.name}</span>
                  </Link>
                ))}
              </nav>
            </div>

            {/* Dashboard Content */}
            <div className="lg:col-span-3 space-y-8">

              {/* Stat Counters Grid */}
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: "Đặt chỗ hành trình", count: stats.bookings, link: "/bookings", icon: Calendar, color: "from-blue-500 to-cyan-500" },
                  // { label: "Yêu thích của bạn", count: stats.wishlist, link: "/wishlist", icon: Heart, color: "from-pink-500 to-red-500" },
                  // { label: "Đánh giá đã viết", count: stats.reviews, link: "/reviews", icon: Star, color: "from-amber-500 to-orange-500" }
                ].map((statCard) => (
                  <Link
                    key={statCard.label}
                    href={statCard.link}
                    className="group bg-white dark:bg-zinc-900 border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-5 shadow-sm hover:shadow-md transition-all duration-300 relative overflow-hidden"
                  >
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <span className="text-[10px] sm:text-[11px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider block">
                          {statCard.label}
                        </span>
                        {loadingStats ? (
                          <Loader2 className="w-5 h-5 text-cyan-500 animate-spin" />
                        ) : (
                          <span className="text-2xl sm:text-3xl font-extrabold text-zinc-900 dark:text-white block">
                            {statCard.count}
                          </span>
                        )}
                      </div>
                      <div className={`p-2 sm:p-3 bg-gradient-to-tr ${statCard.color} text-white rounded-xl shadow-sm group-hover:scale-105 transition-transform duration-300`}>
                        <statCard.icon className="w-4 h-4 sm:w-5 sm:h-5" />
                      </div>
                    </div>
                  </Link>
                ))}
              </div>

              {/* Profile Card / Form */}
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-6 sm:p-8 shadow-sm">

                {/* Title & Actions */}
                <div className="flex justify-between items-center mb-8 pb-5 border-b border-zinc-100 dark:border-zinc-800/80">
                  <div>
                    <h1 className="text-2xl font-extrabold text-zinc-900 dark:text-white">
                      Thông Tin Cá Nhân
                    </h1>
                    <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
                      Quản lý chi tiết tài khoản, bảo mật và thông tin cá nhân của bạn.
                    </p>
                  </div>
                  {!isEditing && (
                    <Button
                      onClick={() => setIsEditing(true)}
                      variant="outline"
                      className="rounded-xl border-zinc-200 dark:border-zinc-800 flex items-center gap-1.5 font-bold transition-all text-xs cursor-pointer"
                    >
                      <Edit2 className="w-3.5 h-3.5" /> Chỉnh sửa
                    </Button>
                  )}
                </div>

                {/* Notifications */}
                {message && (
                  <div className={`mb-6 p-4 rounded-2xl text-xs flex items-start gap-3 border ${message.type === "success"
                    ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
                    : "bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400"
                    }`}>
                    {message.type === "success" ? <CheckCircle2 className="w-4.5 h-4.5 flex-shrink-0" /> : <AlertCircle className="w-4.5 h-4.5 flex-shrink-0" />}
                    <span>{message.text}</span>
                  </div>
                )}

                {/* Form detail */}
                <form onSubmit={handleSave} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {/* Full Name */}
                    <div>
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                        Họ và tên
                      </label>
                      <input
                        type="text"
                        required
                        disabled={!isEditing || saving}
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-850 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 disabled:opacity-75 transition-all"
                      />
                    </div>

                    {/* Email */}
                    <div>
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                        Địa chỉ Email
                      </label>
                      <div className="relative">
                        <span className="absolute left-4 top-3.5 text-zinc-450">
                          <Mail className="w-4 h-4" />
                        </span>
                        <input
                          type="email"
                          disabled
                          value={user.email}
                          className="w-full bg-zinc-100 dark:bg-zinc-950/40 border border-zinc-200 dark:border-zinc-850 rounded-xl pl-11 pr-4 py-3 text-sm text-zinc-450 dark:text-zinc-500 cursor-not-allowed transition-all"
                        />
                      </div>
                    </div>

                    {/* Phone Number */}
                    <div>
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                        Số điện thoại
                      </label>
                      <div className="relative">
                        <span className="absolute left-4 top-3.5 text-zinc-450">
                          <Phone className="w-4 h-4" />
                        </span>
                        <input
                          type="tel"
                          required
                          disabled={!isEditing || saving}
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-850 rounded-xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 disabled:opacity-75 transition-all"
                        />
                      </div>
                    </div>

                    {/* Gender */}
                    <div>
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                        Giới tính
                      </label>
                      <select
                        disabled={!isEditing || saving}
                        value={gender}
                        onChange={(e) => setGender(e.target.value)}
                        className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-850 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 disabled:opacity-75 transition-all"
                      >
                        <option value="male">Nam</option>
                        <option value="female">Nữ</option>
                        <option value="other">Khác</option>
                      </select>
                    </div>

                    {/* Birthday */}
                    <div>
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                        Ngày sinh
                      </label>
                      <input
                        type="date"
                        disabled={!isEditing || saving}
                        value={dob}
                        onChange={(e) => setDob(e.target.value)}
                        className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-850 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 disabled:opacity-75 transition-all"
                      />
                    </div>

                    {/* Address */}
                    <div>
                      <label className="block text-[11px] font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                        Địa chỉ cư trú
                      </label>
                      <div className="relative">
                        <span className="absolute left-4 top-3.5 text-zinc-450">
                          <MapPin className="w-4 h-4" />
                        </span>
                        <input
                          type="text"
                          disabled={!isEditing || saving}
                          placeholder="Ví dụ: Hải Châu, Đà Nẵng"
                          value={address}
                          onChange={(e) => setAddress(e.target.value)}
                          className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-855 rounded-xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 disabled:opacity-75 transition-all"
                        />
                      </div>
                    </div>

                  </div>

                  {/* Joined Date info */}
                  <div className="pt-4 flex items-center gap-1.5 text-xs text-zinc-400">
                    <Calendar className="w-4 h-4" />
                    <span>Ngày tham gia VnTravel: <span className="font-semibold">{user.createdAt || "Chưa rõ"}</span></span>
                  </div>

                  {/* Form Action Buttons */}
                  {isEditing && (
                    <div className="flex gap-3 pt-6 border-t border-zinc-100 dark:border-zinc-800/80">
                      <Button
                        type="button"
                        disabled={saving}
                        onClick={() => {
                          setIsEditing(false);
                          setFullName(user.name || "");
                          setPhone(user.phoneNumber || (user as any).phoneNumber || "");
                          setAddress((user as any).address || "");
                          setGender((user as any).gender || "male");
                          setDob((user as any).dateOfBirth || "");
                        }}
                        variant="outline"
                        className="px-6 py-5 rounded-xl text-zinc-700 dark:text-zinc-350 border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-all font-bold text-xs cursor-pointer bg-transparent"
                      >
                        <X className="w-3.5 h-3.5 gap-1" /> Hủy bỏ
                      </Button>

                      <Button
                        type="submit"
                        disabled={saving}
                        className="px-6 py-5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0 shadow-md font-bold text-xs flex items-center gap-1.5 transition-all cursor-pointer"
                      >
                        {saving ? (
                          <>
                            <Loader2 className="w-3.5 h-3.5 animate-spin" /> Đang lưu...
                          </>
                        ) : (
                          <>
                            <Save className="w-3.5 h-3.5" /> Lưu thay đổi
                          </>
                        )}
                      </Button>
                    </div>
                  )}
                </form>
              </div>

            </div>

          </div>

        </div>
      </main>

      <Footer />
    </div>
  );
}
