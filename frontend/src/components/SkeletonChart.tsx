"use client"
import React from 'react'

const SkeletonChart: React.FC<{ height?: number }> = ({ height = 300 }) => (
  <div className="bg-white dark:bg-gray-800 p-4 rounded shadow w-full">
    <div className="skeleton w-full rounded" style={{ height }} />
  </div>
)

export default SkeletonChart
