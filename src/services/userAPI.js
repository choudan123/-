import api from './api';
import { setTokens, scheduleAutoRefresh, refreshAccessDirect } from './auth';

// 登录：后端为 SimpleJWT 的 TokenObtainPairView（/users/login/）
export async function login({ username, password }) {
  const { data } = await api.post('/users/login/', { username, password });
  // 期望返回：{ access, refresh }
  if (data?.access || data?.refresh) {
    setTokens({ access: data.access, refresh: data.refresh });
    // 让后续请求立刻携带新 token（无需等下一次请求触发拦截器）
    if (data?.access) {
      api.defaults.headers.common.Authorization = `Bearer ${data.access}`;
    }
    // 安排静默刷新（即便在页面中重复调用也安全，内部会取消上一次定时器）
    scheduleAutoRefresh(refreshAccessDirect);
  }
  return data;
}

// 注册：后端的 UserRegisterView（/users/register/）
export async function register({ username, password, nickname, email }) {
  const { data } = await api.post('/users/register/', {
    username,
    password,
    nickname,
    email,
  });
  return data; // { message: "注册成功！" }
}

// 获取个人信息
export async function getProfile() {
  const { data } = await api.get('/users/profile/');
  return data; // { username, nickname, email, avatar_url, is_member }
}

// 更新个人信息（昵称/邮箱/头像URL）
export async function updateProfile(patch) {
  const { data } = await api.patch('/users/profile/', patch);
  return data;
}

// 修改密码
export async function changePassword({ old_password, new_password }) {
  const { data } = await api.post('/users/change-password/', { old_password, new_password });
  return data; // { message: "密码修改成功" }
}

// 上传头像（文件）
export async function uploadAvatar(file) {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/users/avatar/upload/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data; // { avatar_url }
}

// ==================== 会员相关 API ====================

// 获取会员套餐列表
export async function getMembershipPlans(featured = false) {
  const params = featured ? { featured: 'true' } : {};
  const { data } = await api.get('/membership/plans/', { params });
  return data;
}

// 获取用户会员信息
export async function getUserMembershipInfo() {
  const { data } = await api.get('/membership/info/');
  return data;
}

// 创建会员订单
export async function createMembershipOrder({ plan_id, payment_method }) {
  const { data } = await api.post('/membership/orders/create/', {
    plan_id,
    payment_method,
  });
  return data;
}

// 获取用户订单列表
export async function getMembershipOrders() {
  const { data } = await api.get('/membership/orders/');
  return data;
}

// 获取订单详情
export async function getMembershipOrderDetail(out_trade_no) {
  const { data } = await api.get(`/membership/orders/${out_trade_no}/`);
  return data;
}