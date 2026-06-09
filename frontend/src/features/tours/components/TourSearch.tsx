"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, MapPin, Calendar, Users, Plus, Minus, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface LocationOption {
  name: string;
  search_key: string;
}

export default function TourSearch() {
  const router = useRouter();
  const [destination, setDestination] = useState("");
  const [date, setDate] = useState(() => new Date().toISOString().split("T")[0]);

  // Custom Guest State
  const [adults, setAdults] = useState(1);
  const [children, setChildren] = useState(0);
  const [isGuestPickerOpen, setIsGuestPickerOpen] = useState(false);
  const [isDestDropdownOpen, setIsDestDropdownOpen] = useState(false);

  // Switch chọn Trong nước / Nước ngoài
  const [locationType, setLocationType] = useState<"domestic" | "international">("domestic");
  const [locationsList, setLocationsList] = useState<LocationOption[]>([]);
  const [isFetchingLocations, setIsFetchingLocations] = useState(false);

  // Refs để bắt sự kiện click outside
  const destRef = useRef<HTMLDivElement>(null);
  const guestRef = useRef<HTMLDivElement>(null);
  const dateInputRef = useRef<HTMLInputElement>(null);

  // Fetch danh sách địa danh khi locationType thay đổi
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        setIsFetchingLocations(true);
        const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/locations?type=${locationType}`);
        if (res.ok) {
          const data = await res.json();
          setLocationsList(data);
        }
      } catch (err) {
        console.error("Lỗi khi tải danh sách địa danh:", err);
      } finally {
        setIsFetchingLocations(false);
      }
    };
    fetchLocations();
  }, [locationType]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (destRef.current && !destRef.current.contains(event.target as Node)) {
        setIsDestDropdownOpen(false);
      }
      if (guestRef.current && !guestRef.current.contains(event.target as Node)) {
        setIsGuestPickerOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    const params = new URLSearchParams();
    if (destination.trim()) params.append("search", destination.trim());
    if (date) params.append("date", date);
    if (locationType) params.append("type", locationType);

    const totalGuests = adults + children;
    if (totalGuests > 1) {
      params.append("guests", totalGuests.toString());
      params.append("adults", adults.toString());
      if (children > 0) params.append("children", children.toString());
    }

    // Đóng toàn bộ dropdowns
    setIsDestDropdownOpen(false);
    setIsGuestPickerOpen(false);
    //// KHÔNG CẦN SET process.env.NEXT_PUBLIC_WEB_BASE_URL với router ////
    router.push(`/tours?${params.toString()}`);
  };

  const getGuestLabel = () => {
    let label = `${adults} Người lớn`;
    if (children > 0) {
      label += `, ${children} Trẻ em`;
    }
    return label;
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Switch chọn Trong nước / Nước ngoài
      <div className="flex gap-2 mb-3 ml-2 justify-center md:justify-start">
        <button
          type="button"
          onClick={() => {
            setLocationType("domestic");
            setDestination(""); // Xóa điểm đến cũ khi chuyển vùng
          }}
          className={cn(
            "px-5 py-2 text-xs font-bold rounded-full transition-all duration-300 cursor-pointer select-none",
            locationType === "domestic"
              ? "bg-cyan-500 text-white shadow-lg shadow-cyan-500/20"
              : "bg-white/10 dark:bg-zinc-800/40 text-zinc-100 dark:text-zinc-400 hover:bg-white/20"
          )}
        >
          Trong nước
        </button>
        <button
          type="button"
          onClick={() => {
            setLocationType("international");
            setDestination(""); // Xóa điểm đến cũ khi chuyển vùng
          }}
          className={cn(
            "px-5 py-2 text-xs font-bold rounded-full transition-all duration-300 cursor-pointer select-none",
            locationType === "international"
              ? "bg-cyan-500 text-white shadow-lg shadow-cyan-500/20"
              : "bg-white/10 dark:bg-zinc-800/40 text-zinc-100 dark:text-zinc-400 hover:bg-white/20"
          )}
        >
          Nước ngoài
        </button>
      </div>
      */}

      {/* Form tìm kiếm */}
      <form
        onSubmit={handleSearch}
        className="w-full backdrop-blur-xl bg-white/80 dark:bg-zinc-900/80 border border-white/20 dark:border-zinc-800/40 shadow-2xl rounded-3xl p-4 md:p-5 relative z-100"
      >
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">

          {/* 1. Điểm đến (Destination Autocomplete) */}
          <div ref={destRef} className="md:col-span-5 relative flex items-center">
            <div className="absolute left-4 text-zinc-400 dark:text-zinc-500">
              <MapPin className="w-5 h-5" />
            </div>
            <div className="w-full pl-12 pr-10 py-2.5 flex flex-col justify-center">
              <label htmlFor="destination" className="text-[10px] uppercase font-bold tracking-wider text-zinc-400 dark:text-zinc-500 mb-0.5 select-none">
                Bạn Muốn Đi Đâu?
              </label>
              <input
                id="destination"
                type="text"
                placeholder={locationType === "domestic" ? "Hạ Long, Sapa, Phú Quốc..." : "Thái Lan, Nhật Bản, Hàn Quốc..."}
                value={destination}
                onFocus={() => {
                  setIsDestDropdownOpen(true);
                  setIsGuestPickerOpen(false);
                }}
                onChange={(e) => setDestination(e.target.value)}
                className="bg-transparent text-zinc-800 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none text-sm w-full font-semibold"
                autoComplete="off"
              />
            </div>

            {/* Nút xóa nhanh input */}
            {destination && (
              <button
                type="button"
                onClick={() => setDestination("")}
                className="absolute right-4 p-1 rounded-full text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            {/* Dropdown Gợi ý Địa danh */}
            {isDestDropdownOpen && (
              <div className="absolute top-[calc(100%+12px)] left-0 w-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-xl rounded-2xl p-4 z-50 animate-fade-in text-left">
                <p className="text-[10px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider mb-2 select-none flex items-center gap-1.5">
                  {isFetchingLocations ? (
                    <>
                      <Loader2 className="w-3 h-3 animate-spin text-cyan-500" />
                      Đang tải điểm đến...
                    </>
                  ) : (
                    `Điểm đến ${locationType === "domestic" ? "trong nước" : "nước ngoài"} phổ biến`
                  )}
                </p>
                <div className="flex flex-col gap-1 max-h-60 overflow-y-auto">
                  {!isFetchingLocations && locationsList
                    .filter(dest => dest.name.toLowerCase().includes(destination.toLowerCase()))
                    .map((dest, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => {
                          setDestination(dest.search_key);
                          setIsDestDropdownOpen(false);
                        }}
                        className="flex items-center gap-3 w-full px-3 py-2 rounded-xl text-sm font-medium hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-700 dark:text-zinc-200 hover:text-cyan-500 dark:hover:text-cyan-400 transition-colors text-left cursor-pointer"
                      >
                        <MapPin className="w-4 h-4 text-zinc-400" />
                        <span>{dest.name}</span>
                      </button>
                    ))}
                  {!isFetchingLocations && locationsList.filter(dest => dest.name.toLowerCase().includes(destination.toLowerCase())).length === 0 && (
                    <div className="text-zinc-500 text-xs py-2 px-3">
                      Không tìm thấy gợi ý nào phù hợp.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Vạch chia ngăn dọc */}
            <div className="hidden md:block absolute right-0 h-10 w-px bg-zinc-200 dark:bg-zinc-800" />
          </div>

          {/* 2. Ngày đi (Date Picker) */}
          <div className="md:col-span-3 relative flex items-center">
            <div className="absolute left-4 text-zinc-400 dark:text-zinc-500">
              <Calendar className="w-5 h-5" />
            </div>
            <div
              onClick={() => {
                setIsDestDropdownOpen(false);
                setIsGuestPickerOpen(false);
                if (dateInputRef.current) {
                  try {
                    dateInputRef.current.showPicker();
                  } catch {
                    dateInputRef.current.focus();
                  }
                }
              }}
              className="w-full pl-12 pr-4 py-2.5 flex flex-col justify-center cursor-pointer"
            >
              <label htmlFor="date" className="text-[10px] uppercase font-bold tracking-wider text-zinc-400 dark:text-zinc-500 mb-0.5 select-none cursor-pointer">
                Thời Gian
              </label>
              <input
                id="date"
                ref={dateInputRef}
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                onClick={(e) => {
                  e.stopPropagation(); // Ngăn lan truyền lên div cha
                  if (dateInputRef.current) {
                    try {
                      dateInputRef.current.showPicker();
                    } catch {
                      dateInputRef.current.focus();
                    }
                  }
                }}
                min={new Date().toISOString().split("T")[0]}
                className="bg-transparent text-zinc-800 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none text-sm w-full font-semibold cursor-pointer [color-scheme:light] dark:[color-scheme:dark] [&::-webkit-calendar-picker-indicator]:hidden"
              />
            </div>
            {/* Vạch chia ngăn dọc */}
            <div className="hidden md:block absolute right-0 h-10 w-px bg-zinc-200 dark:bg-zinc-800" />
          </div>

          {/* 3. Hành khách (Custom Popover Guest Picker) */}
          <div ref={guestRef} className="md:col-span-3 relative flex items-center">
            <div className="absolute left-4 text-zinc-400 dark:text-zinc-500">
              <Users className="w-5 h-5" />
            </div>
            <div
              onClick={() => {
                setIsGuestPickerOpen(!isGuestPickerOpen);
                setIsDestDropdownOpen(false);
              }}
              className="w-full pl-12 pr-4 py-2.5 flex flex-col justify-center cursor-pointer select-none"
            >
              <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-400 dark:text-zinc-500 mb-0.5">
                Hành Khách
              </span>
              <span className="text-sm font-semibold text-zinc-800 dark:text-zinc-100 truncate">
                {getGuestLabel()}
              </span>
            </div>

            {/* Popover Điều khiển Số khách */}
            {isGuestPickerOpen && (
              <div className="absolute top-[calc(100%+12px)] right-0 w-72 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 shadow-xl rounded-2xl p-5 z-50 animate-fade-in text-left">

                {/* Người lớn */}
                <div className="flex justify-between items-center mb-4">
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-zinc-800 dark:text-zinc-100">Người lớn</span>
                    <span className="text-[10px] text-zinc-400">Từ 12 tuổi trở lên</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setAdults(Math.max(1, adults - 1))}
                      disabled={adults <= 1}
                      className="w-8 h-8 rounded-full border border-zinc-200 dark:border-zinc-700 hover:border-cyan-500 hover:text-cyan-500 flex items-center justify-center disabled:opacity-40 transition-colors cursor-pointer"
                    >
                      <Minus className="w-4.5 h-4.5" />
                    </button>
                    <span className="text-sm font-bold w-4 text-center text-zinc-800 dark:text-zinc-100">{adults}</span>
                    <button
                      type="button"
                      onClick={() => setAdults(adults + 1)}
                      className="w-8 h-8 rounded-full border border-zinc-200 dark:border-zinc-700 hover:border-cyan-500 hover:text-cyan-500 flex items-center justify-center transition-colors cursor-pointer"
                    >
                      <Plus className="w-4.5 h-4.5" />
                    </button>
                  </div>
                </div>

                {/* Trẻ em */}
                <div className="flex justify-between items-center mb-2">
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-zinc-800 dark:text-zinc-100">Trẻ em</span>
                    <span className="text-[10px] text-zinc-400">Từ 2 đến 11 tuổi</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setChildren(Math.max(0, children - 1))}
                      disabled={children <= 0}
                      className="w-8 h-8 rounded-full border border-zinc-200 dark:border-zinc-700 hover:border-cyan-500 hover:text-cyan-500 flex items-center justify-center disabled:opacity-40 transition-colors cursor-pointer"
                    >
                      <Minus className="w-4.5 h-4.5" />
                    </button>
                    <span className="text-sm font-bold w-4 text-center text-zinc-800 dark:text-zinc-100">{children}</span>
                    <button
                      type="button"
                      onClick={() => setChildren(children + 1)}
                      className="w-8 h-8 rounded-full border border-zinc-200 dark:border-zinc-700 hover:border-cyan-500 hover:text-cyan-500 flex items-center justify-center transition-colors cursor-pointer"
                    >
                      <Plus className="w-4.5 h-4.5" />
                    </button>
                  </div>
                </div>

              </div>
            )}
          </div>

          {/* 4. Nút Tìm kiếm */}
          <div className="md:col-span-1 flex justify-end">
            <Button
              type="submit"
              className="w-full md:w-12 md:h-12 lg:w-14 lg:h-14 rounded-2xl md:rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white border-0 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 flex items-center justify-center gap-2 md:gap-0 cursor-pointer"
            >
              <Search className="w-5 h-5" />
              <span className="md:hidden font-medium text-sm">Tìm kiếm</span>
            </Button>
          </div>

        </div>
      </form>
    </div>
  );
}
