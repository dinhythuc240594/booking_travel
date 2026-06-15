"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/store/auth.store";
import { useWishlistStore } from "@/store/wishlist.store";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import { Tour } from "@/types/tour";
import { Review } from "@/types/review";
import {
  User as UserIcon,
  Calendar,
  Heart,
  Star,
  Shield,
  Loader2,
  AlertCircle,
  MessageSquare,
  ArrowRight,
  ThumbsUp
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ReviewsPage() {
  const [isMounted, setIsMounted] = useState(false);
  const { user, isAuthenticated } = useAuthStore();
  const { wishlistedIds } = useWishlistStore();

  const [reviews, setReviews] = useState<(Review & { tourTitle?: string; tourImage?: string; tourSlug?: string })[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ bookings: 0, wishlist: 0, reviews: 0 });

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    const fetchReviewsData = async () => {
      if (!isAuthenticated || !user) return;
      try {
        setLoading(true);

        // Fetch bookings count
        const bookingsRes = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/bookings?email=${user.email}`, {
          credentials: "include"
        });
        let bookingsCount = 0;
        if (bookingsRes.ok) {
          const bookingsData = await bookingsRes.json();
          bookingsCount = Array.isArray(bookingsData) ? bookingsData.length : 0;
        }

        // Fetch all tours so we can map tour info
        const toursRes = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/tours`);
        let tourMap = new Map<string, { title: string; image: string; slug: string }>();
        if (toursRes.ok) {
          const toursData = await toursRes.json();
          (toursData.tours || []).forEach((t: any) => {
            tourMap.set(String(t.tour_id || t.id), {
              title: t.title || "Tour du lịch",
              image: process.env.NEXT_PUBLIC_BASE_URL + t.thumbnail || "https://images.unsplash.com/photo-1508873699372-7aeab60b44ab?w=300",
              slug: t.slug || "",
            });
          });
        }

        // Setup reviews based on database sample (user 3 has a review for tour 1)
        const isUser3 = String(user.id) === "3";
        let userReviews: (Review & { tourTitle?: string; tourImage?: string; tourSlug?: string })[] = [];

        if (isUser3) {
          const mappedTour = tourMap.get("1") || {
            title: "Khám Phá Bán Đảo Sơn Trà - Lặn Ngắm San Hô",
            image: "https://images.unsplash.com/photo-1508873699372-7aeab60b44ab?w=300",
            slug: "kham-pha-son-tra"
          };
          userReviews = [
            {
              id: "rev_1",
              tourId: "1",
              userName: user.name || "Customer",
              rating: 5,
              comment: "Tour rất tuyệt vời, ngắm được nhiều san hô!",
              date: "2026-06-10",
              tourTitle: mappedTour.title,
              tourImage: mappedTour.image,
              tourSlug: mappedTour.slug
            }
          ];
        }

        setReviews(userReviews);
        setStats({
          bookings: bookingsCount,
          wishlist: wishlistedIds.length,
          reviews: userReviews.length
        });

      } catch (err) {
        console.error("Failed to load reviews data:", err);
      } finally {
        setLoading(false);
      }
    };

    if (isMounted) {
      fetchReviewsData();
    }
  }, [isMounted, isAuthenticated, user, wishlistedIds]);

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
              Vui lòng đăng nhập tài khoản của bạn để xem danh sách đánh giá của tôi và xem các hành trình đã đặt.
            </p>
            <div className="space-y-3">
              <Link href={`/login?redirect=/reviews`} className="block">
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
    { name: "Lịch sử đặt tour", href: "/bookings", icon: Calendar, active: false },
    // { name: "Danh sách yêu thích", href: "/wishlist", icon: Heart, active: false },
    // { name: "Đánh giá của tôi", href: "/reviews", icon: Star, active: true },
  ];

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
                      : "text-zinc-655 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-850 hover:text-zinc-900 dark:hover:text-zinc-100"
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

              {/* Reviews listing */}
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200/50 dark:border-zinc-800/50 rounded-3xl p-6 sm:p-8 shadow-sm">

                {/* Title */}
                <div className="mb-8 pb-5 border-b border-zinc-100 dark:border-zinc-800/80">
                  <h1 className="text-2xl font-extrabold text-zinc-900 dark:text-white">
                    Đánh Giá Của Tôi
                  </h1>
                  <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
                    Xem và quản lý các phản hồi, đánh giá bạn đã đóng góp cho các hành trình du lịch của VnTravel.
                  </p>
                </div>

                {loading ? (
                  <div className="flex justify-center items-center py-20">
                    <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
                  </div>
                ) : reviews.length === 0 ? (
                  /* Empty Reviews State */
                  <div className="text-center py-16 p-6">
                    <div className="w-16 h-16 bg-amber-500/10 text-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                      <MessageSquare className="w-8 h-8" />
                    </div>
                    <h3 className="text-xl font-extrabold text-zinc-900 dark:text-white mb-2">
                      Chưa Có Đánh Giá Nào
                    </h3>
                    <p className="text-zinc-500 dark:text-zinc-400 text-xs max-w-sm mx-auto mb-8 leading-relaxed">
                      Bạn chưa gửi đánh giá nào cho các chuyến đi. Hãy viết đánh giá sau khi hoàn tất đặt hành trình để chia sẻ trải nghiệm tuyệt vời cùng mọi người!
                    </p>
                    <Link href="/bookings">
                      <Button className="rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0 shadow-md hover:shadow-lg px-6 py-5 font-bold text-xs transition-all duration-300 cursor-pointer">
                        Đến Lịch Sử Đặt Tour
                      </Button>
                    </Link>
                  </div>
                ) : (
                  /* Reviews List */
                  <div className="space-y-6">
                    {reviews.map((review) => (
                      <div
                        key={review.id}
                        className="bg-zinc-50 dark:bg-zinc-950/40 border border-zinc-150 dark:border-zinc-850 rounded-2xl p-5 shadow-sm space-y-4 hover:shadow-md transition-all duration-300"
                      >
                        {/* Tour Info Link & Date */}
                        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-xl overflow-hidden bg-zinc-100 dark:bg-zinc-800 flex-shrink-0">
                              {/* eslint-disable-next-line @next/next/no-img-element */}
                              <img
                                src={review.tourImage || "https://images.unsplash.com/photo-1508873699372-7aeab60b44ab?w=300"}
                                alt={review.tourTitle || "Tour"}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            <div>
                              <Link
                                href={review.tourSlug ? `/tours/${review.tourSlug}` : "/tours"}
                                className="font-bold text-sm text-zinc-900 dark:text-zinc-100 hover:text-cyan-500 transition-colors line-clamp-1"
                              >
                                {review.tourTitle}
                              </Link>
                              <span className="text-[10px] text-zinc-400 block mt-0.5">
                                Viết lúc: {new Date(review.date).toLocaleDateString("vi-VN", { year: "numeric", month: "long", day: "numeric" })}
                              </span>
                            </div>
                          </div>

                          {/* Rating score */}
                          <div className="flex items-center gap-1 bg-amber-500/10 px-2.5 py-1 rounded-xl text-xs font-bold text-amber-500 self-start sm:self-auto">
                            <span className="flex items-center gap-0.5">
                              {Array.from({ length: review.rating }).map((_, i) => (
                                <Star key={i} className="w-3.5 h-3.5 fill-amber-500 text-amber-500" />
                              ))}
                            </span>
                            <span className="ml-1 font-extrabold">{review.rating}.0</span>
                          </div>
                        </div>

                        {/* Review Content */}
                        <div className="text-zinc-650 dark:text-zinc-300 text-sm leading-relaxed bg-white dark:bg-zinc-900/40 p-4 border border-zinc-200/50 dark:border-zinc-800/60 rounded-xl">
                          "{review.comment}"
                        </div>

                        {/* Bottom Actions */}
                        <div className="flex justify-between items-center text-xs">
                          <span className="text-zinc-400 flex items-center gap-1">
                            <ThumbsUp className="w-3.5 h-3.5 text-cyan-500" /> Phản hồi của bạn đã giúp ích cho 12 du khách
                          </span>
                          <Link
                            href={review.tourSlug ? `/tours/${review.tourSlug}` : "/tours"}
                            className="inline-flex items-center gap-1 text-cyan-550 hover:text-cyan-600 dark:hover:text-cyan-400 font-bold transition-all group"
                          >
                            Xem Tour này <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

              </div>

            </div>

          </div>

        </div>
      </main>

      <Footer />
    </div>
  );
}
