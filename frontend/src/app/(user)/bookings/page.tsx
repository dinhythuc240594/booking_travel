"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/auth.store";
import { useBookingStore } from "@/store/booking.store";
import { useWishlistStore } from "@/store/wishlist.store";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import { BookingStatus, PaymentStatus } from "@/constants/enums";
import { Booking } from "@/types/booking";
import {
  Users,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Loader2,
  Compass,
  History,
  Clock,
  ShieldCheck,
  User as UserIcon,
  Heart,
  Star,
  Shield,
  Calendar,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function BookingsPage() {
  const [isMounted, setIsMounted] = useState(false);
  const [cancellingId, setCancellingId] = useState<string | null>(null);
  const [confirmCancelBooking, setConfirmCancelBooking] = useState<Booking | null>(null);
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [dbBookings, setDbBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);

  const { user, isAuthenticated } = useAuthStore();
  const { bookings, cancelBooking } = useBookingStore();
  const { wishlistedIds } = useWishlistStore();

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsMounted(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  // Lấy dữ liệu đặt chỗ từ API backend
  const fetchBookings = async () => {
    if (!isAuthenticated || !user) {
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/bookings?email=${user.email}`, {
        credentials: "include"
      });
      if (!res.ok) throw new Error("Failed to fetch bookings from server");
      const data = await res.json();

      const mapped: Booking[] = data.map((b: any) => ({
        id: String(b.id),
        tourId: String(b.tourId || b.reference_id),
        tourSlug: b.tourSlug || "",
        tourTitle: b.tourTitle || "Hành trình du lịch",
        tourImage: b.tourImage || "",
        // userId: b.user_id,
        userName: user.name,
        departureDate: b.departureDate || b.check_in_date || new Date().toISOString(),
        adults: b.adults || 1,
        children: b.children || 0,
        totalPrice: Number(b.total_price),
        status: b.status || b.booking_status,
        paymentStatus: b.payment_status || PaymentStatus.PAID,
        paymentMethod: b.payment_method || "credit_card",
        createdAt: b.created_at || new Date().toISOString(),
      }));
      setDbBookings(mapped);
    } catch (err) {
      console.warn("Backend bookings fetch failed, falling back to local storage:", err);
      setDbBookings(bookings.filter((b) => b.userId === user.id));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isMounted) {
      fetchBookings();
    }
  }, [isMounted, isAuthenticated, user, bookings]);

  // Dùng dbBookings thay cho myBookings
  const myBookings = dbBookings;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleCancelClick = (booking: Booking) => {
    setConfirmCancelBooking(booking);
  };

  const handleConfirmCancel = async () => {
    if (confirmCancelBooking) {
      setCancellingId(confirmCancelBooking.id);

      try {
        const isDbBooking = !isNaN(Number(confirmCancelBooking.id));
        if (isDbBooking) {
          const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/bookings/cancel/${confirmCancelBooking.id}`, {
            method: "POST",
            credentials: "include"
          });
          if (!res.ok) {
            throw new Error("Failed to cancel on server");
          }
        }

        cancelBooking(confirmCancelBooking.id);
        await fetchBookings();
      } catch (error) {
        console.error("Cancel booking error:", error);
        cancelBooking(confirmCancelBooking.id);
      } finally {
        setCancellingId(null);
        setConfirmCancelBooking(null);
      }
    }
  };

  const getStatusBadge = (status: BookingStatus) => {
    switch (status) {
      case BookingStatus.PENDING:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400 border border-amber-200/50 dark:border-amber-900/30">
            <Clock className="w-3.5 h-3.5" /> Chờ xác nhận
          </span>
        );
      case BookingStatus.CONFIRMED:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border border-emerald-200/50 dark:border-emerald-900/30">
            <CheckCircle2 className="w-3.5 h-3.5" /> Đã xác nhận
          </span>
        );
      case BookingStatus.COMPLETED:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400 border border-blue-200/50 dark:border-blue-900/30">
            <ShieldCheck className="w-3.5 h-3.5" /> Hoàn thành
          </span>
        );
      case BookingStatus.CANCELLED:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 border border-red-200/50 dark:border-red-900/30">
            <XCircle className="w-3.5 h-3.5" /> Đã hủy
          </span>
        );
      default:
        return null;
    }
  };

  const getPaymentBadge = (status: PaymentStatus) => {
    switch (status) {
      case PaymentStatus.PENDING:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-orange-500/10 text-orange-600 dark:text-orange-400">
            Chưa thanh toán
          </span>
        );
      case PaymentStatus.PAID:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
            Đã thanh toán
          </span>
        );
      case PaymentStatus.FAILED:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-red-500/10 text-red-600 dark:text-red-400">
            Thất bại
          </span>
        );
      case PaymentStatus.REFUNDED:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-zinc-500/10 text-zinc-600 dark:text-zinc-400">
            Đã hoàn tiền
          </span>
        );
      default:
        return null;
    }
  };

  if (!isMounted || (isAuthenticated && user && loading && myBookings.length === 0)) {
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

  // Nếu chưa đăng nhập
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
        <Header />
        <main className="flex-grow flex items-center justify-center px-4 pt-24 pb-16">
          <div className="max-w-md w-full text-center bg-white dark:bg-zinc-900 border border-zinc-200/85 dark:border-zinc-800/85 rounded-3xl p-8 shadow-xl">
            <div className="w-16 h-16 bg-amber-50 dark:bg-amber-950/20 text-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-extrabold text-zinc-900 dark:text-white mb-3">
              Yêu Cầu Đăng Nhập
            </h2>
            <p className="text-zinc-500 dark:text-zinc-400 text-sm mb-8 leading-relaxed">
              Bạn cần đăng nhập tài khoản để xem lịch sử hành trình và các booking đã thực hiện với VnTravel.
            </p>
            <div className="space-y-3">
              <Link href={`/login?redirect=/bookings`} className="block">
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

  const dashboardNav = [
    { name: "Thông tin cá nhân", href: "/profile", icon: UserIcon, active: false },
    { name: "Lịch sử đặt tour", href: "/bookings", icon: Calendar, active: true },
    // { name: "Danh sách yêu thích", href: "/wishlist", icon: Heart, active: false },
    // { name: "Đánh giá của tôi", href: "/reviews", icon: Star, active: false },
  ];

  const wishlistCount = wishlistedIds.length;
  const isUser3 = String(user.id) === "3";
  const reviewsCount = isUser3 ? 1 : 0;

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
      <Header />

      <main className="flex-grow pt-28 sm:pt-36 pb-20">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8">

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
                  { label: "Đặt chỗ hành trình", count: myBookings.length, link: "/bookings", icon: Calendar, color: "from-blue-500 to-cyan-500" },
                  // { label: "Yêu thích của bạn", count: wishlistCount, link: "/wishlist", icon: Heart, color: "from-pink-500 to-red-500" },
                  // { label: "Đánh giá đã viết", count: reviewsCount, link: "/reviews", icon: Star, color: "from-amber-500 to-orange-500" }
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
                        <span className="text-2xl sm:text-3xl font-extrabold text-zinc-900 dark:text-white block">
                          {statCard.count}
                        </span>
                      </div>
                      <div className={`p-2 sm:p-3 bg-gradient-to-tr ${statCard.color} text-white rounded-xl shadow-sm group-hover:scale-105 transition-transform duration-300`}>
                        <statCard.icon className="w-4 h-4 sm:w-5 sm:h-5" />
                      </div>
                    </div>
                  </Link>
                ))}
              </div>

              {/* Bookings Content */}
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-6 sm:p-8 shadow-sm">

                {/* Title */}
                <div className="mb-8 pb-5 border-b border-zinc-100 dark:border-zinc-800/80">
                  <h1 className="text-2xl font-extrabold text-zinc-900 dark:text-white">
                    Hành Trình Đã Đặt
                  </h1>
                  <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
                    Theo dõi lịch trình của bạn, xem lại thông tin đặt vé, trạng thái thanh toán và thực hiện hủy tour.
                  </p>
                </div>

                {myBookings.length === 0 ? (
                  /* Trạng thái trống */
                  <div className="text-center py-16 p-6">
                    <div className="w-16 h-16 bg-gradient-to-tr from-cyan-400/10 to-blue-500/10 text-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                      <Compass className="w-8 h-8 animate-spin-slow" />
                    </div>
                    <h3 className="text-xl font-extrabold text-zinc-900 dark:text-white mb-2">
                      Chưa Có Giao Dịch Nào
                    </h3>
                    <p className="text-zinc-500 dark:text-zinc-400 text-xs max-w-sm mx-auto mb-8 leading-relaxed">
                      Bạn chưa thực hiện bất kỳ đặt chỗ nào. Hãy đồng hành cùng VnTravel để khám phá những danh lam thắng cảnh thiên nhiên tươi đẹp!
                    </p>
                    <Link href="/tours">
                      <Button className="rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0 shadow-md hover:shadow-lg px-6 py-5 font-bold text-xs transition-all duration-300 cursor-pointer">
                        Khám phá các Tours ngay
                      </Button>
                    </Link>
                  </div>
                ) : (
                  /* Có danh sách booking */
                  <div className="space-y-6">

                    {/* DESKTOP TABLE VIEW */}
                    <div className="hidden md:block overflow-hidden bg-white dark:bg-zinc-900 border border-zinc-200/50 dark:border-zinc-800/50 rounded-2xl shadow-sm">
                      <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                          <thead>
                            <tr className="border-b border-zinc-100 dark:border-zinc-800 text-[10px] font-bold uppercase tracking-wider text-zinc-450 dark:text-zinc-500 bg-zinc-50/50 dark:bg-zinc-950/20">
                              <th className="py-4 px-5">Tour</th>
                              {/* <th className="py-4 px-3">Khởi hành</th> */}
                              <th className="py-4 px-3">Hành khách</th>
                              <th className="py-4 px-3">Tổng chi phí</th>
                              <th className="py-4 px-3">Trạng thái</th>
                              {/* <th className="py-4 px-3">Thanh toán</th> */}
                              <th className="py-4 px-5 text-right">Thao tác</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-zinc-100 dark:divide-zinc-850 text-sm">
                            {myBookings.map((booking) => (
                              <tr key={booking.id} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-950/10 transition-colors">
                                {/* Tour details */}
                                <td className="py-4 px-5 max-w-xs">
                                  <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 rounded-xl overflow-hidden bg-zinc-100 dark:bg-zinc-800 flex-shrink-0">
                                      {/* eslint-disable-next-line @next/next/no-img-element */}
                                      <img
                                        src={booking.tourImage.startsWith('http') ? booking.tourImage : (process.env.NEXT_PUBLIC_BASE_URL || "") + booking.tourImage}
                                        alt={booking.tourTitle}
                                        className="w-full h-full object-cover"
                                      />
                                    </div>
                                    <div className="min-w-0">
                                      <Link
                                        href={booking.tourSlug ? `/tours/${booking.tourSlug}` : "/tours"}
                                        className="font-bold text-zinc-900 dark:text-zinc-100 hover:text-cyan-500 dark:hover:text-cyan-400 transition-colors line-clamp-1 text-xs sm:text-sm"
                                      >
                                        {booking.tourTitle}
                                      </Link>
                                      {/* <span className="text-[9px] font-mono text-zinc-400 dark:text-zinc-500 block mt-0.5">
                                        Mã GD: {booking.id}
                                      </span> */}
                                    </div>
                                  </div>
                                </td>
                                {/* Date */}
                                {/* <td className="py-4 px-3 font-semibold text-zinc-700 dark:text-zinc-300 text-xs">
                                  {new Date(booking.departureDate).toLocaleDateString("vi-VN", {
                                    year: "numeric",
                                    month: "short",
                                    day: "numeric",
                                  })}
                                </td> */}
                                {/* Passengers */}
                                <td className="py-4 px-3">
                                  <div className="flex flex-col gap-0.5 text-xs">
                                    <span className="font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-1">
                                      <Users className="w-3.5 h-3.5 text-zinc-400" /> {booking.adults + booking.children} khách
                                    </span>
                                  </div>
                                </td>
                                {/* Total Price */}
                                <td className="py-4 px-3 font-extrabold text-cyan-500 dark:text-cyan-400 text-sm">
                                  {formatCurrency(booking.totalPrice)}
                                </td>
                                {/* Booking status */}
                                <td className="py-4 px-3">
                                  {getStatusBadge(booking.status)}
                                </td>
                                {/* Payment status */}
                                {/* <td className="py-4 px-3">
                                  {getPaymentBadge(booking.paymentStatus)}
                                </td> */}
                                {/* Actions */}
                                <td className="py-4 px-5 text-right">
                                  <div className="flex items-center justify-end gap-2">
                                    <button
                                      onClick={() => setSelectedBooking(booking)}
                                      className="px-3 py-1.5 text-xs font-bold text-cyan-500 hover:text-white border border-cyan-500/30 hover:border-cyan-600 bg-transparent hover:bg-cyan-600 rounded-lg transition-all cursor-pointer"
                                    >
                                      Chi tiết
                                    </button>
                                    {(booking.status === BookingStatus.PENDING || booking.status === BookingStatus.CONFIRMED) ? (
                                      <button
                                        onClick={() => handleCancelClick(booking)}
                                        className="px-3 py-1.5 text-xs font-bold text-red-500 hover:text-white border border-red-500/30 hover:border-red-600 bg-transparent hover:bg-red-600 rounded-lg transition-all cursor-pointer"
                                      >
                                        Hủy tour
                                      </button>
                                    ) : null}
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* MOBILE CARDS VIEW */}
                    <div className="block md:hidden space-y-4">
                      {myBookings.map((booking) => (
                        <div
                          key={booking.id}
                          className="bg-white dark:bg-zinc-900 border border-zinc-200/70 dark:border-zinc-800/70 rounded-2xl p-4 shadow-sm space-y-4"
                        >
                          {/* Top Section: Tour Image & ID */}
                          <div className="flex gap-3">
                            <div className="w-14 h-14 rounded-xl overflow-hidden bg-zinc-100 dark:bg-zinc-800 flex-shrink-0">
                              {/* eslint-disable-next-line @next/next/no-img-element */}
                              <img
                                src={booking.tourImage || "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=150"}
                                alt={booking.tourTitle}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            <div className="min-w-0 flex-1">
                              <Link
                                href={booking.tourId ? `/tours/${booking.tourId}` : "/tours"}
                                className="font-bold text-zinc-900 dark:text-zinc-100 hover:text-cyan-500 dark:hover:text-cyan-400 transition-colors line-clamp-1 block text-sm"
                              >
                                {booking.tourTitle}
                              </Link>
                              {/* <span className="text-[9px] font-mono text-zinc-400 dark:text-zinc-500 block mt-0.5">
                                Mã GD: {booking.id}
                              </span> */}
                              <span className="text-xs text-zinc-600 dark:text-zinc-450 font-semibold mt-1 block">
                                Đi: {new Date(booking.departureDate).toLocaleDateString("vi-VN")}
                              </span>
                            </div>
                          </div>

                          <hr className="border-zinc-100 dark:border-zinc-800/60" />

                          {/* Mid Section: Info List */}
                          <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-xs">
                            <div>
                              <span className="text-zinc-400 dark:text-zinc-500 block mb-0.5">Khách tham gia:</span>
                              <span className="font-semibold text-zinc-800 dark:text-zinc-200">
                                {booking.adults} NL {booking.children > 0 && `, ${booking.children} TE`}
                              </span>
                            </div>
                            <div>
                              <span className="text-zinc-400 dark:text-zinc-500 block mb-0.5">Thanh toán:</span>
                              <span className="font-extrabold text-cyan-500 dark:text-cyan-400">
                                {formatCurrency(booking.totalPrice)}
                              </span>
                            </div>
                            <div>
                              <span className="text-zinc-400 dark:text-zinc-500 block mb-0.5">Trạng thái đặt:</span>
                              <div className="mt-0.5">{getStatusBadge(booking.status)}</div>
                            </div>
                            <div>
                              <span className="text-zinc-400 dark:text-zinc-500 block mb-0.5">Giao dịch:</span>
                              <div className="mt-0.5">{getPaymentBadge(booking.paymentStatus)}</div>
                            </div>
                          </div>

                          {/* Bottom Action Button */}
                          <div className="pt-2 flex gap-2">
                            <button
                              onClick={() => setSelectedBooking(booking)}
                              className="flex-1 py-2 text-xs font-bold text-cyan-500 hover:text-white border border-cyan-500/20 hover:border-cyan-650 bg-cyan-50/5 hover:bg-cyan-600 rounded-xl transition-all cursor-pointer text-center"
                            >
                              Xem chi tiết
                            </button>
                            {(booking.status === BookingStatus.PENDING || booking.status === BookingStatus.CONFIRMED) && (
                              <button
                                onClick={() => handleCancelClick(booking)}
                                className="flex-1 py-2 text-xs font-bold text-red-500 hover:text-white border border-red-500/20 hover:border-red-600 bg-red-50/5 hover:bg-red-600 rounded-xl transition-all cursor-pointer"
                              >
                                Hủy đặt
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>

                  </div>
                )}

              </div>

            </div>

          </div>

        </div>
      </main>

      {/* ================= CONFIRM CANCEL MODAL ================= */}
      {confirmCancelBooking && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
          {/* Backdrop */}
          <div
            onClick={() => setConfirmCancelBooking(null)}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal Content */}
          <div className="relative bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 max-w-md w-full rounded-3xl p-6 sm:p-8 shadow-2xl animate-scale-up text-center z-10">
            <div className="w-14 h-14 bg-red-50 dark:bg-red-950/20 text-red-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-8 h-8" />
            </div>

            <h3 className="text-xl font-extrabold text-zinc-900 dark:text-white mb-2">
              Xác Nhận Hủy Đặt Chỗ?
            </h3>

            <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-6">
              Bạn có chắc chắn muốn hủy yêu cầu đặt tour này không? Thao tác này không thể hoàn tác.
            </p>

            {/* Tour Info Preview */}
            <div className="bg-zinc-50 dark:bg-zinc-950 border border-zinc-200/50 dark:border-zinc-850/50 rounded-2xl p-4 text-left text-xs mb-6 space-y-1.5 text-zinc-650 dark:text-zinc-350">
              <p className="font-bold text-zinc-800 dark:text-zinc-200 text-sm mb-1 line-clamp-1">
                {confirmCancelBooking.tourTitle}
              </p>
              <p>Mã đặt chỗ: <span className="font-mono">{confirmCancelBooking.id}</span></p>
              <p>Ngày đi: {new Date(confirmCancelBooking.departureDate).toLocaleDateString("vi-VN")}</p>
              <p>Tổng tiền: <span className="font-bold text-cyan-500">{formatCurrency(confirmCancelBooking.totalPrice)}</span></p>
            </div>

            {/* Modal Buttons */}
            <div className="flex gap-3">
              <button
                disabled={cancellingId !== null}
                onClick={() => setConfirmCancelBooking(null)}
                className="flex-1 py-3 border border-zinc-200 dark:border-zinc-850 hover:bg-zinc-50 dark:hover:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-bold rounded-xl text-sm transition-all cursor-pointer bg-transparent disabled:opacity-40"
              >
                Quay lại
              </button>
              <button
                disabled={cancellingId !== null}
                onClick={handleConfirmCancel}
                className="flex-1 py-3 bg-red-500 hover:bg-red-650 text-white font-bold rounded-xl text-sm transition-all shadow-md flex items-center justify-center gap-1.5 cursor-pointer border-0 disabled:opacity-40"
              >
                {cancellingId ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Đang hủy...
                  </>
                ) : (
                  "Đồng ý hủy"
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= BOOKING DETAILS MODAL ================= */}
      {selectedBooking && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
          {/* Backdrop */}
          <div
            onClick={() => setSelectedBooking(null)}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal Content */}
          <div className="relative bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 max-w-lg w-full rounded-3xl p-6 sm:p-8 shadow-2xl animate-scale-up z-10 text-left">
            <button
              onClick={() => setSelectedBooking(null)}
              className="absolute top-4 right-4 p-2 text-zinc-400 hover:text-zinc-650 dark:hover:text-zinc-350 transition-colors bg-transparent border-0 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3.5 mb-6 pb-4 border-b border-zinc-100 dark:border-zinc-800/80">
              <div className="p-2.5 bg-gradient-to-tr from-cyan-400 to-blue-500 text-white rounded-2xl shadow-sm">
                <Compass className="w-6 h-6 animate-spin-slow" />
              </div>
              <div>
                <h3 className="text-xl font-extrabold text-zinc-900 dark:text-white">
                  Chi Tiết Đặt Chỗ
                </h3>
                <p className="text-xs text-zinc-450 mt-0.5">
                  Mã giao dịch: <span className="font-mono font-bold text-zinc-650 dark:text-zinc-300">#{selectedBooking.id}</span>
                </p>
              </div>
            </div>

            {/* Tour info snippet */}
            <div className="flex gap-4 mb-6 bg-zinc-50 dark:bg-zinc-950 p-4 border border-zinc-200/50 dark:border-zinc-850/50 rounded-2xl">
              <div className="w-20 h-20 rounded-xl overflow-hidden bg-zinc-100 dark:bg-zinc-855 flex-shrink-0">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={selectedBooking.tourImage.startsWith('http') ? selectedBooking.tourImage : (process.env.NEXT_PUBLIC_BASE_URL || "") + selectedBooking.tourImage}
                  alt={selectedBooking.tourTitle}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1 min-w-0 flex flex-col justify-center">
                <Link
                  href={selectedBooking.tourSlug ? `/tours/${selectedBooking.tourSlug}` : "/tours"}
                  onClick={() => setSelectedBooking(null)}
                  className="font-bold text-sm text-zinc-900 dark:text-zinc-100 hover:text-cyan-500 dark:hover:text-cyan-400 transition-colors line-clamp-2"
                >
                  {selectedBooking.tourTitle}
                </Link>
                <div className="mt-2 flex items-center gap-2">
                  {getStatusBadge(selectedBooking.status)}
                </div>
              </div>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-2 gap-y-4 gap-x-6 text-xs mb-6 border-b border-zinc-100 dark:border-zinc-800/80 pb-6">
              <div>
                <span className="text-zinc-450 dark:text-zinc-500 block mb-0.5 uppercase tracking-wider text-[10px] font-bold">Ngày khởi hành:</span>
                <span className="font-semibold text-zinc-800 dark:text-zinc-200">
                  {new Date(selectedBooking.departureDate).toLocaleDateString("vi-VN", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </span>
              </div>
              <div>
                <span className="text-zinc-450 dark:text-zinc-500 block mb-0.5 uppercase tracking-wider text-[10px] font-bold">Số lượng khách:</span>
                <span className="font-semibold text-zinc-800 dark:text-zinc-200">
                  {selectedBooking.adults} Người lớn {selectedBooking.children > 0 && `, ${selectedBooking.children} Trẻ em`}
                </span>
              </div>
              <div>
                <span className="text-zinc-455 dark:text-zinc-500 block mb-0.5 uppercase tracking-wider text-[10px] font-bold">Thanh toán qua:</span>
                <span className="font-semibold text-zinc-800 dark:text-zinc-200">
                  {selectedBooking.paymentMethod === 'credit_card' ? 'Thẻ tín dụng' :
                    selectedBooking.paymentMethod === 'paypal' ? 'Paypal' :
                      selectedBooking.paymentMethod === 'bank_transfer' ? 'Chuyển khoản' :
                        selectedBooking.paymentMethod === 'cash' ? 'Tiền mặt' : selectedBooking.paymentMethod || 'Thẻ tín dụng'}
                </span>
              </div>
              <div>
                <span className="text-zinc-450 dark:text-zinc-500 block mb-0.5 uppercase tracking-wider text-[10px] font-bold">Tình trạng thanh toán:</span>
                <div className="mt-0.5">{getPaymentBadge(selectedBooking.paymentStatus)}</div>
              </div>
              <div>
                <span className="text-zinc-450 dark:text-zinc-500 block mb-0.5 uppercase tracking-wider text-[10px] font-bold">Tổng chi phí:</span>
                <span className="font-extrabold text-sm text-cyan-500 dark:text-cyan-400">
                  {formatCurrency(selectedBooking.totalPrice)}
                </span>
              </div>
              <div>
                <span className="text-zinc-450 dark:text-zinc-500 block mb-0.5 uppercase tracking-wider text-[10px] font-bold">Thời gian đặt:</span>
                <span className="font-semibold text-zinc-800 dark:text-zinc-200">
                  {new Date(selectedBooking.createdAt).toLocaleString("vi-VN", {
                    year: "numeric",
                    month: "numeric",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit"
                  })}
                </span>
              </div>
            </div>

            {/* Customer Contact details */}
            <div className="space-y-3 mb-6 bg-zinc-50 dark:bg-zinc-950 p-4 border border-zinc-200/50 dark:border-zinc-850/50 rounded-2xl">
              <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-450 dark:text-zinc-500 mb-1">
                Thông tin liên hệ đặt chỗ
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-zinc-400 block mb-0.5">Họ tên khách:</span>
                  <span className="font-semibold text-zinc-800 dark:text-zinc-200">{selectedBooking.userName || user.name}</span>
                </div>
                <div>
                  <span className="text-zinc-400 block mb-0.5">Email liên lạc:</span>
                  <span className="font-semibold text-zinc-800 dark:text-zinc-200 line-clamp-1">{user.email}</span>
                </div>
                {user.phoneNumber && (
                  <div className="col-span-2 mt-1">
                    <span className="text-zinc-400 block mb-0.5">Số điện thoại:</span>
                    <span className="font-semibold text-zinc-800 dark:text-zinc-200">{user.phoneNumber}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setSelectedBooking(null)}
                className="px-6 py-2.5 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-800 dark:text-zinc-200 font-bold rounded-xl text-xs transition-all cursor-pointer border-0"
              >
                Đóng
              </button>
              {(selectedBooking.status === BookingStatus.PENDING || selectedBooking.status === BookingStatus.CONFIRMED) && (
                <button
                  onClick={() => {
                    handleCancelClick(selectedBooking);
                    setSelectedBooking(null);
                  }}
                  className="px-6 py-2.5 bg-red-500 hover:bg-red-650 text-white font-bold rounded-xl text-xs transition-all shadow-md cursor-pointer border-0"
                >
                  Hủy đặt tour
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
}
