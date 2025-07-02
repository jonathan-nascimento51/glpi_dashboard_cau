/* eslint-disable @typescript-eslint/no-require-imports */
const bundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack(config) {
    config.performance = {
      ...config.performance,
      maxAssetSize: 250 * 1024,
      hints: 'error',
    }
    return config
  },
}

module.exports = bundleAnalyzer(nextConfig)
