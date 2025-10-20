import { useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/theme.css';
import './home.css';

const HERO_URL = '/pexels-katie-goertzen-2919898-4491539.jpg';

// 默认基准倾斜与效果（向左倾斜的静态效果）
const DEFAULTS = {
  rx: '2deg',     // 轻微俯仰
  ry: '-10deg',   // 向左倾斜
  scale: '1.02',
  glow: '0.9',
};

export default function Home() {
  const navigate = useNavigate();
  const visRef = useRef(null);
  const copyRef = useRef(null);

  useEffect(() => {
    // 初始化为默认基准状态（向左倾斜）
    const el = visRef.current;
    if (!el) return;
    el.style.setProperty('--rx', DEFAULTS.rx);
    el.style.setProperty('--ry', DEFAULTS.ry);
    el.style.setProperty('--scale', DEFAULTS.scale);
    el.style.setProperty('--glow', DEFAULTS.glow);

    // 页面进入动画
    setTimeout(() => {
      copyRef.current?.classList.add('animate-in');
      visRef.current?.classList.add('animate-in');
    }, 100);
  }, []);

  const onMove = (e) => {
    const el = visRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // 以默认基准为中心的"克制"偏移，贴近 Google 的细腻交互
    const rxDelta = ((rect.height / 2 - y) / rect.height) * 8;  // -4~4左右
    const ryDelta = ((x - rect.width / 2) / rect.width) * 10;   // -5~5左右

    const rx = `${(parseFloat(DEFAULTS.rx) + rxDelta).toFixed(2)}deg`;
    const ry = `${(parseFloat(DEFAULTS.ry) + ryDelta).toFixed(2)}deg`;

    el.style.setProperty('--rx', rx);
    el.style.setProperty('--ry', ry);
    el.style.setProperty('--scale', '1.04');
    el.style.setProperty('--glow', '1'); // 光晕略加强
  };

  const onLeave = () => {
    const el = visRef.current;
    if (!el) return;
    el.style.setProperty('--rx', DEFAULTS.rx);
    el.style.setProperty('--ry', DEFAULTS.ry);
    el.style.setProperty('--scale', DEFAULTS.scale);
    el.style.setProperty('--glow', DEFAULTS.glow);
  };

  const handleQuickGenerate = () => {
    // 跳转到自定义生成页面
    navigate('/poster/generate');
  };

  return (
    <section className="hero-split">
      <div className="hero-split__inner container">
        <div className="hero-copy" ref={copyRef}>
          <h1 className="hero-h1">AI Poster</h1>
          <p className="hero-sub">快速准确海报生成</p>
          <button
            className="hero-cta-btn"
            onClick={handleQuickGenerate}
          >
            快速生成
          </button>
        </div>

        <div
          className="hero-visual"
          ref={visRef}
          onMouseMove={onMove}
          onMouseLeave={onLeave}
        >
          <div className="visual-glow" aria-hidden="true" />
          <img className="visual-img" src={HERO_URL} alt="预览" draggable="false" />
        </div>
      </div>
    </section>
  );
}