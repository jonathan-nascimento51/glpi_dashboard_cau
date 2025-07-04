"use client"
import React from 'react'

const SkeletonHeatmap: React.FC<{ height?: number }> = ({ height = 200 }) => (
  <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
    <div className="skeleton w-full rounded" style={{ height }} />
  </div>
)

export default SkeletonHeatmap
