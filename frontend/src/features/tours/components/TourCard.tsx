"use client";

import React, { useState } from "react";
import Link from "next/link";
import { MapPin, Clock, Users, Star, Heart } from "lucide-react";
import { Tour } from "@/types/tour";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useWishlistStore } from "@/store/wishlist.store";

interface TourCardProps {
  tour: Tour;
}

export default function TourCard({ tour }: TourCardProps) {
  const { wishlistedIds, toggleWishlist } = useWishlistStore();
  const tourIdStr = String(tour.id || tour.tour_id);
  const isWishlisted = wishlistedIds.includes(tourIdStr);

  // Tính phần trăm giảm giá nếu có
  const discountPercent = tour.discountPrice
    ? Math.round(((tour.price - tour.discountPrice) / tour.price) * 100)
    : 0;

  // Định dạng tiền tệ VND
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
    }).format(amount);
  };

  return (
    <div className="group bg-white dark:bg-zinc-900 rounded-3xl overflow-hidden border border-zinc-150/80 dark:border-zinc-800/80 shadow-sm hover:shadow-xl hover:-translate-y-1.5 transition-all duration-300 flex flex-col h-full">
      {/* Banner Ảnh */}
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-zinc-100 dark:bg-zinc-800">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={tour.featuredImage.startsWith("http") ? tour.featuredImage : (process.env.NEXT_PUBLIC_BASE_URL || "") + tour.featuredImage}
          alt={tour.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
          loading="lazy"
        />

        {/* Lớp gradient nhẹ phủ lên dưới cùng của ảnh */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none" />

        {/* Tag giảm giá */}
        {discountPercent > 0 && (
          <div className="absolute top-4 left-4 bg-red-500 text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-md">
            Ưu đãi {discountPercent}%
          </div>
        )}

        {/* Nút yêu thích (Wishlist) */}
        <button style={{ display: "none" }}
          onClick={(e) => {
            e.preventDefault();
            toggleWishlist(tourIdStr);
          }}
          className="absolute top-4 right-4 p-2 bg-white/90 dark:bg-zinc-900/90 hover:bg-white dark:hover:bg-zinc-900 rounded-full shadow-md text-zinc-650 dark:text-zinc-300 hover:text-red-500 dark:hover:text-red-500 transition-all duration-300 cursor-pointer"
        >
          <Heart
            className={cn(
              "w-4 h-4 transition-all duration-300",
              isWishlisted ? "fill-red-500 text-red-500 scale-110" : ""
            )}
          />
        </button>
      </div>

      {/* Chi tiết nội dung */}
      <div className="p-6 flex flex-col flex-1">
        {/* Địa điểm & Đánh giá */}
        <div className="flex justify-between items-center mb-3">
          <div className="flex items-center gap-1 text-xs text-zinc-500 dark:text-zinc-400">
            <MapPin className="w-3.5 h-3.5 text-cyan-500" />
            <span className="truncate max-w-[150px]">{tour.location}</span>
          </div>
          <div style={{ display: "none" }} className="flex items-center gap-1 bg-amber-50 dark:bg-amber-950/20 px-2 py-1 rounded-lg text-xs font-semibold text-amber-600 dark:text-amber-400">
            <Star className="w-3 h-3 fill-amber-500 text-amber-500" />
            <span>{tour.rating}</span>
            <span className="text-zinc-400 font-normal">({tour.reviewsCount})</span>
          </div>
        </div>

        {/* Tiêu đề Tour */}
        <h3 className="font-sans font-bold text-base sm:text-lg text-zinc-900 dark:text-zinc-100 line-clamp-2 mb-3 group-hover:text-cyan-500 transition-colors">
          <Link href={`/tours/${tour.slug}`}>{tour.title}</Link>
        </h3>

        {/* Tiện ích Metadata */}
        <div className="flex items-center gap-4 text-xs text-zinc-500 dark:text-zinc-400 mb-6 border-b border-zinc-100 dark:border-zinc-800/80 pb-4">
          <div className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-zinc-400" />
            <span>{tour.duration}</span>
          </div>
          {/* <div className="flex items-center gap-1">
            <Users className="w-3.5 h-3.5 text-zinc-400" />
            <span>Tối đa {tour.maxGroupSize} người</span>
          </div> */}
        </div>

        {/* Giá & CTA Đặt Tour */}
        <div className="mt-auto flex justify-between items-end">
          <div className="flex flex-col">
            {tour.discountPrice ? (
              <>
                <span className="text-xs text-zinc-400 line-through">
                  {formatCurrency(tour.price)}
                </span>
                <span className="text-base sm:text-lg font-bold text-cyan-500 dark:text-cyan-400">
                  {formatCurrency(tour.discountPrice)}
                </span>
              </>
            ) : (
              <span className="text-base sm:text-lg font-bold text-cyan-500 dark:text-cyan-400">
                {formatCurrency(tour.price)}
              </span>
            )}
            <span className="text-[10px] text-zinc-400 mt-0.5">/ khách</span>
          </div>
          <Link href={`/tours/${tour.slug}`}>
            <Button size="sm" className="rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-medium shadow-sm hover:shadow transition-all text-xs px-4 py-2">
              Khám phá
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
