import { axiosInstance } from "./axios";

/**
 * Hàm fetcher mặc định dùng cho React Query.
 * Tự động gọi phương thức GET tới URL được cung cấp.
 * 
 * @param url Đường dẫn endpoint cần gọi
 * @returns Trả về dữ liệu từ server (response.data)
 */
export const fetcher = async <T>(url: string): Promise<T> => {
  const response = await axiosInstance.get<T>(url);
  return response.data;
};

export default fetcher;
