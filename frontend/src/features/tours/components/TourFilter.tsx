"use client";

import React from "react";
import { Compass, Waves, Mountain, Hotel, Landmark, Plane } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CategoryItem {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
}

const categories: CategoryItem[] = [
  { id: "all", name: "Tất cả", icon: Compass },
  { id: "beach", name: "Biển đảo", icon: Waves },
  { id: "mountain", name: "Núi rừng", icon: Mountain },
  { id: "resort", name: "Nghỉ dưỡng", icon: Hotel },
  { id: "culture", name: "Văn hóa", icon: Landmark },
  // { id: "international", name: "Quốc tế", icon: Plane },
];

interface TourFilterProps {
  activeCategory: string;
  onCategoryChange: (category: string) => void;
}

export default function TourFilter({ activeCategory, onCategoryChange }: TourFilterProps) {
  return (
    <div className="w-full overflow-x-auto pb-4 scrollbar-none">
      <div className="flex space-x-3 md:justify-center min-w-max px-4">
        {categories.map((cat) => {
          const Icon = cat.icon;
          const isActive = activeCategory === cat.id;

          return (
            <button
              key={cat.id}
              onClick={() => onCategoryChange(cat.id)}
              className={cn(
                "flex items-center gap-2 px-5 py-3 rounded-full text-sm font-medium transition-all duration-300 border cursor-pointer",
                isActive
                  ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white border-transparent shadow-md shadow-cyan-500/10 scale-105"
                  : "bg-white dark:bg-zinc-900 text-zinc-600 dark:text-zinc-300 border-zinc-200 dark:border-zinc-800 hover:border-cyan-400 dark:hover:border-cyan-500 hover:text-cyan-500 dark:hover:text-cyan-400"
              )}
            >
              <Icon className="w-4 h-4" />
              <span>{cat.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
