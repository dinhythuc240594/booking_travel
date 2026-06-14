"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { mockTours } from "@/mocks/data/tours";
import { mockReviews } from "@/mocks/data/reviews";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import TourCard from "@/features/tours/components/TourCard";
import TourGallery from "@/features/tours/components/TourGallery";
import TourBookingWidget from "@/features/tours/components/TourBookingWidget";
import {
  MapPin, Clock, Users, Star, Sparkles, Check, Info,
  ChevronRight, Calendar, MessageSquare, ArrowLeft, Loader2
} from "lucide-react";
import { Tour } from "@/types/tour";

const mapCategoryNameToId = (name: string): string => {
  if (!name) return "culture";
  const lower = name.toLowerCase();
  if (lower.includes("biển") || lower.includes("đảo") || lower.includes("beach")) return "beach";
  if (lower.includes("núi") || lower.includes("rừng") || lower.includes("khám phá") || lower.includes("mạo hiểm") || lower.includes("mountain")) return "mountain";
  if (lower.includes("nghỉ dưỡng") || lower.includes("resort")) return "resort";
  if (lower.includes("văn hóa") || lower.includes("lịch sử") || lower.includes("trải nghiệm") || lower.includes("culture")) return "culture";
  return "culture"; // default fallback
};

interface DetailTourProps {
  slug: string;
}

export default function DetailTour({ slug }: DetailTourProps) {
  const [tour, setTour] = useState<Tour | null>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchTourDetails() {
      try {
        setLoading(true);
        setError(null);

        // Fetch from backend API
        const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/tours/${slug}`, {
          credentials: "include"
        });
        if (!res.ok) {
          throw new Error("Tour not found in database");
        }

        const data = await res.json();

        if (isMounted) {
          if (data && data.tour) {
            const apiTour = data.tour;
            // Map backend fields to frontend Tour structure
            const durationDays = apiTour.duration_days || 1;
            const durationStr = `${durationDays} ngày ${Math.max(0, durationDays - 1)} đêm`;

            // Format start dates
            let startDatesList = ["2026-06-15", "2026-06-22", "2026-06-29"];

            // Format images array
            let imagesList = [apiTour.thumbnail || apiTour.featuredImage || "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=800&auto=format&fit=crop&q=80"];
            if (Array.isArray(apiTour.images) && apiTour.images.length > 0) {
              imagesList = apiTour.images;
            }

            const normalizedTour: Tour = {
              id: String(apiTour.tour_id),
              title: apiTour.title || "",
              slug: apiTour.slug || "",
              description: apiTour.content || apiTour.summary || "",
              price: Number(apiTour.price_per_adult) || 0,
              discountPrice: apiTour.discount_price !== undefined && apiTour.discount_price !== null ? Number(apiTour.discount_price) : undefined,
              price_per_child: Number(apiTour.price_per_child) || 0,
              duration: durationStr,
              location: apiTour.location_name || "Việt Nam",
              featuredImage: apiTour.thumbnail || imagesList[0],
              images: imagesList,
              rating: apiTour.rating || 4.8,
              reviewsCount: apiTour.reviewsCount || 15,
              category: mapCategoryNameToId(apiTour.category_name || "culture"),
              maxGroupSize: apiTour.maxGroupSize || 20,
              startDates: startDatesList,
              highlights: apiTour.highlights || [
                "Chuyến đi khám phá thắng cảnh nổi tiếng của địa phương.",
                "Tìm hiểu văn hóa, lối sống và con người nơi đây.",
                "Thưởng thức các đặc sản ẩm thực trứ danh bản địa."
              ],
              included: apiTour.included || [
                "Phương tiện di chuyển chất lượng cao suốt tuyến.",
                "Khách sạn/Resort nghỉ ngơi tiện nghi hiện đại.",
                "Các bữa ăn theo tiêu chuẩn trong chương trình.",
                "Vé tham quan tất cả các điểm có trong lịch trình.",
                "Bảo hiểm du lịch toàn diện trị giá cao."
              ],
              excluded: apiTour.excluded || [
                "Các chi phí cá nhân (điện thoại, giặt ủi, mua sắm,...).",
                "Đồ uống phát sinh tự gọi trong các bữa ăn.",
                "Thuế giá trị gia tăng VAT và tiền Tip cho hướng dẫn viên."
              ],
              itinerary: apiTour.itinerary || []
            };

            setTour(normalizedTour);

            // Filter mock reviews for this tour
            const tourReviews = mockReviews.filter((r) => r.tourId === normalizedTour.id);
            setReviews(tourReviews);
          } else {
            throw new Error("Invalid API response format");
          }
        }
      } catch (err: any) {
        console.warn("API load failed, falling back to mock data:", err.message);

        // Fallback to mock data matching the slug
        const mockTour = mockTours.find((t) => t.slug === slug);
        if (isMounted) {
          if (mockTour) {
            setTour(mockTour);
            const tourReviews = mockReviews.filter((r) => r.tourId === mockTour.id);
            setReviews(tourReviews);
          } else {
            setError("Không tìm thấy tour này");
          }
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchTourDetails();

    return () => {
      isMounted = false;
    };
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
        <Header transparent={false} />
        <main className="flex-grow flex flex-col items-center justify-center py-32">
          <div className="text-center">
            <Loader2 className="w-10 h-10 border-cyan-500 text-cyan-500 animate-spin mx-auto mb-4" />
            <p className="text-zinc-500 dark:text-zinc-400 text-sm font-semibold">
              Đang tải thông tin chi tiết hành trình...
            </p>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !tour) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
        <Header transparent={false} />
        <main className="flex-grow flex flex-col items-center justify-center py-32 px-4">
          <div className="text-center bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-8 max-w-md shadow-lg">
            <Info className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-lg font-bold mb-2">Không tìm thấy tour</h2>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mb-6">
              Hành trình du lịch bạn yêu cầu không tồn tại hoặc đã bị gỡ bỏ khỏi hệ thống.
            </p>
            <Link href="/tours">
              <span className="inline-flex items-center gap-1.5 px-6 py-2.5 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-semibold text-xs shadow-md transition-all cursor-pointer">
                Quay lại danh sách tour
              </span>
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  // Filter related tours (exclude current tour, match same category if possible)
  const relatedTours = mockTours
    .filter((t) => t.slug !== tour.slug)
    .sort((a, b) => (a.category === tour.category ? -1 : 1))
    .slice(0, 3);

  // Generate dynamic itinerary if not present
  let itineraryList = tour.itinerary || [];
  if (itineraryList.length === 0) {
    const getDaysCount = (durationStr: string): number => {
      const match = durationStr.match(/(\d+)\s*ngày/i);
      return match ? parseInt(match[1], 10) : 3;
    };

    const daysCount = getDaysCount(tour.duration);

    const generateItinerary = (dayNum: number, totalDays: number) => {
      const locationName = tour.location.split(",")[0];
      const highlight1 = tour.highlights?.[0] || "Tham quan điểm nhấn chính";
      const highlight2 = tour.highlights?.[1] || "Khám phá ẩm thực & văn hóa bản địa";

      if (dayNum === 1) {
        return {
          day: 1,
          title: `Ngày 1: Khởi hành ➔ Di chuyển đến ${locationName} & Nhận phòng`,
          activities: [
            `Xe và hướng dẫn viên đón đoàn di chuyển đến thung lũng/trung tâm ${locationName}.`,
            "Nhận phòng khách sạn nghỉ ngơi, chuẩn bị sức khỏe cho hành trình tuyệt vời.",
            `Tự do dạo phố, khám phá ẩm thực về đêm tại ${tour.location}.`
          ],
        };
      }

      if (dayNum === totalDays) {
        return {
          day: dayNum,
          title: `Ngày ${dayNum}: Tạm biệt ${locationName} ➔ Trở về`,
          activities: [
            "Thưởng thức điểm tâm sáng buffet tại khách sạn, tự do mua sắm quà lưu niệm địa phương.",
            "Làm thủ tục trả phòng khách sạn.",
            "Xe đưa đoàn quay trở về điểm xuất phát ban đầu. Kết thúc chuyến đi thú vị."
          ],
        };
      }

      return {
        day: dayNum,
        title: `Ngày ${dayNum}: Trải nghiệm ${dayNum === 2 ? highlight1 : highlight2}`,
        activities: [
          `Dùng điểm tâm sáng, khởi hành đến các thắng cảnh kỳ vĩ nhất.`,
          `Trải nghiệm hoạt động độc đáo: ${dayNum === 2 ? highlight1 : highlight2}.`,
          `Dùng bữa trưa và tối với các món ăn đặc sản đậm phong vị bản địa tại nhà hàng.`
        ],
      };
    };

    itineraryList = Array.from({ length: daysCount }, (_, i) =>
      generateItinerary(i + 1, daysCount)
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
      <Header transparent={false} />

      {/* NỘI DUNG CHÍNH TRANG CHI TIẾT */}
      <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 w-full">

        {/* Breadcrumb & Nút Quay lại */}
        <div className="flex items-center justify-between mb-6 select-none">
          <div className="flex items-center gap-1.5 text-xs text-zinc-500 dark:text-zinc-400">
            <Link href="/" className="hover:text-cyan-500">Trang chủ</Link>
            <ChevronRight className="w-3.5 h-3.5" />
            <Link href="/tours" className="hover:text-cyan-500">Tours</Link>
            <ChevronRight className="w-3.5 h-3.5" />
            <span className="text-zinc-800 dark:text-zinc-200 font-medium truncate max-w-[200px] md:max-w-xs">
              {tour.title}
            </span>
          </div>
          <Link
            href="/tours"
            className="inline-flex items-center gap-1 text-xs font-semibold text-zinc-500 hover:text-cyan-500 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Quay lại danh sách
          </Link>
        </div>

        {/* TIÊU ĐỀ TOUR */}
        <div className="mb-8">
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 text-xs font-bold uppercase tracking-wider mb-3">
            <Sparkles className="w-3.5 h-3.5" /> Chuyến đi đặc sắc
          </span>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight leading-tight mb-4">
            {tour.title}
          </h1>

          {/* Metadata phụ */}
          <div className="flex flex-wrap items-center gap-y-3 gap-x-6 text-sm text-zinc-500 dark:text-zinc-400">
            <div style={{ display: "none" }} className="flex items-center gap-1 bg-amber-50 dark:bg-amber-950/20 px-2.5 py-1 rounded-xl text-amber-600 dark:text-amber-400 font-bold">
              <Star className="w-4 h-4 fill-amber-500 text-amber-500" />
              <span>{tour.rating}</span>
              <span className="text-zinc-400 font-normal">({tour.reviewsCount} đánh giá)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <MapPin className="w-4.5 h-4.5 text-cyan-500" />
              <span>{tour.location}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock className="w-4.5 h-4.5 text-zinc-400" />
              <span>{tour.duration}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Users className="w-4.5 h-4.5 text-zinc-400" />
              <span>Tối đa {tour.maxGroupSize} khách</span>
            </div>
          </div>
        </div>

        {/* THƯ VIỆN HÌNH ẢNH AIRBNB */}
        <div className="mb-12">
          <TourGallery images={tour.images} title={tour.title} />
        </div>

        {/* THÔNG TIN CHI TIẾT & BOOKING WIDGET */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10 items-start">

          {/* CỘT TRÁI: THÔNG TIN CHI TIẾT TOUR */}
          <div className="col-span-1 lg:col-span-2 space-y-10">

            {/* 1. Tổng quan mô tả */}
            <section className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-3xl p-6 md:p-8 shadow-sm">
              {/* <h2 className="text-xl font-bold text-zinc-950 dark:text-white mb-4">Mô tả hành trình</h2> */}
              <div 
                className="tour-description-html text-sm text-zinc-600 dark:text-zinc-400 leading-7 font-normal"
                dangerouslySetInnerHTML={{ __html: tour.description || "" }}
              />
            </section>

            {/* 2. Điểm nổi bật (Highlights) */}
            {/* {tour.highlights && tour.highlights.length > 0 && (
              <section className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-3xl p-6 md:p-8 shadow-sm">
                <h2 className="text-xl font-bold text-zinc-950 dark:text-white mb-5">Điểm nhấn nổi bật</h2>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {tour.highlights.map((highlight, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <div className="w-5 h-5 bg-cyan-50 dark:bg-cyan-950/20 text-cyan-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Check className="w-3.5 h-3.5 stroke-[3]" />
                      </div>
                      <span className="text-sm text-zinc-650 dark:text-zinc-400 leading-6">{highlight}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )} */}

            {/* 3. Lịch trình chi tiết (Timeline Itinerary) */}
            {/* <section className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-3xl p-6 md:p-8 shadow-sm">
              <h2 className="text-xl font-bold text-zinc-950 dark:text-white mb-6">Lịch trình chi tiết</h2>
              <div className="relative pl-6 sm:pl-8 border-l border-zinc-200 dark:border-zinc-800 space-y-8">
                {itineraryList.map((item, index) => (
                  <div key={index} className="relative">
                    <span className="absolute -left-[31px] sm:-left-[39px] top-1 w-4 h-4 rounded-full bg-cyan-500 border-4 border-zinc-50 dark:border-zinc-900 shadow-md ring-2 ring-cyan-500/20" />

                    <h3 className="font-bold text-sm sm:text-base text-zinc-950 dark:text-white mb-3">
                      {item.title}
                    </h3>
                    <ul className="space-y-2 text-xs sm:text-sm text-zinc-500 dark:text-zinc-400 pl-4 list-disc marker:text-cyan-500">
                      {item.activities.map((act, i) => (
                        <li key={i} className="leading-6">{act}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section> */}

            {/* 4. Dịch vụ bao gồm & Không bao gồm */}
            {/* <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-emerald-50/20 dark:bg-emerald-950/5 border border-emerald-200/20 dark:border-emerald-900/10 rounded-3xl p-6">
                <h3 className="font-bold text-emerald-700 dark:text-emerald-400 mb-4 text-base flex items-center gap-2">
                  <Check className="w-5 h-5" /> Dịch vụ bao gồm
                </h3>
                <ul className="space-y-3 text-xs sm:text-sm text-zinc-605 dark:text-zinc-400">
                  {tour.included?.map((inc, index) => (
                    <li key={index} className="flex items-start gap-2">✓ {inc}</li>
                  )) || (
                      <>
                        <li className="flex items-start gap-2">✓ Phương tiện vận chuyển chất lượng cao suốt tuyến.</li>
                        <li className="flex items-start gap-2">✓ Khách sạn/Resort nghỉ ngơi tiện nghi hiện đại.</li>
                        <li className="flex items-start gap-2">✓ Các bữa ăn theo tiêu chuẩn trong chương trình.</li>
                      </>
                    )}
                </ul>
              </div> */}

            {/* Không bao gồm */}
            {/* <div className="bg-red-50/20 dark:bg-red-950/5 border border-red-200/20 dark:border-red-900/10 rounded-3xl p-6">
                <h3 className="font-bold text-red-700 dark:text-red-400 mb-4 text-base flex items-center gap-2">
                  <Info className="w-5 h-5" /> Không bao gồm
                </h3>
                <ul className="space-y-3 text-xs sm:text-sm text-zinc-605 dark:text-zinc-400">
                  {tour.excluded?.map((exc, index) => (
                    <li key={index} className="flex items-start gap-2">✗ {exc}</li>
                  )) || (
                      <>
                        <li className="flex items-start gap-2">✗ Các chi phí cá nhân (điện thoại, giặt ủi, mua sắm,...).</li>
                        <li className="flex items-start gap-2">✗ Đồ uống phát sinh tự gọi trong các bữa ăn.</li>
                      </>
                    )}
                </ul>
              </div>
            </section> */}

            {/* 5. Nhận xét đánh giá khách hàng */}
            {/* <section className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-3xl p-6 md:p-8 shadow-sm">
              <h2 className="text-xl font-bold text-zinc-950 dark:text-white mb-6 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-cyan-500" /> Nhận xét khách hàng ({reviews.length})
              </h2>

              {reviews.length > 0 ? (
                <div className="space-y-6 divide-y divide-zinc-100 dark:divide-zinc-850">
                  {reviews.map((rev) => (
                    <div key={rev.id} className="pt-6 first:pt-0">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-400 to-blue-500 flex items-center justify-center text-white font-bold overflow-hidden select-none">
                            {rev.avatarUrl ? (
                              // eslint-disable-next-line @next/next/no-img-element
                              <img src={rev.avatarUrl} alt={rev.userName} className="w-full h-full object-cover" />
                            ) : (
                              rev.userName.charAt(0).toUpperCase()
                            )}
                          </div>
                          <div>
                            <h4 className="font-bold text-sm text-zinc-800 dark:text-zinc-200">{rev.userName}</h4>
                            <span className="text-[10px] text-zinc-400">{new Date(rev.date).toLocaleDateString("vi-VN")}</span>
                          </div>
                        </div>

                        <div style={{ display: "none" }} className="flex items-center gap-1 bg-amber-50 dark:bg-amber-950/20 px-2 py-0.5 rounded-lg text-amber-600 dark:text-amber-400 text-xs font-bold">
                          <Star className="w-3.5 h-3.5 fill-amber-500 text-amber-500" />
                          <span>{rev.rating}</span>
                        </div>
                      </div>
                      <p className="text-xs sm:text-sm text-zinc-650 dark:text-zinc-400 leading-relaxed font-normal">
                        {rev.comment}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-zinc-400">Chưa có nhận xét nào cho tour này.</p>
              )}
            </section> */}

          </div>

          {/* CỘT PHẢI: BOOKING WIDGET (STICKY CARD) */}
          <div className="col-span-1">
            <TourBookingWidget tour={tour} />
          </div>

        </div>

        {/* TOURS LIÊN QUAN */}
        <section className="mt-20 border-t border-zinc-200 dark:border-zinc-850 pt-16">
          <h2 className="text-2xl font-extrabold text-zinc-950 dark:text-white mb-8 text-center sm:text-left">
            Hành Trình Du Lịch Khác
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {relatedTours.map((t) => (
              <TourCard key={t.id} tour={t} />
            ))}
          </div>
        </section>

      </main>

      <Footer />
    </div>
  );
}
