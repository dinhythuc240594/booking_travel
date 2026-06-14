"use client";

import React, { useState } from "react";
import { ChevronLeft, ChevronRight, X, ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface TourGalleryProps {
  images: string[];
  title: string;
}

const fallbackImages = [
  "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&auto=format&fit=crop&q=80",
  "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800&auto=format&fit=crop&q=80",
  "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80",
  "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&auto=format&fit=crop&q=80",
];

export default function TourGallery({ images, title }: TourGalleryProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Đảm bảo có đủ 5 ảnh để tạo grid Airbnb đẹp mắt bằng cách bù ảnh phong cảnh fallback
  const rawImages = [...images];
  let fallbackIdx = 0;
  while (rawImages.length < 5) {
    rawImages.push(fallbackImages[fallbackIdx % fallbackImages.length]);
    fallbackIdx++;
  }

  const displayImages = rawImages.map(img => {
    if (!img) return "";
    if (img.startsWith("http")) return img;
    return (process.env.NEXT_PUBLIC_BASE_URL || "") + (img.startsWith("/") ? img : "/" + img);
  });

  const openLightbox = (index: number) => {
    setCurrentIndex(index);
    setIsOpen(true);
  };

  const closeLightbox = () => {
    setIsOpen(false);
  };

  const prevImage = () => {
    setCurrentIndex((prev) => (prev === 0 ? displayImages.length - 1 : prev - 1));
  };

  const nextImage = () => {
    setCurrentIndex((prev) => (prev === displayImages.length - 1 ? 0 : prev + 1));
  };

  return (
    <div className="relative font-sans select-none">
      {/* LƯỚI ẢNH AIRBNB-STYLE */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-2 md:gap-3 rounded-3xl overflow-hidden aspect-[2/1] min-h-[300px] md:min-h-[400px]">
        {/* Ảnh lớn bên trái */}
        <div
          onClick={() => openLightbox(0)}
          className="md:col-span-2 md:row-span-2 relative cursor-pointer overflow-hidden group bg-zinc-100 dark:bg-zinc-800"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={displayImages[0]}
            alt={`${title} - 1`}
            className="w-full h-full object-cover group-hover:scale-103 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>

        {/* 4 ảnh nhỏ bên phải */}
        {displayImages.slice(1, 5).map((img, i) => (
          <div
            key={i}
            onClick={() => openLightbox(i + 1)}
            className="hidden md:block relative cursor-pointer overflow-hidden group bg-zinc-100 dark:bg-zinc-800"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={img}
              alt={`${title} - ${i + 2}`}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
            <div className="absolute inset-0 bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        ))}

        {/* Nút Xem tất cả ảnh */}
        <button
          onClick={() => openLightbox(0)}
          className="absolute bottom-4 right-4 flex items-center gap-2 px-4 py-2.5 bg-white/90 dark:bg-zinc-900/90 hover:bg-white dark:hover:bg-zinc-900 text-zinc-800 dark:text-zinc-100 rounded-xl shadow-md border border-zinc-200/50 dark:border-zinc-800/50 text-xs font-bold transition-all hover:scale-102 cursor-pointer"
        >
          <ImageIcon className="w-4 h-4 text-cyan-500" />
          Xem tất cả hình ảnh
        </button>
      </div>

      {/* LIGHTBOX MODAL */}
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-black/95 backdrop-blur-md flex items-center justify-center animate-fade-in">
          {/* Nút đóng */}
          <button
            onClick={closeLightbox}
            className="absolute top-6 right-6 p-2 text-zinc-400 hover:text-white bg-white/10 hover:bg-white/20 rounded-full transition-colors cursor-pointer"
            aria-label="Đóng"
          >
            <X className="w-6 h-6" />
          </button>

          {/* Số thứ tự ảnh */}
          <div className="absolute top-6 left-6 text-sm font-semibold text-zinc-400">
            {currentIndex + 1} / {displayImages.length}
          </div>

          {/* Mũi tên Trái */}
          <button
            onClick={prevImage}
            className="absolute left-6 p-3 text-zinc-300 hover:text-white bg-white/5 hover:bg-white/10 rounded-full transition-colors cursor-pointer hidden sm:block"
            aria-label="Ảnh trước"
          >
            <ChevronLeft className="w-8 h-8" />
          </button>

          {/* Ảnh lớn ở giữa */}
          <div className="max-w-[90%] max-h-[80%] flex items-center justify-center relative">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={displayImages[currentIndex]}
              alt={`${title} - Full`}
              className="max-w-full max-h-[75vh] object-contain rounded-lg shadow-2xl animate-scale-up"
            />
          </div>

          {/* Mũi tên Phải */}
          <button
            onClick={nextImage}
            className="absolute right-6 p-3 text-zinc-300 hover:text-white bg-white/5 hover:bg-white/10 rounded-full transition-colors cursor-pointer hidden sm:block"
            aria-label="Ảnh sau"
          >
            <ChevronRight className="w-8 h-8" />
          </button>

          {/* Carousel thumbnails ở dưới cùng */}
          <div className="absolute bottom-6 left-0 right-0 flex justify-center space-x-2 px-4 max-w-xl mx-auto">
            {displayImages.map((img, idx) => (
              <div
                key={idx}
                onClick={() => setCurrentIndex(idx)}
                className={cn(
                  "w-16 h-10 rounded-lg overflow-hidden cursor-pointer border-2 transition-all flex-shrink-0 bg-zinc-800",
                  idx === currentIndex ? "border-cyan-500 scale-105" : "border-transparent opacity-50 hover:opacity-80"
                )}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={img} alt="Thumbnail" className="w-full h-full object-cover" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
