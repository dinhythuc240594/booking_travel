import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { User } from "@/types/user";

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  setLoading: (isLoading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: (user, token) => {
        const normalizedUser = { ...user };
        if (normalizedUser.avatarUrl && !normalizedUser.avatarUrl.startsWith('http')) {
          const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || "";
          normalizedUser.avatarUrl = `${baseUrl}${normalizedUser.avatarUrl.startsWith('/') ? '' : '/'}${normalizedUser.avatarUrl}`;
        }
        set({
          user: normalizedUser,
          token,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      logout: () =>
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        }),

      updateUser: (updatedUser) =>
        set((state) => {
          const normalizedUpdate = { ...updatedUser };
          if (normalizedUpdate.avatarUrl && !normalizedUpdate.avatarUrl.startsWith('http')) {
            const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || "";
            normalizedUpdate.avatarUrl = `${baseUrl}${normalizedUpdate.avatarUrl.startsWith('/') ? '' : '/'}${normalizedUpdate.avatarUrl}`;
          }
          return {
            user: state.user ? { ...state.user, ...normalizedUpdate } : null,
          };
        }),

      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: "auth-storage", // Tên của key trong localStorage
      storage: createJSONStorage(() => localStorage), // Sử dụng localStorage làm nơi lưu trữ
      // Chỉ lưu trữ user và token, không lưu trữ trạng thái isLoading
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

/**
 * Hướng dẫn tránh Hydration Error trong Next.js App Router khi dùng persistent store:
 * 
 * 1. Cách 1: Sử dụng useEffect để đợi client mount xong:
 *    const [isMounted, setIsMounted] = useState(false);
 *    useEffect(() => setIsMounted(true), []);
 *    const user = useAuthStore((state) => state.user);
 *    if (!isMounted) return null; // Hoặc render loading skeleton
 * 
 * 2. Cách 2: Tạo một custom hook bọc để lấy dữ liệu an toàn:
 *    export const useAuth = () => {
 *      const store = useAuthStore();
 *      const [state, setState] = useState<typeof store | null>(null);
 *      useEffect(() => {
 *        setState(store);
 *      }, [store]);
 *      return state;
 *    };
 */
