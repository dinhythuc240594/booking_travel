"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth.store";
import Header from "@/components/common/Header";
import Footer from "@/components/common/Footer";
import { Loader2 } from "lucide-react";

export default function UserLayout({ children }: { children: React.ReactNode }) {
  const [isMounted, setIsMounted] = useState(false);
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (isMounted && (!isAuthenticated || !user)) {
      const redirectUrl = encodeURIComponent(window.location.pathname + window.location.search);
      router.push(`/login?redirect=${redirectUrl}`);
    }
  }, [isMounted, isAuthenticated, user, router]);

  if (!isMounted) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
        <Header />
        <main className="flex-grow flex items-center justify-center pt-24 pb-16">
          <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
        </main>
        <Footer />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black text-zinc-900 dark:text-zinc-50 flex flex-col font-sans">
        <Header />
        <main className="flex-grow flex items-center justify-center pt-24 pb-16">
          <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
        </main>
        <Footer />
      </div>
    );
  }

  return <>{children}</>;
}
