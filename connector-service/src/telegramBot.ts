import TelegramBot from 'node-telegram-bot-api';
import { config } from './config.js';
import { processMessage } from './botService.js';

export class TelegramBotHandler {
  private bot: TelegramBot;

  constructor() {
    this.bot = new TelegramBot(config.telegram.botToken, { polling: true });
    this.setupHandlers();
  }

  private setupHandlers(): void {
    // Handle any text message
    this.bot.on('message', async (msg) => {
      // Only process text messages
      if (!msg.text) {
        return;
      }

      const chatId = msg.chat.id;
      const telegramId = msg.from?.id.toString() || 'unknown';
      const username = msg.from?.username || msg.from?.first_name || 'Unknown';
      const messageText = msg.text;

      console.log(`\n[MESSAGE] Received from ${username} (${telegramId})`);
      console.log(`[MESSAGE] Content: "${messageText}"`);

      try {
        // Send to Bot Service for processing
        const result = await processMessage(telegramId, username, messageText);

        // Handle successful expense addition
        if (result.success && result.message) {
          await this.bot.sendMessage(chatId, result.message);
          console.log(`[SUCCESS] Sent response to ${username}: ${result.message}`);
          return;
        }

        if (result.message === 'User not authorized') {
          console.log(`[UNAUTHORIZED] User ${username} (${telegramId}) is not whitelisted - ignoring silently`);
        } else if (result.message) {
          await this.bot.sendMessage(chatId, result.message);
          console.log(`[NOT_EXPENSE] Message from ${username} not recognized as expense: "${messageText}" - sent help message`);
        } else {
          // Other unexpected cases - log but don't respond
          console.log(`[INFO] Message from ${username} not processed: ${result.message}`);
        }
      } catch (error) {
        console.error(`[ERROR] Error processing message from ${username}:`, error);
        
        // Don't send error messages to user, just log them
        // This maintains the "silent ignore" behavior for unauthorized/invalid messages
      }
    });

    // Handle polling errors
    this.bot.on('polling_error', (error) => {
      console.error('[POLLING_ERROR]', error.message);
    });

    console.log('[TELEGRAM_BOT] Bot is running and listening for messages...');
    console.log('[TELEGRAM_BOT] Waiting for incoming messages...\n');
  }

  public async sendMessage(chatId: number, text: string): Promise<void> {
    try {
      await this.bot.sendMessage(chatId, text);
    } catch (error) {
      console.error('[ERROR] Error sending message:', error);
      throw error;
    }
  }

  public stop(): void {
    this.bot.stopPolling();
    console.log('[TELEGRAM_BOT] Bot stopped');
  }
}

