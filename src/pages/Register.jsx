import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../services/userAPI';
import './auth.css';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: '',
    nickname: '',
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState('');
  const [ok, setOk] = useState('');

  const onChange = (e) => {
    setForm((s) => ({ ...s, [e.target.name]: e.target.value }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr('');
    setOk('');
    if ((form.password || '').length < 8) {
      setErr('密码长度至少为8位');
      return;
    }
    try {
      setLoading(true);
      await register(form);
      setOk('注册成功！即将跳转登录页...');
      // 1.5秒后跳转登录
      setTimeout(() => navigate('/login'), 1500);
    } catch (error) {
      const data = error?.response?.data;
      // 尝试拼接后端返回的字段级错误
      const msg =
        data?.detail ||
        data?.message ||
        Object.values(data || {}).flat().join('；') ||
        '注册失败，请检查填写内容';
      setErr(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={onSubmit}>
        <h2 className="auth-title">注册</h2>

        {err && <div className="auth-error">{err}</div>}
        {ok && <div className="auth-ok">{ok}</div>}

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

        <label className="auth-label">昵称</label>
        <input
          className="auth-input"
          name="nickname"
          placeholder="请输入昵称"
          value={form.nickname}
          onChange={onChange}
          required
        />

        <label className="auth-label">邮箱</label>
        <input
          className="auth-input"
          name="email"
          type="email"
          placeholder="请输入邮箱"
          value={form.email}
          onChange={onChange}
          autoComplete="email"
          required
        />

        <label className="auth-label">密码（至少8位）</label>
        <input
          className="auth-input"
          type="password"
          name="password"
          placeholder="请输入密码"
          value={form.password}
          onChange={onChange}
          autoComplete="new-password"
          required
        />

        <button className="auth-button" type="submit" disabled={loading}>
          {loading ? '注册中...' : '注册'}
        </button>

        <div className="auth-foot">
          已有账号？<Link to="/login">去登录</Link>
        </div>
      </form>
    </div>
  );
}