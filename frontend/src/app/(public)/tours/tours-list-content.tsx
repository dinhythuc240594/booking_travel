"use client";

import React, { useState, useEffect, useTransition } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Tour } from "@/types/tour";
import { mockTours } from "@/mocks/data/tours";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import TourCard from "@/features/tours/components/TourCard";
import Pagination from "@/components/common/Pagination";
import {
  Filter, SlidersHorizontal, ArrowUpDown, RefreshCw, MapPin,
  Clock, Star, Compass, Grid, X
} from "lucide-react";
import { Button } from "@/components/ui/button";

const ITEMS_PER_PAGE = 6;

const mapCategoryNameToId = (name: string): string => {
  if (!name) return "culture";
  const lower = name.toLowerCase();
  if (lower.includes("biển") || lower.includes("đảo") || lower.includes("beach")) return "beach";
  if (lower.includes("núi") || lower.includes("rừng") || lower.includes("khám phá") || lower.includes("mạo hiểm") || lower.includes("mountain")) return "mountain";
  if (lower.includes("nghỉ dưỡng") || lower.includes("resort")) return "resort";
  if (lower.includes("văn hóa") || lower.includes("lịch sử") || lower.includes("trải nghiệm") || lower.includes("culture")) return "culture";
  return "culture"; // default fallback
};

export default function ToursListContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [, startTransition] = useTransition();

  // Đọc các giá trị ban đầu từ URL
  const initialSearch = searchParams.get("search") || "";
  const initialType = searchParams.get("type") || "all";
  const initialCategory = searchParams.get("category") || "all";
  const initialDate = searchParams.get("date") || "";
  const initialGuests = searchParams.get("guests") || "0";
  const initialAdults = searchParams.get("adults") || "0";
  const initialChildren = searchParams.get("children") || "0";

  // State các bộ lọc
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const [region, setRegion] = useState<string>(initialType);
  const [category, setCategory] = useState<string>(initialCategory);
  const [maxPrice, setMaxPrice] = useState<number>(10000000); // Mặc định 10 triệu
  const [duration, setDuration] = useState<string>("all"); // all, short, medium, long
  const [minRating, setMinRating] = useState<number>(0); // 0 (tất cả), 3, 4, 5 sao
  const [sortBy, setSortBy] = useState<string>("recommended");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);
  const [tours, setTours] = useState<Tour[]>([]);
  const [date, setDate] = useState<string>(initialDate);
  const [guests, setGuests] = useState<number>(Number(initialGuests));
  const [adults, setAdults] = useState<number>(Number(initialAdults));
  const [children, setChildren] = useState<number>(Number(initialChildren));

  // Cập nhật state khi URL thay đổi (nhấn Tìm kiếm từ trang chủ chuyển hướng qua)
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchQuery(initialSearch);
      if (initialType !== "all") setRegion(initialType);
      if (initialCategory !== "all") setCategory(initialCategory);
      if (initialDate) setDate(initialDate);
      if (initialGuests) setGuests(Number(initialGuests));
      if (initialAdults) setAdults(Number(initialAdults));
      if (initialChildren) setChildren(Number(initialChildren));
    }, 0);
    return () => clearTimeout(timer);
  }, [initialSearch, initialType, initialCategory, initialDate, initialGuests, initialAdults, initialChildren]);

  // Đồng bộ hóa các bộ lọc lên URL (Debounced để tránh giật lag khi kéo giá)
  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      const params = new URLSearchParams();
      if (searchQuery) params.append("search", searchQuery);
      if (date) params.append("date", date);
      if (guests) params.append("guests", guests.toString());
      if (adults) params.append("adults", adults.toString());
      if (children) params.append("children", children.toString());
      if (region !== "all") params.append("type", region);
      if (category !== "all") params.append("category", category);
      if (maxPrice < 10000000) params.append("maxPrice", maxPrice.toString());
      if (duration !== "all") params.append("duration", duration);
      if (minRating > 0) params.append("rating", minRating.toString());
      if (sortBy !== "recommended") params.append("sortBy", sortBy);
      if (currentPage > 1) params.append("page", currentPage.toString());

      startTransition(() => {
        router.push(`/tours?${params.toString()}`);
      });
    }, 400);

    return () => clearTimeout(delayDebounce);
  }, [searchQuery, region, category, maxPrice, duration, minRating, sortBy, currentPage, router]);

  useEffect(() => {
    const search = async () => {
      try {
        const params = new URLSearchParams();
        if (searchQuery) params.append("search", searchQuery);
        if (date) params.append("date", date);
        if (guests) params.append("guests", guests.toString());
        if (adults) params.append("adults", adults.toString());
        if (children) params.append("children", children.toString());
        const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/search?${params.toString()}`);
        if (!res.ok) throw new Error("Failed to fetch search API");
        const json = await res.json();
        const data = json.tours || [];
        const normalized = data.map((t: any) => {
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
            country: t.country || "Việt Nam",
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
        setTours(normalized);
      } catch (err) {
        console.warn("API search failed, falling back to mock data:", err);
        // Fallback to mock data matching search query
        const filteredMock = mockTours.filter((t) => {
          if (searchQuery.trim()) {
            const term = searchQuery.toLowerCase();
            return t.title.toLowerCase().includes(term) || t.location.toLowerCase().includes(term);
          }
          return true;
        });
        setTours(filteredMock);
      }
    }
    search();
  }, [searchQuery, date, guests, adults, children]);


  // Hàm Reset bộ lọc
  const handleResetFilters = () => {
    setSearchQuery("");
    setRegion("all");
    setCategory("all");
    setMaxPrice(10000000);
    setDuration("all");
    setMinRating(0);
    setSortBy("recommended");
    setCurrentPage(1);
  };

  // Trích xuất số ngày từ chuỗi duration (Ví dụ: "3 ngày 2 đêm" -> 3)
  const parseDays = (durationStr: string): number => {
    const match = durationStr.match(/(\d+)\s*ngày/i);
    return match ? parseInt(match[1], 10) : 0;
  };

  // LỌC DANH SÁCH TOUR
  const filteredTours = tours.filter((tour) => {
    // 1. Lọc theo từ khóa tìm kiếm (tiêu đề hoặc địa điểm)
    if (searchQuery.trim()) {
      const term = searchQuery.toLowerCase();
      const inTitle = tour.title.toLowerCase().includes(term);
      const inLocation = tour.location_name?.toLowerCase()?.includes(term) || tour.location?.toLowerCase()?.includes(term) || false;
      if (!inTitle && !inLocation) return false;
    }

    // 2. Lọc theo thể loại
    if (category !== "all" && tour.category !== category) return false;

    // 3. Lọc theo vùng miền (domestic / international)
    if (region !== "all") {
      const countryStr = tour.country || (tour.location ? (tour.location.toLowerCase().includes("thái lan") || tour.location.toLowerCase().includes("anh quốc") || tour.location.toLowerCase().includes("quốc tế") ? "Thái Lan" : "Việt Nam") : "Việt Nam");
      const isTourInt = countryStr.toLowerCase() !== "vietnam" && countryStr.toLowerCase() !== "việt nam";
      if (region === "domestic" && isTourInt) return false;
      if (region === "international" && !isTourInt) return false;
    }

    // 4. Lọc theo giá (Lấy giá ưu đãi nếu có, ngược lại lấy giá gốc)
    const effectivePrice = tour.discountPrice || tour.price;
    if (effectivePrice > maxPrice) return false;

    // 5. Lọc theo thời gian (Số ngày)
    if (duration !== "all") {
      const days = parseDays(tour.duration);
      if (duration === "short" && days > 2) return false;
      if (duration === "medium" && (days < 3 || days > 4)) return false;
      if (duration === "long" && days < 5) return false;
    }

    // 6. Lọc theo đánh giá
    if (minRating > 0 && tour.rating < minRating) return false;

    return true;
  });

  // SẮP XẾP DANH SÁCH TOUR
  const sortedTours = [...filteredTours].sort((a, b) => {
    const priceA = a.discountPrice || a.price;
    const priceB = b.discountPrice || b.price;

    if (sortBy === "priceAsc") return priceA - priceB;
    if (sortBy === "priceDesc") return priceB - priceA;
    if (sortBy === "rating") return b.rating - a.rating;
    return 0; // "recommended" - giữ nguyên thứ tự mặc định
  });

  // PHÂN TRANG TOURS
  const totalPages = Math.ceil(sortedTours.length / ITEMS_PER_PAGE);
  const paginatedTours = sortedTours.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  // Định dạng tiền tệ VND
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const categories = [
    { id: "all", name: "Tất cả loại hình" },
    { id: "beach", name: "Biển đảo" },
    { id: "mountain", name: "Khám phá núi rừng" },
    { id: "resort", name: "Nghỉ dưỡng 5 sao" },
    { id: "culture", name: "Văn hóa - Lịch sử" },
    // { id: "international", name: "Du lịch quốc tế" },
  ];

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
      <Header transparent={false} />

      {/* BANNER ĐẦU TRANG */}
      <section className="relative py-16 md:py-24 bg-zinc-900 text-white mt-16 overflow-hidden">
        {/* Background Image phong cảnh mờ */}
        <div className="absolute inset-0 z-0 opacity-40">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=1600&auto=format&fit=crop&q=80"
            alt="Tours Banner"
            className="w-full h-full object-cover"
          />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-zinc-950 via-zinc-900/80 to-transparent z-0" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-300 text-xs font-semibold uppercase tracking-wider mb-3 border border-cyan-400/20">
            <Compass className="w-3.5 h-3.5" /> Khám phá hành trình
          </span>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight mb-3">
            Danh Sách Tour Du Lịch
          </h1>
          <p className="text-sm sm:text-base text-zinc-300 max-w-xl leading-relaxed">
            Tìm kiếm hành trình mơ ước của bạn. Lọc qua hàng chục điểm đến thú vị được thiết kế với dịch vụ cao cấp và hướng dẫn viên tận tình.
          </p>
        </div>
      </section>

      {/* BỐ CỤC CHÍNH */}
      <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

          {/* ================= sidebaR BỘ LỌC (DESKTOP) ================= */}
          <aside className="hidden lg:block lg:col-span-1 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-3xl p-6 shadow-sm h-fit sticky top-24">
            <div className="flex justify-between items-center pb-4 border-b border-zinc-100 dark:border-zinc-800 mb-6">
              <span className="flex items-center gap-2 font-bold text-base">
                <SlidersHorizontal className="w-5 h-5 text-cyan-500" />
                Bộ Lọc Tìm Kiếm
              </span>
              <button
                onClick={handleResetFilters}
                className="text-xs font-semibold text-zinc-400 hover:text-cyan-500 flex items-center gap-1 transition-colors cursor-pointer"
                title="Đặt lại bộ lọc"
              >
                <RefreshCw className="w-3 h-3" /> Đặt lại
              </button>
            </div>

            <div className="space-y-6">

              {/* Lọc: Từ khóa tìm kiếm */}
              <div>
                <label htmlFor="search" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                  Từ khóa điểm đến
                </label>
                <div className="relative">
                  <input
                    id="search"
                    type="text"
                    placeholder="Tìm tên tour, địa danh..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 placeholder-zinc-400 transition-all"
                  />
                </div>
              </div>

              {/* Lọc: Vùng miền (Commented out because system only has domestic tours)
              <div>
                <span className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2.5">
                  Phân vùng địa lý
                </span>
                <div className="flex flex-col gap-2">
                  {[
                    { id: "all", label: "Tất cả" },
                    { id: "domestic", label: "Trong nước" },
                    { id: "international", label: "Nước ngoài / Quốc tế" },
                  ].map((item) => (
                    <label key={item.id} className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-300 cursor-pointer select-none">
                      <input
                        type="radio"
                        name="region"
                        checked={region === item.id}
                        onChange={() => {
                          setRegion(item.id);
                          setCurrentPage(1);
                        }}
                        className="w-4 h-4 text-cyan-500 focus:ring-cyan-500 border-zinc-300 dark:border-zinc-700 bg-transparent"
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              */}

              {/* Lọc: Loại hình tour */}
              <div>
                <label htmlFor="category" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                  Loại hình du lịch
                </label>
                <select
                  id="category"
                  value={category}
                  onChange={(e) => {
                    setCategory(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 cursor-pointer transition-all"
                >
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id} className="text-zinc-800 dark:text-zinc-100">
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Lọc: Giá tối đa */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
                    Ngân sách tối đa
                  </span>
                  <span className="text-sm font-bold text-cyan-500 dark:text-cyan-400">
                    {formatCurrency(maxPrice)}
                  </span>
                </div>
                <input
                  type="range"
                  min="2000000"
                  max="12000000"
                  step="500000"
                  value={maxPrice}
                  onChange={(e) => {
                    setMaxPrice(parseInt(e.target.value, 10));
                    setCurrentPage(1);
                  }}
                  className="w-full h-1.5 bg-zinc-200 dark:bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                />
                <div className="flex justify-between text-[10px] text-zinc-400 mt-1.5">
                  <span>{formatCurrency(2000000)}</span>
                  <span>{formatCurrency(12000000)}</span>
                </div>
              </div>

              {/* Lọc: Thời gian */}
              <div>
                <span className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2.5">
                  Thời lượng chuyến đi
                </span>
                <div className="flex flex-col gap-2">
                  {[
                    { id: "all", label: "Tất cả thời gian" },
                    { id: "short", label: "Ngắn ngày (1 - 2 ngày)" },
                    { id: "medium", label: "Trung bình (3 - 4 ngày)" },
                    { id: "long", label: "Dài ngày (từ 5 ngày trở lên)" },
                  ].map((item) => (
                    <label key={item.id} className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-300 cursor-pointer select-none">
                      <input
                        type="radio"
                        name="duration"
                        checked={duration === item.id}
                        onChange={() => {
                          setDuration(item.id);
                          setCurrentPage(1);
                        }}
                        className="w-4 h-4 text-cyan-500 focus:ring-cyan-500 border-zinc-300 dark:border-zinc-700 bg-transparent"
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Lọc: Đánh giá */}
              {/* <div>
                <span className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2.5">
                  Đánh giá tối thiểu
                </span>
                <div className="flex flex-col gap-2">
                  {[
                    { id: 0, label: "Tất cả đánh giá" },
                    { id: 4.8, label: "Xuất sắc (Từ 4.8★)" },
                    { id: 4.6, label: "Rất tốt (Từ 4.6★)" },
                  ].map((item) => (
                    <label key={item.id} className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-300 cursor-pointer select-none">
                      <input
                        type="radio"
                        name="minRating"
                        checked={minRating === item.id}
                        onChange={() => {
                          setMinRating(item.id);
                          setCurrentPage(1);
                        }}
                        className="w-4 h-4 text-cyan-500 focus:ring-cyan-500 border-zinc-300 dark:border-zinc-700 bg-transparent"
                      />
                      <span className="flex items-center gap-1">
                        {item.label}
                      </span>
                    </label>
                  ))}
                </div>
              </div> */}

            </div>
          </aside>

          {/* ================= DANH SÁCH TOURS BÊN PHẢI ================= */}
          <div className="col-span-1 lg:col-span-3 flex flex-col">

            {/* THANH SẮP XẾP VÀ SỐ LƯỢNG KẾT QUẢ */}
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-2xl p-4 mb-8 flex flex-col sm:flex-row justify-between items-center gap-4 shadow-sm select-none">

              {/* Thống kê số lượng */}
              <div className="text-sm font-semibold text-zinc-500 dark:text-zinc-400 flex items-center gap-1.5">
                <Grid className="w-4.5 h-4.5 text-cyan-500" />
                Tìm thấy <span className="text-zinc-800 dark:text-white font-bold">{sortedTours.length}</span> kết quả phù hợp
              </div>

              {/* Sắp xếp & Nút lọc Mobile */}
              <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
                <button
                  type="button"
                  onClick={() => setIsMobileFilterOpen(true)}
                  className="lg:hidden flex items-center gap-1.5 px-4 py-2 border border-zinc-200 dark:border-zinc-800 rounded-xl text-sm font-semibold text-zinc-700 dark:text-zinc-300 hover:border-cyan-500 transition-all cursor-pointer"
                >
                  <Filter className="w-4 h-4 text-cyan-500" /> Bộ lọc
                </button>

                <div className="flex items-center gap-2">
                  <ArrowUpDown className="w-4 h-4 text-zinc-400 hidden sm:block" />
                  <select
                    value={sortBy}
                    onChange={(e) => {
                      setSortBy(e.target.value);
                      setCurrentPage(1);
                    }}
                    className="bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 cursor-pointer"
                  >
                    <option value="recommended">Đề xuất hàng đầu</option>
                    <option value="priceAsc">Giá: Từ thấp đến cao</option>
                    <option value="priceDesc">Giá: Từ cao đến thấp</option>
                    <option value="rating">Đánh giá tốt nhất</option>
                  </select>
                </div>
              </div>

            </div>

            {/* LƯỚI HIỂN THỊ TOURS */}
            {paginatedTours.length > 0 ? (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 flex-grow">
                  {paginatedTours.map((tour) => (
                    <div key={tour.id} className="animate-fade-in duration-500">
                      <TourCard tour={tour} />
                    </div>
                  ))}
                </div>

                {/* PHÂN TRANG */}
                <div className="mt-12">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={setCurrentPage}
                  />
                </div>
              </>
            ) : (
              /* TRẠNG THÁI TRỐNG (EMPTY STATE) */
              <div className="flex flex-col items-center justify-center py-20 px-4 bg-white dark:bg-zinc-900 border border-zinc-200/80 dark:border-zinc-800/80 rounded-3xl text-center shadow-sm">
                <div className="p-4 bg-zinc-100 dark:bg-zinc-850 rounded-full mb-4 text-zinc-400">
                  <Compass className="w-12 h-12 animate-pulse text-cyan-500" />
                </div>
                <h3 className="text-lg font-bold text-zinc-950 dark:text-white mb-2">Không tìm thấy tour phù hợp</h3>
                <p className="text-sm text-zinc-500 dark:text-zinc-400 max-w-sm mb-6 leading-relaxed">
                  Chúng tôi không tìm thấy kết quả nào khớp với các bộ lọc hiện tại của bạn. Hãy thử thay đổi mức ngân sách hoặc từ khóa tìm kiếm.
                </p>
                <Button
                  onClick={handleResetFilters}
                  className="rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white border-0 cursor-pointer shadow-md"
                >
                  Xóa tất cả bộ lọc
                </Button>
              </div>
            )}

          </div>
        </div>
      </main>

      {/* ================= MOBILE FILTER DRAWER (DRAWER TRƯỢT MOBILE) ================= */}
      {isMobileFilterOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex justify-end animate-fade-in">
          {/* Backdrop tối */}
          <div
            onClick={() => setIsMobileFilterOpen(false)}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Nội dung Drawer */}
          <div className="relative w-80 max-w-[85%] bg-white dark:bg-zinc-900 h-full p-6 flex flex-col shadow-2xl animate-slide-in-right z-10 overflow-y-auto">
            <div className="flex justify-between items-center pb-4 border-b border-zinc-100 dark:border-zinc-800 mb-6 flex-shrink-0">
              <span className="flex items-center gap-2 font-bold text-base">
                <Filter className="w-5 h-5 text-cyan-500" />
                Bộ lọc nâng cao
              </span>
              <button
                onClick={() => setIsMobileFilterOpen(false)}
                className="p-1 rounded-lg text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Các trường lọc (tương tự Desktop) */}
            <div className="space-y-6 pb-12">

              {/* Lọc: Từ khóa */}
              <div>
                <label htmlFor="search-mobile" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                  Từ khóa điểm đến
                </label>
                <input
                  id="search-mobile"
                  type="text"
                  placeholder="Tìm tên tour, địa danh..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-850 dark:text-zinc-100 placeholder-zinc-400 transition-all"
                />
              </div>

              {/* Lọc: Vùng miền (Commented out because system only has domestic tours)
              <div>
                <span className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2.5">
                  Phân vùng địa lý
                </span>
                <div className="flex flex-col gap-2">
                  {[
                    { id: "all", label: "Tất cả" },
                    { id: "domestic", label: "Trong nước" },
                    { id: "international", label: "Nước ngoài" },
                  ].map((item) => (
                    <label key={item.id} className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-300 cursor-pointer select-none">
                      <input
                        type="radio"
                        name="region-mobile"
                        checked={region === item.id}
                        onChange={() => {
                          setRegion(item.id);
                          setCurrentPage(1);
                        }}
                        className="w-4 h-4 text-cyan-500 focus:ring-cyan-500 border-zinc-300 dark:border-zinc-700 bg-transparent"
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              */}

              {/* Lọc: Thể loại */}
              <div>
                <label htmlFor="category-mobile" className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2">
                  Loại hình du lịch
                </label>
                <select
                  id="category-mobile"
                  value={category}
                  onChange={(e) => {
                    setCategory(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="w-full bg-zinc-50 dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 text-zinc-800 dark:text-zinc-100 cursor-pointer transition-all"
                >
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id} className="text-zinc-800 dark:text-zinc-100">
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Lọc: Ngân sách */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500">
                    Ngân sách tối đa
                  </span>
                  <span className="text-sm font-bold text-cyan-500 dark:text-cyan-400">
                    {formatCurrency(maxPrice)}
                  </span>
                </div>
                <input
                  type="range"
                  min="2000000"
                  max="12000000"
                  step="500000"
                  value={maxPrice}
                  onChange={(e) => {
                    setMaxPrice(parseInt(e.target.value, 10));
                    setCurrentPage(1);
                  }}
                  className="w-full h-1.5 bg-zinc-200 dark:bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                />
              </div>

              {/* Lọc: Thời gian */}
              <div>
                <span className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2.5">
                  Thời lượng chuyến đi
                </span>
                <div className="flex flex-col gap-2">
                  {[
                    { id: "all", label: "Tất cả thời gian" },
                    { id: "short", label: "Ngắn ngày (1 - 2 ngày)" },
                    { id: "medium", label: "Trung bình (3 - 4 ngày)" },
                    { id: "long", label: "Dài ngày (từ 5 ngày)" },
                  ].map((item) => (
                    <label key={item.id} className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-300 cursor-pointer select-none">
                      <input
                        type="radio"
                        name="duration-mobile"
                        checked={duration === item.id}
                        onChange={() => {
                          setDuration(item.id);
                          setCurrentPage(1);
                        }}
                        className="w-4 h-4 text-cyan-500 focus:ring-cyan-500 border-zinc-300 dark:border-zinc-700 bg-transparent"
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Lọc: Đánh giá */}
              <div>
                <span className="block text-xs font-bold uppercase tracking-wider text-zinc-400 dark:text-zinc-500 mb-2.5">
                  Đánh giá tối thiểu
                </span>
                <div className="flex flex-col gap-2">
                  {[
                    { id: 0, label: "Tất cả đánh giá" },
                    { id: 4.8, label: "Xuất sắc (Từ 4.8★)" },
                    { id: 4.6, label: "Rất tốt (Từ 4.6★)" },
                  ].map((item) => (
                    <label key={item.id} className="flex items-center gap-3 text-sm text-zinc-600 dark:text-zinc-300 cursor-pointer select-none">
                      <input
                        type="radio"
                        name="minRating-mobile"
                        checked={minRating === item.id}
                        onChange={() => {
                          setMinRating(item.id);
                          setCurrentPage(1);
                        }}
                        className="w-4 h-4 text-cyan-500 focus:ring-cyan-500 border-zinc-300 dark:border-zinc-700 bg-transparent"
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>

            </div>

            {/* Nút bấm ở chân Drawer mobile */}
            <div className="mt-auto pt-4 border-t border-zinc-100 dark:border-zinc-800 flex gap-3 flex-shrink-0">
              <Button
                variant="outline"
                onClick={handleResetFilters}
                className="flex-1 rounded-full border-zinc-300 dark:border-zinc-700 text-xs cursor-pointer"
              >
                Xóa tất cả
              </Button>
              <Button
                onClick={() => setIsMobileFilterOpen(false)}
                className="flex-1 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white border-0 text-xs cursor-pointer shadow-md"
              >
                Áp dụng
              </Button>
            </div>
          </div>
        </div>
      )}

      <Footer />
    </div>
  );
}
