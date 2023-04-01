/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "export",
  images: {
    // Necessary for static export.
    unoptimized: true,
  }
}

module.exports = nextConfig
