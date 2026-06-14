"use client";

import React, { useEffect, useState } from "react";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import TourSearch from "@/features/tours/components/TourSearch";
import TourFilter from "@/features/tours/components/TourFilter";
import TourCard from "@/features/tours/components/TourCard";
import { useRouter } from "next/navigation";
import { Tour } from "@/types/tour";

import {
  ShieldCheck,
  BadgePercent,
  Landmark,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

const mapCategoryNameToId = (name: string): string => {
  if (!name) return "culture";
  const lower = name.toLowerCase();
  if (lower.includes("biển") || lower.includes("đảo") || lower.includes("beach")) return "beach";
  if (lower.includes("núi") || lower.includes("rừng") || lower.includes("khám phá") || lower.includes("mạo hiểm") || lower.includes("mountain")) return "mountain";
  if (lower.includes("nghỉ dưỡng") || lower.includes("resort")) return "resort";
  if (lower.includes("văn hóa") || lower.includes("lịch sử") || lower.includes("trải nghiệm") || lower.includes("culture")) return "culture";
  return "culture"; // default fallback
};

export default function PublicPage() {
  const [activeCategory, setActiveCategory] = useState("all");
  const [listTours, setListTours] = useState<Tour[]>([]);
  const [isFetchingTour, setIsFetchingTours] = useState(false);

  const [listDestinations, setListDestinations] = useState<Tour[]>([]);
  const [isFetchingDestinations, setIsFetchingDestinations] = useState(false);

  useEffect(() => {
    const filteredTours = async () => {
      try {
        setIsFetchingTours(true);
        const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/tours?category=${activeCategory}`);
        if (res.ok) {
          const data = await res.json();
          const normalized = (data.tours || []).map((t: any) => {
            const durationDays = t.duration_days || 1;
            const durationStr = `${durationDays} ngày ${Math.max(0, durationDays - 1)} đêm`;
            return {
              ...t,
              id: String(t.tour_id || t.id),
              title: t.title || "",
              slug: t.slug || "",
              description: t.content || t.summary || "",
              price: Number(t.price_per_adult || t.price || 0),
              discountPrice: t.discount_price !== undefined && t.discount_price !== null ? Number(t.discount_price) : (t.discountPrice || undefined),
              price_per_child: Number(t.price_per_child) || 0,
              duration: t.duration ? t.duration : durationStr,
              location: t.location_name || t.location || "Việt Nam",
              featuredImage: t.thumbnail ? (t.thumbnail.startsWith('http') ? t.thumbnail : (process.env.NEXT_PUBLIC_BASE_URL || "") + t.thumbnail) : (t.featuredImage ? (t.featuredImage.startsWith('http') ? t.featuredImage : (process.env.NEXT_PUBLIC_BASE_URL || "") + t.featuredImage) : "https://images.unsplash.com/photo-1508873699372-7aeab60b44ab?w=800&auto=format&fit=crop&q=80"),
              images: Array.isArray(t.images) && t.images.length > 0 
                ? t.images.map((img: string) => img.startsWith('http') ? img : (process.env.NEXT_PUBLIC_BASE_URL || "") + img)
                : [t.thumbnail ? (t.thumbnail.startsWith('http') ? t.thumbnail : (process.env.NEXT_PUBLIC_BASE_URL || "") + t.thumbnail) : (t.featuredImage ? (t.featuredImage.startsWith('http') ? t.featuredImage : (process.env.NEXT_PUBLIC_BASE_URL || "") + t.featuredImage) : "https://images.unsplash.com/photo-1508873699372-7aeab60b44ab?w=800&auto=format&fit=crop&q=80")],
              rating: t.rating || 4.8,
              reviewsCount: t.reviewsCount || 12,
              category: mapCategoryNameToId(t.category_name || t.category || "culture"),
              maxGroupSize: t.maxGroupSize || 20,
              startDates: t.startDates || ["2026-06-12", "2026-06-19", "2026-06-26"],
              highlights: t.highlights || []
            };
          });
          setListTours(normalized);
        }
      } catch (err) {
        console.error("Lỗi khi tải danh sách tour theo category:", err);
      } finally {
        setIsFetchingTours(false);
      }
    };
    filteredTours();
  }, [activeCategory]);

  useEffect(() => {
    const filteredDestinations = async () => {
      try {
        setIsFetchingDestinations(true);
        const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/locations?is_popular=true&type=domestic`);
        if (res.ok) {
          const data = await res.json();
          setListDestinations(data);
        }
      } catch (err) {
        console.error("Lỗi khi tải danh sách địa danh:", err);
      } finally {
        setIsFetchingDestinations(false);
      }
    };
    filteredDestinations();
  }, [activeCategory]);

  // Danh sách các điểm đến hàng đầu để dựng Spotlight Grid
  // const spotDestinations = [
  //   {
  //     name: "Vịnh Hạ Long",
  //     toursCount: 42,
  //     image:
  //       "https://images.unsplash.com/photo-1528127269322-539801943592?w=800&auto=format&fit=crop&q=80",
  //     className: "md:col-span-2 md:row-span-2 h-[340px] md:h-[420px]",
  //   },
  //   {
  //     name: "Đảo Phú Quốc",
  //     toursCount: 28,
  //     image:
  //       "https://images.unsplash.com/photo-1583212292454-1fe6229603b7?w=800&auto=format&fit=crop&q=80",
  //     className: "md:col-span-1 md:row-span-1 h-[200px]",
  //   },
  //   {
  //     name: "Phố Cổ Hội An",
  //     toursCount: 19,
  //     image:
  //       "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&auto=format&fit=crop&q=80",
  //     className: "md:col-span-1 md:row-span-2 h-[340px] md:h-[420px]",
  //   },
  //   {
  //     name: "Đồng Văn, Hà Giang",
  //     toursCount: 15,
  //     image:
  //       "https://images.unsplash.com/photo-1605538032432-a9f0c8d9baac?w=800&auto=format&fit=crop&q=80",
  //     className: "md:col-span-1 md:row-span-1 h-[200px]",
  //   },
  // ];

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
      {/* Header dạng trong suốt trên nền Hero */}
      <Header transparent={true} />

      <main className="flex-grow">
        {/* 1. HERO SECTION */}
        <section className="relative h-screen flex items-center justify-center z-20">
          {/* Background Image phong cảnh đẹp */}
          <div className="absolute inset-0 z-0 overflow-hidden">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1600&auto=format&fit=crop&q=80"
              alt="Travel Banner"
              className="w-full h-full object-cover brightness-[0.7] scale-105 animate-subtle-zoom"
            />
            {/* Lớp phủ mờ tối */}
            <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/30 to-zinc-50 dark:to-black" />
          </div>

          {/* Slogan & Tour Search */}
          <div className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white mt-12">
            <div className="max-w-3xl mx-auto mb-8 animate-fade-in-up">
              <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-cyan-500/20 backdrop-blur-md text-cyan-300 text-xs font-semibold uppercase tracking-wider mb-4 border border-cyan-400/30">
                <Sparkles className="w-3.5 h-3.5" /> Khám phá các chân trời mới
              </span>
              <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight leading-tight mb-4">
                Bắt Đầu Từ Một{" "}
                <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  Điểm Chạm
                </span>
              </h1>
              <p className="text-base sm:text-lg md:text-xl text-zinc-200/90 font-medium">
                Tìm kiếm hàng trăm gói du lịch độc đáo, nghỉ dưỡng sang trọng và
                tour khám phá được thiết kế riêng cho bạn.
              </p>
            </div>

            {/* Thanh tìm kiếm */}
            <div className="animate-fade-in-up delay-200">
              <TourSearch />
            </div>
          </div>
        </section>

        {/* 2. QUICK FILTER & FEATURED TOURS SECTION */}
        <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50">
              Những Hành Trình Nổi Bật
            </h2>
            <p className="text-zinc-500 dark:text-zinc-400 mt-3 text-sm sm:text-base">
              Lựa chọn những hành trình chất lượng cao được thiết kế chu đáo,
              mang đến những trải nghiệm đáng nhớ nhất.
            </p>
          </div>

          {/* Bộ lọc theo danh mục */}
          <div className="mb-10">
            <TourFilter
              activeCategory={activeCategory}
              onCategoryChange={setActiveCategory}
            />
          </div>

          {/* Grid danh sách TourCard */}
          {listTours.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {listTours.map((tour) => (
                <div key={tour.tour_id} className="animate-fade-in duration-500">
                  <TourCard tour={tour} />
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-16 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-8">
              <p className="text-zinc-500 dark:text-zinc-400">
                Không tìm thấy tour nào thuộc danh mục này.
              </p>
            </div>
          )}
        </section>

        {/* 3. DESTINATIONS SPOTLIGHT SECTION */}
        <section className="py-20 bg-zinc-100 dark:bg-zinc-950/40 border-y border-zinc-200/50 dark:border-zinc-800/40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-12 gap-4">
              <div>
                <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50">
                  Điểm Đến Hàng Đầu
                </h2>
                <p className="text-zinc-500 dark:text-zinc-400 mt-2 text-sm sm:text-base">
                  Khám phá những điểm đến du lịch được yêu thích nhất tại Việt
                  Nam.
                </p>
              </div>
              <Link
                href="/tours"
                className="inline-flex items-center gap-1.5 text-cyan-500 hover:text-cyan-600 dark:hover:text-cyan-400 font-semibold text-sm transition-colors group"
              >
                Xem tất cả điểm đến{" "}
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>

            {/* Grid Spotlight */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {listDestinations?.map((dest, i) => (
                <div
                  key={i}
                  className={cn(
                    "relative overflow-hidden rounded-3xl group shadow-sm hover:shadow-lg cursor-pointer",
                    dest.className,
                  )}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={dest.image_url || dest.image}
                    alt={dest.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    loading="lazy"
                  />
                  {/* Lớp phủ màu mờ */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent transition-opacity group-hover:opacity-90" />

                  {/* Nội dung chữ trên ảnh */}
                  <div className="absolute bottom-6 left-6 text-white z-10">
                    <p className="text-xs text-cyan-300 font-bold uppercase tracking-wider mb-1">
                      {dest.toursCount} Tours
                    </p>
                    <h3 className="text-xl md:text-2xl font-bold tracking-tight">
                      {dest.name}
                    </h3>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 4. WHY CHOOSE US SECTION */}
        <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-50">
              Tại Sao Chọn VnTravel?
            </h2>
            <p className="text-zinc-500 dark:text-zinc-400 mt-3 text-sm sm:text-base">
              Chúng tôi luôn nỗ lực hết mình để đem lại những trải nghiệm tốt
              nhất trên từng dặm đường của quý khách.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            {/* An toàn */}
            <div className="bg-white dark:bg-zinc-900 border border-zinc-150 dark:border-zinc-800 rounded-3xl p-8 hover:shadow-lg transition-all duration-300 flex flex-col items-center text-center">
              <div className="w-14 h-14 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 rounded-2xl flex items-center justify-center mb-6">
                <ShieldCheck className="w-7 h-7" />
              </div>
              <h3 className="font-bold text-lg text-zinc-900 dark:text-zinc-100 mb-3">
                An Toàn Tuyệt Đối
              </h3>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-6">
                Mọi tour diễn ra đều có bảo hiểm du lịch toàn diện và đội ngũ
                hướng dẫn viên chuyên nghiệp theo sát hỗ trợ.
              </p>
            </div>

            {/* Giá tốt nhất */}
            <div className="bg-white dark:bg-zinc-900 border border-zinc-150 dark:border-zinc-800 rounded-3xl p-8 hover:shadow-lg transition-all duration-300 flex flex-col items-center text-center">
              <div className="w-14 h-14 bg-cyan-50 dark:bg-cyan-950/20 text-cyan-500 rounded-2xl flex items-center justify-center mb-6">
                <BadgePercent className="w-7 h-7" />
              </div>
              <h3 className="font-bold text-lg text-zinc-900 dark:text-zinc-100 mb-3">
                Giá Tốt & Ưu Đãi Lớn
              </h3>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-6">
                Cam kết giá cạnh tranh nhất thị trường cùng các ưu đãi giảm giá
                độc quyền cho khách hàng thân thiết hàng tháng.
              </p>
            </div>

            {/* Trải nghiệm độc đáo */}
            <div className="bg-white dark:bg-zinc-900 border border-zinc-150 dark:border-zinc-800 rounded-3xl p-8 hover:shadow-lg transition-all duration-300 flex flex-col items-center text-center">
              <div className="w-14 h-14 bg-blue-50 dark:bg-blue-950/20 text-blue-500 rounded-2xl flex items-center justify-center mb-6">
                <Landmark className="w-7 h-7" />
              </div>
              <h3 className="font-bold text-lg text-zinc-900 dark:text-zinc-100 mb-3">
                Trải Nghiệm Độc Đáo
              </h3>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-6">
                Hành trình được thiết kế đan xen linh hoạt giữa nghỉ ngơi giải
                trí và khám phá sâu sắc văn hóa địa phương.
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* Footer ở dưới cùng */}
      <Footer />
    </div>
  );
}
