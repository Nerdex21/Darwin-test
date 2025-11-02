import { TelegramBotHandler } from './telegramBot.js';
import { checkBotServiceHealth } from './botService.js';

async function main() {
  console.log('[STARTUP] Starting Expense Tracker Connector Service...\n');

  // Check if Bot Service is available
  console.log('[STARTUP] Checking Bot Service health...');
  const isHealthy = await checkBotServiceHealth();
  
  if (!isHealthy) {
    console.warn('[WARNING] Bot Service is not responding');
    console.warn('[WARNING] The connector will start anyway, but messages may fail\n');
  }

  // Start Telegram bot
  console.log('[STARTUP] Initializing Telegram bot...\n');
  const bot = new TelegramBotHandler();

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n\n[SHUTDOWN] Shutting down gracefully...');
    bot.stop();
    process.exit(0);
  });

  process.on('SIGTERM', () => {
    console.log('\n\n[SHUTDOWN] Shutting down gracefully...');
    bot.stop();
    process.exit(0);
  });
}

// Start the service
main().catch((error) => {
  console.error('[FATAL] Fatal error starting service:', error);
  process.exit(1);
});

