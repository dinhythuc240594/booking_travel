import React from "react";
import DetailTour from "@/features/tours/components/DetailTour";

interface TourDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function TourDetailPage({ params }: TourDetailPageProps) {
  // Giải nén slug bất đồng bộ theo tiêu chuẩn Next.js 16
  const { slug } = await params;

  return <DetailTour slug={slug} />;
}
