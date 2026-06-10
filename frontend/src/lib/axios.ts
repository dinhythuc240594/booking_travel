import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
// Sẽ import auth store để truy cập token và gọi hàm logout
import { useAuthStore } from "@/store/auth.store";

// Base URL cho API lấy từ biến môi trường hoặc mặc định là endpoint cục bộ
const API_URL = process.env.NEXT_PUBLIC_API_URL || "/api";

export const axiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 15000, // 15 giây timeout
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Request Interceptor: Tự động đính kèm Token xác thực
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Lấy token từ Zustand Auth Store (Zustand cho phép dùng getState() ngoài React Context)
    const token = useAuthStore.getState().token;

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Xử lý lỗi tập trung
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    const status = error.response?.status;
    const errorData = error.response?.data as { message?: string } | undefined;

    // Xử lý lỗi 401 Unauthorized (ví dụ: token hết hạn hoặc không hợp lệ)
    if (status === 401) {
      console.warn("Unauthorized request detected. Logging out...");
      // Gọi hàm logout từ Zustand Auth Store để xóa thông tin phiên đăng nhập
      useAuthStore.getState().logout();
      
      // Nếu đang chạy ở phía trình duyệt, tự động redirect về trang login
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }

    // Trích xuất thông báo lỗi từ server hoặc dùng thông báo mặc định của Axios
    const customErrorMessage = errorData?.message || error.message || "Đã có lỗi xảy ra. Vui lòng thử lại.";
    
    return Promise.reject(new Error(customErrorMessage));
  }
);

export default axiosInstance;
