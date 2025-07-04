/* eslint-disable @typescript-eslint/no-require-imports */
const bundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true,
  },
  experimental: {
    modularizeImports: {
      '@mui/icons-material': { transform: '@mui/icons-material/{{member}}' },
    },
  },
  webpack(config) {
    config.performance = {
      ...config.performance,
      maxAssetSize: 250 * 1024,
      hints: 'warning', // <-- troque 'error' por 'warning'
    }
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        ...(config.optimization?.splitChunks ?? {}),
        cacheGroups: {
          ...(config.optimization?.splitChunks?.cacheGroups ?? {}),
          visualization: {
            test: /[\\/]node_modules[\\/](chart\.js|recharts|react-calendar-heatmap)[\\/]/,
            name: 'visualization',
            chunks: 'all',
            priority: 20,
          },
        },
      },
    }
    return config
  },
}

module.exports = bundleAnalyzer(nextConfig)
