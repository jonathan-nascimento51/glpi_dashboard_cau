import createBundleAnalyzer from '@next/bundle-analyzer'

const withBundleAnalyzer = createBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true,
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

export default withBundleAnalyzer(nextConfig)
