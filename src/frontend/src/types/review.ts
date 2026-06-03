export interface Review {
  id: string;
  tourId: string;
  userName: string;
  avatarUrl?: string;
  rating: number; // Điểm đánh giá (từ 1 đến 5 sao)
  comment: string;
  date: string; // Định dạng YYYY-MM-DD
}
