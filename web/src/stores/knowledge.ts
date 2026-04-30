import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { knowledgeApi, type KnowledgeBase, type Document } from '@/api/knowledge'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const knowledgeBases = ref<KnowledgeBase[]>([])
  const currentKnowledgeBase = ref<KnowledgeBase | null>(null)
  const documents = ref<Document[]>([])
  const loading = ref(false)

  const totalDocuments = computed(() => {
    return knowledgeBases.value.reduce((sum, kb) => sum + kb.document_count, 0)
  })

  // 知识库操作
  async function fetchKnowledgeBases() {
    loading.value = true
    try {
      const response = await knowledgeApi.getKnowledgeBases()
      knowledgeBases.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function createKnowledgeBase(name: string, description?: string) {
    const response = await knowledgeApi.createKnowledgeBase({ name, description })
    const newKB = response.data
    knowledgeBases.value.push(newKB)
    return newKB
  }

  async function updateKnowledgeBase(id: number, data: { name?: string; description?: string }) {
    const response = await knowledgeApi.updateKnowledgeBase(id, data)
    const index = knowledgeBases.value.findIndex(kb => kb.id === id)
    if (index !== -1) {
      knowledgeBases.value[index] = response.data
    }
    return response.data
  }

  async function deleteKnowledgeBase(id: number) {
    await knowledgeApi.deleteKnowledgeBase(id)
    knowledgeBases.value = knowledgeBases.value.filter(kb => kb.id !== id)
  }

  // 文档操作
  async function fetchDocuments(knowledgeBaseId: number) {
    loading.value = true
    try {
      const response = await knowledgeApi.getDocuments(knowledgeBaseId)
      documents.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function uploadDocument(knowledgeBaseId: number, file: File) {
    const response = await knowledgeApi.uploadDocument(knowledgeBaseId, file)
    const newDoc = response.data
    documents.value.push(newDoc)
    // 更新知识库文档计数
    const kb = knowledgeBases.value.find(k => k.id === knowledgeBaseId)
    if (kb) {
      kb.document_count++
    }
    return newDoc
  }

  async function deleteDocument(knowledgeBaseId: number, documentId: number) {
    await knowledgeApi.deleteDocument(knowledgeBaseId, documentId)
    documents.value = documents.value.filter(d => d.id !== documentId)
    // 更新知识库文档计数
    const kb = knowledgeBases.value.find(k => k.id === knowledgeBaseId)
    if (kb) {
      kb.document_count--
    }
  }

  async function fetchAllDocuments() {
    loading.value = true
    try {
      const response = await knowledgeApi.getAllDocuments()
      documents.value = response.data
    } finally {
      loading.value = false
    }
  }

  return {
    knowledgeBases,
    currentKnowledgeBase,
    documents,
    loading,
    totalDocuments,
    fetchKnowledgeBases,
    createKnowledgeBase,
    updateKnowledgeBase,
    deleteKnowledgeBase,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
    fetchAllDocuments,
  }
})
