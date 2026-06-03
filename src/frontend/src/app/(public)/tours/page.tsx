import { Suspense } from "react";
import ToursListContent from "./tours-list-content";

export default function ToursPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-zinc-50 dark:bg-black flex items-center justify-center font-sans">
          <div className="text-center">
            <div className="w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-zinc-500 dark:text-zinc-400 text-sm font-semibold">
              Đang tải danh sách hành trình...
            </p>
          </div>
        </div>
      }
    >
      <ToursListContent />
    </Suspense>
  );
}
