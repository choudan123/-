import api from './api';

// 基础尺寸
export async function getPosterBaseConfig() {
  const { data } = await api.get('/poster/config/');
  return data;
}


// 新的专用上传接口
export async function uploadPosterImage(file) {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/poster/upload-image/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data; // { image_url }
}

// 关键修改：组图延长超时（默认 120s），单图也适当放宽
export async function generatePoster(payload) {
  const isGroup = payload?.sequential_image_generation === 'auto' || payload?.generation_mode === 'group';
  const timeout = isGroup ? 120000 : 45000; // 组图 120s，单图 45s
  const { data } = await api.post('/poster/generate/', payload, { timeout });
  return data;
}

export async function getPosterHistory() {
  const { data } = await api.get('/poster/history/');
  return data;
}

export async function getPosterUsage() {
  const { data } = await api.get('/poster/usage/');
  return data; // { is_member, free_remaining }
}