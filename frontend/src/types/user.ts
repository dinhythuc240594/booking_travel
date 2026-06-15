import { UserRole } from "@/constants/enums";

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatarUrl?: string;
  phoneNumber?: string;
  createdAt: string;
  updatedAt: string;
  address?: string;
  dateOfBirth?: string;
  gender?: "male" | "female" | "other";
}

// export interface UserProfile extends User {
//   address?: string;
//   dateOfBirth?: string;
//   gender?: "male" | "female" | "other";
// }
