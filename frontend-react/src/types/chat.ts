export interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export interface ChatbotResponse {
  answer: string;
  source: string;
  disclaimer?: string;
}