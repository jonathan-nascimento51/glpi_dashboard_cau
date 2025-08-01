import type { FC } from 'react'

const SkeletonHeatmap: FC<{ heightClass?: string }> = ({
  heightClass = 'h-[200px]',
}) => (
  <div className="bg-surface dark:bg-gray-900 border border-border rounded-2xl shadow-lg p-6 flex flex-col justify-center items-center">
    <div
      className={`skeleton w-full rounded-xl ${heightClass} bg-gray-200 dark:bg-gray-700 animate-pulse`}
    />
  </div>
)

export default SkeletonHeatmap
