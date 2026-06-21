"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React, { useState, useEffect } from "react";
import { useAuthStore } from "@/store/auth.store";
import { axiosInstance } from "@/lib/axios";

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

  // Global Session validation and Fetch interceptor
  useEffect(() => {
    if (typeof window === "undefined") return;

    // 1. Setup global fetch interceptor to catch any 401 response
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
      const response = await originalFetch(...args);

      if (response.status === 401) {
        console.warn("Fetch interceptor detected 401 Unauthorized. Logging out...");
        useAuthStore.getState().logout();

        const currentPath = window.location.pathname;
        const isProtectedRoute = currentPath.startsWith("/profile") || 
                                 currentPath.startsWith("/bookings") || 
                                 currentPath.startsWith("/wishlist") || 
                                 currentPath.startsWith("/reviews");
        
        if (isProtectedRoute) {
          const fullPath = window.location.pathname + window.location.search;
          window.location.href = `/login?redirect=${encodeURIComponent(fullPath)}`;
        }
      }

      return response;
    };

    // 2. Perform a check of the session on mount if Zustand state says isAuthenticated is true
    const verifySession = async () => {
      const { isAuthenticated, logout } = useAuthStore.getState();
      if (isAuthenticated) {
        try {
          // Gửi request tới /profile (GET) để kiểm tra session cookie
          const res = await axiosInstance.get("/profile");
          // Nếu backend trả về status = false hoặc code = 401
          if (res.data && res.data.status === false) {
            console.warn("Session invalid on mount. Logging out...");
            logout();
            
            const currentPath = window.location.pathname;
            const isProtectedRoute = currentPath.startsWith("/profile") || 
                                     currentPath.startsWith("/bookings") || 
                                     currentPath.startsWith("/wishlist") || 
                                     currentPath.startsWith("/reviews");
            
            if (isProtectedRoute) {
              const fullPath = window.location.pathname + window.location.search;
              window.location.href = `/login?redirect=${encodeURIComponent(fullPath)}`;
            }
          }
        } catch (error) {
          // Lỗi 401 sẽ tự động được xử lý bởi axiosInstance interceptor hoặc catch tại đây
          console.error("Session verification failed:", error);
        }
      }
    };

    verifySession();

    return () => {
      window.fetch = originalFetch;
    };
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
