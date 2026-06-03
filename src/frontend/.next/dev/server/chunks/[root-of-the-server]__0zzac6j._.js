module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/@opentelemetry/api [external] (next/dist/compiled/@opentelemetry/api, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/@opentelemetry/api", () => require("next/dist/compiled/@opentelemetry/api"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[project]/src/app/api/locations/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "GET",
    ()=>GET
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/server.js [app-route] (ecmascript)");
;
const locations = {
    domestic: [
        {
            name: "Sa Pa, Lào Cai",
            searchKey: "Sa Pa"
        },
        {
            name: "Vịnh Hạ Long, Quảng Ninh",
            searchKey: "Hạ Long"
        },
        {
            name: "Đảo Phú Quốc, Kiên Giang",
            searchKey: "Phú Quốc"
        },
        {
            name: "Hội An, Quảng Nam",
            searchKey: "Hội An"
        },
        {
            name: "Đồng Văn, Hà Giang",
            searchKey: "Hà Giang"
        },
        {
            name: "Đà Lạt, Lâm Đồng",
            searchKey: "Đà Lạt"
        },
        {
            name: "Nha Trang, Khánh Hòa",
            searchKey: "Nha Trang"
        }
    ],
    international: [
        {
            name: "Bangkok - Pattaya, Thái Lan",
            searchKey: "Thái Lan"
        },
        {
            name: "Tokyo - Kyoto, Nhật Bản",
            searchKey: "Nhật Bản"
        },
        {
            name: "Seoul - Đảo Jeju, Hàn Quốc",
            searchKey: "Hàn Quốc"
        },
        {
            name: "Singapore Marina Bay, Singapore",
            searchKey: "Singapore"
        },
        {
            name: "Bali, Indonesia",
            searchKey: "Bali"
        },
        {
            name: "Paris, Pháp",
            searchKey: "Pháp"
        }
    ]
};
async function GET(request) {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get("type") || "domestic";
    if (type === "international") {
        return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(locations.international);
    }
    return __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json(locations.domestic);
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__0zzac6j._.js.map