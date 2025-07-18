"use client";
import { jsx as _jsx } from "react/jsx-runtime";
const SkeletonChart = ({ heightClass = 'h-[300px]', }) => (_jsx("div", { className: "bg-white dark:bg-gray-800 p-4 rounded shadow w-full", children: _jsx("div", { className: `skeleton w-full rounded ${heightClass}` }) }));
export default SkeletonChart;
