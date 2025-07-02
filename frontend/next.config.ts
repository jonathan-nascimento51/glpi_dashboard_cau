import type { NextConfig } from "next";
import bundleAnalyzer from "@next/bundle-analyzer";

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

const nextConfig: NextConfig = {
  webpack(config) {
    config.performance = {
      ...config.performance,
      maxAssetSize: 250 * 1024,
      hints: "error",
    };
    return config;
  },
};

export default withBundleAnalyzer(nextConfig);
