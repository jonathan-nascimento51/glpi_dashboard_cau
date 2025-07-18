"use client";
import { jsx as _jsx } from "react/jsx-runtime";
const SkeletonHeatmap = ({ heightClass = 'h-[200px]', }) => (_jsx("div", { className: "bg-white dark:bg-gray-800 p-4 rounded shadow", children: _jsx("div", { className: `skeleton w-full rounded ${heightClass}` }) }));
export default SkeletonHeatmap;
