from flask import Flask, render_template_string, jsonify, request
import requests
import secrets
import string

app = Flask(__name__)
API_URL = "https://api.mail.tm"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VaultMail — Disposable Email</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg:        #0a0c10;
            --surface:   #0f1218;
            --surface2:  #141820;
            --border:    #1e2535;
            --border2:   #2a3349;
            --cyan:      #00e5c4;
            --cyan-dim:  #00b09b;
            --cyan-glow: rgba(0, 229, 196, 0.12);
            --cyan-glow2:rgba(0, 229, 196, 0.06);
            --green:     #39ff7e;
            --amber:     #ffb340;
            --red:       #ff4d6d;
            --text:      #e2e8f0;
            --text2:     #7a8aa0;
            --text3:     #3d4f65;
            --mono:      'JetBrains Mono', monospace;
            --sans:      'Syne', sans-serif;
            --radius:    8px;
            --radius-lg: 14px;
        }

        /* ─── Scrollbar ─── */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: var(--surface); }
        ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 99px; }

        body {
            font-family: var(--mono);
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ─── Animated background grid ─── */
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(rgba(0,229,196,.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,229,196,.03) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
        }

        /* ─── Nav ─── */
        nav {
            position: sticky; top: 0; z-index: 200;
            background: rgba(10,12,16,0.85);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            padding: 0 32px;
            height: 60px;
            display: flex; align-items: center; justify-content: space-between;
        }
        .logo {
            display: flex; align-items: center; gap: 12px;
            font-family: var(--sans); font-size: 20px; font-weight: 800;
            letter-spacing: -0.5px; text-decoration: none; color: var(--text);
        }
        .logo-icon {
            width: 34px; height: 34px;
            background: linear-gradient(135deg, var(--cyan), var(--green));
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            font-size: 16px;
        }
        .logo span { color: var(--cyan); }
        .nav-pills { display: flex; gap: 8px; }
        .nav-pill {
            font-family: var(--mono); font-size: 11px; font-weight: 500;
            padding: 4px 12px; border-radius: 99px;
            border: 1px solid var(--border2);
            color: var(--text2);
        }
        .nav-pill.active { border-color: var(--cyan); color: var(--cyan); background: var(--cyan-glow2); }

        /* ─── Hero ─── */
        .hero {
            position: relative;
            padding: 56px 32px 64px;
            text-align: center;
            overflow: hidden;
        }
        .hero-glow {
            position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
            width: 600px; height: 300px;
            background: radial-gradient(ellipse, rgba(0,229,196,.13) 0%, transparent 70%);
            pointer-events: none;
        }
        .hero-label {
            display: inline-flex; align-items: center; gap: 6px;
            font-size: 11px; font-weight: 500;
            color: var(--cyan); letter-spacing: 1.5px; text-transform: uppercase;
            border: 1px solid rgba(0,229,196,0.25);
            background: rgba(0,229,196,0.06);
            padding: 5px 14px; border-radius: 99px;
            margin-bottom: 20px;
        }
        .hero-label::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--cyan); animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
        .hero h1 {
            font-family: var(--sans);
            font-size: clamp(32px, 5vw, 54px);
            font-weight: 800;
            letter-spacing: -1.5px;
            line-height: 1.08;
            margin-bottom: 14px;
        }
        .hero h1 .accent { color: var(--cyan); }
        .hero p {
            font-size: 14px; color: var(--text2); line-height: 1.7;
            max-width: 440px; margin: 0 auto 36px;
        }

        /* ─── Email Bar ─── */
        .email-bar {
            position: relative;
            max-width: 720px; margin: 0 auto;
            background: var(--surface);
            border: 1px solid var(--border2);
            border-radius: var(--radius-lg);
            padding: 6px 6px 6px 20px;
            display: flex; align-items: center; gap: 12px;
            transition: border-color .25s;
        }
        .email-bar:focus-within,
        .email-bar.active { border-color: var(--cyan); box-shadow: 0 0 0 3px var(--cyan-glow); }
        .email-cursor {
            font-size: 12px; color: var(--text3); flex-shrink: 0;
            font-family: var(--mono);
        }
        .email-bar.active .email-cursor { color: var(--cyan); }
        #email-addr {
            flex: 1; min-width: 0;
            font-family: var(--mono); font-size: 15px; font-weight: 500;
            color: var(--cyan);
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
        }
        .email-placeholder-text { color: var(--text3); font-weight: 300; }
        .divider-v { width: 1px; height: 24px; background: var(--border); flex-shrink: 0; }
        #btn-copy {
            background: none; border: none; cursor: pointer;
            padding: 8px; border-radius: 6px;
            color: var(--text3); transition: color .15s, background .15s;
            display: flex; align-items: center; flex-shrink: 0;
        }
        #btn-copy:hover:not(:disabled) { color: var(--cyan); background: var(--cyan-glow2); }
        #btn-copy:disabled { opacity: .3; cursor: not-allowed; }
        #btn-copy svg { width: 16px; height: 16px; }
        .bar-actions { display: flex; gap: 6px; flex-shrink: 0; }

        /* ─── Buttons ─── */
        .btn {
            font-family: var(--mono); font-size: 12px; font-weight: 500;
            padding: 10px 18px; border-radius: 8px; border: none;
            cursor: pointer; transition: all .15s;
            display: inline-flex; align-items: center; gap: 6px;
            white-space: nowrap; flex-shrink: 0;
        }
        .btn:active { transform: scale(.96); }
        .btn:disabled { opacity: .35; cursor: not-allowed; }
        .btn-primary {
            background: var(--cyan);
            color: #050810;
            font-weight: 700;
        }
        .btn-primary:hover:not(:disabled) { background: #00f5d4; }
        .btn-ghost {
            background: none;
            border: 1px solid var(--border2);
            color: var(--text2);
        }
        .btn-ghost:hover:not(:disabled) { border-color: var(--border2); color: var(--text); background: var(--surface2); }
        .btn-danger {
            background: none;
            border: 1px solid rgba(255,77,109,0.3);
            color: #ff6b85;
        }
        .btn-danger:hover:not(:disabled) { background: rgba(255,77,109,0.08); border-color: var(--red); }

        /* ─── Main Layout ─── */
        .main-wrap {
            position: relative; z-index: 1;
            max-width: 1140px; margin: 0 auto;
            padding: 28px 24px;
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 16px;
        }
        @media(max-width: 768px) { .main-wrap { grid-template-columns: 1fr; } }

        /* ─── Panels ─── */
        .panel {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            overflow: hidden;
            display: flex; flex-direction: column;
        }
        .panel-header {
            padding: 14px 18px;
            border-bottom: 1px solid var(--border);
            display: flex; align-items: center; justify-content: space-between;
            gap: 10px;
        }
        .panel-title {
            font-size: 10px; font-weight: 700;
            text-transform: uppercase; letter-spacing: 1.8px;
            color: var(--text3);
            display: flex; align-items: center; gap: 8px;
        }
        .status-dot {
            width: 6px; height: 6px; border-radius: 50%;
            background: var(--text3);
            transition: background .3s;
        }
        .status-dot.live { background: var(--green); box-shadow: 0 0 6px var(--green); animation: pulse 2s infinite; }
        .badge-count {
            font-size: 10px; font-weight: 700;
            padding: 3px 9px; border-radius: 99px;
            background: rgba(0,229,196,0.08);
            color: var(--cyan);
            border: 1px solid rgba(0,229,196,0.2);
        }

        /* ─── Mail List ─── */
        .mail-list {
            flex: 1; overflow-y: auto;
            min-height: 420px; max-height: 580px;
        }
        .mail-empty {
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            height: 100%; min-height: 360px;
            color: var(--text3); text-align: center; padding: 40px; gap: 14px;
        }
        .mail-empty-icon { font-size: 40px; opacity: .5; }
        .mail-empty p { font-size: 12px; line-height: 1.8; color: var(--text3); }
        .mail-empty .tip {
            font-size: 11px; color: var(--text3);
            border: 1px dashed var(--border2);
            border-radius: var(--radius);
            padding: 10px 16px;
            line-height: 1.6;
        }

        .mail-item {
            padding: 16px 18px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: background .12s;
            position: relative;
        }
        .mail-item::before {
            content: '';
            position: absolute; left: 0; top: 0; bottom: 0;
            width: 2px;
            background: var(--cyan);
            transform: scaleY(0);
            transition: transform .15s;
        }
        .mail-item:hover { background: var(--surface2); }
        .mail-item.active { background: rgba(0,229,196,0.05); }
        .mail-item.active::before { transform: scaleY(1); }
        .mail-from {
            font-size: 12px; font-weight: 600; color: var(--text);
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            margin-bottom: 4px;
        }
        .mail-subject {
            font-size: 11px; color: var(--text2);
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            margin-bottom: 6px;
        }
        .mail-time {
            font-size: 10px; color: var(--text3);
            display: flex; align-items: center; gap: 6px;
        }
        .mail-time::before { content: '⏱'; font-size: 9px; }

        /* ─── Viewer Panel ─── */
        .viewer-empty {
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            height: 100%; min-height: 460px;
            color: var(--text3); text-align: center; gap: 14px; padding: 32px;
        }
        .viewer-empty-icon { font-size: 48px; opacity: .3; }
        .viewer-empty p { font-size: 13px; color: var(--text3); line-height: 1.7; }
        .viewer-header {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border);
            background: var(--surface2);
        }
        .viewer-subject {
            font-family: var(--sans);
            font-size: 16px; font-weight: 700; color: var(--text);
            margin-bottom: 8px;
        }
        .viewer-meta {
            font-size: 11px; color: var(--text2);
            display: flex; gap: 16px; flex-wrap: wrap;
        }
        .viewer-meta-item { display: flex; align-items: center; gap: 5px; }
        .viewer-meta-label { color: var(--text3); }
        .viewer-body iframe {
            width: 100%; height: 520px; border: none;
            background: #fff;
        }

        /* ─── Spinner ─── */
        .spinner {
            width: 18px; height: 18px;
            border: 2px solid rgba(0,229,196,.2);
            border-top-color: var(--cyan);
            border-radius: 50%;
            animation: spin .7s linear infinite;
            display: inline-block;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ─── Toasts ─── */
        .toast-wrap {
            position: fixed; bottom: 24px; right: 24px;
            z-index: 999; display: flex; flex-direction: column; gap: 8px;
        }
        .toast {
            font-family: var(--mono); font-size: 12px;
            background: var(--surface2);
            border: 1px solid var(--border2);
            color: var(--text);
            padding: 12px 18px; border-radius: 10px;
            box-shadow: 0 8px 32px rgba(0,0,0,.4);
            animation: toastIn .25s ease;
            display: flex; align-items: center; gap: 8px;
            max-width: 300px;
        }
        .toast.success { border-color: rgba(0,229,196,0.3); color: var(--cyan); }
        .toast.error { border-color: rgba(255,77,109,0.3); color: #ff6b85; }
        @keyframes toastIn { from { transform: translateX(20px); opacity:0; } to { transform: translateX(0); opacity:1; } }

        /* ─── Info Section ─── */
        .info-section {
            position: relative; z-index: 1;
            max-width: 1140px; margin: 0 auto 60px;
            padding: 0 24px;
        }
        .section-label {
            font-size: 10px; font-weight: 700; letter-spacing: 2px;
            text-transform: uppercase; color: var(--cyan);
            margin-bottom: 10px;
        }
        .section-title {
            font-family: var(--sans); font-size: 26px; font-weight: 800;
            letter-spacing: -0.5px; color: var(--text);
            margin-bottom: 28px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px; margin-bottom: 48px;
        }
        .info-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            transition: border-color .2s, transform .2s;
        }
        .info-card:hover { border-color: var(--border2); transform: translateY(-2px); }
        .info-card-icon {
            width: 40px; height: 40px; border-radius: 10px;
            background: var(--surface2);
            border: 1px solid var(--border2);
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; margin-bottom: 16px;
        }
        .info-card h3 {
            font-family: var(--sans); font-size: 15px; font-weight: 700;
            color: var(--text); margin-bottom: 8px;
        }
        .info-card p { font-size: 12px; color: var(--text2); line-height: 1.8; }

        /* ─── FAQ ─── */
        .faq { display: flex; flex-direction: column; gap: 10px; }
        .faq-item {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 20px 24px;
            transition: border-color .2s;
        }
        .faq-item:hover { border-color: var(--border2); }
        .faq-item h4 {
            font-family: var(--sans); font-size: 14px; font-weight: 700;
            color: var(--cyan); margin-bottom: 8px;
            display: flex; align-items: center; gap: 8px;
        }
        .faq-item h4::before { content: '//'; color: var(--text3); font-family: var(--mono); font-size: 12px; }
        .faq-item p { font-size: 12px; color: var(--text2); line-height: 1.8; }

        /* ─── Footer ─── */
        footer {
            position: relative; z-index: 1;
            border-top: 1px solid var(--border);
            text-align: center; padding: 24px;
            font-size: 11px; color: var(--text3);
        }
        footer a { color: var(--cyan); text-decoration: none; }

        /* ─── Auto-refresh indicator ─── */
        .refresh-bar {
            height: 2px;
            background: var(--border);
            overflow: hidden;
            flex-shrink: 0;
        }
        .refresh-progress {
            height: 100%;
            background: linear-gradient(90deg, var(--cyan), var(--green));
            width: 0%;
            transition: width linear;
        }
    </style>
</head>
<body>

<!-- Nav -->
<nav>
    <a class="logo" href="#">
        <div class="logo-icon">✉</div>
        Vault<span>Mail</span>
    </a>
    <div class="nav-pills">
        <span class="nav-pill active">anonymous</span>
        <span class="nav-pill">no logs</span>
        <span class="nav-pill">free</span>
    </div>
</nav>

<!-- Hero -->
<div class="hero">
    <div class="hero-glow"></div>
    <div class="hero-label">🔐 Encrypted · Disposable · Anonymous</div>
    <h1>Temporary <span class="accent">Inbox</span>,<br>Zero Traces</h1>
    <p>Generate a burner email address in one click. Receive messages privately. No account. No data. No noise.</p>

    <div class="email-bar" id="email-bar">
        <span class="email-cursor">$</span>
        <span id="email-addr"><span class="email-placeholder-text">awaiting address generation…</span></span>
        <button id="btn-copy" onclick="copyEmail()" disabled title="Copy address">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
        </button>
        <div class="divider-v"></div>
        <div class="bar-actions">
            <button class="btn btn-primary" id="btn-generate" onclick="generateInbox()">⚡ Generate</button>
            <button class="btn btn-ghost" id="btn-refresh" onclick="refreshInbox()" disabled>↻ Refresh</button>
            <button class="btn btn-danger" id="btn-delete" onclick="deleteInbox()" disabled>✕ Delete</button>
        </div>
    </div>
</div>

<!-- Main -->
<div class="main-wrap">
    <!-- Inbox List -->
    <div class="panel">
        <div class="panel-header">
            <div class="panel-title">
                <div class="status-dot" id="status-dot"></div>
                Inbox
            </div>
            <span class="badge-count" id="msg-count">0 messages</span>
        </div>
        <div class="refresh-bar"><div class="refresh-progress" id="refresh-bar"></div></div>
        <div class="mail-list" id="mail-list">
            <div class="mail-empty">
                <div class="mail-empty-icon">📭</div>
                <p>No inbox generated yet.</p>
                <div class="tip">Click <strong style="color:var(--cyan)">⚡ Generate</strong> above<br>to create your temporary address.</div>
            </div>
        </div>
    </div>

    <!-- Viewer -->
    <div class="panel" id="viewer-panel">
        <div class="viewer-empty">
            <div class="viewer-empty-icon">📂</div>
            <p>Select a message from<br>your inbox to read it here.</p>
        </div>
    </div>
</div>

<!-- Info -->
<div class="info-section">
    <div class="section-label">// why vaultmail</div>
    <div class="section-title">Privacy shouldn't be complicated.</div>
    <div class="info-grid">
        <div class="info-card">
            <div class="info-card-icon">🛡️</div>
            <h3>Privacy First</h3>
            <p>Keep your real address hidden. Use a disposable one for any site you don't fully trust.</p>
        </div>
        <div class="info-card">
            <div class="info-card-icon">🚫</div>
            <h3>Zero Spam</h3>
            <p>Sign up for anything without flooding your real inbox with marketing noise.</p>
        </div>
        <div class="info-card">
            <div class="info-card-icon">⚡</div>
            <h3>Instant Setup</h3>
            <p>No registration, no credit card, no personal info. One click and you're done.</p>
        </div>
        <div class="info-card">
            <div class="info-card-icon">🔑</div>
            <h3>Cryptographically Secure</h3>
            <p>Every inbox gets a randomly generated password. Nobody else can peek inside.</p>
        </div>
    </div>

    <div class="section-label">// faq</div>
    <div class="section-title">Common questions.</div>
    <div class="faq">
        <div class="faq-item">
            <h4>What is a disposable email?</h4>
            <p>A temporary address that works like a real inbox — receives emails, shows attachments — but disappears when you're done. Perfect for one-time verifications.</p>
        </div>
        <div class="faq-item">
            <h4>How long does the inbox last?</h4>
            <p>As long as your browser session is active. Click "Delete" or close the tab and the address is gone permanently — no recovery possible.</p>
        </div>
        <div class="faq-item">
            <h4>Can I send emails?</h4>
            <p>No — VaultMail is receive-only. It's built purely for capturing verification and sign-up emails securely.</p>
        </div>
        <div class="faq-item">
            <h4>Is it truly anonymous?</h4>
            <p>Yes. No account, name, or personal data is ever required or stored. Every address and credential is randomly generated server-side.</p>
        </div>
    </div>
</div>

<footer>
    <p>© 2025 VaultMail · Disposable email with no strings attached · <a href="#">Privacy Policy</a></p>
</footer>

<div class="toast-wrap" id="toasts"></div>

<script>
    let token = null;
    let currentEmail = null;
    let messages = [];
    let refreshTimer = null;
    let progressTimer = null;
    const REFRESH_INTERVAL = 10000;

    function toast(msg, type = '') {
        const el = document.createElement('div');
        el.className = 'toast ' + type;
        el.textContent = msg;
        document.getElementById('toasts').appendChild(el);
        setTimeout(() => el.remove(), 3200);
    }

    function setLive(on) {
        document.getElementById('status-dot').className = 'status-dot' + (on ? ' live' : '');
        document.getElementById('email-bar').classList.toggle('active', on);
    }

    function startRefreshBar() {
        const bar = document.getElementById('refresh-bar');
        bar.style.transition = 'none';
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.transition = `width ${REFRESH_INTERVAL}ms linear`;
            bar.style.width = '100%';
        }, 50);
    }

    async function generateInbox() {
        const btn = document.getElementById('btn-generate');
        btn.disabled = true;
        btn.innerHTML = '<div class="spinner"></div> Generating…';
        try {
            const res = await fetch('/api/create_account', { method: 'POST' });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error);
            token = data.token;
            currentEmail = data.address;
            document.getElementById('email-addr').textContent = currentEmail;
            document.getElementById('btn-copy').disabled = false;
            document.getElementById('btn-refresh').disabled = false;
            document.getElementById('btn-delete').disabled = false;
            setLive(true);
            toast('✅ Inbox generated!', 'success');
            await refreshInbox();
            if (refreshTimer) clearInterval(refreshTimer);
            refreshTimer = setInterval(() => { refreshInbox(); startRefreshBar(); }, REFRESH_INTERVAL);
            startRefreshBar();
        } catch (e) {
            toast('❌ ' + e.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '⚡ Generate';
        }
    }

    async function refreshInbox() {
        if (!token) return;
        try {
            const res = await fetch('/api/get_messages', {
                headers: { 'Authorization': token }
            });
            if (res.status === 401) { toast('Session expired — generate a new inbox.', 'error'); return; }
            messages = await res.json();
            renderMailList();
        } catch (e) { console.error(e); }
    }

    function renderMailList() {
        const list = document.getElementById('mail-list');
        const countEl = document.getElementById('msg-count');
        countEl.textContent = messages.length + (messages.length === 1 ? ' message' : ' messages');

        if (messages.length === 0) {
            list.innerHTML = `
                <div class="mail-empty">
                    <div class="mail-empty-icon">📭</div>
                    <p>No emails yet.</p>
                    <div class="tip">Inbox auto-refreshes every 10 seconds.<br>Send an email to your temp address!</div>
                </div>`;
            return;
        }

        list.innerHTML = messages.map(m => `
            <div class="mail-item" data-id="${escHtml(m.id)}">
                <div class="mail-from">${escHtml(m.from.address)}</div>
                <div class="mail-subject">${escHtml(m.subject || '(No Subject)')}</div>
                <div class="mail-time">${new Date(m.createdAt).toLocaleTimeString()}</div>
            </div>
        `).join('');

        list.querySelectorAll('.mail-item').forEach(item => {
            item.addEventListener('click', function () {
                openMessage(this.dataset.id, this);
            });
        });
    }

    async function openMessage(id, el) {
        document.querySelectorAll('.mail-item').forEach(i => i.classList.remove('active'));
        if (el) el.classList.add('active');

        const panel = document.getElementById('viewer-panel');
        panel.innerHTML = `<div class="viewer-empty"><div class="spinner" style="width:32px;height:32px;border-width:3px;"></div></div>`;

        try {
            const res = await fetch('/api/get_message/' + id, {
                headers: { 'Authorization': token }
            });
            if (!res.ok) throw new Error('Server returned ' + res.status);
            const msg = await res.json();

            let bodyHtml;
            if (msg.html && msg.html.length > 0) {
                bodyHtml = Array.isArray(msg.html) ? msg.html.join('') : msg.html;
            } else {
                bodyHtml = `<html><body style="font-family:monospace;padding:24px;background:#fff;color:#111;white-space:pre-wrap;font-size:13px;line-height:1.7;">${escHtml(msg.text || '(No content)')}</body></html>`;
            }

            const blob = new Blob([bodyHtml], { type: 'text/html' });
            const blobUrl = URL.createObjectURL(blob);

            panel.innerHTML = `
                <div class="viewer-header">
                    <div class="viewer-subject">${escHtml(msg.subject || '(No Subject)')}</div>
                    <div class="viewer-meta">
                        <div class="viewer-meta-item"><span class="viewer-meta-label">from</span> ${escHtml(msg.from.address)}</div>
                        <div class="viewer-meta-item"><span class="viewer-meta-label">at</span> ${new Date(msg.createdAt).toLocaleString()}</div>
                    </div>
                </div>
                <div class="viewer-body">
                    <iframe id="msg-iframe" sandbox="allow-popups allow-same-origin"></iframe>
                </div>`;

            const iframe = document.getElementById('msg-iframe');
            iframe.src = blobUrl;
            iframe.onload = () => URL.revokeObjectURL(blobUrl);
        } catch (e) {
            panel.innerHTML = `
                <div class="viewer-empty">
                    <div class="viewer-empty-icon">⚠️</div>
                    <p style="color:#ff6b85;font-size:12px;">Failed to load message.<br>${escHtml(e.message)}</p>
                </div>`;
            toast('Failed to load message', 'error');
        }
    }

    function copyEmail() {
        if (!currentEmail) return;
        navigator.clipboard.writeText(currentEmail);
        const btn = document.getElementById('btn-copy');
        btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="var(--cyan)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:16px;height:16px"><polyline points="20 6 9 17 4 12"/></svg>`;
        setTimeout(() => {
            btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
        }, 2000);
        toast('📋 Address copied!', 'success');
    }

    function deleteInbox() {
        if (!confirm('Delete this inbox permanently? This cannot be undone.')) return;
        setLive(false);
        if (refreshTimer) clearInterval(refreshTimer);
        location.reload();
    }

    function escHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/create_account', methods=['POST'])
def create_account():
    try:
        d_res = requests.get(f"{API_URL}/domains")
        if d_res.status_code != 200:
            return jsonify({"error": "Mail server unavailable"}), 503
        domains = d_res.json().get('hydra:member', [])
        if not domains:
            return jsonify({"error": "No domains found"}), 500
        domain = domains[0]['domain']
        user = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        address = f"{user}@{domain}"
        password = secrets.token_urlsafe(15)
        reg = requests.post(f"{API_URL}/accounts", json={"address": address, "password": password})
        if reg.status_code != 201:
            return jsonify({"error": "Account creation failed"}), 400
        tok = requests.post(f"{API_URL}/token", json={"address": address, "password": password})
        token_data = tok.json()
        return jsonify({"address": address, "token": token_data.get('token')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_messages')
def get_messages():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify([]), 401
    r = requests.get(f"{API_URL}/messages", headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200:
        return jsonify([]), r.status_code
    return jsonify(r.json().get('hydra:member', []))

@app.route('/api/get_message/<path:msg_id>')
def get_message(msg_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    r = requests.get(f"{API_URL}/messages/{msg_id}", headers={"Authorization": f"Bearer {token}"})
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(debug=True, port=5000)