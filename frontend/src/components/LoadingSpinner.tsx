import React from 'react'

export function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center p-4" role="status">
      <span className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></span>
    </div>
  )
}
