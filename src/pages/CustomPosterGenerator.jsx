import { useEffect, useRef, useState, useCallback } from 'react';
import '../styles/theme.css';
import './custom-poster-generator.css';
import { getPosterBaseConfig, uploadPosterImage, generatePoster, getPosterUsage, getPosterHistory } from '../services/posterAPI';

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

export default function CustomPosterGenerator() {
  // 枚举
  const [sizes, setSizes] = useState([]);

  // 选择状态
  const [sizeId, setSizeId] = useState(null);

  // 输入与参考图
  const [prompt, setPrompt] = useState('');
  const [mode, setMode] = useState('single'); // single | group
  const [imageCount, setImageCount] = useState(3); // 组图期望数量（语义 + 上限），1~15
  const [images, setImages] = useState([]); // [{name,url}]

  // 使用情况
  const [usage, setUsage] = useState({ is_member: false, free_remaining: 0 });

  // 结果 & 状态
  const [generating, setGenerating] = useState(false);
  const [results, setResults] = useState([]);
  const [err, setErr] = useState('');
  const [msg, setMsg] = useState('');
  const [loadingEnums, setLoadingEnums] = useState(true);

  // 侧栏
  const [activeTab, setActiveTab] = useState('generate');
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [promptOpen, setPromptOpen] = useState(true);

  // Lightbox
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxIndex, setLightboxIndex] = useState(0);

  const fileInputRef = useRef(null);

  // 初始化：只获取尺寸枚举和使用状态
  useEffect(() => {
    (async () => {
      try {
        const base = await getPosterBaseConfig();
        setSizes(base.sizes || []);
        if (base.sizes?.length) setSizeId(base.sizes[0].id);
      } catch {
        setErr('参数加载失败');
      } finally {
        setLoadingEnums(false);
      }
      try {
        const u = await getPosterUsage();
        setUsage(u);
      } catch (e) {
        if (e?.response?.status === 401) {
          window.location.href = '/login';
        } else {
          setErr('无法获取使用状态');
        }
      }
    })();
  }, []);

  // 自动清理提示消息
  useEffect(() => {
    if (!msg) return;
    const t = setTimeout(() => setMsg(''), 1800);
    return () => clearTimeout(t);
  }, [msg]);

  // Lightbox 键盘支持
  useEffect(() => {
    if (!lightboxOpen) return;
    const onKey = (e) => {
      if (e.key === 'Escape') setLightboxOpen(false);
      if (e.key === 'ArrowRight') setLightboxIndex((i) => (i + 1) % results.length);
      if (e.key === 'ArrowLeft') setLightboxIndex((i) => (i - 1 + results.length) % results.length);
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [lightboxOpen, results.length]);

  const generationModeLabel = mode === 'single'
    ? (images.length === 0 ? '文字生单图' : (images.length === 1 ? '单图生单图' : '多图生单图'))
    : (images.length === 0 ? '文字生组图' : (images.length === 1 ? '单图生组图' : '多图生组图'));

  const overQuota = !usage.is_member && usage.free_remaining <= 0;
  const canGenerate = prompt.trim() && sizeId && !generating && !overQuota;

  // 上传参考图：两种模式都允许 0~10
  const onFiles = async (files) => {
    const arr = Array.from(files);
    if (!arr.length) return;
    setErr('');
    try {
      const uploaded = [];
      for (const f of arr) {
        const r = await uploadPosterImage(f);
        const url = r?.image_url;
        if (url) uploaded.push({ name: f.name, url });
      }
      setImages(prev => {
        const merged = [...prev, ...uploaded].slice(0, 10);
        return merged;
      });
      setMsg('图片已上传');
    } catch (e) {
      if (e?.response?.status === 401) {
        window.location.href = '/login';
        return;
      }
      setErr(e?.response?.data?.error || '图片上传失败');
    }
  };
  const removeImage = (idx) => setImages(prev => prev.filter((_, i) => i !== idx));

  // Ark 约束校验（组图仅校验上限规则）
  const validateArkConstraints = () => {
    const refCount = images.length;
    if (refCount > 10) return '参考图片最多 10 张';
    if (mode === 'group') {
      if (imageCount < 1 || imageCount > 15) return '期望生成数量需在 1~15 之间';
      if (refCount + imageCount > 15) return '参考图数量与上限之和不能超过 15';
    }
    return null;
  };

  // 超时后轮询：尝试从历史记录补回最新结果
  async function pollLatestAfter(startMs, maxTries = 12, intervalMs = 3000) {
    for (let i = 0; i < maxTries; i++) {
      await new Promise(r => setTimeout(r, intervalMs));
      try {
        const list = await getPosterHistory();
        const first = Array.isArray(list) ? list[0] : null;
        if (!first) continue;
        const createdAt = new Date(first.created_at || first.updated_at || 0).getTime();
        const imgs = normalizeImages(first.images);
        if (imgs.length && createdAt >= (startMs - 10000)) {
          return { imgs, record: first };
        }
      } catch {
        // 忽略本轮错误
      }
    }
    return null;
  }

  // 生成
  const handleGenerate = async () => {
    setErr('');
    setMsg('');
    setResults([]);

    if (!prompt.trim()) return setErr('请输入提示描述');
    if (!sizeId) return setErr('尺寸缺失');
    if (overQuota) return setErr('免费次数已用尽，请升级会员');

    const rule = validateArkConstraints();
    if (rule) return setErr(rule);

    const startMs = Date.now();
    setGenerating(true);
    try {
      const payload = {
        prompt: prompt.trim(),
        size_id: sizeId,
        generation_mode: mode,
      };

      // 参考图：统一走 images 数组
      if (images.length > 0) {
        payload.images = images.map(i => i.url);
      }

      if (mode === 'group') {
        payload.sequential_image_generation = 'auto';
        payload.image_count_hint = imageCount; // 由后端补语义
        const cap = Math.max(1, Math.min(imageCount, 15 - (images.length || 0)));
        payload.sequential_image_generation_options = { max_images: cap }; // 上限
      } else {
        payload.sequential_image_generation = 'disabled';
      }

      const resp = await generatePoster(payload);

      const imgs1 = normalizeImages(resp?.images);
      const imgs2 = normalizeImages(resp?.urls);
      const arr = imgs1.length ? imgs1 : imgs2;

      setResults(arr);

      const successFlag = (arr && arr.length > 0) || resp?.status === 'success';
      if (successFlag) {
        setMsg('生成完成');
        if (!usage.is_member) {
          setUsage(u => ({ ...u, free_remaining: Math.max(0, u.free_remaining - 1) }));
        }
      } else {
        setErr(resp?.error_message || resp?.detail || '生成失败');
      }
    } catch (error) {
      const isTimeout = error?.code === 'ECONNABORTED' || /timeout/i.test(error?.message || '');
      if (isTimeout && mode === 'group') {
        setErr('生成超时，后台仍在处理，正在为你同步结果...');
        const polled = await pollLatestAfter(startMs, 12, 3000); // ~36s
        if (polled && polled.imgs.length) {
          setResults(polled.imgs);
          setErr('');
          setMsg('生成完成（已从后台同步结果）');
        } else {
          setErr('生成超时。请稍后在“生成历史”中查看，或重试。');
        }
      } else {
        // 非超时：兜底——有图就显示（部分成功）
        const body = error?.response?.data;
        const imgs1 = normalizeImages(body?.images);
        const imgs2 = normalizeImages(body?.urls);
        const arr = imgs1.length ? imgs1 : imgs2;

        if (arr && arr.length) {
          setResults(arr);
          setErr(body?.error_message || body?.detail || '部分成功：已生成部分图片');
        } else {
          if (error?.response?.status === 401) {
            window.location.href = '/login';
          } else {
            setErr(body?.detail || body?.error || error?.message || '生成失败');
          }
        }
      }
    } finally {
      setGenerating(false);
    }
  };

  // 结果网格
  const ResultGrid = useCallback(() => {
    if (!results.length) return null;
    return (
      <div className="result-card card">
        <div className="result-head">
          <h3 className="result-title">生成结果 ({results.length})</h3>
        </div>
        <div className="result-grid fill">
          {results.map((u, i) => (
            <div
              key={i}
              className="result-item"
              onClick={() => { setLightboxIndex(i); setLightboxOpen(true); }}
            >
              <img src={u} alt={`海报 ${i + 1}`} className="result-img" />
              <span className="badge index-badge">{i + 1}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }, [results]);

  if (loadingEnums) {
    return (
      <div className="custom-page container">
        <div className="page-head">
          <h1 className="page-title">自定义生成</h1>
        </div>
        <div className="card loading-card">
          <div className="spinner" />
          <div className="loading-text">加载参数...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="custom-page container">
      <div className="page-head">
        <h1 className="page-title">自定义生成</h1>
        <span className="mode-pill">{generationModeLabel}</span>
        <div className="head-actions">
          <span className="badge usage">
            {usage.is_member ? '会员：无限次' : `免费剩余：${usage.free_remaining} 次`}
          </span>
        </div>
      </div>

      {err && <div className="alert alert-danger">{err}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}

      <div className={`workspace ${drawerOpen ? 'open' : 'closed'}`}>
        {/* 左侧 rail */}
        <aside className="left-rail" aria-label="工具栏">
          <div className="rail-header">
            <button
              className="rail-toggle"
              onClick={() => setDrawerOpen(v => !v)}
              aria-expanded={drawerOpen}
              title={drawerOpen ? '收起设置' : '展开设置'}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
                <path fill="currentColor" d={drawerOpen ? "M15 18l-6-6 6-6" : "M9 6l6 6-6 6"} />
              </svg>
            </button>
          </div>

          <button
            className={`rail-btn ${activeTab === 'generate' ? 'active' : ''}`}
            onClick={() => setActiveTab('generate')}
            title="生成"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
              <path fill="currentColor" d="M13 2s2 2 2 5c0 2-1 4-3 5 0 0 5-1 5-6 0-3-2-5-4-6z"/>
            </svg>
            <span>生成</span>
          </button>

          <button
            className={`rail-btn ${activeTab === 'edit' ? 'active' : ''}`}
            onClick={() => setActiveTab('edit')}
            title="编辑"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
              <path fill="currentColor" d="M4 7h10v2H4V7zm0 8h16v2H4v-2zm12-8h4v2h-4V7zM8 11h12v2H8v-2z"/>
            </svg>
            <span>编辑</span>
          </button>
        </aside>

        {/* 抽屉侧栏 */}
        <aside className="drawer">
          {activeTab === 'generate' ? (
            <div className="side-scroll">
              {/* 生成模式 */}
              <div className="card section">
                <h2 className="section-title">生成模式</h2>
                <div style={{ display: 'flex', gap: 12 }}>
                  <label className="radio-chip">
                    <input
                      type="radio"
                      name="gen-mode"
                      value="single"
                      checked={mode === 'single'}
                      onChange={() => setMode('single')}
                    />
                    <span>单图</span>
                  </label>
                  <label className="radio-chip">
                    <input
                      type="radio"
                      name="gen-mode"
                      value="group"
                      checked={mode === 'group'}
                      onChange={() => setMode('group')}
                    />
                    <span>组图</span>
                  </label>
                </div>
                <div className="small-muted" style={{ marginTop: 6 }}>
                  组图：期望数量会作为提示词语义和最多输出的上限。
                </div>
              </div>

              {/* 提示描述（可折叠） */}
              <div className={`card section collapsible ${promptOpen ? 'open' : 'closed'}`}>
                <div
                  className="section-header"
                  onClick={() => setPromptOpen(v => !v)}
                  role="button"
                  aria-expanded={promptOpen}
                >
                  <h2 className="section-title">提示描述</h2>
                  <span className={`collapse-arrow ${promptOpen ? 'up' : ''}`} aria-hidden>▾</span>
                </div>
                {promptOpen && (
                  <>
                    <textarea
                      className="prompt-box"
                      rows={6}
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="例如：极简风格咖啡店开业海报，暖棕主色……（组图可写：生成3张图片，分别体现清晨/午后/夜晚）"
                      maxLength={1000}
                    />
                    <div className="char-hint">{prompt.length} / 1000</div>
                  </>
                )}
              </div>

              {/* 参考图片 */}
              <div className="card section">
                <h2 className="section-title">
                  参考图片 <small className="muted">（最多 10 张；组图需满足“参考图 + 上限 ≤ 15”）</small>
                </h2>
                <div className="images-wrap">
                  {images.map((img, idx) => (
                    <div className="img-box" key={idx}>
                      <img src={img.url} alt={img.name} />
                      <button className="remove-btn" onClick={() => removeImage(idx)} title="移除">✕</button>
                    </div>
                  ))}
                  {images.length < 10 && (
                    <button className="img-upload-btn" onClick={() => fileInputRef.current?.click()} type="button">
                      <span className="plus">+</span>
                      <span className="tip">添加图片</span>
                    </button>
                  )}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    multiple
                    style={{ display: 'none' }}
                    onChange={(e) => onFiles(e.target.files)}
                  />
                </div>
              </div>

              {/* 参数与生成 */}
              <div className="card section">
                <h2 className="section-title">参数选择</h2>
                <div className="form-grid">
                  <div className="field">
                    <label className="label">尺寸</label>
                    <select className="input select" value={sizeId || ''} onChange={(e) => setSizeId(Number(e.target.value))}>
                      {sizes.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                    </select>
                  </div>
                  {mode === 'group' && (
                    <div className="field">
                      <label className="label">期望数量 (1-15，作为上限)</label>
                      <input
                        type="number" min={1} max={15} className="input"
                        value={imageCount}
                        onChange={(e) => {
                          const v = Number(e.target.value) || 1;
                          setImageCount(Math.min(15, Math.max(1, v)));
                        }}
                      />
                    </div>
                  )}
                </div>

                <div className="generate-bar">
                  <button
                    className="btn btn-primary"
                    disabled={!canGenerate}
                    onClick={handleGenerate}
                    title={overQuota ? '免费次数已用尽' : ''}
                  >
                    {generating ? '生成中...' : (mode === 'single' ? '生成单图' : '生成组图')}
                  </button>
                  <span className="muted tip-inline">
                    当前：{generationModeLabel}{mode === 'group' ? ` | 期望：${imageCount} 张（上限）` : ''}
                  </span>
                </div>
              </div>
            </div>
          ) : (
            <div className="card section">
              <h2 className="section-title">编辑（占位）</h2>
              <div className="muted">这里预留编辑区域，后续补充。</div>
            </div>
          )}
        </aside>

        {/* 右侧预览 */}
        <main className="preview-panel">
          {generating && (
            <div className="card loading-card">
              <div className="spinner" />
              <div className="loading-text">AI 正在创作，请稍候...</div>
            </div>
          )}
          {!generating && !results.length && (
            <div className="card placeholder-card">
              <h3 className="ph-title">如何获得更好的结果？</h3>
              <ul className="ph-tips">
                <li>描述清晰：主题 / 场景 / 主体元素 / 氛围 / 色彩</li>
                <li>适度添加风格词：极简、赛博、复古、商业、高端等</li>
                <li>参考图片最多 10 张；组图时需满足“参考图 + 上限 ≤ 15”</li>
              </ul>
              <div className="ph-footer muted">左侧设置完成后点击“{mode === 'single' ? '生成单图' : '生成组图'}”</div>
            </div>
          )}
          <ResultGrid />
        </main>
      </div>

      {/* Lightbox */}
      {lightboxOpen && results.length > 0 && (
        <div className="lightbox" onClick={() => setLightboxOpen(false)}>
          <div className="lightbox-inner" onClick={(e) => e.stopPropagation()}>
            <img src={results[lightboxIndex]} alt="预览大图" className="lightbox-img" />
            {results.length > 1 && (
              <>
                <button className="lightbox-nav left" onClick={() => setLightboxIndex((i) => (i - 1 + results.length) % results.length)} title="上一张">‹</button>
                <button className="lightbox-nav right" onClick={() => setLightboxIndex((i) => (i + 1) % results.length)} title="下一张">›</button>
              </>
            )}
            <button className="lightbox-close" onClick={() => setLightboxOpen(false)} title="关闭">×</button>
          </div>
        </div>
      )}
    </div>
  );
}