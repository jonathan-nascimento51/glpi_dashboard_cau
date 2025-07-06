"use client"
import React from 'react'

const SkeletonHeatmap: React.FC<{ heightClass?: string }> = ({
  heightClass = 'h-[200px]',
}) => (
  <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
    <div className={`skeleton w-full rounded ${heightClass}`} />
  </div>
)

export default SkeletonHeatmap
