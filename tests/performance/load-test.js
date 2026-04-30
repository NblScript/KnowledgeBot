import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// 自定义指标
const errorRate = new Rate('errors');
const authLatency = new Trend('auth_latency');
const chatLatency = new Trend('chat_latency');
const embeddingLatency = new Trend('embedding_latency');

// 测试配置
export const options = {
  stages: [
    { duration: '1m', target: 10 },   // 预热
    { duration: '3m', target: 50 },   // 正常负载
    { duration: '2m', target: 100 },  // 高负载
    { duration: '1m', target: 200 },  // 峰值
    { duration: '2m', target: 0 },    // 冷却
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    errors: ['rate<0.05'],
    auth_latency: ['p(95)<200'],
    chat_latency: ['p(95)<2000'],
    embedding_latency: ['p(95)<500'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://staging.knowledgebot.example.com';

// 登录获取 Token
export function setup() {
  const loginRes = http.post(`${BASE_URL}/v1/auth/login`, JSON.stringify({
    email: 'test@example.com',
    password: 'testpassword123',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });

  const token = loginRes.json('data.access_token');
  return { token };
}

// 主测试场景
export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${data.token}`,
  };

  // 场景 1: 获取知识库列表
  const kbStart = new Date();
  const kbRes = http.get(`${BASE_URL}/v1/knowledge-bases`, { headers });
  const kbEnd = new Date();
  
  check(kbRes, {
    'knowledge bases status 200': (r) => r.status === 200,
    'knowledge bases has data': (r) => r.json('success') === true,
  });
  errorRate.add(kbRes.status !== 200);

  sleep(1);

  // 场景 2: 向量检索
  const searchStart = new Date();
  const searchRes = http.post(`${BASE_URL}/v1/embeddings/search`, JSON.stringify({
    knowledge_base_id: 'kb_test_001',
    query: '什么是知识图谱？',
    top_k: 5,
  }), { headers });
  const searchEnd = new Date();
  
  embeddingLatency.add(searchEnd - searchStart);
  check(searchRes, {
    'search status 200': (r) => r.status === 200,
    'search has results': (r) => r.json('data.results') !== undefined,
  });
  errorRate.add(searchRes.status !== 200);

  sleep(2);

  // 场景 3: 对话
  const chatStart = new Date();
  const chatRes = http.post(`${BASE_URL}/v1/chat/completions`, JSON.stringify({
    conversation_id: 'conv_test_001',
    message: '请介绍一下RAG技术',
    knowledge_base_ids: ['kb_test_001'],
    stream: false,
  }), { headers });
  const chatEnd = new Date();
  
  chatLatency.add(chatEnd - chatStart);
  check(chatRes, {
    'chat status 200': (r) => r.status === 200,
    'chat has response': (r) => r.json('data.content') !== undefined,
  });
  errorRate.add(chatRes.status !== 200);

  sleep(3);

  // 场景 4: 上传文档（模拟）
  // 只测试 API 响应，不实际上传文件
  const uploadRes = http.get(`${BASE_URL}/v1/knowledge-bases/kb_test_001/documents`, { headers });
  
  check(uploadRes, {
    'documents list status 200': (r) => r.status === 200,
  });

  sleep(1);
}

// 清理
export function teardown(data) {
  console.log('Performance test completed');
}