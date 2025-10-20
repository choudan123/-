import { useEffect, useState, useRef } from 'react';
import '../styles/theme.css';
import './poster-history.css';
import { getPosterHistory } from '../services/posterAPI';

// 兼容 images 为数组或字符串（'["url1","url2"]'）
function normalizeImages(imgs) {
  if (Array.isArray(imgs)) return imgs.filter(Boolean);
  if (typeof imgs === 'string') {
    try {
      const arr = JSON.parse(imgs);
      return Array.isArray(arr) ? arr.filter(Boolean) : (imgs ? [imgs] : []);
    } catch {
      return imgs ? [imgs] : [];
    }
  }
  return [];
}

export default function PosterHistory() {
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(true);

  // 预览 Lightbox
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxIndex, setLightboxIndex] = useState(0);
  const [lightboxList, setLightboxList] = useState([]);

  // 动态加载压缩库（避免全局体积）
  const zipLib = useRef({ JSZip: null, saveAs: null });
  async function ensureZipLibs() {
    if (!zipLib.current.JSZip) {
      const [{ default: JSZip }, { saveAs }] = await Promise.all([
        import('jszip'),
        import('file-saver'),
      ]);
      zipLib.current = { JSZip, saveAs };
    }
    return zipLib.current;
  }

  useEffect(() => {
    (async () => {
      try {
        const data = await getPosterHistory();
        setRows(Array.isArray(data) ? data : []);
      } catch (error) {
        setErr(error?.response?.data?.detail || error?.message || '获取历史失败（请确认已登录）');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // 键盘控制 Lightbox
  useEffect(() => {
    if (!lightboxOpen) return;
    const onKey = (e) => {
      if (e.key === 'Escape') setLightboxOpen(false);
      if (e.key === 'ArrowRight') {
        setLightboxIndex((i) => (lightboxList.length ? (i + 1) % lightboxList.length : 0));
      }
      if (e.key === 'ArrowLeft') {
        setLightboxIndex((i) => (lightboxList.length ? (i - 1 + lightboxList.length) % lightboxList.length : 0));
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [lightboxOpen, lightboxList.length]);

  const openPreview = (images, index = 0) => {
    const list = normalizeImages(images);
    if (!list.length) return;
    setLightboxList(list);
    setLightboxIndex(index);
    setLightboxOpen(true);
  };

  async function downloadAsZip(imgs, id) {
    try {
      const { JSZip, saveAs } = await ensureZipLibs();
      const zip = new JSZip();
      for (let i = 0; i < imgs.length; i++) {
        const url = imgs[i];
        const res = await fetch(url, { mode: 'cors' });
        if (!res.ok) throw new Error(`下载失败: ${url}`);
        const blob = await res.blob();
        const ext = /\.jpe?g(\?|$)/i.test(url) ? 'jpg' : /\.png(\?|$)/i.test(url) ? 'png' : 'img';
        zip.file(`poster_${id}_${i + 1}.${ext}`, blob);
      }
      const content = await zip.generateAsync({ type: 'blob' });
      saveAs(content, `poster_${id}.zip`);
    } catch {
      // 回退为逐个触发 a.click()（可能被浏览器拦截多个下载）
      imgs.forEach((u, i) => {
        const a = document.createElement('a');
        a.href = u;
        a.download = `poster_${id}_${i + 1}.png`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      });
    }
  }

  if (loading) {
    return (
      <div className="history-page container">
        <div className="history-head">
          <h1 className="history-title">生成历史</h1>
        </div>
        <div className="card history-loading">
          <div className="spinner" />
          <div className="loading-text">加载中...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="history-page container">
      <div className="history-head">
        <h1 className="history-title">生成历史</h1>
      </div>

      {err && <div className="alert alert-danger">{err}</div>}
      {!rows.length && !err && <div className="muted">暂无记录</div>}

      <div className="history-grid">
        {rows.map((r) => {
          const imgs = normalizeImages(r.images);
          const firstImg = imgs[0];
          const count = imgs.length;
          const success = r.status === 'success';

          return (
            <div key={r.id} className="history-card card">
              <div className="card-top">
                <span className="history-id">#{r.id}</span>
                <span className={`history-status ${success ? 'ok' : 'fail'}`}>
                  {success ? '成功' : '失败'}
                </span>
              </div>

              {/* 点击缩略图 -> 打开 Lightbox 预览（不再下载/新窗口） */}
              <div
                className={`thumb ${firstImg ? '' : 'empty'}`}
                onClick={() => firstImg && openPreview(imgs, 0)}
                role={firstImg ? 'button' : 'img'}
                title={firstImg ? '点击预览' : '无图片'}
              >
                {firstImg ? (
                  <img src={firstImg} alt={`海报#${r.id}`} />
                ) : (
                  <div className="thumb-empty">无图片</div>
                )}
                {count > 1 && <div className="thumb-count-badge">{count} 张</div>}
              </div>

              <div className="card-foot">
                <button
                  className="btn btn-ghost btn-sm"
                  disabled={!count}
                  onClick={() => downloadAsZip(imgs, r.id)}
                  title="打包下载全部图片"
                >
                  批量下载
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Lightbox 放大预览（层级高于导航） */}
      {lightboxOpen && lightboxList.length > 0 && (
        <div className="lightbox" onClick={() => setLightboxOpen(false)} role="dialog" aria-modal="true">
          <div className="lightbox-inner" onClick={(e) => e.stopPropagation()}>
            <img src={lightboxList[lightboxIndex]} alt="预览大图" className="lightbox-img" />
            {lightboxList.length > 1 && (
              <>
                <button
                  className="lightbox-nav left"
                  onClick={() => setLightboxIndex((i) => (i - 1 + lightboxList.length) % lightboxList.length)}
                  title="上一张"
                >
                  ‹
                </button>
                <button
                  className="lightbox-nav right"
                  onClick={() => setLightboxIndex((i) => (i + 1) % lightboxList.length)}
                  title="下一张"
                >
                  ›
                </button>
              </>
            )}
            <button className="lightbox-close" onClick={() => setLightboxOpen(false)} title="关闭">×</button>
          </div>
        </div>
      )}
    </div>
  );
}