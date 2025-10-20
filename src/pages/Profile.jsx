import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  getProfile,
  updateProfile,
  changePassword,
  uploadAvatar,
  getMembershipPlans,
  getUserMembershipInfo,
  createMembershipOrder,
  getMembershipOrders,
  getMembershipOrderDetail,
} from '../services/userAPI';
import { logout } from '../services/auth';
import '../styles/theme.css';
import './settings.css';

export default function Profile() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // 数据与状态
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');
  const [nickname, setNickname] = useState('');
  const [email, setEmail] = useState('');
  const [pwOld, setPwOld] = useState('');
  const [pwNew, setPwNew] = useState('');
  const [saving, setSaving] = useState(false);
  const [changingPw, setChangingPw] = useState(false);
  const [avatarUploading, setAvatarUploading] = useState(false);

  // 会员相关状态
  const [membershipInfo, setMembershipInfo] = useState(null);
  const [membershipPlans, setMembershipPlans] = useState([]);
  const [membershipLoading, setMembershipLoading] = useState(false);
  const [purchaseLoading, setPurchaseLoading] = useState(false);

  // 新增订单相关状态
  const [orders, setOrders] = useState([]);
  const [orderLoading, setOrderLoading] = useState(false);
  const [orderDetail, setOrderDetail] = useState(null);

  // 侧边导航（中文）
  const menu = useMemo(
    () => [
      {
        title: '账户',
        items: [
          { key: 'account', label: '账号设置' },
          { key: 'membership', label: '会员与充值' },
          { key: 'appearance', label: '外观' },
          { key: 'accessibility', label: '辅助功能' },
          { key: 'notifications', label: '通知' },
        ],
      },
      {
        title: '访问',
        items: [{ key: 'password', label: '密码与认证' }],
      },
      {
        title: '代码与自动化',
        items: [
          { key: 'models', label: '模型' },
          { key: 'packages', label: '软件包' },
        ],
      },
    ],
    []
  );

  const [section, setSection] = useState('account');

  // 检查支付结果
  useEffect(() => {
    const paymentStatus = searchParams.get('payment');
    if (paymentStatus === 'success') {
      setMsg('支付成功！会员权益即将生效');
      setSection('membership');
      setSearchParams(new URLSearchParams());
      setTimeout(() => {
        loadMembershipData();
      }, 1000);
    }
  }, [searchParams, setSearchParams]);

  useEffect(() => {
    (async () => {
      try {
        const data = await getProfile();
        setProfile(data);
        setNickname(data.nickname || '');
        setEmail(data.email || '');
      } catch (e) {
        setErr(e?.response?.data?.detail || '获取用户信息失败');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // 加载会员信息和订单列表
  const loadMembershipData = async () => {
    if (section !== 'membership') return;
    setMembershipLoading(true);
    try {
      const [membershipData, plansData, ordersData] = await Promise.all([
        getUserMembershipInfo(),
        getMembershipPlans(),
        getMembershipOrders(),
      ]);
      setMembershipInfo(membershipData);
      setMembershipPlans(plansData);
      setOrders(ordersData);
    } catch (e) {
      setErr(e?.response?.data?.detail || '获取会员信息失败');
    } finally {
      setMembershipLoading(false);
    }
  };

  // 查看订单详情
  const onOrderDetail = async (out_trade_no) => {
    setOrderLoading(true);
    try {
      const detail = await getMembershipOrderDetail(out_trade_no);
      setOrderDetail(detail);
    } catch (e) {
      setErr(e?.response?.data?.detail || '获取订单详情失败');
    } finally {
      setOrderLoading(false);
    }
  };

  const closeOrderDetail = () => setOrderDetail(null);

  useEffect(() => {
    if (section === 'membership') {
      loadMembershipData();
    }
  }, [section]);

  useEffect(() => {
    if (!msg) return;
    const t = setTimeout(() => setMsg(''), 3000);
    return () => clearTimeout(t);
  }, [msg]);

  const onSaveProfile = async (e) => {
    e.preventDefault();
    if (!profile) return;
    setErr('');
    setMsg('');
    setSaving(true);
    try {
      const data = await updateProfile({ nickname, email });
      setProfile((p) => ({ ...p, ...data }));
      setMsg('资料已更新');
    } catch (e) {
      const d = e?.response?.data;
      setErr(
        d?.detail ||
          d?.message ||
          Object.values(d || {}).flat().join('；') ||
          '更新失败'
      );
    } finally {
      setSaving(false);
    }
  };

  const onChangePassword = async (e) => {
    e.preventDefault();
    setErr('');
    setMsg('');
    if ((pwNew || '').length < 8) {
      setErr('新密码长度至少8位');
      return;
    }
    setChangingPw(true);
    try {
      await changePassword({ old_password: pwOld, new_password: pwNew });
      setMsg('密码修改成功，下次会话请使用新密码登录');
      setPwOld('');
      setPwNew('');
    } catch (e) {
      setErr(e?.response?.data?.error || '修改密码失败');
    } finally {
      setChangingPw(false);
    }
  };

  const onAvatarFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setErr('');
    setMsg('');
    setAvatarUploading(true);
    try {
      const { avatar_url } = await uploadAvatar(file);
      setProfile((p) => ({ ...p, avatar_url }));
      setMsg('头像已更新');
    } catch (e) {
      setErr(e?.response?.data?.error || '头像上传失败');
    } finally {
      setAvatarUploading(false);
      e.target.value = '';
    }
  };

  // 购买会员套餐
  const onPurchasePlan = async (planId) => {
    setErr('');
    setMsg('');
    setPurchaseLoading(true);
    try {
      const orderData = await createMembershipOrder({
        plan_id: planId,
        payment_method: 'alipay',
      });

      if (orderData.payment_info?.pay_url) {
        window.location.href = orderData.payment_info.pay_url;
      } else {
        setErr('创建支付订单失败');
      }
    } catch (e) {
      setErr(e?.response?.data?.detail || '购买失败');
    } finally {
      setPurchaseLoading(false);
    }
  };

  const onLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  // 格式化时间
  const formatDate = (dateString) => {
    if (!dateString) return '暂无';
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getPlanTypeName = (planType) => {
    const typeMap = {
      monthly: '月度会员',
      quarterly: '季度会员',
      yearly: '年度会员',
      lifetime: '终身会员',
    };
    return typeMap[planType] || planType;
  };

  const renderAccount = () => {
    const member = !!profile?.is_member;
    return (
      <div className="card">
        <h2 className="settings-h2">账号设置</h2>
        {err && <div className="alert alert-danger">{err}</div>}
        {msg && <div className="alert alert-success">{msg}</div>}
        <div className="account-grid">
          <section>
            <h3 className="settings-h3">头像</h3>
            <div className="avatar-row">
              <img
                className="avatar-img"
                src={
                  profile?.avatar_url ||
                  'https://via.placeholder.com/132x132?text=Avatar'
                }
                alt="avatar"
              />
              <label className="btn btn-ghost btn-sm">
                {avatarUploading ? '上传中...' : '更换头像'}
                <input
                  type="file"
                  accept="image/*"
                  onChange={onAvatarFile}
                  disabled={avatarUploading}
                  style={{ display: 'none' }}
                />
              </label>
            </div>
          </section>

          <section>
            <h3 className="settings-h3">公开资料</h3>
            <form onSubmit={onSaveProfile} className="settings-form">
              <div className="field">
                <label className="label">用户名（只读）</label>
                <input
                  className="input"
                  value={profile?.username || ''}
                  readOnly
                />
              </div>
              <div className="field">
                <label className="label">昵称</label>
                <input
                  className="input"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label className="label">邮箱</label>
                <input
                  className="input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="toolbar">
                <button
                  className="btn btn-primary"
                  type="submit"
                  disabled={saving}
                >
                  {saving ? '保存中...' : '保存资料'}
                </button>
                <span className={`badge ${member ? 'ok' : 'off'}`}>
                  <span className="dot" />
                  会员状态：{member ? '是' : '否'}
                </span>
              </div>
            </form>
          </section>
        </div>
      </div>
    );
  };

  const renderMembership = () => (
    <div className="card">
      <h2 className="settings-h2">会员与充值</h2>
      {err && <div className="alert alert-danger">{err}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}
      {membershipLoading ? (
        <div className="membership-loading">
          <div className="skeleton" style={{ height: 200 }} />
        </div>
      ) : (
        <div className="membership-content">
          {/* 会员状态 */}
          <section className="membership-status">
            <h3 className="settings-h3">当前会员状态</h3>
            <div className="membership-card">
              {membershipInfo?.is_active ? (
                <div className="membership-active">
                  <div className="membership-info">
                    <div className="membership-plan-name">
                      {membershipInfo.plan?.name || '会员用户'}
                    </div>
                    <div className="membership-details">
                      <span className="membership-type">
                        {getPlanTypeName(membershipInfo.plan?.plan_type)}
                      </span>
                      <span className="membership-expires">
                        到期时间：{formatDate(membershipInfo.expires_at)}
                      </span>
                      <span className="membership-days">
                        剩余 {membershipInfo.days_left || 0} 天
                      </span>
                    </div>
                  </div>
                  <div className="membership-badge">
                    <span className="badge ok">
                      <span className="dot" />
                      会员有效
                    </span>
                  </div>
                </div>
              ) : (
                <div className="membership-inactive">
                  <div className="membership-info">
                    <div className="membership-plan-name">普通用户</div>
                    <div className="membership-details">
                      <span>您还不是会员，开通会员享受更多特权</span>
                    </div>
                  </div>
                  <div className="membership-badge">
                    <span className="badge off">
                      <span className="dot" />
                      未开通
                    </span>
                  </div>
                </div>
              )}
            </div>
            <div className="membership-stats" style={{ marginTop: 12 }}>
              <div className="stat-item">
                <span className="stat-label">累计订单</span>
                <span className="stat-value">{membershipInfo?.total_orders || 0}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">累计消费</span>
                <span className="stat-value">¥{membershipInfo?.total_spent || '0.00'}</span>
              </div>
            </div>
          </section>

          {/* 会员套餐 */}
          <section className="membership-plans">
            <h3 className="settings-h3">会员套餐</h3>
            <div className="plans-grid">
              {membershipPlans.map((plan) => (
                <div key={plan.id} className={`plan-card ${plan.is_featured ? 'featured' : ''}`}>
                  {plan.is_featured && <div className="plan-badge">推荐</div>}
                  <div className="plan-header">
                    <h4 className="plan-name">{plan.name}</h4>
                    <div className="plan-type">{getPlanTypeName(plan.plan_type)}</div>
                  </div>
                  <div className="plan-price">
                    <span className="current-price">¥{plan.price}</span>
                    {plan.original_price && plan.original_price > plan.price && (
                      <span className="original-price">¥{plan.original_price}</span>
                    )}
                    {plan.discount_percentage > 0 && (
                      <span className="discount">-{plan.discount_percentage}%</span>
                    )}
                  </div>
                  <div className="plan-duration">有效期：{plan.duration_days} 天</div>
                  {plan.description && (
                    <div className="plan-description">{plan.description}</div>
                  )}
                  <div className="plan-features">
                    {plan.features?.map((feature, index) => (
                      <div key={index} className="feature-item">
                        <span className="feature-icon">✓</span>
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                  <div className="plan-quota">
                    <div className="quota-item">
                      <span>海报配额：</span>
                      <span>{plan.poster_quota === -1 ? '无限' : plan.poster_quota}</span>
                    </div>
                    <div className="quota-item">
                      <span>最大尺寸：</span>
                      <span>{plan.max_image_size}</span>
                    </div>
                    {plan.priority_generation && (
                      <div className="quota-item">
                        <span>优先生成：</span>
                        <span>是</span>
                      </div>
                    )}
                  </div>
                  <button
                    className="btn btn-primary w-full plan-buy-btn"
                    onClick={() => onPurchasePlan(plan.id)}
                    disabled={purchaseLoading}
                  >
                    {purchaseLoading ? '处理中...' : '立即购买'}
                  </button>
                </div>
              ))}
            </div>
          </section>

          {/* 订单信息美化展示 */}
          <section className="membership-orders">
            <h3 className="settings-h3">订单信息</h3>
            {orderLoading ? (
              <div className="membership-loading">
                <div className="skeleton" style={{ height: 80 }} />
              </div>
            ) : orders.length === 0 ? (
              <div className="text-muted" style={{ padding: '24px 0' }}>暂无订单记录</div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="orders-table">
                  <thead>
                    <tr>
                      <th>订单号</th>
                      <th>套餐</th>
                      <th>金额</th>
                      <th>状态</th>
                      <th>时间</th>
                      <th>详情</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map((order) => (
                      <tr key={order.out_trade_no}>
                        <td>{order.out_trade_no}</td>
                        <td>{order.plan_name || order.plan?.name}</td>
                        <td>¥{order.amount}</td>
                        <td>
                          <span className={`badge ${order.status === 'SUCCESS' ? 'ok' : 'off'}`}>
                            <span className="dot" />
                            {order.status === 'SUCCESS' ? '已支付' : order.status}
                          </span>
                        </td>
                        <td>{formatDate(order.created_at)}</td>
                        <td>
                          <button
                            className="btn btn-sm"
                            onClick={() => onOrderDetail(order.out_trade_no)}
                          >
                            查看
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* 订单详情弹窗 */}
            {orderDetail && (
              <div className="order-detail-modal-bg" onClick={closeOrderDetail}>
                <div className="order-detail-modal" onClick={e => e.stopPropagation()}>
                  <h3>订单详情</h3>
                  <div className="order-fields">
                    <div><b>订单号：</b>{orderDetail.out_trade_no}</div>
                    <div><b>套餐：</b>{orderDetail.plan_name || orderDetail.plan?.name}</div>
                    <div><b>金额：</b>¥{orderDetail.amount}</div>
                    <div><b>状态：</b>{orderDetail.status === 'SUCCESS' ? '已支付' : orderDetail.status}</div>
                    <div><b>创建时间：</b>{formatDate(orderDetail.created_at)}</div>
                    <div><b>支付方式：</b>{orderDetail.payment_method || '-'}</div>
                    <div><b>支付时间：</b>{orderDetail.paid_at ? formatDate(orderDetail.paid_at) : '-'}</div>
                    {orderDetail.remark && <div><b>备注：</b>{orderDetail.remark}</div>}
                  </div>
                  <div style={{ textAlign: 'right', marginTop: 16 }}>
                    <button className="btn btn-outline btn-sm" onClick={closeOrderDetail}>关闭</button>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      )}
    </div>
  );

  const renderPassword = () => (
    <div className="card">
      <h2 className="settings-h2">密码与认证</h2>
      {err && <div className="alert alert-danger">{err}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}

      <form onSubmit={onChangePassword} className="settings-form">
        <div className="field">
          <label className="label">旧密码</label>
          <input
            className="input"
            type="password"
            value={pwOld}
            onChange={(e) => setPwOld(e.target.value)}
            required
          />
        </div>
        <div className="field">
          <label className="label">新密码（至少8位）</label>
          <input
            className="input"
            type="password"
            value={pwNew}
            onChange={(e) => setPwNew(e.target.value)}
            required
          />
        </div>
        <div className="toolbar">
          <button
            className="btn btn-primary"
            type="submit"
            disabled={changingPw}
          >
            {changingPw ? '修改中...' : '确认修改'}
          </button>
        </div>
      </form>
    </div>
  );

  const renderSoon = (title) => (
    <div className="card">
      <h2 className="settings-h2">{title}</h2>
      <div className="text-muted">该模块暂未开通，敬请期待。</div>
    </div>
  );

  if (loading) {
    return (
      <div className="settings-page">
        <div className="settings-layout">
          <aside className="settings-sidebar skeleton" style={{ height: 420 }} />
          <main className="settings-main">
            <div className="card">
              <div className="skeleton" style={{ height: 160 }} />
            </div>
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="settings-header">
        <div className="brand">设置</div>
        <div className="grow" />
        <button className="btn btn-outline btn-sm" onClick={onLogout}>
          退出登录
        </button>
      </div>

      <div className="settings-layout">
        <aside className="settings-sidebar">
          {menu.map((group) => (
            <div className="settings-group" key={group.title}>
              <div className="settings-group-title">{group.title}</div>
              <ul className="settings-nav">
                {group.items.map((i) => (
                  <li
                    key={i.key}
                    className={`settings-item ${section === i.key ? 'active' : ''}`}
                    onClick={() => setSection(i.key)}
                  >
                    {i.label}
                  </li>
                ))}
              </ul>
            </div>
          ))}
          <div className="settings-logout">
            <button
              className="btn btn-ghost btn-sm w-full"
              onClick={onLogout}
            >
              退出登录
            </button>
          </div>
        </aside>

        <main className="settings-main">
          {section === 'account' && renderAccount()}
          {section === 'membership' && renderMembership()}
          {section === 'password' && renderPassword()}
          {section !== 'account' &&
            section !== 'membership' &&
            section !== 'password' &&
            renderSoon(
              menu
                .flatMap((g) => g.items)
                .find((i) => i.key === section)?.label || '设置'
            )}
        </main>
      </div>
    </div>
  );
}