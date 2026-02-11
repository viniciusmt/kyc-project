/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Removido 'output: export' - não funciona com rotas dinâmicas
  images: { unoptimized: true },
  trailingSlash: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
