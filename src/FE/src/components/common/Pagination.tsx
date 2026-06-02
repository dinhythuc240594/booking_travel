"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  // Logic sinh mảng số trang hiển thị (kèm dấu ba chấm rút gọn)
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const delta = 1; // Số lượng trang hiển thị xung quanh trang hiện tại

    for (let i = 1; i <= totalPages; i++) {
      if (
        i === 1 ||
        i === totalPages ||
        (i >= currentPage - delta && i <= currentPage + delta)
      ) {
        pages.push(i);
      } else if (
        pages[pages.length - 1] !== "..." &&
        (i < currentPage - delta || i > currentPage + delta)
      ) {
        pages.push("...");
      }
    }
    return pages;
  };

  const pages = getPageNumbers();

  return (
    <nav className="flex justify-center items-center space-x-1.5 py-8 select-none font-sans">
      
      {/* Nút Trở về trước */}
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
        className={cn(
          "p-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-300 hover:text-cyan-500 dark:hover:text-cyan-400 hover:border-cyan-400 dark:hover:border-cyan-500 disabled:opacity-40 disabled:hover:text-zinc-600 disabled:hover:border-zinc-200 transition-all duration-300 cursor-pointer disabled:cursor-not-allowed"
        )}
        aria-label="Trang trước"
      >
        <ChevronLeft className="w-4 h-4" />
      </button>

      {/* Số trang */}
      <div className="flex items-center space-x-1">
        {pages.map((page, index) => {
          if (page === "...") {
            return (
              <span
                key={`ellipsis-${index}`}
                className="w-10 h-10 flex items-center justify-center text-zinc-400 text-sm font-semibold select-none"
              >
                ...
              </span>
            );
          }

          const pageNum = page as number;
          const isActive = currentPage === pageNum;

          return (
            <button
              key={`page-${pageNum}`}
              onClick={() => onPageChange(pageNum)}
              className={cn(
                "w-10 h-10 rounded-xl text-sm font-bold transition-all duration-300 border cursor-pointer",
                isActive
                  ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white border-transparent shadow-md shadow-cyan-500/10 scale-105"
                  : "bg-white dark:bg-zinc-900 text-zinc-600 dark:text-zinc-300 border-zinc-200 dark:border-zinc-800 hover:border-cyan-400 dark:hover:border-cyan-500 hover:text-cyan-500 dark:hover:text-cyan-400"
              )}
            >
              {pageNum}
            </button>
          );
        })}
      </div>

      {/* Nút Tiếp theo */}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className={cn(
          "p-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 text-zinc-600 dark:text-zinc-300 hover:text-cyan-500 dark:hover:text-cyan-400 hover:border-cyan-400 dark:hover:border-cyan-500 disabled:opacity-40 disabled:hover:text-zinc-600 disabled:hover:border-zinc-200 transition-all duration-300 cursor-pointer disabled:cursor-not-allowed"
        )}
        aria-label="Trang sau"
      >
        <ChevronRight className="w-4 h-4" />
      </button>

    </nav>
  );
}
