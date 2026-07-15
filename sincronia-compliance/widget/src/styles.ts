export const CSS_TEXT = `
:host, .scw-root {
  all: initial;
  display: block;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif;
  color-scheme: dark;
}
.scw-root * {
  box-sizing: border-box;
  font-family: inherit;
}
.scw-root {
  --bg: #05070d;
  --surface: #0b0f1a;
  --surface-raised: #101625;
  --border: #1e2434;
  --fg: #e8ecf5;
  --muted: #8992a9;
  --accent: #4f6bff;
  --accent-soft: #7c93ff;
  --accent-contrast: #04060c;
  --risk-unacceptable: #ef4444;
  --risk-high: #f97316;
  --risk-limited: #eab308;
  --risk-minimal: #22c55e;

  background: var(--bg);
  color: var(--fg);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 24px;
  max-width: 720px;
  line-height: 1.5;
  font-size: 14px;
}
.scw-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.scw-brand { font-weight: 600; font-size: 15px; }
.scw-brand span { color: var(--accent); }
.scw-subtitle { color: var(--muted); font-size: 12px; margin-top: 2px; }
.scw-lang-btn {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.scw-lang-btn:hover { color: var(--fg); border-color: var(--accent); }

.scw-steps { display: flex; gap: 6px; margin-bottom: 20px; }
.scw-step-dot { height: 5px; flex: 1; border-radius: 999px; background: var(--border); }
.scw-step-dot.active { background: var(--accent); }

h2.scw-title { font-size: 19px; font-weight: 600; margin: 0 0 4px; letter-spacing: -0.01em; }
p.scw-desc { color: var(--muted); font-size: 13px; margin: 0 0 18px; }

.scw-field { margin-bottom: 18px; }
.scw-label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 8px; }
.scw-input {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  color: var(--fg);
  font-size: 13px;
}
.scw-input:focus { outline: none; border-color: var(--accent); }

.scw-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.scw-card {
  border: 1px solid var(--border);
  background: var(--surface-raised);
  border-radius: 12px;
  padding: 12px;
  cursor: pointer;
  text-align: left;
  color: var(--fg);
  font-size: 13px;
}
.scw-card:hover { border-color: rgba(79,107,255,0.5); }
.scw-card.selected { border-color: var(--accent); background: rgba(79,107,255,0.1); }
.scw-card-title { font-weight: 600; font-size: 13px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.scw-tag {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 1px 7px;
  font-size: 10px;
  color: var(--muted);
}
.scw-card-desc { color: var(--muted); font-size: 12px; margin-top: 4px; }

.scw-toggle-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border);
}
.scw-toggle-row:last-child { border-bottom: none; }
.scw-toggle-q { color: var(--muted); font-size: 12.5px; flex: 1; }
.scw-toggle-group { display: flex; border: 1px solid var(--border); border-radius: 999px; overflow: hidden; flex-shrink: 0; }
.scw-toggle-btn { padding: 6px 12px; font-size: 12px; font-weight: 600; background: var(--surface); color: var(--muted); cursor: pointer; border: none; }
.scw-toggle-btn.active { background: var(--accent); color: var(--accent-contrast); }

.scw-tool-block { border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-bottom: 12px; background: var(--surface-raised); }
.scw-tool-name { font-size: 13px; font-weight: 600; margin-bottom: 6px; }

.scw-actions { display: flex; justify-content: space-between; margin-top: 22px; }
.scw-btn {
  border-radius: 999px;
  padding: 9px 18px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}
.scw-btn.primary { background: var(--accent); color: var(--accent-contrast); }
.scw-btn.primary:hover { background: var(--accent-soft); }
.scw-btn.primary:disabled { opacity: 0.5; cursor: not-allowed; }
.scw-btn.secondary { background: var(--surface-raised); border: 1px solid var(--border); color: var(--fg); }
.scw-btn.ghost { background: transparent; color: var(--muted); }
.scw-btn.ghost:disabled { visibility: hidden; }

.scw-badge {
  display: inline-flex; align-items: center; gap: 6px;
  border-radius: 999px; padding: 5px 12px; font-size: 12px; font-weight: 600; border: 1px solid;
}
.scw-badge .dot { width: 7px; height: 7px; border-radius: 999px; }
.scw-badge.unacceptable { color: var(--risk-unacceptable); border-color: rgba(239,68,68,0.4); background: rgba(239,68,68,0.1); }
.scw-badge.unacceptable .dot { background: var(--risk-unacceptable); }
.scw-badge.high { color: var(--risk-high); border-color: rgba(249,115,22,0.4); background: rgba(249,115,22,0.1); }
.scw-badge.high .dot { background: var(--risk-high); }
.scw-badge.limited { color: var(--risk-limited); border-color: rgba(234,179,8,0.4); background: rgba(234,179,8,0.1); }
.scw-badge.limited .dot { background: var(--risk-limited); }
.scw-badge.minimal { color: var(--risk-minimal); border-color: rgba(34,197,94,0.4); background: rgba(34,197,94,0.1); }
.scw-badge.minimal .dot { background: var(--risk-minimal); }

.scw-overall { text-align: center; border: 1px solid var(--border); border-radius: 14px; padding: 18px; margin-bottom: 18px; }
.scw-overall-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); margin-bottom: 8px; }
.scw-overall-summary { color: var(--muted); font-size: 12.5px; margin-top: 10px; max-width: 440px; margin-left: auto; margin-right: auto; }

.scw-alert { border: 1px solid rgba(249,115,22,0.3); background: rgba(249,115,22,0.06); border-radius: 12px; padding: 12px 14px; margin-bottom: 12px; }
.scw-alert-title { font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.scw-alert-body { font-size: 12px; color: var(--muted); }

.scw-articles { display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0; }
.scw-article-chip { border: 1px solid var(--border); background: var(--surface); border-radius: 999px; padding: 4px 10px; font-size: 11px; color: var(--muted); }

.scw-obl-title { font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); margin: 10px 0 6px; }
.scw-obl-item { margin-bottom: 8px; }
.scw-obl-label { font-weight: 600; font-size: 12.5px; }
.scw-obl-desc { color: var(--muted); font-size: 12px; }

.scw-warning { display: flex; gap: 8px; font-size: 12px; color: var(--muted); background: rgba(234,179,8,0.06); border: 1px solid rgba(234,179,8,0.25); border-radius: 10px; padding: 8px 10px; margin-top: 6px; }

.scw-footer { text-align: center; margin-top: 22px; }
.scw-footer-note { color: var(--muted); font-size: 11px; margin-bottom: 14px; }
.scw-powered { text-align: center; margin-top: 16px; font-size: 11px; color: var(--muted); }
.scw-powered a { color: var(--accent-soft); text-decoration: none; }

.scw-center { text-align: center; }
.scw-mt-14 { margin-top: 14px; }
.scw-row-between { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.scw-actions-center { justify-content: center; gap: 10px; }

@media (max-width: 480px) {
  .scw-grid { grid-template-columns: 1fr; }
}
`;
