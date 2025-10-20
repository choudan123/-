import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { getProfile } from '../services/userAPI';
import { logout } from '../services/auth';
import '../styles/theme.css';
import './navbar.css';

function generateDefaultAvatar(initial = 'U', size = 40) {
  const first = String(initial).trim().charAt(0) || 'U';
  const display = first.toUpperCase();
  const svg = `
  <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">
    <defs>
      <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#60a5fa"/>
        <stop offset="1" stop-color="#2563eb"/>
      </linearGradient>
      <clipPath id="r"><rect rx="${size/2}" ry="${size/2}" x="0" y="0" width="${size}" height="${size}"/></clipPath>
    </defs>
    <rect width="100%" height="100%" fill="url(#g)" clip-path="url(#r)"/>
    <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle"
      font-family="ui-sans-serif, -apple-system, 'Noto Sans SC', 'Segoe UI', Roboto, Arial"
      font-size="${Math.round(size * 0.5)}" fill="#fff" font-weight="700">${display}</text>
  </svg>`;
  return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
}

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [open, setOpen] = useState(false);
  const [posterMenuOpen, setPosterMenuOpen] = useState(false);
  const wrapRef = useRef(null);
  const posterMenuRef = useRef(null);
  const hoverTimer = useRef(null);
  const posterHoverTimer = useRef(null);

  // 新增：滚动隐藏/显示
  const [hidden, setHidden] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const lastY = useRef(0);

  useEffect(() => {
    (async () => {
      try {
        const data = await getProfile();
        setUser(data);
      } catch {}
    })();
  }, []);

  // 监听滚动方向：下滑隐藏，上滑显示；并在滚动后改变背景（防止文字重叠不可读）
  useEffect(() => {
    lastY.current = window.scrollY || 0;
    const onScroll = () => {
      const y = window.scrollY || 0;
      const diff = y - lastY.current;
      if (Math.abs(diff) > 6) {
        if (y > 56 && diff > 0) setHidden(true);  // 下滑
        if (diff < 0) setHidden(false);           // 上滑
        lastY.current = y;
      }
      setScrolled(y > 2);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // 路由切换时重置可见
  useEffect(() => {
    setHidden(false);
    setScrolled(false);
    lastY.current = window.scrollY || 0;
  }, [location.pathname]);

  useEffect(() => {
    const onDocClick = (e) => {
      if (!wrapRef.current) return;
      if (!wrapRef.current.contains(e.target)) setOpen(false);

      if (!posterMenuRef.current) return;
      if (!posterMenuRef.current.contains(e.target)) setPosterMenuOpen(false);
    };
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setOpen(false);
        setPosterMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', onDocClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDocClick);
      document.removeEventListener('keydown', onKey);
    };
  }, []);

  const onLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const onEnter = () => {
    if (hoverTimer.current) clearTimeout(hoverTimer.current);
    setOpen(true);
  };
  const onLeave = () => {
    if (hoverTimer.current) clearTimeout(hoverTimer.current);
    hoverTimer.current = setTimeout(() => setOpen(false), 120);
  };

  const onPosterEnter = () => {
    if (posterHoverTimer.current) clearTimeout(posterHoverTimer.current);
    setPosterMenuOpen(true);
  };
  const onPosterLeave = () => {
    if (posterHoverTimer.current) clearTimeout(posterHoverTimer.current);
    posterHoverTimer.current = setTimeout(() => setPosterMenuOpen(false), 150);
  };

  const nameLabel = user?.nickname || user?.username || '用户';
  const avatarSrc = generateDefaultAvatar(nameLabel, 40);

  return (
    <header className={`navbar ${hidden ? 'hidden' : ''} ${scrolled ? 'scrolled' : ''}`}>
      <div className="container nav-inner">
        {/* Logo */}
        <Link to="/" className="brand-logo" aria-label="AI Poster">
          <img src="/logo.png" alt="AI Poster" className="logo-img" />
        </Link>

        {/* 导航链接 */}
        <nav className="nav-links">
          <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
            首页
          </Link>

          <div
            className="nav-dropdown"
            ref={posterMenuRef}
            onMouseEnter={onPosterEnter}
            onMouseLeave={onPosterLeave}
          >
            <button
              className={`nav-link dropdown-trigger ${location.pathname.startsWith('/poster') ? 'active' : ''}`}
              onClick={() => setPosterMenuOpen(!posterMenuOpen)}
            >
              海报生成
              <svg className={`dropdown-arrow ${posterMenuOpen ? 'up' : ''}`} width="16" height="16" viewBox="0 0 24 24">
                <path fill="currentColor" d="M7 10l5 5 5-5z"></path>
              </svg>
            </button>

            {posterMenuOpen && (
              <div className="dropdown-menu">
                <Link to="/poster/quick" className="dropdown-item">
                  <div className="item-content">
                    <div className="item-title">快速生成</div>
                    <div className="item-desc">使用模板快速创建海报</div>
                  </div>
                </Link>
                <Link to="/poster/custom" className="dropdown-item">
                  <div className="item-content">
                    <div className="item-title">自定义生成</div>
                    <div className="item-desc">完全自定义设计海报</div>
                  </div>
                </Link>
                <Link to="/poster/history" className="dropdown-item">
                  <div className="item-content">
                    <div className="item-title">历史记录</div>
                    <div className="item-desc">查看已生成海报</div>
                  </div>
                </Link>
              </div>
            )}
          </div>
        </nav>

        <div className="nav-spacer" />

        <div
          className="avatar-wrap"
          ref={wrapRef}
          onMouseEnter={onEnter}
          onMouseLeave={onLeave}
        >
          <button
            className="avatar-btn"
            aria-haspopup="menu"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
            title={nameLabel}
          >
            <img className="nav-avatar-img" src={avatarSrc} alt="avatar" />
            <svg className={`chev ${open ? 'up' : 'down'}`} width="14" height="14" viewBox="0 0 24 24">
              <path fill="currentColor" d="M7 10l5 5 5-5z"></path>
            </svg>
          </button>

          {open && (
            <div className="user-menu" role="menu">
              <div className="user-info">
                <img className="nav-avatar-lg" src={avatarSrc} alt="avatar" />
                <div className="meta">
                  <div className="name">{nameLabel}</div>
                  {user?.email ? <div className="muted">{user.email}</div> : null}
                </div>
              </div>

              <div className="menu-sep" />
              <Link to="/profile" className="menu-item" role="menuitem">个人资料</Link>
              <Link to="/profile" className="menu-item" role="menuitem">设置</Link>
              <div className="menu-sep" />
              <button className="menu-item danger" onClick={onLogout} role="menuitem">退出登录</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}