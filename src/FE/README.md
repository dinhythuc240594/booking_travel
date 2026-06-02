# ViTravel - Hệ Thống Đặt Tour Du Lịch Thông Minh 🚀

> ViTravel là nền tảng đặt tour du lịch trực tuyến hiện đại, mang đến trải nghiệm tìm kiếm, lựa chọn và đặt tour nhanh chóng, thuận tiện cho người dùng, đồng thời cung cấp hệ thống quản trị (Admin panel) mạnh mẽ cho doanh nghiệp lữ hành.

Dự án được xây dựng dựa trên framework **Next.js** phiên bản mới nhất kết hợp với các thư viện quản lý trạng thái, xử lý biểu mẫu và truy vấn dữ liệu hàng đầu hiện nay.

---

## 🛠️ Công Nghệ Sử Dụng (Tech Stack)

Dự án sử dụng các công nghệ tiên tiến nhất nhằm tối ưu hóa hiệu năng, trải nghiệm người dùng (UX) và tăng tốc độ phát triển (Developer Experience):

*   **Core Framework:** [Next.js 16.2.6 (App Router)](https://nextjs.org/) & [React 19.2.4](https://react.dev/)
*   **Ngôn ngữ lập trình:** [TypeScript 5](https://www.typescriptlang.org/)
*   **Styling (CSS):** [Tailwind CSS v4](https://tailwindcss.com/)
*   **Quản lý trạng thái (State Management):** [Zustand 5.0.14](https://zustand-demo.pmnd.rs/) (Client-side state)
*   **Truy vấn & Đồng bộ dữ liệu (Data Fetching):** [TanStack React Query v5](https://tanstack.com/query/latest) kết hợp với [Axios](https://axios-http.com/)
*   **Xử lý Form & Validation:** [React Hook Form 7.76](https://react-hook-form.com/) & [Zod 4](https://zod.dev/) & [@hookform/resolvers](https://github.com/react-hook-form/resolvers)
*   **UI Components & Icons:** [Radix UI](https://www.radix-ui.com/), [class-variance-authority (CVA)](https://cva.style/), [lucide-react](https://lucide.dev/)

---

## 🏗️ Cấu Trúc Thư Mục Dự Án (Project Structure)

Thư mục nguồn `src` được thiết kế theo hướng **Feature-based Architecture** (tổ chức theo tính năng) kết hợp với **Layered Architecture** (tổ chức theo lớp xử lý) để dự án có khả năng mở rộng tốt và dễ bảo trì:

```text
src/
├── app/                       # 🌐 Next.js App Router (Routing & Pages)
│   ├── (admin)/               # Route Group cho phân hệ Quản trị viên (Dashboard, Tours, Bookings, Customers, Reports)
│   ├── (auth)/                # Route Group cho Xác thực (Login, Register, Forgot Password)
│   ├── (public)/              # Route Group cho trang công khai (Home, Tour List, Tour Detail)
│   ├── (user)/                # Route Group cho người dùng cá nhân (Profile, Bookings, Wishlist, Reviews)
│   ├── api/                   # API Routes (BFF - Backend for Frontend)
│   ├── globals.css            # CSS Toàn cục (Cấu hình Tailwind CSS v4)
│   ├── layout.tsx             # Root layout của ứng dụng
│   └── not-found.tsx          # Trang 404 tùy chỉnh
│
├── components/                # 🧱 Component dùng chung toàn hệ thống
│   ├── common/                # Header, Footer, Loading, Pagination, v.v.
│   └── ui/                    # Base UI components (Button, Input, Dialog, v.v. - cấu hình theo Shadcn UI)
│
├── constants/                 # 📌 Hằng số hệ thống
│   ├── config.ts              # Cấu hình app, env variables
│   ├── enums.ts               # Các định nghĩa Enum (Trạng thái đơn hàng, Vai trò người dùng,...)
│   └── routes.ts              # Quản lý tập trung các liên kết định tuyến (Client routes)
│
├── features/                  # 🧩 Các module tính năng cốt lõi (Feature-based folders)
│   ├── auth/                  # Tính năng Xác thực & Quản lý tài khoản
│   ├── bookings/              # Tính năng Đặt tour & Quản lý đơn hàng
│   ├── payments/              # Tính năng Thanh toán & Tích hợp cổng thanh toán
│   └── tours/                 # Tính năng Tour (Danh sách, Tìm kiếm, Chi tiết, Gallery, Bộ lọc)
│       ├── components/        # UI components dành riêng cho tính năng Tour
│       └── types.ts           # Types nội bộ cho tính năng Tour
│
├── hooks/                     # 🎣 Custom React Hooks dùng chung (useDebounce, usePagination,...)
│
├── lib/                       # 🛠️ Thư viện bổ trợ & Cấu hình Client (Axios Instance, Fetcher, Auth helpers, Helpers)
│
├── mocks/                     # 🧪 Dữ liệu giả lập (Mocking data phục vụ phát triển & test)
│   └── data/                  # Mock dữ liệu thực tế (tours.ts, bookings.ts, users.ts, reviews.ts)
│
├── services/                  # 📡 Các service gọi API bên ngoài (auth.service, api-client, upload.service,...)
│
├── store/                     # 🗄️ Quản lý Global State bằng Zustand (auth.store, booking.store, search.store)
│
└── types/                     # 🏷️ Các định nghĩa TypeScript Type dùng chung toàn dự án
```

---

## ⚡ Bắt Đầu Nhanh (Quick Start)

Làm theo các bước sau để thiết lập môi trường phát triển cục bộ:

### Yêu Cầu Hệ Thống (Prerequisites)
*   [Node.js](https://nodejs.org/) (Khuyến nghị phiên bản LTS mới nhất, Node 20+)
*   [PNPM](https://pnpm.io/) (Trình quản lý package được khuyến nghị sử dụng cho dự án này)

### Các Bước Cài Đặt
1.  **Clone dự án:**
    ```bash
    git clone <repository_url>
    cd vitravel2
    ```

2.  **Cài đặt dependencies:**
    ```bash
    pnpm install
    ```

3.  **Cấu hình biến môi trường:**
    Sao chép tệp `.env.local` (hoặc tạo mới từ file mẫu nếu có) và cấu hình các thông số cần thiết:
    ```bash
    # Ví dụ nội dung .env.local
    NEXT_PUBLIC_API_URL=https://api.vitravel.example.com
    ```

4.  **Chạy server phát triển (Development server):**
    ```bash
    pnpm dev
    ```
    Mở trình duyệt truy cập địa chỉ [http://localhost:3000](http://localhost:3000) để xem ứng dụng.

---

## 🔧 Các Lệnh Có Sẵn (Available Scripts)

| Lệnh | Mô tả |
| :--- | :--- |
| `pnpm dev` | Chạy ứng dụng trong chế độ Development với Hot Reloading. |
| `pnpm build` | Biên dịch ứng dụng Next.js tối ưu cho Production. |
| `pnpm start` | Chạy ứng dụng đã build ở chế độ Production. |
| `pnpm lint` | Quét kiểm tra lỗi cú pháp và định dạng code bằng ESLint. |

---

## 📐 Bộ Quy Tắc Phát Triển Dự Án
Để dự án duy trì được chất lượng code cao, nhất quán và dễ mở rộng, toàn bộ lập trình viên tham gia dự án bắt buộc phải đọc và tuân thủ các quy tắc trong [Bộ Quy Tắc Làm Việc (CODING_RULES.md)](./CODING_RULES.md).
