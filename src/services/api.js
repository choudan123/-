
import axios from 'axios';
import { refreshAccessDirect, scheduleAutoRefresh, clearTokens } from './auth';

// 统一的 axios 实例，开发环境下建议在 Vite 里配置 /api 代理到 http://localhost:8000
const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
});

// 在每个请求上自动附加 Bearer Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 并发 401 时只触发一次刷新
let refreshingPromise = null;

// 统一处理 401：尝试用 refresh 刷新 access，并重放原请求
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true;

      try {
        if (!refreshingPromise) {
          // 使用 auth.js 的刷新逻辑，避免与拦截器互相影响
          refreshingPromise = refreshAccessDirect()
            .then((newAccess) => {
              // 成功后重新安排静默刷新（refreshAccessDirect 内已安排，这里是冗余保护）
              scheduleAutoRefresh(refreshAccessDirect);
              return newAccess;
            })
            .finally(() => {
              refreshingPromise = null;
            });
        }

        const newAccess = await refreshingPromise;
        // 更新当前重放请求的 Authorization 头
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return api(originalRequest);
      } catch {
        // 刷新失败，清理本地并跳转登录
        clearTokens();
        try {
          // 避免在某些内嵌环境抛异常
          window.location.href = '/login';
        } catch {}
      }
    }

    return Promise.reject(error);
  }
);

export default api;