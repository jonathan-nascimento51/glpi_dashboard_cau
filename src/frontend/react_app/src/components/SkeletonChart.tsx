import type { FC } from 'react'

const SkeletonChart: FC<{ heightClass?: string }> = ({
  heightClass = 'h-[300px]',
}) => (
  <div className="bg-white dark:bg-gray-800 p-4 rounded shadow w-full">
    <div className={`skeleton w-full rounded ${heightClass}`} />
  </div>
)

export default SkeletonChart
