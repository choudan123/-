// 轻量 JWT 启动自检 + 自动续期工具（无第三方依赖）

// base64url 解码并解析 JWT payload
export function decodeJwt(token) {
  try {
    const payload = token.split('.')[1];
    const base = payload.replace(/-/g, '+').replace(/_/g, '/');
    const json = decodeURIComponent(
      atob(base)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function getTokens() {
  return {
    access: localStorage.getItem('access_token') || null,
    refresh: localStorage.getItem('refresh_token') || null,
  };
}
export function setTokens({ access, refresh }) {
  if (access) localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
}
export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export function isAccessValid(access, skewSeconds = 30) {
  if (!access) return false;
  const payload = decodeJwt(access);
  if (!payload?.exp) return false;
  const now = Math.floor(Date.now() / 1000);
  return payload.exp - now > skewSeconds;
}

let refreshTimer = null;
export function cancelScheduledRefresh() {
  if (refreshTimer) {
    clearTimeout(refreshTimer);
    refreshTimer = null;
  }
}

// 根据 access 的 exp 计划一次静默刷新（提前 marginSeconds 执行）
export function scheduleAutoRefresh(fetchNewAccess, marginSeconds = 120) {
  cancelScheduledRefresh();
  const { access } = getTokens();
  const payload = access ? decodeJwt(access) : null;
  if (!payload?.exp) return;

  const nowMs = Date.now();
  const dueMs = payload.exp * 1000 - marginSeconds * 1000;
  const delay = Math.max(1000, dueMs - nowMs); // 最少1秒后触发，避免负数

  refreshTimer = setTimeout(async () => {
    try {
      await fetchNewAccess(); // 成功后会重新 schedule
    } catch {
      // 刷新失败不在这里跳转，让全局拦截器/调用方处理
    }
  }, delay);
}

// 尝试用 refresh 刷新 access（独立于 axios 实例，避免拦截器循环）
export async function refreshAccessDirect() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) throw new Error('no-refresh-token');

  const resp = await fetch('/api/users/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
    credentials: 'same-origin',
  });
  if (!resp.ok) throw new Error('refresh-failed');
  const data = await resp.json();
  if (!data?.access) throw new Error('no-access');

  // 兼容可能的 refresh 轮换
  if (data?.refresh) {
    setTokens({ access: data.access, refresh: data.refresh });
  } else {
    setTokens({ access: data.access });
  }

  // 刷新成功后，继续计划下一次静默刷新
  scheduleAutoRefresh(refreshAccessDirect);
  return data.access;
}

// 启动自检：返回 true 表示已就绪且处于登录态；false 表示需要登录
export async function bootstrapAuth() {
  const { access, refresh } = getTokens();

  if (access && isAccessValid(access)) {
    // access 仍有效，计划静默刷新
    scheduleAutoRefresh(refreshAccessDirect);
    return true;
  }
  if (refresh) {
    try {
      await refreshAccessDirect();
      return true;
    } catch {
      clearTokens();
      cancelScheduledRefresh();
      return false;
    }
  }
  return false;
}

// 新增：登出（清理令牌并取消自动刷新）
export function logout() {
  cancelScheduledRefresh();
  clearTokens();
}