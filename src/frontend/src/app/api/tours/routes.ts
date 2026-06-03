import { NextResponse } from "next/server";

const tours = [
  {
    id: 1,
    name: "Tour 1",
    price: 100,
    image: "https://images.unsplash.com/photo-1506967730738-5f746541cf9e?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
  },
  {
    id: 2,
    name: "Tour 2",
    price: 200,
    image: "https://images.unsplash.com/photo-1506967730738-5f746541cf9e?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
  },
];

export async function GET() {
  return NextResponse.json(tours);
}
