/**
 * Message request sent to Bot Service
 */
export interface MessageRequest {
  telegram_id: string;
  username: string | null;
  message: string;
}

/**
 * Response from Bot Service
 */
export interface MessageResponse {
  success: boolean;
  message: string;
}

