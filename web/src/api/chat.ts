import apiClient from './client'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  knowledge_base_ids?: number[]
  stream?: boolean
  model?: string
  temperature?: number
  max_tokens?: number
}

export interface ChatResponse {
  id: string
  choices: {
    index: number
    message: ChatMessage
    finish_reason: string
  }[]
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

export interface ChatHistory {
  id: string
  title: string
  messages: ChatMessage[]
  created_at: string
}

export const chatApi = {
  // 发送聊天消息
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/chat/completions', data)
    return response.data
  },

  // 流式聊天（使用 fetch 实现）
  async streamChat(
    data: ChatRequest, 
    onMessage: (text: string) => void,
    token?: string
  ): Promise<void> {
    const response = await fetch('/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ ...data, stream: true }),
    })

    const reader = response.body?.getReader()
    if (!reader) return

    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      const text = decoder.decode(value)
      const lines = text.split('\n').filter(line => line.startsWith('data:'))
      
      for (const line of lines) {
        const data = line.replace('data: ', '')
        if (data === '[DONE]') return
        
        try {
          const json = JSON.parse(data)
          const content = json.choices?.[0]?.delta?.content
          if (content) {
            onMessage(content)
          }
        } catch {
          // 忽略解析错误
        }
      }
    }
  },

  // 获取聊天历史
  getChatHistories() {
    return apiClient.get<ChatHistory[]>('/chat/histories')
  },

  // 获取单个聊天历史
  getChatHistory(id: string) {
    return apiClient.get<ChatHistory>(`/chat/histories/${id}`)
  },

  // 删除聊天历史
  deleteChatHistory(id: string) {
    return apiClient.delete(`/chat/histories/${id}`)
  },
}