// ZYKai.net Automated Portal Account Provisioning (0-Quota Default), Job Fast-Track & Multi-Rail Checkout
document.addEventListener('DOMContentLoaded', () => {
  const STORAGE_KEY = 'zykai_portal_account_v1';
  const API_ENDPOINTS = ['https://him-ai.0604.ai/v1/zykai-portal', 'http://127.0.0.1:8788/api/zykai-portal'];

  const getAccount = () => {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null'); } catch (_) { return null; }
  };
  const saveAccount = (acct) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(acct));
    renderDashboard(acct);
  };

  const renderDashboard = (acct) => {
    if (!acct) return;
    const titleEl = document.getElementById('zyk-dash-title');
    const subEl = document.getElementById('zyk-dash-sub');
    const quotaEl = document.getElementById('zyk-dash-quota');
    const tierEl = document.getElementById('zyk-dash-tier');
    const refEl = document.getElementById('zyk-dash-refcode');
    const cnPreview = document.getElementById('zyk-cn-acct-preview');
    if (titleEl) titleEl.textContent = `Welcome, ${acct.full_name} (${acct.account_id})`;
    if (subEl) subEl.innerHTML = `Account active for <strong>${acct.email}</strong> · Target: <strong>${acct.target_campus}</strong>. Your CV submissions automatically carry William Morris's official Nord Anglia internal referral tag.`;
    if (quotaEl) quotaEl.textContent = `${acct.ai_quota_balance || 0} Credits`;
    if (tierEl) tierEl.textContent = acct.tier === 'free_zero_quota' ? 'Free Explorer (0 AI Quota — Upgrade to unlock AI tools)' : `Active Tier: ${acct.tier.toUpperCase()}`;
    if (refEl) refEl.textContent = `Code: ${acct.referral_tracking_code}`;
    if (cnPreview) cnPreview.textContent = acct.account_id;
    updateCheckoutLinks(acct);
  };

  const updateCheckoutLinks = (acct) => {
    const sel = document.getElementById('zyk-checkout-tier');
    if (!sel) return;
    const opt = sel.options[sel.selectedIndex];
    const tier = sel.value;
    const usd = opt.getAttribute('data-usd') || '12';
    const rmb = opt.getAttribute('data-rmb') || '80';
    const acctTag = acct ? `${acct.account_id} (${acct.email})` : 'New Portal Member';
    const ppBtn = document.getElementById('zyk-paypal-btn');
    if (ppBtn) {
      const itemName = `ZYKai Portal ${tier.toUpperCase()} Membership - ${acctTag}`;
      ppBtn.href = `https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=${encodeURIComponent('william@zykai.net')}&currency_code=USD&amount=${encodeURIComponent(usd)}.00&item_name=${encodeURIComponent(itemName)}`;
      ppBtn.textContent = `Pay with PayPal ($${usd} USD) →`;
    }
    const wcBtn = document.getElementById('zyk-wechat-btn');
    if (wcBtn) {
      const subj = `WeChat Pay / Alipay Activation [¥${rmb} RMB - ${tier.toUpperCase()}] - ${acctTag}`;
      const body = `Hello ZYKai Concierge,\n\nPlease send the WeChat Pay / Alipay RMB QR code to activate my portal membership:\n- Portal Account ID: ${acct ? acct.account_id : 'Pending Sign-Up'}\n- Name: ${acct ? acct.full_name : ''}\n- Email: ${acct ? acct.email : ''}\n- Selected Tier: ${tier.toUpperCase()} (¥${rmb} RMB / $${usd} USD per month)\n- Official Referrer Locked: William Morris (NAS Jiaxing)\n`;
      wcBtn.href = `mailto:1@0604.ai?cc=aiclub@zykai.net&subject=${encodeURIComponent(subj)}&body=${encodeURIComponent(body)}`;
    }
  };

  const signupForm = document.getElementById('zyk-portal-signup-form');
  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const full_name = document.getElementById('zyk-name').value.trim();
      const email = document.getElementById('zyk-email').value.trim();
      const role = document.getElementById('zyk-role').value;
      const target_campus = document.getElementById('zyk-campus').value;
      const subject_specialty = document.getElementById('zyk-specialty').value.trim() || 'General Education';
      const hashNum = Math.abs(Array.from(email).reduce((a, c) => ((a << 5) - a) + c.charCodeAt(0), 0)) % 9000 + 1000;
      const acct = {
        account_id: `ZYK-2026-${hashNum}`,
        full_name,
        email,
        role,
        target_campus,
        subject_specialty,
        tier: 'free_zero_quota',
        ai_quota_balance: 0,
        referrer_locked: 'William Morris (Senior Educator, Nord Anglia School Jiaxing)',
        referral_tracking_code: `NAE-WM-2026-${hashNum}`,
        created_at: new Date().toISOString()
      };
      saveAccount(acct);
      for (const ep of API_ENDPOINTS) {
        try {
          fetch(ep + '/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(acct)
          }).catch(() => {});
        } catch (_) {}
      }
      const dash = document.getElementById('zyk-account-dashboard');
      if (dash) dash.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  const checkoutSel = document.getElementById('zyk-checkout-tier');
  if (checkoutSel) {
    checkoutSel.addEventListener('change', () => updateCheckoutLinks(getAccount()));
  }

  document.querySelectorAll('[data-select-tier]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const t = btn.getAttribute('data-select-tier');
      if (checkoutSel && t) {
        checkoutSel.value = t;
        updateCheckoutLinks(getAccount());
      }
    });
  });

  document.querySelectorAll('.zyk-apply-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const acct = getAccount();
      const baseMailto = btn.getAttribute('data-mailto') || '';
      if (acct && baseMailto) {
        const extra = `\nPortal Account ID: ${acct.account_id} (${acct.full_name} - ${acct.email})\nPersonal Referral Code: ${acct.referral_tracking_code}`;
        window.location.href = baseMailto + encodeURIComponent(extra);
      } else if (baseMailto) {
        window.location.href = baseMailto;
      }
    });
  });

  const existing = getAccount();
  if (existing) renderDashboard(existing);
  else updateCheckoutLinks(null);
});
