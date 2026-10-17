# ================================================================
# HireLens — Complete UI Redesign
# Production-grade aesthetic: dark luxury, editorial precision
# ================================================================

import os
import tempfile
import pandas as pd
import streamlit as st

from video_interview import render_video_interview_tab
from resume_parser import parse_resume
from ai_resume_parser import ai_parse_resume
from ai_jd_parser import ai_parse_jd
from ranking_engine import ai_score_candidate


# ── BRAND ────────────────────────────────────────────────────────
BRAND     = "HireLens"
TAGLINE   = "Screen, rank, and video-interview candidates — in one workflow."
LOGO_PATH = "assets/hirelens_logo.png"

st.set_page_config(page_title=BRAND, layout="wide", initial_sidebar_state="expanded")


# ================================================================
# GLOBAL CSS — Dark Luxury + Editorial precision
# Fonts: Sora (display) + DM Sans (body)
# ================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── TOKENS ─────────────────────────────────────── */
:root {
  --bg:        #07080f;
  --bg-1:      #0c0e1a;
  --bg-2:      #111321;
  --bg-3:      #161928;
  --panel:     #1a1d2e;
  --panel-2:   #1f2235;
  --border:    rgba(255,255,255,0.06);
  --border-2:  rgba(255,255,255,0.10);
  --border-3:  rgba(255,255,255,0.16);
  --text:      #f0f1f8;
  --text-2:    #9a9cb8;
  --text-3:    #5c5e7a;

  /* accent palette */
  --indigo:    #6366f1;
  --indigo-l:  #818cf8;
  --indigo-2:  #4338ca;
  --violet:    #8b5cf6;
  --cyan:      #06b6d4;
  --teal:      #14b8a6;
  --emerald:   #10b981;
  --amber:     #f59e0b;
  --rose:      #f43f5e;
  --slate:     #64748b;

  --r-sm: 8px;
  --r-md: 12px;
  --r-lg: 18px;
  --r-xl: 24px;

  --shadow-sm: 0 2px 8px rgba(0,0,0,0.4);
  --shadow-md: 0 4px 24px rgba(0,0,0,0.5);
  --shadow-lg: 0 8px 48px rgba(0,0,0,0.6);
  --glow-ind:  0 0 32px rgba(99,102,241,0.25);
  --glow-cyn:  0 0 32px rgba(6,182,212,0.2);
}

/* ── RESET & BASE ───────────────────────────────── */
*, *::before, *::after {
  font-family: 'DM Sans', sans-serif !important;
  box-sizing: border-box;
}
.stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* ── SIDEBAR ────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: var(--bg-1) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 260px !important;
}
[data-testid="stSidebarContent"] { padding: 28px 20px !important; }

.brand-wordmark {
  font-family: 'Sora', sans-serif !important;
  font-size: 22px !important;
  font-weight: 800 !important;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, #818cf8 0%, #06b6d4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
  margin-bottom: 6px;
}
.brand-sub {
  font-size: 11px !important;
  color: var(--text-3) !important;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 500 !important;
  display: block;
  margin-bottom: 32px;
}

/* sidebar nav radio */
div[data-testid="stSidebar"] .stRadio > div {
  gap: 4px !important;
}
div[data-testid="stSidebar"] .stRadio label {
  background: transparent !important;
  border: 1px solid transparent !important;
  border-radius: var(--r-md) !important;
  padding: 9px 14px !important;
  color: var(--text-2) !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  cursor: pointer !important;
  transition: all 0.15s !important;
  display: block !important;
}
div[data-testid="stSidebar"] .stRadio label:hover {
  background: var(--bg-2) !important;
  color: var(--text) !important;
  border-color: var(--border-2) !important;
}
div[data-testid="stSidebar"] .stRadio label[data-testid="stMarkdownContainer"] p {
  color: inherit !important;
  font-size: 13px !important;
}

/* sidebar divider */
.sidebar-divider {
  height: 1px;
  background: var(--border);
  margin: 20px 0;
}
.sidebar-section-label {
  font-size: 10px !important;
  font-weight: 600 !important;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-3) !important;
  margin-bottom: 10px;
  display: block;
}

/* sidebar job pills */
.job-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--r-md);
  border: 1px solid var(--border);
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.15s;
}
.job-pill:hover, .job-pill.active {
  background: var(--bg-2);
  border-color: var(--indigo);
}
.job-pill-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--indigo-l);
  flex-shrink: 0;
}
.job-pill-name {
  font-size: 12px !important;
  font-weight: 500 !important;
  color: var(--text) !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.job-pill-count {
  font-size: 10px !important;
  color: var(--text-3) !important;
  margin-left: auto;
}

/* ── TYPOGRAPHY ─────────────────────────────────── */
h1,h2,h3,h4,h5 {
  font-family: 'Sora', sans-serif !important;
  color: var(--text) !important;
  letter-spacing: -0.025em;
}
p, span, div, label, li, td, th {
  color: var(--text) !important;
}
.muted { color: var(--text-2) !important; }
.dimmed { color: var(--text-3) !important; }
code, pre {
  font-family: 'JetBrains Mono', monospace !important;
  background: var(--bg-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  color: var(--cyan) !important;
  font-size: 12px !important;
}

/* ── LAYOUT PRIMITIVES ──────────────────────────── */
.page-header {
  padding: 32px 0 24px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 32px;
}
.page-title {
  font-family: 'Sora', sans-serif !important;
  font-size: 28px !important;
  font-weight: 700 !important;
  letter-spacing: -0.03em;
  color: var(--text) !important;
  margin: 0 0 6px !important;
}
.page-subtitle {
  font-size: 14px !important;
  color: var(--text-2) !important;
}

/* ── CARDS ──────────────────────────────────────── */
.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 24px;
  margin-bottom: 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.card:hover { border-color: var(--border-2); }

.card-glass {
  background: rgba(26,29,46,0.7);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-2);
  border-radius: var(--r-lg);
  padding: 24px;
  margin-bottom: 16px;
}

.card-accent {
  background: linear-gradient(135deg,
    rgba(99,102,241,0.08) 0%,
    rgba(6,182,212,0.04) 100%);
  border: 1px solid rgba(99,102,241,0.2);
  border-radius: var(--r-lg);
  padding: 24px;
  margin-bottom: 16px;
}

.card-sm {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 16px 20px;
  margin-bottom: 10px;
}

/* ── HERO ───────────────────────────────────────── */
.hero-wrap {
  position: relative;
  overflow: hidden;
  border-radius: var(--r-xl);
  border: 1px solid var(--border-2);
  background:
    radial-gradient(ellipse 80% 60% at 15% -20%, rgba(99,102,241,0.18) 0%, transparent 70%),
    radial-gradient(ellipse 60% 50% at 85% 10%, rgba(6,182,212,0.12) 0%, transparent 60%),
    radial-gradient(ellipse 50% 80% at 50% 110%, rgba(139,92,246,0.08) 0%, transparent 60%),
    var(--bg-1);
  padding: 56px 52px;
  margin-bottom: 32px;
}
.hero-wrap::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255,255,255,0.025) 1px, transparent 1px);
  background-size: 32px 32px;
  pointer-events: none;
}
.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--indigo-l) !important;
  background: rgba(99,102,241,0.1);
  border: 1px solid rgba(99,102,241,0.25);
  border-radius: 999px;
  padding: 4px 14px;
  margin-bottom: 20px;
}
.hero-title {
  font-family: 'Sora', sans-serif !important;
  font-size: 52px !important;
  font-weight: 800 !important;
  letter-spacing: -0.04em;
  line-height: 1.05;
  margin: 0 0 20px !important;
  color: var(--text) !important;
}
.hero-title span {
  background: linear-gradient(135deg, #818cf8 0%, #06b6d4 50%, #10b981 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-body {
  font-size: 17px !important;
  color: var(--text-2) !important;
  line-height: 1.65;
  max-width: 580px;
  margin: 0 0 32px !important;
}
.hero-cta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, var(--indigo) 0%, var(--indigo-2) 100%);
  border: none;
  border-radius: 12px;
  color: white !important;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.01em;
  cursor: pointer;
  box-shadow: 0 4px 24px rgba(99,102,241,0.4);
  transition: all 0.2s;
  text-decoration: none;
}
.hero-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(99,102,241,0.55);
}
.hero-ghost {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 13px 24px;
  background: transparent;
  border: 1px solid var(--border-3);
  border-radius: 12px;
  color: var(--text-2) !important;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.hero-ghost:hover { border-color: var(--indigo); color: var(--indigo-l) !important; }

/* ── FEATURE CARDS ──────────────────────────────── */
.feat-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 28px 26px;
  position: relative;
  overflow: hidden;
  transition: all 0.25s;
}
.feat-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  opacity: 0;
  transition: opacity 0.25s;
}
.feat-card:hover { border-color: var(--border-2); transform: translateY(-3px); box-shadow: var(--shadow-md); }
.feat-card:hover::before { opacity: 1; }
.feat-card.ind::before { background: linear-gradient(90deg, var(--indigo), var(--violet)); }
.feat-card.cyn::before { background: linear-gradient(90deg, var(--cyan), var(--teal)); }
.feat-card.grn::before { background: linear-gradient(90deg, var(--emerald), var(--teal)); }
.feat-card.amb::before { background: linear-gradient(90deg, var(--amber), var(--rose)); }

.feat-icon {
  width: 44px; height: 44px;
  border-radius: var(--r-sm);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  margin-bottom: 18px;
}
.feat-icon.ind { background: rgba(99,102,241,0.12); }
.feat-icon.cyn { background: rgba(6,182,212,0.10); }
.feat-icon.grn { background: rgba(16,185,129,0.10); }
.feat-icon.amb { background: rgba(245,158,11,0.10); }
.feat-title {
  font-family: 'Sora', sans-serif !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em;
  margin: 0 0 8px !important;
  color: var(--text) !important;
}
.feat-desc {
  font-size: 13px !important;
  color: var(--text-2) !important;
  line-height: 1.6;
}

/* ── STEP FLOW ──────────────────────────────────── */
.step-item {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  padding: 28px;
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  background: var(--panel);
  margin-bottom: 12px;
  transition: border-color 0.2s;
}
.step-item:hover { border-color: var(--border-2); }
.step-num {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--indigo), var(--violet));
  display: flex; align-items: center; justify-content: center;
  font-family: 'Sora', sans-serif !important;
  font-size: 16px !important;
  font-weight: 800 !important;
  color: white !important;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(99,102,241,0.4);
}
.step-body h4 {
  font-family: 'Sora', sans-serif !important;
  font-size: 15px !important;
  font-weight: 700 !important;
  margin: 0 0 6px !important;
  color: var(--text) !important;
}
.step-body p {
  font-size: 13px !important;
  color: var(--text-2) !important;
  margin: 0 !important;
  line-height: 1.55;
}

/* ── STAT STRIP ─────────────────────────────────── */
.stat-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
  margin: 32px 0;
}
.stat-cell {
  background: var(--panel);
  padding: 28px 24px;
  text-align: center;
}
.stat-num {
  font-family: 'Sora', sans-serif !important;
  font-size: 36px !important;
  font-weight: 800 !important;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, var(--indigo-l), var(--cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
  line-height: 1;
  margin-bottom: 6px;
}
.stat-label {
  font-size: 12px !important;
  color: var(--text-3) !important;
  font-weight: 500 !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* ── KPI CARDS (dashboard metrics) ─────────────── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}
.kpi-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 20px;
  position: relative;
  overflow: hidden;
}
.kpi-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: var(--accent-grad, linear-gradient(90deg, var(--indigo), var(--cyan)));
}
.kpi-label {
  font-size: 11px !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-3) !important;
  margin-bottom: 8px;
  display: block;
}
.kpi-value {
  font-family: 'Sora', sans-serif !important;
  font-size: 30px !important;
  font-weight: 800 !important;
  letter-spacing: -0.03em;
  color: var(--text) !important;
  line-height: 1;
  margin-bottom: 4px;
  display: block;
}
.kpi-sub {
  font-size: 11px !important;
  color: var(--text-3) !important;
}

/* ── SCORE RING ─────────────────────────────────── */
.score-ring {
  width: 72px; height: 72px;
  border-radius: 50%;
  border: 3px solid var(--indigo);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Sora', sans-serif !important;
  font-size: 22px !important;
  font-weight: 800 !important;
  color: var(--indigo-l) !important;
  background: rgba(99,102,241,0.08);
  box-shadow: 0 0 24px rgba(99,102,241,0.3), inset 0 0 12px rgba(99,102,241,0.05);
  flex-shrink: 0;
}
.score-ring.high {
  border-color: var(--emerald);
  color: #34d399 !important;
  background: rgba(16,185,129,0.08);
  box-shadow: 0 0 24px rgba(16,185,129,0.25), inset 0 0 12px rgba(16,185,129,0.05);
}
.score-ring.mid {
  border-color: var(--amber);
  color: #fcd34d !important;
  background: rgba(245,158,11,0.08);
  box-shadow: 0 0 24px rgba(245,158,11,0.2), inset 0 0 12px rgba(245,158,11,0.05);
}
.score-ring.low {
  border-color: var(--rose);
  color: #fb7185 !important;
  background: rgba(244,63,94,0.08);
  box-shadow: 0 0 24px rgba(244,63,94,0.2), inset 0 0 12px rgba(244,63,94,0.05);
}

/* ── SKILL BAR ──────────────────────────────────── */
.skill-bar-wrap {
  margin-bottom: 14px;
}
.skill-bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.skill-bar-name {
  font-size: 12px !important;
  color: var(--text-2) !important;
  font-weight: 500 !important;
}
.skill-bar-pct {
  font-size: 12px !important;
  font-family: 'JetBrains Mono', monospace !important;
  color: var(--indigo-l) !important;
  font-weight: 500 !important;
}
.skill-bar-track {
  height: 6px;
  background: var(--bg-2);
  border-radius: 999px;
  overflow: hidden;
}
.skill-bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--indigo), var(--cyan));
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.skill-bar-fill.high { background: linear-gradient(90deg, var(--emerald), var(--teal)); }
.skill-bar-fill.mid  { background: linear-gradient(90deg, var(--amber), var(--rose)); }

/* ── CANDIDATE LEADERBOARD CARD ─────────────────── */
.cand-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 22px 24px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
.cand-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 3px;
  border-radius: 2px 0 0 2px;
  background: var(--cand-accent, var(--indigo));
  opacity: 0;
  transition: opacity 0.2s;
}
.cand-card:hover { border-color: var(--border-2); transform: translateX(3px); }
.cand-card:hover::before { opacity: 1; }
.cand-medal {
  font-size: 20px;
  flex-shrink: 0;
  width: 28px;
  text-align: center;
}
.cand-info { flex: 1; min-width: 0; }
.cand-name {
  font-family: 'Sora', sans-serif !important;
  font-size: 15px !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  margin: 0 0 4px !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.cand-meta {
  font-size: 12px !important;
  color: var(--text-3) !important;
  white-space: nowrap;
}
.cand-scores {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-shrink: 0;
}
.score-pill {
  text-align: center;
  min-width: 54px;
}
.score-pill-val {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  display: block;
  color: var(--text) !important;
  line-height: 1.2;
}
.score-pill-lbl {
  font-size: 9px !important;
  color: var(--text-3) !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.fit-badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px !important;
  font-weight: 600 !important;
  letter-spacing: 0.04em;
  flex-shrink: 0;
}
.fit-strong { background: rgba(16,185,129,0.12); color: #34d399 !important; border: 1px solid rgba(16,185,129,0.3); }
.fit-good   { background: rgba(6,182,212,0.10);  color: #22d3ee !important; border: 1px solid rgba(6,182,212,0.25); }
.fit-mod    { background: rgba(245,158,11,0.10); color: #fcd34d !important; border: 1px solid rgba(245,158,11,0.25); }
.fit-weak   { background: rgba(244,63,94,0.10);  color: #fb7185 !important; border: 1px solid rgba(244,63,94,0.25); }

/* ── TAGS ───────────────────────────────────────── */
.tag {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 11px !important;
  font-weight: 500 !important;
  margin: 2px 3px 2px 0;
  background: var(--bg-2);
  border: 1px solid var(--border-2);
  color: var(--text-2) !important;
  transition: border-color 0.15s;
}
.tag:hover { border-color: var(--indigo); color: var(--indigo-l) !important; }
.tag-green {
  background: rgba(16,185,129,0.08);
  border-color: rgba(16,185,129,0.2);
  color: #34d399 !important;
}
.tag-red {
  background: rgba(244,63,94,0.08);
  border-color: rgba(244,63,94,0.2);
  color: #fb7185 !important;
}
.tag-blue {
  background: rgba(99,102,241,0.08);
  border-color: rgba(99,102,241,0.2);
  color: var(--indigo-l) !important;
}
.tag-amber {
  background: rgba(245,158,11,0.08);
  border-color: rgba(245,158,11,0.2);
  color: #fcd34d !important;
}

/* ── EVIDENCE CARDS ─────────────────────────────── */
.evidence-card {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 14px 16px;
  margin-bottom: 8px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.evidence-card-icon {
  font-size: 14px;
  flex-shrink: 0;
  margin-top: 1px;
}
.evidence-card-req {
  font-size: 13px !important;
  font-weight: 600 !important;
  color: var(--text) !important;
  margin: 0 0 3px !important;
}
.evidence-card-ev {
  font-size: 12px !important;
  color: var(--text-2) !important;
  margin: 0 !important;
}
.conf-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px !important;
  font-weight: 600 !important;
  margin-left: auto;
  flex-shrink: 0;
}
.conf-high { background: rgba(16,185,129,0.12); color: #34d399 !important; }
.conf-med  { background: rgba(245,158,11,0.12); color: #fcd34d !important; }
.conf-low  { background: rgba(244,63,94,0.12);  color: #fb7185 !important; }

/* ── TIMELINE / SECTION HEADER ──────────────────── */
.section-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 28px 0 16px;
}
.section-num {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: rgba(99,102,241,0.12);
  border: 1px solid rgba(99,102,241,0.3);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--indigo-l) !important;
  flex-shrink: 0;
}
.section-title {
  font-family: 'Sora', sans-serif !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  margin: 0 !important;
}
.section-line {
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ── DIVIDERS ───────────────────────────────────── */
.divider { height: 1px; background: var(--border); margin: 24px 0; }
.divider-glow {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent);
  margin: 32px 0;
}

/* ── EXPANDER ICON OVERLAP FIX ──────────────────── */
/* Streamlit renders expander as: details > summary > [svg/icon] + [p with label] */
/* The icon and text overlap when the icon uses absolute/float positioning */
[data-testid="stExpander"] details summary {
  position: relative !important;
  padding-left: 16px !important;
  padding-right: 40px !important;
}
/* Push the toggle icon to the far right, away from label text */
[data-testid="stExpander"] details summary svg,
[data-testid="stExpander"] details summary [data-testid="stExpanderToggleIcon"] {
  position: absolute !important;
  right: 14px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  flex-shrink: 0 !important;
}
/* Ensure the label paragraph doesn't overlap with icon */
[data-testid="stExpander"] details summary p {
  margin: 0 !important;
  padding-right: 28px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  color: var(--text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: var(--panel) !important;
  border-radius: var(--r-xl) !important;
  padding: 5px !important;
  gap: 2px !important;
  border: 1px solid var(--border) !important;
  margin-bottom: 28px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 14px !important;
  color: var(--text-2) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  padding: 8px 20px !important;
  border: none !important;
  transition: all 0.2s !important;
  letter-spacing: 0.01em !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--indigo) 0%, var(--indigo-2) 100%) !important;
  color: white !important;
  font-weight: 700 !important;
  box-shadow: 0 2px 16px rgba(99,102,241,0.45) !important;
}
button[data-testid="baseButton-tab"]:hover:not([aria-selected="true"]) {
  background: var(--bg-2) !important;
  color: var(--text) !important;
}

/* Buttons */
.stButton > button {
  background: linear-gradient(135deg, var(--indigo) 0%, var(--indigo-2) 100%) !important;
  color: white !important;
  border-radius: var(--r-md) !important;
  padding: 10px 22px !important;
  border: none !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  letter-spacing: 0.01em !important;
  box-shadow: 0 2px 16px rgba(99,102,241,0.35) !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 24px rgba(99,102,241,0.5) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
button[kind="secondary"] {
  background: var(--bg-2) !important;
  border: 1px solid var(--border-2) !important;
  color: var(--text-2) !important;
  box-shadow: none !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
  background: var(--bg-2) !important;
  border: 1px solid var(--border-2) !important;
  border-radius: var(--r-md) !important;
  color: var(--text) !important;
  font-size: 14px !important;
  font-family: 'DM Sans', sans-serif !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--indigo) !important;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
  outline: none !important;
}
.stTextInput > label, .stTextArea > label, .stSelectbox > label {
  color: var(--text-2) !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  margin-bottom: 6px !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
  background: var(--bg-2) !important;
  border: 2px dashed var(--border-2) !important;
  border-radius: var(--r-lg) !important;
  padding: 20px !important;
  transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--indigo) !important;
  background: rgba(99,102,241,0.04) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { color: var(--text-2) !important; }

/* Expander — modern Streamlit selectors (replaces deprecated .streamlit-expanderHeader) */
[data-testid="stExpander"] {
  background: var(--panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  overflow: hidden !important;
  margin-bottom: 8px !important;
}
[data-testid="stExpander"]:hover {
  border-color: var(--border-2) !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] details summary {
  background: var(--panel) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  padding: 14px 18px !important;
  list-style: none !important;
  cursor: pointer !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 8px !important;
  transition: background 0.15s !important;
}
/* The actual expander header button */
[data-testid="stExpander"] > details > summary {
  padding: 12px 16px !important;
}
/* Hide the default marker arrow that causes overlap */
[data-testid="stExpander"] summary::-webkit-details-marker { display: none !important; }
[data-testid="stExpander"] summary::marker { display: none !important; }
/* Expander header via button selector (newer Streamlit versions) */
[data-testid="stExpanderToggleIcon"] {
  flex-shrink: 0 !important;
  margin-left: auto !important;
}
/* The text label inside the expander header — prevent it from running into the icon */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
details[data-testid="stExpander"] summary {
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  padding-right: 32px !important;
}
/* Expander content area */
[data-testid="stExpander"] > details > div,
[data-testid="stExpander"] .streamlit-expanderContent {
  background: var(--panel) !important;
  border-top: 1px solid var(--border) !important;
  padding: 16px 18px !important;
}

/* Metrics */
[data-testid="stMetric"] {
  background: var(--panel) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-md) !important;
  padding: 18px !important;
}
[data-testid="stMetricLabel"] {
  color: var(--text-3) !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  font-family: 'Sora', sans-serif !important;
  color: var(--text) !important;
  font-weight: 800 !important;
}

/* Alerts / info */
div[data-baseweb="notification"] {
  border-radius: var(--r-md) !important;
  background: var(--bg-2) !important;
  border: 1px solid var(--border) !important;
}
.stAlert { border-radius: var(--r-md) !important; }
[data-testid="stInfo"] {
  background: rgba(99,102,241,0.08) !important;
  border-color: rgba(99,102,241,0.25) !important;
}
[data-testid="stSuccess"] {
  background: rgba(16,185,129,0.08) !important;
  border-color: rgba(16,185,129,0.25) !important;
}
[data-testid="stWarning"] {
  background: rgba(245,158,11,0.08) !important;
  border-color: rgba(245,158,11,0.25) !important;
}
[data-testid="stError"] {
  background: rgba(244,63,94,0.08) !important;
  border-color: rgba(244,63,94,0.25) !important;
}

/* Progress bar */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--indigo), var(--cyan)) !important;
  border-radius: 999px !important;
}
.stProgress > div > div {
  background: var(--bg-2) !important;
  border-radius: 999px !important;
  height: 6px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--r-lg) !important;
  overflow: hidden !important;
}
.dvn-scroller { background: var(--panel) !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--indigo) !important; }

/* Checkbox / toggle */
.stCheckbox label { color: var(--text-2) !important; }
.stToggle label { color: var(--text-2) !important; font-size: 13px !important; }

/* Select box dropdown */
[data-baseweb="popover"] { background: var(--panel) !important; border: 1px solid var(--border-2) !important; }
[data-baseweb="menu"] { background: var(--panel) !important; }
[data-baseweb="list-item"] { color: var(--text) !important; }
[data-baseweb="list-item"]:hover { background: var(--bg-2) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-3); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--indigo); }

/* ── FORM STYLING ───────────────────────────────── */
[data-testid="stForm"] {
  background: linear-gradient(135deg,
    rgba(99,102,241,0.08) 0%,
    rgba(6,182,212,0.04) 100%) !important;
  border: 1px solid rgba(99,102,241,0.2) !important;
  border-radius: var(--r-lg) !important;
  padding: 20px 24px !important;
  margin-bottom: 16px !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden !important; }

/* Hide sidebar collapse button icon text bleed */
[data-testid="collapsedControl"] { display: none !important; }
button[kind="header"] { display: none !important; }
.css-1q1n0ol { display: none !important; }
section[data-testid="stSidebar"] > div:first-child > div:first-child > div > button {
  display: none !important;
}
/* Specifically target the keyboard_double_arrow Material icon */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarUserContent"] ~ div button {
  visibility: hidden !important;
  width: 0 !important;
  height: 0 !important;
  overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)


# ================================================================
# HELPERS
# ================================================================
def save_uploaded_file(uploaded_file):
    d = os.path.join(tempfile.gettempdir(), "hirelens_uploads")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, uploaded_file.name)
    with open(p, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return p


def tags(items, limit=30, color="default"):
    items = [x for x in (items or []) if isinstance(x, str) and x.strip()][:limit]
    if not items:
        st.markdown("<span style='color:var(--text-3);font-size:12px;'>None detected</span>", unsafe_allow_html=True)
        return
    cls_map = {"green": "tag-green", "red": "tag-red", "blue": "tag-blue", "amber": "tag-amber", "default": ""}
    cls = cls_map.get(color, "")
    html = "".join(f"<span class='tag {cls}'>{i}</span>" for i in items)
    st.markdown(html, unsafe_allow_html=True)


def skill_bar(label, value, color="ind"):
    pct = min(100, max(0, int(value)))
    bar_class = "high" if pct >= 70 else ("mid" if pct >= 40 else "")
    st.markdown(f"""
    <div class="skill-bar-wrap">
      <div class="skill-bar-header">
        <span class="skill-bar-name">{label}</span>
        <span class="skill-bar-pct">{pct}%</span>
      </div>
      <div class="skill-bar-track">
        <div class="skill-bar-fill {bar_class}" style="width:{pct}%"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def kpi_row(metrics: list):
    """metrics = [(label, value, sub, grad_class), ...]"""
    grads = {
        "ind": "linear-gradient(90deg,#6366f1,#8b5cf6)",
        "cyn": "linear-gradient(90deg,#06b6d4,#14b8a6)",
        "grn": "linear-gradient(90deg,#10b981,#06b6d4)",
        "amb": "linear-gradient(90deg,#f59e0b,#f43f5e)",
    }
    cols = st.columns(len(metrics))
    for (lbl, val, sub, gc), col in zip(metrics, cols):
        g = grads.get(gc, grads["ind"])
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="--accent-grad:{g}">
              <span class="kpi-label">{lbl}</span>
              <span class="kpi-value">{val}</span>
              <span class="kpi-sub">{sub}</span>
            </div>
            """, unsafe_allow_html=True)


def section_header(n, title):
    st.markdown(f"""
    <div class="section-header">
      <div class="section-num">{n}</div>
      <h3 class="section-title">{title}</h3>
      <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# SESSION STATE
# ================================================================
for k, v in [("jobs", {}), ("job_counter", 1), ("selected_job_id", None), ("view", "Home")]:
    if k not in st.session_state:
        st.session_state[k] = v


def get_current_job():
    jid = st.session_state.get("selected_job_id")
    return (jid, st.session_state["jobs"].get(jid)) if jid else (None, None)


# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown(f"""
    <span class="brand-wordmark">⬡ {BRAND}</span>
    <span class="brand-sub">AI Hiring Platform</span>
    """, unsafe_allow_html=True)

    st.session_state["view"] = st.radio(
        "Navigation",
        ["Home", "Dashboard"],
        index=0 if st.session_state["view"] == "Home" else 1,
        label_visibility="collapsed",
    )

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    # Active roles
    if st.session_state["jobs"]:
        st.markdown("<span class='sidebar-section-label'>Active Roles</span>", unsafe_allow_html=True)
        for jid, job in st.session_state["jobs"].items():
            is_active = st.session_state["selected_job_id"] == jid
            n_cands = len(job.get("candidates", []))
            n_scored = sum(1 for c in job.get("candidates", []) if c.get("scoring"))
            cls = "job-pill active" if is_active else "job-pill"
            if st.button(job["title"][:26], key=f"sb_sel_{jid}", use_container_width=True):
                st.session_state["selected_job_id"] = jid
                st.session_state["view"] = "Dashboard"
                st.rerun()
        st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)

    st.markdown("<span class='sidebar-section-label'>Developer</span>", unsafe_allow_html=True)
    developer_mode = st.toggle("Dev mode", value=False)
    st.markdown("<p style='font-size:11px;color:var(--text-3);margin-top:6px;'>Disable for HR demos</p>", unsafe_allow_html=True)


# ================================================================
# LANDING PAGE
# ================================================================
if st.session_state["view"] == "Home":

    # HERO
    st.markdown(f"""
    <div class="hero-wrap">
      <h1 class="hero-title">Hire the right people,<br><span>faster than ever.</span></h1>
      <p class="hero-body">
        HireLens combines AI resume parsing, multi-signal candidate ranking,
        and structured timed interviews into a single seamless workflow —
        so your team spends time on people, not paperwork.
      </p>
    </div>
    """, unsafe_allow_html=True)

    col_cta1, col_cta2, col_cta3 = st.columns([1, 1, 4])
    with col_cta1:
        if st.button("🚀  Launch App", key="hero_cta"):
            st.session_state["view"] = "Dashboard"
            st.rerun()
    with col_cta2:
        st.markdown("<span class='muted' style='display:block;padding-top:12px;font-size:12px;'>No signup · Free demo</span>", unsafe_allow_html=True)

    # STAT STRIP
    st.markdown("""
    <div class="stat-strip">
      <div class="stat-cell">
        <span class="stat-num">10×</span>
        <span class="stat-label">Faster Screening</span>
      </div>
      <div class="stat-cell">
        <span class="stat-num">4</span>
        <span class="stat-label">Scoring Signals</span>
      </div>
      <div class="stat-cell">
        <span class="stat-num">AI</span>
        <span class="stat-label">Semantic Match</span>
      </div>
      <div class="stat-cell">
        <span class="stat-num">∞</span>
        <span class="stat-label">Roles & Candidates</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # FEATURE GRID
    st.markdown("""
    <h2 style="font-family:'Sora',sans-serif;font-size:32px;font-weight:800;letter-spacing:-0.03em;margin-bottom:8px;">
      Everything your team needs
    </h2>
    <p style="color:var(--text-2);font-size:15px;margin-bottom:28px;">
      One platform. From JD to offer.
    </p>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    feats = [
        (f1, "ind", "🧠", "AI JD Parser", "Extracts every skill, tool, and requirement from any job description automatically."),
        (f2, "cyn", "📄", "Resume Intel", "Parses PDFs, DOCX, even scanned images — builds structured candidate profiles in seconds."),
        (f3, "grn", "📊", "Smart Ranking", "Multi-signal scoring: skill match, semantic AI, experience years, and interview performance."),
        (f4, "amb", "🎥", "Video Interviews", "Live Jitsi video rooms with AI-generated questions, real-time rubric scoring, and per-question timers."),
    ]
    for col, accent, icon, title, desc in feats:
        with col:
            st.markdown(f"""
            <div class="feat-card {accent}">
              <div class="feat-icon {accent}">{icon}</div>
              <div class="feat-title">{title}</div>
              <div class="feat-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)

    # HOW IT WORKS
    st.markdown("""
    <h2 style="font-family:'Sora',sans-serif;font-size:28px;font-weight:800;letter-spacing:-0.03em;margin-bottom:20px;">
      How it works
    </h2>
    """, unsafe_allow_html=True)

    steps = [
        ("1", "Create a Role", "Paste your job description. AI extracts skills, tools, seniority, and must-haves automatically."),
        ("2", "Upload Resumes", "Drop in any number of CVs — PDF, Word, or image. Each becomes a structured candidate profile."),
        ("3", "Compute Rankings", "4-signal scoring engine ranks every candidate with matched vs. missing skills and AI reasoning."),
        ("4", "Video Interview", "Launch a live Jitsi video room. AI generates 6 tailored questions per candidate. HR navigates through them during the call."),
    ]
    for n, title, desc in steps:
        st.markdown(f"""
        <div class="step-item">
          <div class="step-num">{n}</div>
          <div class="step-body">
            <h4>{title}</h4>
            <p>{desc}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)

    # FAQ
    st.markdown("<h2 style=\"font-family:'Sora',sans-serif;font-size:24px;font-weight:700;letter-spacing:-0.02em;margin-bottom:20px;\">FAQ</h2>", unsafe_allow_html=True)
    faq_items = [
        ("Is this an ATS?", "HireLens is a hiring intelligence layer — screening, ranking, and structured interviewing. ATS integrations can be added to production builds."),
        ("Are resumes stored?", "This is a demo. Data lives only in your browser session. Production deployments support encrypted storage."),
        ("What file formats work?", "PDF, DOCX, PNG and JPG — including scanned documents via OCR."),
        ("Can I use it for any role?", "Yes. The AI extracts context from whatever JD you paste. Works best with detailed descriptions."),
    ]
    for q, a in faq_items:
        with st.expander(q):
            st.write(a)

    st.markdown("""
    <div class="divider"></div>
    <p style="text-align:center;font-size:12px;color:var(--text-3);padding-bottom:24px;">
      © 2026 HireLens — Built for modern HR teams
    </p>
    """, unsafe_allow_html=True)
    st.stop()


# ================================================================
# DASHBOARD
# ================================================================
jid_top, job_top = get_current_job()

# Dashboard header
total_jobs = len(st.session_state["jobs"])
total_cands = sum(len(j.get("candidates", [])) for j in st.session_state["jobs"].values())
total_scored = sum(1 for j in st.session_state["jobs"].values() for c in j.get("candidates", []) if c.get("scoring"))

kpi_row([
    ("Active Roles", total_jobs or "—", "across all positions", "ind"),
    ("Total Candidates", total_cands or "—", "uploaded so far", "cyn"),
    ("Ranked", total_scored or "—", "candidates scored", "grn"),
    ("Selected Role", (job_top["title"][:20] + "…") if job_top else "None", "tap Roles tab to pick", "amb"),
])

tab_jobs, tab_candidates, tab_scoring, tab_video = st.tabs([
    "📌  Roles", "📂  Candidates", "📊  Ranking", "🎥  Video Interview"
])


# ================================================================
# ROLES TAB
# ================================================================
with tab_jobs:
    section_header("01", "Create a New Role")

    with st.form("job_form"):
        title = st.text_input("Role title", placeholder="e.g. Senior Backend Engineer")
        desc = st.text_area("Job description", height=180, placeholder="Paste the full job description here…")
        submitted = st.form_submit_button("✦  Create Role")

    if submitted:
        if not title.strip() or not desc.strip():
            st.error("Both fields are required.")
        else:
            jid = f"job_{st.session_state['job_counter']}"
            st.session_state["job_counter"] += 1
            st.session_state["jobs"][jid] = {
                "title": title.strip(),
                "description": desc.strip(),
                "ai_jd": None,
                "candidates": [],
            }
            st.session_state["selected_job_id"] = jid
            st.success(f"Role '{title.strip()}' created and selected.")

    # All roles
    if not st.session_state["jobs"]:
        st.markdown("<div class='card' style='text-align:center;padding:40px;'><p style='color:var(--text-3);'>No roles yet. Create your first role above.</p></div>", unsafe_allow_html=True)
    else:
        section_header("02", "All Roles")
        for jid, job in st.session_state["jobs"].items():
            is_sel = st.session_state["selected_job_id"] == jid
            n_c = len(job["candidates"])
            n_s = sum(1 for c in job["candidates"] if c.get("scoring"))
            border_style = "border-color: rgba(99,102,241,0.4) !important;" if is_sel else ""

            with st.expander(f"{'★ ' if is_sel else ''}{job['title']} · {n_c} candidates · {n_s} scored"):
                st.markdown(f"<p class='muted' style='font-size:13px;line-height:1.6;'>{job['description'][:400]}{'…' if len(job['description'])>400 else ''}</p>", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("🔍  Analyze Role", key=f"parse_{jid}"):
                        with st.spinner("Analyzing with AI…"):
                            result = ai_parse_jd(job["description"])
                        if result.get("error"):
                            st.error(f"Analysis failed: {result['error']}")
                        elif not result.get("role_title") and not result.get("required_tech_skills"):
                            st.error("Analysis returned empty. Check your API key.")
                        else:
                            job["ai_jd"] = result
                            st.success(f"Analyzed — {len(result.get('all_skills_extracted') or [])} skills found.")
                with c2:
                    if st.button("✓  Select Role", key=f"sel_{jid}"):
                        st.session_state["selected_job_id"] = jid
                        st.success("Role selected.")
                with c3:
                    if st.button("✕  Delete", key=f"del_{jid}"):
                        del st.session_state["jobs"][jid]
                        if st.session_state["selected_job_id"] == jid:
                            st.session_state["selected_job_id"] = None
                        st.rerun()

                if job.get("ai_jd"):
                    jd = job["ai_jd"]
                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

                    col_l, col_r = st.columns([1.2, 1])
                    with col_l:
                        st.markdown(f"<p style='font-size:13px;color:var(--text-2);line-height:1.65;'>{jd.get('role_summary','')}</p>", unsafe_allow_html=True)
                        st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-top:16px;margin-bottom:8px;'>Required Skills</p>", unsafe_allow_html=True)
                        tags((jd.get("required_tech_skills", []) or []) + (jd.get("tools", []) or []), limit=35, color="blue")

                    with col_r:
                        kpi_row([
                            ("Experience", f"{jd.get('experience_years_required', 0)}y", "required", "ind"),
                            ("Skills", str(len(jd.get("all_skills_extracted", []) or [])), "extracted", "cyn"),
                        ])
                        if jd.get("must_have"):
                            st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-bottom:8px;'>Must-Have</p>", unsafe_allow_html=True)
                            tags(jd.get("must_have", [])[:12], color="amber")

                    if developer_mode:
                        st.json(jd)


# ================================================================
# CANDIDATES TAB
# ================================================================
with tab_candidates:
    jid, job = get_current_job()

    if not job:
        st.info("Select a role first from the Roles tab.")
    else:
        st.markdown(f"<p style='font-size:12px;text-transform:uppercase;letter-spacing:0.1em;color:var(--text-3);margin-bottom:4px;'>Uploading to</p><h3 style='font-family:Sora,sans-serif;font-size:20px;font-weight:700;margin-top:0;'>{job['title']}</h3>", unsafe_allow_html=True)

        section_header("01", "Upload Resumes")
        files = st.file_uploader("Drop resumes here", type=["pdf", "docx", "png", "jpg", "jpeg"], accept_multiple_files=True)

        if st.button("⬆  Parse & Add Candidates"):
            if not files:
                st.error("Upload at least one resume first.")
            else:
                added, failed = 0, []
                prog = st.progress(0, text="Parsing resumes…")
                for i, f in enumerate(files):
                    try:
                        path = save_uploaded_file(f)
                        parsed = parse_resume(path)
                        raw_text = parsed.get("raw_text", "") or ""
                        if not raw_text.strip():
                            failed.append(f"{f.name} — no text extracted")
                            continue
                        structured = ai_parse_resume(raw_text)
                        name = parsed["contact"].get("name") or f.name.replace(".pdf","").replace(".docx","").replace(".png","").replace(".jpg","").replace(".jpeg","").replace("_"," ").replace("-"," ").strip()
                        job["candidates"].append({
                            "name": name,
                            "name_confirmed": bool(parsed["contact"].get("name")),
                            "file": f.name,
                            "raw_text": raw_text,
                            "old": parsed,
                            "ai": structured,
                        })
                        added += 1
                    except Exception as e:
                        failed.append(f"{f.name} — {str(e)[:100]}")
                    prog.progress((i+1)/len(files), text=f"Parsed {i+1}/{len(files)}…")
                prog.empty()
                if added:
                    st.success(f"✓ {added} candidate(s) added successfully.")
                for err in failed:
                    st.error(f"Skipped: {err}")

        if not job["candidates"]:
            st.markdown("<div class='card' style='text-align:center;padding:40px;'><p style='color:var(--text-3);'>No candidates yet. Upload resumes above.</p></div>", unsafe_allow_html=True)
        else:
            section_header("02", f"Candidate Profiles  ·  {len(job['candidates'])} uploaded")

            for idx, cand in enumerate(job["candidates"]):
                score = cand.get("scoring", {})
                final = score.get("final_score") if score else None
                ring = "high" if final and final >= 80 else ("mid" if final and final >= 55 else "low") if final else ""

                label = cand["name"] if cand.get("name_confirmed") else f"⚠  {cand['name']}"
                with st.expander(f"{label} {'· Score: ' + str(final) + '/100' if final else ''}"):

                    if not cand.get("name_confirmed"):
                        new_name = st.text_input("Confirm candidate name:", value=cand["name"], key=f"name_{idx}")
                        if st.button("Save name", key=f"nconf_{idx}"):
                            cand["name"] = new_name.strip() or cand["name"]
                            cand["name_confirmed"] = True
                            st.rerun()
                        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

                    col_l, col_r = st.columns([1.3, 1])

                    with col_l:
                        st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-bottom:8px;'>Summary</p>", unsafe_allow_html=True)
                        summary = cand["ai"].get("summary") or ""
                        st.markdown(f"<p style='font-size:13px;color:var(--text-2);line-height:1.65;'>{summary or 'No summary available.'}</p>", unsafe_allow_html=True)

                        exp_yr = cand["ai"].get("experience_years", 0)
                        titles = cand["ai"].get("job_titles", []) or []
                        kpi_row([
                            ("Experience", f"{exp_yr}y", "total", "ind"),
                            ("Last Title", (titles[0][:14] + "…") if titles else "—", titles[1] if len(titles) > 1 else "", "cyn"),
                        ])

                        st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-bottom:8px;margin-top:16px;'>Skills</p>", unsafe_allow_html=True)
                        all_skills = list(dict.fromkeys(
                            [s for s in (cand["ai"].get("tech_skills", []) or []) + (cand["ai"].get("tools", []) or []) + (cand["old"].get("skills", []) or []) if isinstance(s, str) and s.strip()]
                        ))
                        tags(all_skills, limit=40, color="blue")

                        soft = cand["ai"].get("soft_skills", []) or []
                        if soft:
                            st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin:12px 0 8px;'>Soft Skills</p>", unsafe_allow_html=True)
                            tags(soft, limit=15)

                    with col_r:
                        edu = cand["old"].get("education", []) or []
                        if edu:
                            st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-bottom:8px;'>Education</p>", unsafe_allow_html=True)
                            for e in edu[:2]:
                                line = e.get("raw_line", str(e)) if isinstance(e, dict) else str(e)
                                st.markdown(f"<p style='font-size:12px;color:var(--text-2);margin:0 0 4px;'>— {line}</p>", unsafe_allow_html=True)

                        exp_lines = cand["old"].get("experience_lines", []) or []
                        if exp_lines:
                            st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin:14px 0 8px;'>Work History</p>", unsafe_allow_html=True)
                            for ln in exp_lines[:4]:
                                st.markdown(f"<p style='font-size:12px;color:var(--text-2);margin:0 0 4px;'>— {ln}</p>", unsafe_allow_html=True)

                        if score:
                            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                            st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-bottom:10px;'>Score Breakdown</p>", unsafe_allow_html=True)
                            skill_bar("Skill Match", score.get("skill_match_percent", 0))
                            skill_bar("AI Semantic", score.get("ai_semantic_score", 0))
                            skill_bar("Experience", score.get("experience_score", 0))

                    if developer_mode:
                        st.json({"parsed": cand["old"], "ai": cand["ai"]})


# ================================================================
# RANKING TAB
# ================================================================
with tab_scoring:
    jid, job = get_current_job()

    if not job:
        st.info("Select a role first.")
    elif not job["candidates"]:
        st.info("Upload candidates first.")
    elif not job.get("ai_jd"):
        st.warning("Analyze the role first (Roles tab).")
    else:
        section_header("01", "Compute Rankings")
        st.markdown(f"<p class='muted' style='font-size:13px;margin-bottom:16px;'>{len(job['candidates'])} candidates · Role: {job['title']}</p>", unsafe_allow_html=True)

        if st.button("⚡  Run AI Ranking Engine"):
            total = len(job["candidates"])
            prog = st.progress(0)
            status = st.empty()
            errors = []
            for i, cand in enumerate(job["candidates"]):
                status.markdown(f"<p class='muted' style='font-size:13px;'>Scoring <b>{cand['name']}</b> ({i+1}/{total})…</p>", unsafe_allow_html=True)
                try:
                    cand["scoring"] = ai_score_candidate(
                        jd_text=job["description"],
                        jd_ai=job["ai_jd"],
                        resume_text=cand["raw_text"],
                        resume_ai=cand["ai"],
                    )
                except Exception as e:
                    errors.append(f"{cand['name']}: {str(e)[:100]}")
                prog.progress((i+1)/total)
            prog.empty()
            status.empty()
            for err in errors:
                st.error(err)
            scored = [c for c in job["candidates"] if c.get("scoring")]
            if scored:
                st.success(f"✓ Ranking complete — {len(scored)} candidates scored.")

        # LEADERBOARD
        scored_cands = sorted(
            [c for c in job["candidates"] if isinstance(c.get("scoring"), dict)],
            key=lambda c: c["scoring"].get("final_score", 0), reverse=True
        )

        if scored_cands:
            st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)
            section_header("02", "Leaderboard")

            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            fit_classes = {"Strong": "fit-strong", "Good": "fit-good", "Moderate": "fit-mod", "Weak": "fit-weak"}
            accent_colors = {"Strong": "#10b981", "Good": "#06b6d4", "Moderate": "#f59e0b", "Weak": "#f43f5e"}

            for rank, cand in enumerate(scored_cands, 1):
                r = cand["scoring"]
                final   = r.get("final_score", 0)
                fit     = r.get("fit_label", "—")
                sk_pct  = r.get("skill_match_percent", 0)
                ai_sc   = r.get("ai_semantic_score", 0)
                exp_sc  = r.get("experience_score", 0)

                ring_cls = "high" if final >= 80 else ("mid" if final >= 55 else "low")
                fit_cls  = fit_classes.get(fit, "")
                accent   = accent_colors.get(fit, "#6366f1")
                medal    = medals.get(rank, f"#{rank}")

                with st.expander(f"{medal} {cand['name']} · {final}/100 · {fit}", expanded=(rank == 1)):

                    # Build name safe string
                    name_safe = cand['name'].replace("<","&lt;").replace(">","&gt;")

                    # Top row: ring + name + fit badge
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:20px;margin-bottom:20px;">
                      <div class="score-ring {ring_cls}">{final}</div>
                      <div style="flex:1;">
                        <div style="font-family:Sora,sans-serif;font-size:18px;font-weight:700;color:var(--text);">{name_safe}</div>
                        <div style="font-size:12px;color:var(--text-3);margin-top:3px;">
                          Skill {r.get('skill_match_ratio_text','0/0')} &nbsp;·&nbsp; AI {ai_sc}/100 &nbsp;·&nbsp; Exp {exp_sc}/100
                        </div>
                      </div>
                      <span class="fit-badge {fit_cls}">{fit}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Score breakdown bars
                    col_bars, col_match = st.columns([1, 1])
                    with col_bars:
                        st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-bottom:12px;'>Score Breakdown</p>", unsafe_allow_html=True)
                        skill_bar("Skill Match (42.5%)", sk_pct)
                        skill_bar("AI Semantic (42.5%)", ai_sc)
                        skill_bar("Experience (15%)", exp_sc)

                    with col_match:
                        st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-bottom:12px;'>Skills</p>", unsafe_allow_html=True)
                        st.markdown("<p style='font-size:11px;color:var(--emerald);font-weight:600;margin-bottom:6px;'>✓ Matched</p>", unsafe_allow_html=True)
                        tags((r.get("matched_tech") or []) + (r.get("matched_tools") or []) + (r.get("matched_soft") or []), limit=25, color="green")
                        st.markdown("<p style='font-size:11px;color:var(--rose);font-weight:600;margin:12px 0 6px;'>⚠ Missing</p>", unsafe_allow_html=True)
                        tags((r.get("missing_tech") or []) + (r.get("missing_tools") or []) + (r.get("missing_soft") or []), limit=25, color="red")

                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

                    # AI Reasoning
                    st.markdown("<p style='font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-3);margin-bottom:12px;'>AI Reasoning</p>", unsafe_allow_html=True)
                    summary = r.get("ai_reasoning_summary") or ""
                    if summary:
                        st.markdown(f"<p style='font-size:13px;color:var(--text-2);line-height:1.65;margin-bottom:16px;'>{summary}</p>", unsafe_allow_html=True)

                    ev_col, gap_col = st.columns(2)
                    with ev_col:
                        matches = r.get("evidence_matches") or []
                        if matches:
                            st.markdown("<p style='font-size:11px;font-weight:600;color:var(--text-3);margin-bottom:8px;'>Evidence from Resume</p>", unsafe_allow_html=True)
                            for m in matches[:4]:
                                req  = m.get("requirement", "")
                                ev   = m.get("evidence_from_resume", "")
                                conf = m.get("confidence", "Medium")
                                conf_cls = {"High": "conf-high", "Medium": "conf-med", "Low": "conf-low"}.get(conf, "conf-med")
                                if req:
                                    st.markdown(f"""
                                    <div class="evidence-card">
                                      <div class="evidence-card-icon">{'✅' if conf=='High' else '🔶' if conf=='Medium' else '❌'}</div>
                                      <div style="flex:1;min-width:0;">
                                        <p class="evidence-card-req">{req}</p>
                                        <p class="evidence-card-ev">{ev}</p>
                                      </div>
                                      <span class="conf-badge {conf_cls}">{conf}</span>
                                    </div>
                                    """, unsafe_allow_html=True)

                    with gap_col:
                        gaps = r.get("evidence_gaps") or []
                        suggestions = r.get("suggested_improvements") or []
                        if gaps:
                            st.markdown("<p style='font-size:11px;font-weight:600;color:var(--text-3);margin-bottom:8px;'>Gaps</p>", unsafe_allow_html=True)
                            for g in gaps[:4]:
                                miss = g.get("missing_requirement", "")
                                why  = g.get("why_it_matters", "")
                                if miss:
                                    st.markdown(f"""
                                    <div class="evidence-card">
                                      <div class="evidence-card-icon">⚠️</div>
                                      <div style="flex:1;">
                                        <p class="evidence-card-req">{miss}</p>
                                        <p class="evidence-card-ev">{why}</p>
                                      </div>
                                    </div>
                                    """, unsafe_allow_html=True)

                        if suggestions:
                            st.markdown("<p style='font-size:11px;font-weight:600;color:var(--text-3);margin:14px 0 8px;'>Suggestions</p>", unsafe_allow_html=True)
                            for s in suggestions[:3]:
                                st.markdown(f"<p style='font-size:12px;color:var(--text-2);margin:0 0 4px;'>→ {s}</p>", unsafe_allow_html=True)

                    if developer_mode:
                        st.json(r)


# ================================================================
# INTERVIEW TABS
# ================================================================
# ================================================================
# VIDEO INTERVIEW TAB
# ================================================================
with tab_video:
    jid, job = get_current_job()
    if not job:
        st.info("Select a role first.")
    else:
        render_video_interview_tab(job, jid)