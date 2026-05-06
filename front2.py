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
    <title>VoidMail — Vanishing Inbox</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg-deep: #060810;
            --bg-mid: #0d1117;
            --bg-surface: #111720;
            --bg-glass: rgba(255,255,255,0.04);
            --bg-glass-hover: rgba(255,255,255,0.07);
            --border: rgba(255,255,255,0.07);
            --border-bright: rgba(0,225,255,0.25);
            --cyan: #00e5ff;
            --cyan-dim: rgba(0,229,255,0.12);
            --cyan-glow: rgba(0,229,255,0.35);
            --magenta: #ff2d78;
            --gold: #ffd166;
            --text-primary: #e8edf5;
            --text-secondary: #7a8599;
            --text-dim: #3d4659;
            --radius-sm: 8px;
            --radius: 14px;
            --radius-lg: 20px;
        }

        html { scroll-behavior: smooth; }

        body {
            font-family: 'Syne', sans-serif;
            background: var(--bg-deep);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ─── BACKGROUND EFFECTS ─── */
        .bg-orbs {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }
        .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(120px);
            opacity: 0.18;
        }
        .orb-1 { width: 600px; height: 600px; background: #00e5ff; top: -200px; left: -200px; animation: drift1 18s ease-in-out infinite; }
        .orb-2 { width: 500px; height: 500px; background: #ff2d78; bottom: -200px; right: -150px; animation: drift2 22s ease-in-out infinite; }
        .orb-3 { width: 350px; height: 350px; background: #7c3aed; top: 40%; left: 50%; transform: translate(-50%,-50%); animation: drift3 15s ease-in-out infinite; }

        @keyframes drift1 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(60px,40px)} }
        @keyframes drift2 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-50px,-30px)} }
        @keyframes drift3 { 0%,100%{transform:translate(-50%,-50%)} 50%{transform:translate(-40%,-60%)} }

        /* Grid overlay */
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image: linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
            background-size: 60px 60px;
            pointer-events: none;
            z-index: 0;
        }

        /* ─── LAYOUT ─── */
        .wrap { position: relative; z-index: 1; }

        /* ─── NAV ─── */
        nav {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 40px;
            height: 64px;
            border-bottom: 1px solid var(--border);
            background: rgba(6,8,16,0.85);
            backdrop-filter: blur(24px);
            position: sticky;
            top: 0;
            z-index: 200;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-decoration: none;
        }
        .logo-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--cyan), #7c3aed);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            box-shadow: 0 0 20px var(--cyan-glow);
        }
        .logo-text { color: var(--text-primary); }
        .logo-text span { color: var(--cyan); }

        .nav-pill {
            background: var(--bg-glass);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .nav-pill-dot {
            width: 6px;
            height: 6px;
            background: #22c55e;
            border-radius: 50%;
            box-shadow: 0 0 6px #22c55e;
            animation: pulse-dot 2s ease-in-out infinite;
        }
        @keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.4} }

        /* ─── HERO ─── */
        .hero {
            text-align: center;
            padding: 70px 20px 60px;
            position: relative;
        }
        .hero-eyebrow {
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: var(--cyan);
            margin-bottom: 20px;
            opacity: 0;
            animation: fadeUp 0.6s ease forwards 0.1s;
        }
        .hero h1 {
            font-size: clamp(36px, 6vw, 64px);
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -2px;
            margin-bottom: 18px;
            opacity: 0;
            animation: fadeUp 0.6s ease forwards 0.25s;
        }
        .hero h1 .gradient-text {
            background: linear-gradient(135deg, var(--cyan) 0%, #7c3aed 60%, var(--magenta) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .hero-sub {
            font-size: 16px;
            color: var(--text-secondary);
            max-width: 480px;
            margin: 0 auto 40px;
            line-height: 1.7;
            font-weight: 400;
            opacity: 0;
            animation: fadeUp 0.6s ease forwards 0.4s;
        }
        @keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }

        /* ─── EMAIL BAR ─── */
        .email-bar-wrap {
            max-width: 740px;
            margin: 0 auto;
            opacity: 0;
            animation: fadeUp 0.6s ease forwards 0.55s;
        }
        .email-bar {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 8px 8px 8px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        .email-bar.active {
            border-color: var(--border-bright);
            box-shadow: 0 0 0 1px var(--border-bright), 0 0 40px var(--cyan-dim);
        }
        .email-display {
            flex: 1;
            min-width: 0;
        }
        .email-label {
            font-family: 'DM Mono', monospace;
            font-size: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--text-dim);
            margin-bottom: 3px;
        }
        #email-addr {
            font-family: 'DM Mono', monospace;
            font-size: 15px;
            font-weight: 400;
            color: var(--cyan);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        #email-addr.placeholder {
            color: var(--text-dim);
            font-style: italic;
        }
        .bar-actions {
            display: flex;
            align-items: center;
            gap: 6px;
            flex-shrink: 0;
        }
        .icon-btn {
            width: 38px;
            height: 38px;
            border: 1px solid var(--border);
            background: var(--bg-glass);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--text-secondary);
            transition: all 0.2s;
            font-size: 16px;
        }
        .icon-btn:hover { border-color: var(--border-bright); color: var(--cyan); background: var(--cyan-dim); }
        .icon-btn:disabled { opacity: 0.3; cursor: not-allowed; }
        .icon-btn:disabled:hover { border-color: var(--border); color: var(--text-secondary); background: var(--bg-glass); }

        .sep { width: 1px; height: 28px; background: var(--border); flex-shrink: 0; }

        .btn-generate {
            background: linear-gradient(135deg, var(--cyan) 0%, #7c3aed 100%);
            color: #fff;
            border: none;
            border-radius: var(--radius-sm);
            padding: 0 20px;
            height: 40px;
            font-family: 'Syne', sans-serif;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.3px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 7px;
            transition: all 0.2s;
            white-space: nowrap;
            box-shadow: 0 4px 20px rgba(0,229,255,0.2);
        }
        .btn-generate:hover { transform: translateY(-1px); box-shadow: 0 8px 30px rgba(0,229,255,0.35); }
        .btn-generate:active { transform: translateY(0); }
        .btn-generate:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

        .btn-danger {
            background: rgba(255,45,120,0.08);
            color: var(--magenta);
            border: 1px solid rgba(255,45,120,0.25);
            border-radius: var(--radius-sm);
            padding: 0 14px;
            height: 40px;
            font-family: 'Syne', sans-serif;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
            white-space: nowrap;
        }
        .btn-danger:hover { background: rgba(255,45,120,0.15); }
        .btn-danger:disabled { opacity: 0.3; cursor: not-allowed; }

        /* ─── MAIN LAYOUT ─── */
        .main-grid {
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 16px;
            max-width: 1200px;
            margin: 0 auto;
            padding: 28px 24px 60px;
        }
        @media(max-width: 860px) { .main-grid { grid-template-columns: 1fr; } }

        /* ─── PANELS ─── */
        .panel {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .panel-head {
            padding: 16px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }
        .panel-title {
            font-family: 'DM Mono', monospace;
            font-size: 10px;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: var(--text-dim);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .panel-title-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--cyan);
            box-shadow: 0 0 8px var(--cyan);
        }
        .count-badge {
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            background: var(--cyan-dim);
            color: var(--cyan);
            border: 1px solid rgba(0,229,255,0.2);
            padding: 3px 10px;
            border-radius: 20px;
        }

        /* ─── MAIL LIST ─── */
        .mail-list {
            flex: 1;
            overflow-y: auto;
            min-height: 420px;
            max-height: 580px;
            scrollbar-width: thin;
            scrollbar-color: var(--border) transparent;
        }
        .mail-list::-webkit-scrollbar { width: 4px; }
        .mail-list::-webkit-scrollbar-track { background: transparent; }
        .mail-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

        .mail-empty {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            min-height: 320px;
            gap: 14px;
            padding: 40px 24px;
        }
        .mail-empty-glyph {
            font-size: 48px;
            filter: grayscale(1);
            opacity: 0.4;
        }
        .mail-empty-title {
            font-size: 14px;
            font-weight: 700;
            color: var(--text-dim);
        }
        .mail-empty-sub {
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: var(--text-dim);
            text-align: center;
            line-height: 1.8;
        }

        .mail-item {
            padding: 14px 20px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.15s;
            position: relative;
        }
        .mail-item::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: var(--cyan);
            opacity: 0;
            transition: opacity 0.15s;
        }
        .mail-item:hover { background: var(--bg-glass-hover); }
        .mail-item:hover::before { opacity: 0.5; }
        .mail-item.active { background: var(--cyan-dim); }
        .mail-item.active::before { opacity: 1; }

        .mail-from {
            font-size: 13px;
            font-weight: 700;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 5px;
        }
        .mail-subject {
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .mail-time {
            font-family: 'DM Mono', monospace;
            font-size: 10px;
            color: var(--text-dim);
            margin-top: 6px;
        }
        .mail-unread-dot {
            position: absolute;
            top: 50%;
            right: 16px;
            transform: translateY(-50%);
            width: 7px;
            height: 7px;
            background: var(--cyan);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--cyan);
        }

        /* ─── VIEWER ─── */
        .viewer-empty {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            min-height: 520px;
            gap: 16px;
            padding: 40px;
        }
        .viewer-empty-glyph {
            font-size: 56px;
            opacity: 0.25;
            filter: grayscale(1);
        }
        .viewer-empty-text {
            font-size: 14px;
            color: var(--text-dim);
            text-align: center;
        }

        .viewer-head {
            padding: 20px 24px;
            border-bottom: 1px solid var(--border);
            flex-shrink: 0;
        }
        .viewer-subject {
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.3px;
            color: var(--text-primary);
            margin-bottom: 8px;
        }
        .viewer-meta {
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: var(--text-secondary);
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
        }
        .viewer-meta-chip {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .viewer-meta-chip span:first-child { color: var(--text-dim); }

        .viewer-body {
            flex: 1;
        }
        .viewer-body iframe {
            width: 100%;
            height: 520px;
            border: none;
            background: #fff;
        }

        /* ─── SPINNER ─── */
        .spinner {
            width: 18px;
            height: 18px;
            border: 2px solid rgba(255,255,255,0.2);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
            display: inline-block;
            flex-shrink: 0;
        }
        .spinner-cyan {
            border-color: var(--cyan-dim);
            border-top-color: var(--cyan);
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ─── TOASTS ─── */
        .toast-wrap {
            position: fixed;
            bottom: 28px;
            right: 28px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 8px;
            pointer-events: none;
        }
        .toast {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 13px 18px;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 600;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            animation: toastIn 0.3s cubic-bezier(0.175,0.885,0.32,1.275) forwards;
            display: flex;
            align-items: center;
            gap: 9px;
            backdrop-filter: blur(12px);
        }
        .toast.success { border-color: rgba(0,229,255,0.3); }
        .toast.error { border-color: rgba(255,45,120,0.3); }
        @keyframes toastIn {
            from { opacity: 0; transform: translateY(12px) scale(0.95); }
            to   { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* ─── FEATURES SECTION ─── */
        .features {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px 80px;
        }
        .section-label {
            font-family: 'DM Mono', monospace;
            font-size: 10px;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: var(--cyan);
            margin-bottom: 12px;
        }
        .section-title {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 32px;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-bottom: 56px;
        }
        .feature-card {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 24px;
            transition: border-color 0.2s, transform 0.2s;
            position: relative;
            overflow: hidden;
        }
        .feature-card::after {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, var(--cyan-dim) 0%, transparent 60%);
            opacity: 0;
            transition: opacity 0.3s;
        }
        .feature-card:hover { border-color: var(--border-bright); transform: translateY(-2px); }
        .feature-card:hover::after { opacity: 1; }
        .feature-icon {
            font-size: 28px;
            margin-bottom: 14px;
            display: block;
        }
        .feature-title {
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .feature-desc {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.7;
            font-weight: 400;
        }

        /* ─── FAQ ─── */
        .faq-list { display: flex; flex-direction: column; gap: 10px; }
        .faq-item {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
        }
        .faq-q {
            padding: 18px 22px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            transition: color 0.2s;
        }
        .faq-q:hover { color: var(--cyan); }
        .faq-arrow { color: var(--text-dim); font-size: 18px; transition: transform 0.25s; }
        .faq-item.open .faq-arrow { transform: rotate(45deg); }
        .faq-a {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        .faq-item.open .faq-a { max-height: 200px; }
        .faq-a-inner {
            padding: 0 22px 18px;
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.8;
            font-weight: 400;
        }

        /* ─── FOOTER ─── */
        footer {
            border-top: 1px solid var(--border);
            padding: 28px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }
        .footer-text {
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: var(--text-dim);
        }
        .footer-text a { color: var(--cyan); text-decoration: none; }

        /* ─── TICKER STRIP ─── */
        .ticker {
            background: var(--cyan-dim);
            border-top: 1px solid rgba(0,229,255,0.12);
            border-bottom: 1px solid rgba(0,229,255,0.12);
            padding: 10px 0;
            overflow: hidden;
            margin-bottom: 0;
        }
        .ticker-inner {
            display: flex;
            gap: 60px;
            animation: ticker 20s linear infinite;
            width: max-content;
        }
        .ticker-item {
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            color: var(--cyan);
            white-space: nowrap;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .ticker-item::before { content: '//'; opacity: 0.4; }
        @keyframes ticker { from{transform:translateX(0)} to{transform:translateX(-50%)} }

        /* ─── COPY ICON ─── */
        .copy-icon { width: 16px; height: 16px; }
    </style>
</head>
<body>

<div class="bg-orbs">
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
</div>

<div class="wrap">

    <!-- NAV -->
    <nav>
        <a class="logo" href="#">
            <div class="logo-icon">✉</div>
            <span class="logo-text">Void<span>Mail</span></span>
        </a>
        <div class="nav-pill">
            <span class="nav-pill-dot"></span>
            Free &amp; Anonymous
        </div>
    </nav>

    <!-- TICKER -->
    <div class="ticker">
        <div class="ticker-inner">
            <span class="ticker-item">No registration</span>
            <span class="ticker-item">Instant inbox</span>
            <span class="ticker-item">Zero tracking</span>
            <span class="ticker-item">Auto-refresh every 10 sec</span>
            <span class="ticker-item">Cryptographic password</span>
            <span class="ticker-item">Burner address</span>
            <span class="ticker-item">Spam-proof</span>
            <span class="ticker-item">No registration</span>
            <span class="ticker-item">Instant inbox</span>
            <span class="ticker-item">Zero tracking</span>
            <span class="ticker-item">Auto-refresh every 10 sec</span>
            <span class="ticker-item">Cryptographic password</span>
            <span class="ticker-item">Burner address</span>
            <span class="ticker-item">Spam-proof</span>
        </div>
    </div>

    <!-- HERO -->
    <section class="hero">
        <div class="hero-eyebrow">// Disposable Temporary Email</div>
        <h1>Your Inbox.<br><span class="gradient-text">Gone in a Flash.</span></h1>
        <p class="hero-sub">Generate a burner email address in one click. No sign-up, no trace, no spam — ever.</p>
        <div class="email-bar-wrap">
            <div class="email-bar" id="email-bar">
                <div class="email-display">
                    <div class="email-label">// email address</div>
                    <div id="email-addr" class="placeholder">click generate to conjure your inbox…</div>
                </div>
                <div class="bar-actions">
                    <button class="icon-btn" id="btn-copy" onclick="copyEmail()" title="Copy address" disabled>
                        <svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                        </svg>
                    </button>
                    <button class="icon-btn" id="btn-refresh" onclick="refreshInbox()" title="Refresh" disabled>🔄</button>
                    <div class="sep"></div>
                    <button class="btn-generate" id="btn-generate" onclick="generateInbox()">
                        <span>⚡</span> Generate
                    </button>
                    <button class="btn-danger" id="btn-delete" onclick="deleteInbox()" disabled>🗑</button>
                </div>
            </div>
        </div>
    </section>

    <!-- MAIN PANELS -->
    <div class="main-grid">

        <!-- INBOX LIST -->
        <div class="panel">
            <div class="panel-head">
                <div class="panel-title">
                    <div class="panel-title-dot"></div>
                    Inbox
                </div>
                <div class="count-badge" id="msg-count">0 messages</div>
            </div>
            <div class="mail-list" id="mail-list">
                <div class="mail-empty">
                    <div class="mail-empty-glyph">📭</div>
                    <div class="mail-empty-title">Empty Void</div>
                    <div class="mail-empty-sub">Generate an address above.<br>Messages appear here automatically.</div>
                </div>
            </div>
        </div>

        <!-- MESSAGE VIEWER -->
        <div class="panel" id="viewer-panel">
            <div class="viewer-empty">
                <div class="viewer-empty-glyph">📩</div>
                <div class="viewer-empty-text">Select a message to read it.</div>
            </div>
        </div>

    </div>

    <!-- FEATURES -->
    <section class="features">
        <div class="section-label">// Why VoidMail</div>
        <div class="section-title">Your privacy, non-negotiable.</div>
        <div class="feature-grid">
            <div class="feature-card">
                <span class="feature-icon">🛡️</span>
                <div class="feature-title">Stay Anonymous</div>
                <p class="feature-desc">Your real inbox stays hidden. Share a burner address with any service — risk-free.</p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🚫</span>
                <div class="feature-title">Kill Spam at Source</div>
                <p class="feature-desc">Sign up for anything. When the spam starts, delete the address — done. No unsubscribing.</p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">⚡</span>
                <div class="feature-title">Zero Friction</div>
                <p class="feature-desc">No account. No credit card. No name. One click and you have a working inbox instantly.</p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🔐</span>
                <div class="feature-title">Cryptographically Secured</div>
                <p class="feature-desc">Each inbox is protected by a cryptographically random password nobody — including us — knows.</p>
            </div>
        </div>

        <div class="section-label">// FAQ</div>
        <div class="section-title">Common questions.</div>
        <div class="faq-list">
            <div class="faq-item">
                <div class="faq-q" onclick="toggleFaq(this)">
                    What exactly is a disposable email?
                    <span class="faq-arrow">+</span>
                </div>
                <div class="faq-a"><div class="faq-a-inner">A disposable (temporary) email is a short-lived inbox you can use instead of your real email. It receives messages normally — but vanishes when you delete it or close the app, leaving zero trace.</div></div>
            </div>
            <div class="faq-item">
                <div class="faq-q" onclick="toggleFaq(this)">
                    How long does my inbox last?
                    <span class="faq-arrow">+</span>
                </div>
                <div class="faq-a"><div class="faq-a-inner">Your inbox is valid for the duration of your browser session. Click "Delete" or close the tab and it's gone permanently — no recovery possible.</div></div>
            </div>
            <div class="faq-item">
                <div class="faq-q" onclick="toggleFaq(this)">
                    Can I send email from this address?
                    <span class="faq-arrow">+</span>
                </div>
                <div class="faq-a"><div class="faq-a-inner">No — VoidMail is receive-only. It's designed to receive verification and sign-up emails without exposing your real address.</div></div>
            </div>
            <div class="faq-item">
                <div class="faq-q" onclick="toggleFaq(this)">
                    Is this truly anonymous?
                    <span class="faq-arrow">+</span>
                </div>
                <div class="faq-a"><div class="faq-a-inner">Yes. No account, no personal details, no tracking cookies. The address and password are randomly generated server-side on every request.</div></div>
            </div>
        </div>
    </section>

    <!-- FOOTER -->
    <footer>
        <div class="footer-text">© 2025 VoidMail · Free disposable email · <a href="#">Privacy</a></div>
        <div class="footer-text">// auto-refresh every 10 seconds · receive-only</div>
    </footer>

</div>

<!-- TOASTS -->
<div class="toast-wrap" id="toasts"></div>

<script>
    let token = null;
    let currentEmail = null;
    let messages = [];

    /* ── TOAST ── */
    function toast(msg, type = '') {
        const el = document.createElement('div');
        el.className = 'toast ' + type;
        const icon = type === 'success' ? '✦' : type === 'error' ? '✕' : 'ℹ';
        el.innerHTML = `<span style="color:${type==='success'?'var(--cyan)':type==='error'?'var(--magenta)':'var(--text-secondary)'}">${icon}</span> ${escHtml(msg)}`;
        document.getElementById('toasts').appendChild(el);
        setTimeout(() => { el.style.opacity='0'; el.style.transform='translateY(8px)'; el.style.transition='all 0.25s'; setTimeout(()=>el.remove(),250); }, 2800);
    }

    /* ── GENERATE ── */
    async function generateInbox() {
        const btn = document.getElementById('btn-generate');
        btn.disabled = true;
        btn.innerHTML = '<div class="spinner"></div> Conjuring…';
        try {
            const res = await fetch('/api/create_account', { method: 'POST' });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error);
            token = data.token;
            currentEmail = data.address;
            const addrEl = document.getElementById('email-addr');
            addrEl.textContent = currentEmail;
            addrEl.classList.remove('placeholder');
            document.getElementById('email-bar').classList.add('active');
            document.getElementById('btn-copy').disabled = false;
            document.getElementById('btn-refresh').disabled = false;
            document.getElementById('btn-delete').disabled = false;
            toast('Inbox generated successfully', 'success');
            refreshInbox();
        } catch (e) {
            toast(e.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<span>⚡</span> Generate';
        }
    }

    /* ── REFRESH ── */
    async function refreshInbox() {
        if (!token) return;
        try {
            const res = await fetch('/api/get_messages', { headers: { 'Authorization': token } });
            if (res.status === 401) { toast('Session expired — generate a new inbox', 'error'); return; }
            messages = await res.json();
            renderMailList();
        } catch (e) { console.error(e); }
    }

    /* ── RENDER LIST ── */
    function renderMailList() {
        const list = document.getElementById('mail-list');
        const countEl = document.getElementById('msg-count');
        countEl.textContent = messages.length + ' message' + (messages.length !== 1 ? 's' : '');

        if (messages.length === 0) {
            list.innerHTML = `
                <div class="mail-empty">
                    <div class="mail-empty-glyph">📭</div>
                    <div class="mail-empty-title">No messages yet</div>
                    <div class="mail-empty-sub">Auto-refreshes every 10 seconds.<br>Go trigger a verification email.</div>
                </div>`;
            return;
        }

        list.innerHTML = messages.map(m => `
            <div class="mail-item" data-id="${escHtml(m.id)}">
                <div class="mail-unread-dot"></div>
                <div class="mail-from">${escHtml(m.from.address)}</div>
                <div class="mail-subject">${escHtml(m.subject || '(no subject)')}</div>
                <div class="mail-time">${new Date(m.createdAt).toLocaleTimeString()}</div>
            </div>
        `).join('');

        list.querySelectorAll('.mail-item').forEach(item => {
            item.addEventListener('click', function () {
                openMessage(this.dataset.id, this);
            });
        });
    }

    /* ── OPEN MESSAGE ── */
    async function openMessage(id, el) {
        document.querySelectorAll('.mail-item').forEach(i => i.classList.remove('active'));
        if (el) {
            el.classList.add('active');
            const dot = el.querySelector('.mail-unread-dot');
            if (dot) dot.remove();
        }

        const panel = document.getElementById('viewer-panel');
        panel.innerHTML = `<div class="viewer-empty"><div class="spinner spinner-cyan" style="width:32px;height:32px;"></div></div>`;

        try {
            const res = await fetch('/api/get_message/' + id, { headers: { 'Authorization': token } });
            if (!res.ok) throw new Error('Server returned ' + res.status);
            const msg = await res.json();

            let bodyHtml;
            if (msg.html && msg.html.length > 0) {
                bodyHtml = Array.isArray(msg.html) ? msg.html.join('') : msg.html;
            } else {
                bodyHtml = '<html><body style="font-family:monospace;padding:24px;color:#2d3748;background:#fff;white-space:pre-wrap;">'
                    + escHtml(msg.text || '(No content)')
                    + '</body></html>';
            }

            const blob = new Blob([bodyHtml], { type: 'text/html' });
            const blobUrl = URL.createObjectURL(blob);

            panel.innerHTML = `
                <div class="viewer-head">
                    <div class="viewer-subject">${escHtml(msg.subject || '(no subject)')}</div>
                    <div class="viewer-meta">
                        <div class="viewer-meta-chip"><span>From</span><span>${escHtml(msg.from.address)}</span></div>
                        <div class="viewer-meta-chip"><span>Received</span><span>${new Date(msg.createdAt).toLocaleString()}</span></div>
                    </div>
                </div>
                <div class="viewer-body">
                    <iframe id="msg-iframe" sandbox="allow-popups allow-same-origin" style="width:100%;height:520px;border:none;"></iframe>
                </div>`;

            document.getElementById('msg-iframe').src = blobUrl;
            document.getElementById('msg-iframe').onload = () => URL.revokeObjectURL(blobUrl);

        } catch (e) {
            panel.innerHTML = `
                <div class="viewer-empty">
                    <div style="font-size:40px;opacity:0.3">⚠</div>
                    <div style="color:var(--magenta);font-size:13px;text-align:center;">Failed to load message<br><span style="color:var(--text-dim)">${escHtml(e.message)}</span></div>
                </div>`;
            toast('Failed to load message', 'error');
        }
    }

    /* ── COPY ── */
    function copyEmail() {
        if (!currentEmail) return;
        navigator.clipboard.writeText(currentEmail).then(() => {
            const btn = document.getElementById('btn-copy');
            btn.innerHTML = `<svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="var(--cyan)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
            setTimeout(() => {
                btn.innerHTML = `<svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
            }, 1800);
            toast('Address copied to clipboard', 'success');
        });
    }

    /* ── DELETE ── */
    function deleteInbox() {
        if (!confirm('Permanently delete this inbox?')) return;
        location.reload();
    }

    /* ── FAQ TOGGLE ── */
    function toggleFaq(el) {
        const item = el.closest('.faq-item');
        item.classList.toggle('open');
    }

    /* ── UTILS ── */
    function escHtml(str) {
        if (!str) return '';
        return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    /* ── AUTO-REFRESH ── */
    setInterval(() => { if (token) refreshInbox(); }, 10000);
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