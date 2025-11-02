import dotenv from 'dotenv';

dotenv.config();

interface Config {
  telegram: {
    botToken: string;
  };
  botService: {
    url: string;
  };
}

export const config: Config = {
  telegram: {
    botToken: process.env.TELEGRAM_BOT_TOKEN || '',
  },
  botService: {
    url: process.env.BOT_SERVICE_URL || 'http://bot-service:8000',
  },
};

// Validate required configuration
if (!config.telegram.botToken) {
  throw new Error('TELEGRAM_BOT_TOKEN is required in environment variables');
}

console.log('[CONFIG] Configuration loaded successfully');
console.log(`[CONFIG] Bot Service URL: ${config.botService.url}`);

