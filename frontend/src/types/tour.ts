export interface ItineraryDay {
  day: number;
  title: string;
  activities: string[];
}

export interface Tour {
  id?: string;
  tour_id: string;
  title: string;
  slug: string;
  description: string;
  price: number;
  discountPrice?: number;
  price_per_child?: number;
  duration: string; // Ví dụ: "3 ngày 2 đêm", "4 ngày 3 đêm"
  location: string; // Địa điểm: "Sapa, Lào Cai"
  featuredImage: string; // URL ảnh đại diện nổi bật
  images: string[]; // Danh sách ảnh chi tiết trong gallery
  rating: number; // Điểm đánh giá trung bình (ví dụ: 4.8)
  reviewsCount: number; // Số lượng đánh giá
  category: string; // Loại hình tour: "beach", "mountain", "culture", "resort", "international"
  maxGroupSize: number; // Số khách tối đa
  startDates: string[]; // Danh sách các ngày khởi hành (ví dụ: ["2026-06-15", "2026-06-20"])
  highlights?: string[]; // Điểm nổi bật trong hành trình
  included?: string[]; // Dịch vụ bao gồm (xe đưa đón, khách sạn,...)
  excluded?: string[]; // Dịch vụ không bao gồm (tip, chi phí cá nhân,...)
  itinerary?: ItineraryDay[];
  location_name?: string;
  country?: string;
  className?: string;
  image_url?: string;
  name?: string;
  toursCount?: number;
}

export interface TourFilterOptions {
  searchQuery?: string;
  location?: string;
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  duration?: string;
}
