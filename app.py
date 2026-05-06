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
    <title>TempMail - Free Disposable Email Address</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --teal: #00b09b; --teal-dark: #008f7d; --teal-light: #e6f7f5;
            --teal-grad: linear-gradient(135deg, #00b09b, #96c93d);
            --bg: #f4f6f9; --white: #ffffff; --border: #e2e8f0;
            --text: #2d3748; --text2: #718096; --text3: #a0aec0;
            --danger: #e53e3e; --shadow: 0 2px 12px rgba(0,0,0,0.08); --radius: 10px;
        }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
        nav { background: var(--white); border-bottom: 1px solid var(--border); padding: 0 32px; height: 58px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,0,0,0.06); position: sticky; top: 0; z-index: 100; }
        .nav-logo { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 20px; color: var(--teal); text-decoration: none; }
        .nav-logo span { color: var(--text); }
        .nav-badge { background: var(--teal-grad); color: #fff; font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 20px; }
        .hero { background: var(--teal-grad); padding: 40px 32px 48px; text-align: center; color: #fff; }
        .hero h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
        .hero p { font-size: 15px; opacity: .88; max-width: 480px; margin: 0 auto 28px; }
        .email-bar { background: var(--white); border-radius: var(--radius); box-shadow: 0 4px 24px rgba(0,0,0,0.13); padding: 14px 16px; display: flex; align-items: center; gap: 10px; max-width: 700px; margin: 0 auto; }
        .email-icon { font-size: 22px; flex-shrink: 0; }
        #email-addr { flex: 1; font-size: 16px; font-weight: 600; color: var(--teal-dark); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
        .email-placeholder { color: var(--text3); font-weight: 400; font-size: 14px; }
        #btn-copy { background: none; border: none; cursor: pointer; padding: 6px; border-radius: 6px; color: var(--teal); display: flex; align-items: center; transition: background .15s; flex-shrink: 0; }
        #btn-copy:hover { background: var(--teal-light); }
        #btn-copy svg { width: 20px; height: 20px; }
        .divider-v { width: 1px; height: 28px; background: var(--border); flex-shrink: 0; }
        .btn { display: inline-flex; align-items: center; gap: 6px; padding: 9px 16px; border-radius: 8px; border: none; font-size: 13px; font-weight: 600; cursor: pointer; transition: opacity .15s, transform .1s; flex-shrink: 0; }
        .btn:active { transform: scale(.97); }
        .btn:disabled { opacity: .45; cursor: not-allowed; }
        .btn-teal { background: var(--teal-grad); color: #fff; }
        .btn-outline { background: none; border: 1.5px solid var(--border); color: var(--text2); }
        .btn-outline:hover { border-color: var(--teal); color: var(--teal); }
        .btn-danger { background: none; border: 1.5px solid #fca5a5; color: var(--danger); }
        .btn-danger:hover { background: #fff5f5; }
        .main-wrap { max-width: 1100px; margin: 0 auto; padding: 28px 20px; display: grid; grid-template-columns: 320px 1fr; gap: 20px; }
        @media(max-width: 720px) { .main-wrap { grid-template-columns: 1fr; } }
        .panel { background: var(--white); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; display: flex; flex-direction: column; }
        .panel-header { padding: 14px 18px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
        .panel-title { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .6px; color: var(--text2); }
        .badge-count { background: var(--teal-light); color: var(--teal-dark); font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 20px; }
        .mail-list { flex: 1; overflow-y: auto; min-height: 400px; max-height: 560px; }
        .mail-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 300px; color: var(--text3); text-align: center; padding: 32px; gap: 10px; }
        .mail-empty-icon { font-size: 44px; }
        .mail-empty p { font-size: 13px; line-height: 1.6; }
        .mail-item { padding: 14px 18px; border-bottom: 1px solid var(--border); cursor: pointer; transition: background .12s; }
        .mail-item:hover { background: var(--teal-light); }
        .mail-item.active { background: var(--teal-light); border-left: 3px solid var(--teal); }
        .mail-from { font-size: 13px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }
        .mail-subject { font-size: 12px; color: var(--text2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .mail-time { font-size: 11px; color: var(--text3); margin-top: 4px; }
        .viewer-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 400px; color: var(--text3); text-align: center; gap: 12px; }
        .viewer-empty-icon { font-size: 52px; }
        .viewer-header { padding: 18px 22px; border-bottom: 1px solid var(--border); }
        .viewer-subject { font-size: 17px; font-weight: 700; color: var(--text); margin-bottom: 6px; }
        .viewer-meta { font-size: 12px; color: var(--text2); }
        .viewer-body { flex: 1; padding: 0; overflow: hidden; }
        .viewer-body iframe { width: 100%; height: 500px; border: none; }
        .spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,.4); border-top-color: #fff; border-radius: 50%; animation: spin .7s linear infinite; display: inline-block; }
        .spinner-teal { border-color: var(--teal-light); border-top-color: var(--teal); }
        @keyframes spin { to { transform: rotate(360deg); } }
        .toast-wrap { position: fixed; bottom: 24px; right: 24px; z-index: 999; display: flex; flex-direction: column; gap: 8px; }
        .toast { background: var(--text); color: #fff; padding: 11px 18px; border-radius: 8px; font-size: 13px; box-shadow: 0 4px 16px rgba(0,0,0,.18); animation: slideIn .25s ease; }
        .toast.success { background: var(--teal); }
        .toast.error { background: var(--danger); }
        @keyframes slideIn { from { transform: translateY(16px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .info-section { max-width: 1100px; margin: 0 auto 48px; padding: 0 20px; }
        .info-section h2 { font-size: 22px; font-weight: 700; margin-bottom: 20px; color: var(--text); }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 36px; }
        .info-card { background: var(--white); border-radius: var(--radius); padding: 22px; box-shadow: var(--shadow); }
        .info-card-icon { font-size: 28px; margin-bottom: 12px; }
        .info-card h3 { font-size: 15px; font-weight: 700; margin-bottom: 8px; }
        .info-card p { font-size: 13px; color: var(--text2); line-height: 1.7; }
        .faq { display: flex; flex-direction: column; gap: 14px; }
        .faq-item { background: var(--white); border-radius: var(--radius); padding: 18px 22px; box-shadow: var(--shadow); }
        .faq-item h4 { font-size: 14px; font-weight: 600; margin-bottom: 6px; color: var(--teal-dark); }
        .faq-item p { font-size: 13px; color: var(--text2); line-height: 1.7; }
        footer { background: var(--white); border-top: 1px solid var(--border); text-align: center; padding: 22px; font-size: 12px; color: var(--text3); }
        footer a { color: var(--teal); text-decoration: none; }
    </style>
</head>
<body>

<nav>
    <a class="nav-logo" href="#"> ✉️ <span>Temp<b style="color:var(--teal)">Mail</b></span> </a>
    <span class="nav-badge">🆓 Free & Anonymous</span>
</nav>

<div class="hero">
    <h1>Disposable Temporary Email</h1>
    <p>Protect your real inbox. Generate a free temporary email address instantly — no sign-up required.</p>
    <div class="email-bar">
        <span class="email-icon">📬</span>
        <span id="email-addr"><span class="email-placeholder">Click "Generate" to get your temp email…</span></span>
        <button id="btn-copy" onclick="copyEmail()" title="Copy email address" disabled>
            <svg id="icon-copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
        </button>
        <div class="divider-v"></div>
        <button class="btn btn-teal" id="btn-generate" onclick="generateInbox()">⚡ Generate</button>
        <button class="btn btn-outline" id="btn-refresh" onclick="refreshInbox()" disabled>🔄 Refresh</button>
        <button class="btn btn-danger" id="btn-delete" onclick="deleteInbox()" disabled>🗑 Delete</button>
    </div>
</div>

<div class="main-wrap">
    <div class="panel">
        <div class="panel-header">
            <span class="panel-title">📥 Inbox</span>
            <span class="badge-count" id="msg-count">0 messages</span>
        </div>
        <div class="mail-list" id="mail-list">
            <div class="mail-empty">
                <div class="mail-empty-icon">📭</div>
                <p>Your inbox is empty.<br>Generate an address and wait for emails to arrive.</p>
            </div>
        </div>
    </div>
    <div class="panel" id="viewer-panel">
        <div class="viewer-empty">
            <div class="viewer-empty-icon">📧</div>
            <p style="font-size:14px; color:var(--text2)">Select a message to read it here.</p>
        </div>
    </div>
</div>

<div class="info-section">
    <h2>Why use a Temporary Email?</h2>
    <div class="info-grid">
        <div class="info-card"><div class="info-card-icon">🛡️</div><h3>Protect Your Privacy</h3><p>Keep your real email address private. Never expose it to sites you don't trust.</p></div>
        <div class="info-card"><div class="info-card-icon">🚫</div><h3>Stop Spam</h3><p>Use a disposable address for sign-ups and say goodbye to unsolicited marketing emails forever.</p></div>
        <div class="info-card"><div class="info-card-icon">⚡</div><h3>Instant & Free</h3><p>No registration, no credit card, no personal info required. Ready in one click.</p></div>
        <div class="info-card"><div class="info-card-icon">🔒</div><h3>Secure by Design</h3><p>Each inbox uses a cryptographically secure random password. Nobody else can access your temp mail.</p></div>
    </div>
    <h2>Frequently Asked Questions</h2>
    <div class="faq">
        <div class="faq-item"><h4>What is a temporary email address?</h4><p>A temporary (disposable) email address is a short-lived inbox you can use instead of your real email. It receives messages just like a normal address but disappears when you delete it or close the tab.</p></div>
        <div class="faq-item"><h4>How long does the inbox last?</h4><p>Your inbox is valid as long as your current browser session is active. When you click "Delete" or close the app, the address is gone permanently.</p></div>
        <div class="faq-item"><h4>Can I send emails from this address?</h4><p>No — this service is receive-only. It is designed purely to receive verification and sign-up emails safely.</p></div>
        <div class="faq-item"><h4>Is it really anonymous?</h4><p>Yes. No account, name, or personal data is ever required. The address and password are randomly generated on the server side every time.</p></div>
    </div>
</div>

<footer>
    <p>© 2025 TempMail · Free disposable email service · No registration required · <a href="#">Privacy</a></p>
</footer>

<div class="toast-wrap" id="toasts"></div>

<script>
    let token = null;
    let currentEmail = null;
    let messages = [];

    function toast(msg, type = '') {
        const el = document.createElement('div');
        el.className = 'toast ' + type;
        el.textContent = msg;
        document.getElementById('toasts').appendChild(el);
        setTimeout(() => el.remove(), 3000);
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
            toast('✅ New inbox generated!', 'success');
            refreshInbox();
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
            if (res.status === 401) { toast('Session expired. Generate a new inbox.', 'error'); return; }
            messages = await res.json();
            renderMailList();
        } catch (e) { console.error(e); }
    }

    function renderMailList() {
        const list = document.getElementById('mail-list');
        const count = document.getElementById('msg-count');
        count.textContent = messages.length + ' message' + (messages.length !== 1 ? 's' : '');

        if (messages.length === 0) {
            list.innerHTML = `<div class="mail-empty"><div class="mail-empty-icon">📭</div><p>No emails yet.<br>Emails auto-refresh every 10 seconds.</p></div>`;
            return;
        }

        // ✅ FIX: data-id instead of inline onclick
        list.innerHTML = messages.map(m => `
            <div class="mail-item" data-id="${escHtml(m.id)}">
                <div class="mail-from">${escHtml(m.from.address)}</div>
                <div class="mail-subject">${escHtml(m.subject || 'No Subject')}</div>
                <div class="mail-time">${new Date(m.createdAt).toLocaleTimeString()}</div>
            </div>
        `).join('');

        // ✅ FIX: addEventListener instead of inline onclick
        list.querySelectorAll('.mail-item').forEach(item => {
            item.addEventListener('click', function() {
                openMessage(this.dataset.id, this);
            });
        });
    }

    async function openMessage(id, el) {
        document.querySelectorAll('.mail-item').forEach(i => i.classList.remove('active'));
        if (el) el.classList.add('active');

        const panel = document.getElementById('viewer-panel');
        panel.innerHTML = '<div class="viewer-empty"><div class="spinner spinner-teal" style="width:28px;height:28px;"></div></div>';

        try {
            const res = await fetch('/api/get_message/' + id, {
                headers: { 'Authorization': token }
            });

            if (!res.ok) throw new Error('Server returned ' + res.status);

            const msg = await res.json();

            // ✅ FIX: msg.html is an array in mail.tm API
            let bodyHtml;
            if (msg.html && msg.html.length > 0) {
                bodyHtml = Array.isArray(msg.html) ? msg.html.join('') : msg.html;
            } else {
                bodyHtml = '<html><body><pre style="padding:16px;color:#2d3748;white-space:pre-wrap;">'
                    + escHtml(msg.text || '(No content)')
                    + '</pre></body></html>';
            }

            // ✅ FIX: Blob URL instead of srcdoc (no escaping issues)
            const blob = new Blob([bodyHtml], { type: 'text/html' });
            const blobUrl = URL.createObjectURL(blob);

            panel.innerHTML = `
                <div class="viewer-header">
                    <div class="viewer-subject">${escHtml(msg.subject || 'No Subject')}</div>
                    <div class="viewer-meta">From: ${escHtml(msg.from.address)} &nbsp;·&nbsp; ${new Date(msg.createdAt).toLocaleString()}</div>
                </div>
                <div class="viewer-body">
                    <iframe id="msg-iframe" sandbox="allow-popups allow-same-origin"
                        style="width:100%;height:500px;border:none;"></iframe>
                </div>
            `;

            document.getElementById('msg-iframe').src = blobUrl;
            document.getElementById('msg-iframe').onload = () => URL.revokeObjectURL(blobUrl);

        } catch(e) {
            panel.innerHTML = `
                <div class="viewer-empty">
                    <div class="viewer-empty-icon">⚠️</div>
                    <p style="color:var(--danger);font-size:13px;">Failed to load message.<br>${escHtml(e.message)}</p>
                </div>`;
            toast('Failed to load message', 'error');
        }
    }

    function copyEmail() {
        if (!currentEmail) return;
        navigator.clipboard.writeText(currentEmail);
        const btn = document.getElementById('btn-copy');
        btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px;color:#00b09b"><polyline points="20 6 9 17 4 12"/></svg>`;
        setTimeout(() => {
            btn.innerHTML = `<svg id="icon-copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
        }, 1800);
        toast('📋 Copied to clipboard!', 'success');
    }

    function deleteInbox() {
        if (!confirm('Delete this inbox? This cannot be undone.')) return;
        location.reload();
    }

    function escHtml(str) {
        if (!str) return '';
        return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

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

# ✅ FIX: <path:msg_id> handles all ID formats
@app.route('/api/get_message/<path:msg_id>')
def get_message(msg_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Unauthorized"}), 401
    r = requests.get(f"{API_URL}/messages/{msg_id}", headers={"Authorization": f"Bearer {token}"})
    return jsonify(r.json())

if __name__ == '__main__':
    app.run(debug=True, port=5000)