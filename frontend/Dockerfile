# ---------- BUILD STAGE ----------
    FROM node:20-alpine AS builder

    WORKDIR /app
    
    # Accept public runtime environment variables
    ARG NEXT_PUBLIC_API_URL
    ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
    
    # Optional platform settings for edge cases
    ENV npm_config_platform=linux
    ENV npm_config_arch=x64
    
    # Copy package files and install dependencies
    COPY package*.json ./
    RUN npm install
    
    # Workaround for lightningcss (specific to Tailwind + Next.js users)
    RUN npm install lightningcss@latest --platform=linux --arch=x64
    
    # Copy application code
    COPY . .
    
    # Build the frontend (NEXT_PUBLIC_API_URL gets embedded here)
    RUN npm run build
    
    # ---------- RUNTIME STAGE ----------
    FROM node:20-alpine AS runner
    
    WORKDIR /app
    
    # Copy only what's needed to run
    COPY --from=builder /app/package*.json ./
    RUN npm install --omit=dev
    
    COPY --from=builder /app/.next ./.next
    COPY --from=builder /app/public ./public
    COPY --from=builder /app/next.config.js ./
    COPY --from=builder /app/node_modules ./node_modules
    
    ENV NODE_ENV=production
    ENV PORT=3000
    ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
    
    EXPOSE 3000
    
    CMD ["npm", "start"]
    