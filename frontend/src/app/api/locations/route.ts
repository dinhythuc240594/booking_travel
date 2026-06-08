// import { NextResponse } from "next/server";

// const locations = {
//   domestic: [
//     { name: "Sa Pa, Lào Cai", searchKey: "Sa Pa" },
//     { name: "Vịnh Hạ Long, Quảng Ninh", searchKey: "Hạ Long" },
//     { name: "Đảo Phú Quốc, Kiên Giang", searchKey: "Phú Quốc" },
//     { name: "Hội An, Quảng Nam", searchKey: "Hội An" },
//     { name: "Đồng Văn, Hà Giang", searchKey: "Hà Giang" },
//     { name: "Đà Lạt, Lâm Đồng", searchKey: "Đà Lạt" },
//     { name: "Nha Trang, Khánh Hòa", searchKey: "Nha Trang" },
//   ],
//   // international: [
//   //   { name: "Bangkok - Pattaya, Thái Lan", searchKey: "Thái Lan" },
//   //   { name: "Tokyo - Kyoto, Nhật Bản", searchKey: "Nhật Bản" },
//   //   { name: "Seoul - Đảo Jeju, Hàn Quốc", searchKey: "Hàn Quốc" },
//   //   { name: "Singapore Marina Bay, Singapore", searchKey: "Singapore" },
//   //   { name: "Bali, Indonesia", searchKey: "Bali" },
//   //   { name: "Paris, Pháp", searchKey: "Pháp" },
//   // ],
// };

// export async function GET(request: Request) {
//   const { searchParams } = new URL(request.url);
//   const type = searchParams.get("type") || "domestic";

//   if (type === "international") {
//     return NextResponse.json(locations.international);
//   }
//   return NextResponse.json(locations.domestic);
// }
