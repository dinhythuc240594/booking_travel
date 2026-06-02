"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React, { useState } from "react";

export default function QueryProvider({ children }: { children: React.ReactNode }) {
  // Đảm bảo mỗi request trong SSR có một QueryClient riêng biệt, tránh chia sẻ cache giữa các user.
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // Dữ liệu được coi là fresh trong 5 phút
            refetchOnWindowFocus: false, // Tránh gọi API lại khi user tab out/tab in trong môi trường phát triển
            retry: 1, // Thử lại tối đa 1 lần khi request thất bại
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
