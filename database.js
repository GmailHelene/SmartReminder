const databaseUrl = process.env.NODE_ENV === 'production' 
  ? process.env.DATABASE_URL  // Railway internal URL
  : process.env.DATABASE_URL_EXTERNAL; // External URL for local dev
