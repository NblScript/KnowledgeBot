import apiClient from './client'

export interface KnowledgeBase {
  id: number
  name: string
  description: string
  document_count: number
  created_at: string
  updated_at: string
}

export interface CreateKnowledgeBaseRequest {
  name: string
  description?: string
}

export interface UpdateKnowledgeBaseRequest {
  name?: string
  description?: string
}

export interface Document {
  id: number
  knowledge_base_id: number
  filename: string
  file_size: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  chunk_count: number
  created_at: string
}

export const knowledgeApi = {
  // 知识库 CRUD
  getKnowledgeBases() {
    return apiClient.get<KnowledgeBase[]>('/knowledge-bases')
  },

  getKnowledgeBase(id: number) {
    return apiClient.get<KnowledgeBase>(`/knowledge-bases/${id}`)
  },

  createKnowledgeBase(data: CreateKnowledgeBaseRequest) {
    return apiClient.post<KnowledgeBase>('/knowledge-bases', data)
  },

  updateKnowledgeBase(id: number, data: UpdateKnowledgeBaseRequest) {
    return apiClient.put<KnowledgeBase>(`/knowledge-bases/${id}`, data)
  },

  deleteKnowledgeBase(id: number) {
    return apiClient.delete(`/knowledge-bases/${id}`)
  },

  // 文档管理
  getDocuments(knowledgeBaseId: number) {
    return apiClient.get<Document[]>(`/knowledge-bases/${knowledgeBaseId}/documents`)
  },

  uploadDocument(knowledgeBaseId: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post<Document>(
      `/knowledge-bases/${knowledgeBaseId}/documents`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000, // 上传文件超时时间更长
      }
    )
  },

  deleteDocument(knowledgeBaseId: number, documentId: number) {
    return apiClient.delete(`/knowledge-bases/${knowledgeBaseId}/documents/${documentId}`)
  },

  getAllDocuments() {
    return apiClient.get<Document[]>('/documents')
  },
}