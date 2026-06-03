import { User } from "@/types/user";
import { UserRole } from "@/constants/enums";

export interface MockUser extends User {
  password?: string;
}

export const mockUsers: MockUser[] = [
  {
    id: "u-customer",
    email: "customer@vitravel.com",
    name: "Nguyễn Văn Khách",
    role: UserRole.CUSTOMER,
    password: "customer123",
    phoneNumber: "0901234567",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "u-admin",
    email: "admin@vitravel.com",
    name: "Trần Thị Admin",
    role: UserRole.ADMIN,
    password: "admin123",
    phoneNumber: "0907654321",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "u-user",
    email: "user@vitravel.com",
    name: "Phạm Văn Người Dùng",
    role: UserRole.USER,
    password: "user123",
    phoneNumber: "0988888888",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
];
