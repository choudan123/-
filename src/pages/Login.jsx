import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../services/userAPI';
import './auth.css';
import { scheduleAutoRefresh, refreshAccessDirect } from '../services/auth';

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');
  const [success, setSuccess] = useState('');

  const onChange = (e) => {
    setForm((s) => ({ ...s, [e.target.name]: e.target.value }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await login(form);
      console.log('登录成功:', result); // 调试用

      scheduleAutoRefresh(refreshAccessDirect);
      setSuccess('登录成功！即将跳转...');
      setTimeout(() => navigate('/'), 1000);

    } catch (error) {
      console.error('登录错误:', error); // 调试用 - 查看完整错误对象

      // 更详细的错误处理
      let errorMessage = '登录失败，请检查用户名或密码';

      if (error?.response?.status === 401) {
        errorMessage = '用户名或密码错误';
      } else if (error?.response?.status === 400) {
        errorMessage = error?.response?.data?.detail ||
                     error?.response?.data?.message ||
                     '请求参数错误';
      } else if (error?.response?.data) {
        // 处理可能的字段级错误
        const data = error.response.data;
        if (typeof data === 'object') {
          // 如果是对象，提取所有错误信息
          const errors = Object.values(data).flat().join('；');
          errorMessage = errors || errorMessage;
        } else if (data.detail || data.message) {
          errorMessage = data.detail || data.message;
        }
      } else if (error?.message) {
        errorMessage = error.message;
      }

      console.log('显示错误信息:', errorMessage); // 调试用
      setErr(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={onSubmit}>
        <h2 className="auth-title">登录</h2>

        {err && (
          <div className="auth-error">
            {err}
          </div>
        )}
        {success && (
          <div className="auth-ok">
            {success}
          </div>
        )}

        <label className="auth-label">用户名</label>
        <input
          className="auth-input"
          name="username"
          placeholder="请输入用户名"
          value={form.username}
          onChange={onChange}
          autoComplete="username"
          required
        />

        <label className="auth-label">密码</label>
        <input
          className="auth-input"
          type="password"
          name="password"
          placeholder="请输入密码"
          value={form.password}
          onChange={onChange}
          autoComplete="current-password"
          required
        />

        <button className="auth-button" type="submit" disabled={loading}>
          {loading ? '登录中...' : '登录'}
        </button>

        <div className="auth-foot">
          还没有账号？<Link to="/register">去注册</Link>
        </div>
      </form>
    </div>
  );
}