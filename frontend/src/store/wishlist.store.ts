import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

interface WishlistState {
  wishlistedIds: string[];
  toggleWishlist: (tourId: string) => void;
  setWishlist: (tourIds: string[]) => void;
  clearWishlist: () => void;
}

export const useWishlistStore = create<WishlistState>()(
  persist(
    (set) => ({
      wishlistedIds: [],
      
      toggleWishlist: (tourId) =>
        set((state) => {
          const isExist = state.wishlistedIds.includes(tourId);
          const newIds = isExist
            ? state.wishlistedIds.filter((id) => id !== tourId)
            : [...state.wishlistedIds, tourId];
          return { wishlistedIds: newIds };
        }),

      setWishlist: (tourIds) => set({ wishlistedIds: tourIds }),
      
      clearWishlist: () => set({ wishlistedIds: [] }),
    }),
    {
      name: "wishlist-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);
