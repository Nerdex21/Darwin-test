import axios, { AxiosError } from 'axios';
import { config } from './config.js';
import type { MessageRequest, MessageResponse } from './types.js';

/**
 * Send a message to the Bot Service for processing
 */
export async function processMessage(
  telegramId: string,
  username: string | null,
  message: string
): Promise<MessageResponse> {
  try {
    const payload: MessageRequest = {
      telegram_id: telegramId,
      username: username || 'Unknown',
      message: message,
    };

    console.log(`[BOT_SERVICE] Sending to Bot Service: ${message.substring(0, 50)}...`);

    const response = await axios.post<MessageResponse>(
      `${config.botService.url}/process-message`,
      payload,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000, // 30 seconds timeout
      }
    );

    console.log(`[BOT_SERVICE] Response: ${response.data.message}`);
    return response.data;
  } catch (error) {
    if (error instanceof AxiosError) {
      const status = error.response?.status;
      
      // Handle expected HTTP errors
      if (status === 403) {
        console.log(`[BOT_SERVICE] User ${telegramId} not whitelisted (403)`);
        return {
          success: false,
          message: 'User not authorized',
        };
      }
      
      // Unexpected errors
      console.error('[BOT_SERVICE] Error communicating with Bot Service:');
      console.error(`[BOT_SERVICE] Status: ${status}`);
      console.error(`[BOT_SERVICE] Message: ${error.message}`);
      
      if (error.response?.data) {
        console.error('[BOT_SERVICE] Response data:', error.response.data);
      }
    } else {
      console.error('[ERROR] Unexpected error:', error);
    }
    
    throw error;
  }
}

/**
 * Check if Bot Service is healthy
 */
export async function checkBotServiceHealth(): Promise<boolean> {
  try {
    const response = await axios.get(`${config.botService.url}/health`, {
      timeout: 5000,
    });
    
    if (response.status === 200) {
      console.log('[HEALTH] Bot Service is healthy');
      return true;
    }
    
    return false;
  } catch (error) {
    console.error('[HEALTH] Bot Service health check failed');
    return false;
  }
}

