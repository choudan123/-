import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import { bootstrapAuth } from './services/auth';
import Profile from './pages/Profile';
import Home from './pages/Home';
import CustomPosterGenerator from './pages/CustomPosterGenerator';
import PosterHistory from './pages/PosterHistory';

function Guard({ children }) {
  const [ready, setReady] = useState(false);
  const [authed, setAuthed] = useState(false);
  const location = useLocation();

  useEffect(() => {
    (async () => {
      const ok = await bootstrapAuth();
      setAuthed(ok);
      setReady(true);
    })();
  }, []);

  if (!ready) return <div style={{ color: '#999', padding: 24 }}>正在初始化...</div>;

  // 仅放行注册与登录页，其他都需要已登录
  const path = location.pathname;
  const publicPaths = ['/login', '/register'];
  const isPublic = publicPaths.includes(path);

  return (
    <>
      {/* 仅在已登录的受保护路由显示导航栏 */}
      {!isPublic && authed && <Navbar />}
      {isPublic ? children : authed ? children : <Navigate to="/login" replace />}
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Guard>
        <Routes>
          {/* 登录 / 注册（公共路由） */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* 受保护路由 */}
          <Route path="/poster/history" element={<PosterHistory />} />
          <Route path="/poster/custom" element={<CustomPosterGenerator />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/" element={<Home />} />

          {/* 兜底 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Guard>
    </BrowserRouter>
  );
}