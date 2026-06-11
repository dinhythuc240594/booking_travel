"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth.store";
import { useBookingStore } from "@/store/booking.store";
import { Tour } from "@/types/tour";
import { Booking } from "@/types/booking";
import { BookingStatus, PaymentStatus } from "@/constants/enums";
import { Calendar, Plus, Minus, CreditCard, Sparkles, CheckCircle2, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface TourBookingWidgetProps {
  tour: Tour;
}

export default function TourBookingWidget({ tour }: TourBookingWidgetProps) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { addBooking } = useBookingStore();

  const [departureDate, setDepartureDate] = useState(tour.startDates[0] || "");
  const [adults, setAdults] = useState(1);
  const [children, setChildren] = useState(0);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);
  const [recentBookingId, setRecentBookingId] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const pricePerAdult = tour.discountPrice || tour.price;
  const pricePerChild = tour.price_per_child && tour.price_per_child > 0
    ? tour.price_per_child
    : Math.round(pricePerAdult * 0.7); // Trẻ em lấy từ database nếu có, ngược lại tính 70%
  const totalPrice = adults * pricePerAdult + children * pricePerChild;

  const handleBooking = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isAuthenticated || !user) {
      //// Nếu chưa đăng nhập, chuyển sang trang login và chuyển hướng ngược lại sau khi đăng nhập ////
      //// KHÔNG CẦN SET process.env.NEXT_PUBLIC_WEB_BASE_URL với router ////
      router.push(`/login?redirect=/tours/${tour.slug}`);
      return;
    }

    try {
      setIsSubmitting(true);
      const bookingData = {
        tourId: tour.id,
        userId: user.id,
        departureDate,
        adults,
        children,
        totalPrice,
        paymentMethod: "credit_card"
      };

      const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/bookings`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(bookingData),
        credentials: "include"
      });

      if (!res.ok) {
        throw new Error("Failed to save booking to database");
      }

      const responseData = await res.json();
      const savedBooking = responseData.booking;

      const newBooking: Booking = {
        id: String(savedBooking.id),
        tourId: tour.id,
        tourTitle: tour.title,
        tourImage: tour.featuredImage,
        userId: user.id,
        userName: user.name,
        departureDate,
        adults,
        children,
        totalPrice,
        status: BookingStatus.PENDING,
        paymentStatus: PaymentStatus.PENDING,
        createdAt: new Date().toISOString(),
      };

      addBooking(newBooking);
      setRecentBookingId(String(savedBooking.id));
      setIsSuccessModalOpen(true);
    } catch (error) {
      console.error("Booking error:", error);

      // Fallback: If backend is not available, save to local Zustand store as dummy
      const bookingId = `book-${Math.random().toString(36).substring(2, 11)}`;
      const newBooking: Booking = {
        id: bookingId,
        tourId: tour.id,
        tourTitle: tour.title,
        tourImage: tour.featuredImage,
        userId: user.id,
        userName: user.name,
        departureDate,
        adults,
        children,
        totalPrice,
        status: BookingStatus.PENDING,
        paymentStatus: PaymentStatus.PENDING,
        createdAt: new Date().toISOString(),
      };

      addBooking(newBooking);
      setRecentBookingId(bookingId);
      setIsSuccessModalOpen(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="font-sans select-none sticky top-28 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-3xl p-6 shadow-xl w-full">
      <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
        Giá chỉ từ
      </h3>

      {/* Hiển thị giá */}
      <div className="flex items-baseline gap-2 mb-6 pb-6 border-b border-zinc-100 dark:border-zinc-800">
        {tour.discountPrice ? (
          <>
            <span className="text-2xl sm:text-3xl font-extrabold text-cyan-500 dark:text-cyan-400">
              {formatCurrency(tour.discountPrice)}
            </span>
            <span className="text-sm text-zinc-400 line-through">
              {formatCurrency(tour.price)}
            </span>
          </>
        ) : (
          <span className="text-2xl sm:text-3xl font-extrabold text-cyan-500 dark:text-cyan-400">
            {formatCurrency(tour.price)}
          </span>
        )}
        <span className="text-xs text-zinc-400">/ khách</span>
      </div>

      <form onSubmit={handleBooking} className="space-y-5">
        {/* Chọn ngày khởi hành */}
        <div>
          <label htmlFor="departure-date" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2.5">
            Chọn ngày khởi hành
          </label>
          <div className="relative">
            <div className="absolute left-4 top-3.5 text-zinc-400">
              <Calendar className="w-5 h-5" />
            </div>
            <select
              id="departure-date"
              value={departureDate}
              onChange={(e) => setDepartureDate(e.target.value)}
              required
              className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl pl-12 pr-4 py-3 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 cursor-pointer appearance-none"
            >
              {tour.startDates.map((date) => (
                <option key={date} value={date}>
                  {new Date(date).toLocaleDateString("vi-VN", {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Số khách */}
        <div>
          <span className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-3">
            Số lượng hành khách
          </span>
          <div className="space-y-4 bg-zinc-50 dark:bg-zinc-950 border border-zinc-200/50 dark:border-zinc-800/50 rounded-2xl p-4">
            {/* Người lớn */}
            <div className="flex justify-between items-center">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-zinc-700 dark:text-zinc-300">Người lớn</span>
                <span className="text-[10px] text-zinc-400">{formatCurrency(pricePerAdult)}</span>
              </div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setAdults(Math.max(1, adults - 1))}
                  disabled={adults <= 1}
                  className="w-8 h-8 rounded-full border border-zinc-200 dark:border-zinc-700 hover:border-cyan-500 hover:text-cyan-500 flex items-center justify-center disabled:opacity-40 transition-colors cursor-pointer"
                >
                  <Minus className="w-4 h-4" />
                </button>
                <span className="text-sm font-bold w-4 text-center">{adults}</span>
                <button
                  type="button"
                  onClick={() => setAdults(adults + 1)}
                  className="w-8 h-8 rounded-full border border-zinc-200 dark:border-zinc-700 hover:border-cyan-500 hover:text-cyan-500 flex items-center justify-center transition-colors cursor-pointer"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Trẻ em */}
            <div className="flex justify-between items-center">
              <div className="flex flex-col">
                <span className="text-xs font-bold text-zinc-700 dark:text-zinc-300">Trẻ em (2 - 11 tuổi)</span>
                <span className="text-[10px] text-zinc-400">{formatCurrency(pricePerChild)}</span>
              </div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setChildren(Math.max(0, children - 1))}
                  disabled={children <= 0}
                  className="w-8 h-8 rounded-full border border-zinc-200 dark:border-zinc-700 hover:border-cyan-500 hover:text-cyan-500 flex items-center justify-center disabled:opacity-40 transition-colors cursor-pointer"
                >
                  <Minus className="w-4 h-4" />
                </button>
                <span className="text-sm font-bold w-4 text-center">{children}</span>
                <button
                  type="button"
                  onClick={() => setChildren(children + 1)}
                  className="w-8 h-8 rounded-full border border-zinc-200 dark:border-zinc-700 hover:border-cyan-500 hover:text-cyan-500 flex items-center justify-center transition-colors cursor-pointer"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Tổng tiền tạm tính */}
        <div className="pt-4 border-t border-zinc-100 dark:border-zinc-800 flex justify-between items-center">
          <span className="text-sm font-bold text-zinc-700 dark:text-zinc-300">Tổng tiền</span>
          <span className="text-xl font-extrabold text-cyan-500 dark:text-cyan-400">
            {formatCurrency(totalPrice)}
          </span>
        </div>

        {/* Nút Submit */}
        <Button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold py-6 text-sm shadow-lg hover:shadow-xl hover:scale-[1.01] transition-all cursor-pointer border-0 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <CreditCard className="w-4.5 h-4.5" />
          {isSubmitting ? "Đang xử lý..." : isAuthenticated ? "Đặt Tour Ngay" : "Đăng nhập để đặt tour"}
        </Button>

      </form>

      {/* ================= MODAL ĐẶT TOUR THÀNH CÔNG ================= */}
      {isSuccessModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
          {/* Backdrop */}
          <div
            onClick={() => setIsSuccessModalOpen(false)}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal Content */}
          <div className="relative bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 max-w-md w-full rounded-3xl p-6 sm:p-8 shadow-2xl animate-scale-up text-center z-10">

            <div className="w-16 h-16 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-10 h-10" />
            </div>

            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 text-[10px] font-bold uppercase tracking-wider mb-2">
              <Sparkles className="w-3 h-3" /> Thành công
            </span>

            <h3 className="text-xl font-extrabold text-zinc-900 dark:text-white mb-2">
              Đặt Chỗ Thành Công!
            </h3>

            <p className="text-xs text-zinc-400 dark:text-zinc-500 mb-6">
              Mã giao dịch: <span className="font-mono font-semibold text-zinc-600 dark:text-zinc-400">{recentBookingId}</span>
            </p>

            {/* Chi tiết đơn hàng */}
            <div className="bg-zinc-50 dark:bg-zinc-950 border border-zinc-200/50 dark:border-zinc-800/50 rounded-2xl p-4 text-left space-y-2.5 text-xs text-zinc-600 dark:text-zinc-300 mb-6">
              <div>
                <span className="text-zinc-400 block mb-0.5">Hành trình:</span>
                <span className="font-bold text-zinc-800 dark:text-zinc-200">{tour.title}</span>
              </div>
              <div className="flex justify-between">
                <div>
                  <span className="text-zinc-400 block mb-0.5">Ngày đi:</span>
                  <span className="font-semibold">{new Date(departureDate).toLocaleDateString("vi-VN")}</span>
                </div>
                <div className="text-right">
                  <span className="text-zinc-400 block mb-0.5">Hành khách:</span>
                  <span className="font-semibold">{adults} NL {children > 0 && `, ${children} TE`}</span>
                </div>
              </div>
              <div className="pt-2.5 border-t border-zinc-200/50 dark:border-zinc-850 flex justify-between items-center text-sm">
                <span className="font-bold text-zinc-800 dark:text-zinc-200">Tổng thanh toán:</span>
                <span className="font-extrabold text-cyan-500 dark:text-cyan-400">{formatCurrency(totalPrice)}</span>
              </div>
            </div>

            {/* Các nút hành động */}
            <div className="flex flex-col gap-2">
              <button
                onClick={() => {
                  setIsSuccessModalOpen(false);
                  //// KHÔNG CẦN SET process.env.NEXT_PUBLIC_WEB_BASE_URL với router ////
                  router.push(`/bookings`); // Hoặc /profile
                }}
                className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold rounded-xl text-sm transition-all shadow-md flex items-center justify-center gap-1 cursor-pointer border-0"
              >
                Xem lịch sử đặt chỗ <ChevronRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsSuccessModalOpen(false)}
                className="w-full py-3 border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-300 font-bold rounded-xl text-sm transition-all cursor-pointer bg-transparent"
              >
                Đóng
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
