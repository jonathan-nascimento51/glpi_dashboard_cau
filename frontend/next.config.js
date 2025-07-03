/* eslint-disable @typescript-eslint/no-require-imports */
const bundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack(config) {
    config.performance = {
      ...config.performance,
      maxAssetSize: 250 * 1024,
      hints: 'warning', // <-- troque 'error' por 'warning'
    }
    return config
  },
}

module.exports = bundleAnalyzer(nextConfig)
