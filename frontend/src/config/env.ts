export const env = {
  api: {
    url: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    version: process.env.NEXT_PUBLIC_API_VERSION || 'v1',
  },
  isDevelopment: process.env.NODE_ENV === 'development',
} as const;

// Type-safe environment variables
export type Env = typeof env;

// Validate required environment variables
const requiredEnvVars = ['NEXT_PUBLIC_API_URL'] as const;

requiredEnvVars.forEach((envVar) => {
  if (!process.env[envVar]) {
    console.warn(`Warning: Missing environment variable: ${envVar}. Using default value.`);
  }
}); 