const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Alan Moreira";
pres.title = "UG54 Big Picture Review — Chapters 4–13";

// ─── COLOR PALETTE ───
const C = {
  navy:      "1A2744",
  darkNavy:  "0F1A2E",
  midBlue:   "2E5090",
  accent:    "3B82F6",
  teal:      "0D9488",
  gold:      "F59E0B",
  coral:     "EF4444",
  ice:       "CADCFC",
  lightBg:   "F0F4FA",
  offWhite:  "F8FAFC",
  white:     "FFFFFF",
  text:      "1E293B",
  muted:     "64748B",
  green:     "10B981",
};

const mkShadow = () => ({ type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.12 });

const TOTAL = 33;
let sn = 0;

function addSlideNumber(slide, num, total) {
  slide.addText(`${num} / ${total}`, {
    x: 8.5, y: 5.2, w: 1.2, h: 0.35, fontSize: 9,
    color: C.muted, align: "right", fontFace: "Calibri"
  });
}
function darkSlide(s) { s.background = { color: C.navy }; }
function lightSlide(s) { s.background = { color: C.offWhite }; }

function chapterTitleSlide(chNum, title, bigIdea, accentColor) {
  sn++;
  let s = pres.addSlide();
  darkSlide(s);
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.12, h: 5.625, fill: { color: accentColor } });
  s.addText(`Chapter ${chNum}`, {
    x: 0.5, y: 1.3, w: 9, h: 0.6, fontSize: 16, fontFace: "Calibri",
    color: accentColor, bold: true, margin: 0
  });
  s.addText(title, {
    x: 0.5, y: 1.9, w: 9, h: 1.0, fontSize: 36, fontFace: "Georgia",
    color: C.white, bold: true, margin: 0
  });
  s.addText(bigIdea, {
    x: 0.5, y: 3.3, w: 8, h: 1.2, fontSize: 16, fontFace: "Calibri",
    color: C.ice, italic: true, margin: 0
  });
  addSlideNumber(s, sn, TOTAL);
}

function contentSlide(title) {
  sn++;
  let s = pres.addSlide();
  lightSlide(s);
  s.addText(title, {
    x: 0.6, y: 0.3, w: 9, h: 0.6, fontSize: 24, fontFace: "Georgia",
    color: C.navy, bold: true, margin: 0
  });
  addSlideNumber(s, sn, TOTAL);
  return s;
}

// ════════════════════════════════════════════════
//  SLIDE 1 — TITLE
// ════════════════════════════════════════════════
{
  sn++;
  let s = pres.addSlide();
  darkSlide(s);
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 1.8, w: 10, h: 2.2, fill: { color: C.midBlue, transparency: 30 } });
  s.addText("UG54 — Big Picture Review", {
    x: 0.7, y: 1.85, w: 8.6, h: 1.0, fontSize: 40, fontFace: "Georgia",
    color: C.white, bold: true, margin: 0
  });
  s.addText("Chapters 4 – 13  |  Data-Driven Investing with Python", {
    x: 0.7, y: 2.85, w: 8.6, h: 0.6, fontSize: 18, fontFace: "Calibri",
    color: C.ice, margin: 0
  });
  s.addText("Alan Moreira  •  NYU Stern", {
    x: 0.7, y: 4.6, w: 5, h: 0.4, fontSize: 13, color: C.muted, fontFace: "Calibri", margin: 0
  });
  addSlideNumber(s, sn, TOTAL);
}

// ════════════════════════════════════════════════
//  SLIDE 2 — THREE PILLARS
// ════════════════════════════════════════════════
{
  sn++;
  let s = pres.addSlide();
  lightSlide(s);
  s.addText("Three Pillars of the Course", {
    x: 0.6, y: 0.3, w: 9, h: 0.7, fontSize: 32, fontFace: "Georgia",
    color: C.navy, bold: true, margin: 0
  });

  const pillars = [
    { title: "MEASURE", sub: "Chapters 4–5", desc: "Returns, risk premia,\nSharpe ratios, timing", color: C.accent },
    { title: "DECOMPOSE", sub: "Chapters 6–9", desc: "Factor models, alpha/beta,\nportfolios, estimation", color: C.teal },
    { title: "CONSTRUCT", sub: "Chapters 10–13", desc: "Strategies, allocation,\nevaluation, ML", color: C.gold },
  ];

  pillars.forEach((p, i) => {
    const bx = 0.6 + i * 3.1;
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 1.4, w: 2.8, h: 3.4, fill: { color: C.white }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 1.4, w: 2.8, h: 0.08, fill: { color: p.color } });
    s.addText(p.title, {
      x: bx, y: 1.65, w: 2.8, h: 0.55, fontSize: 22, fontFace: "Georgia",
      color: p.color, bold: true, align: "center", margin: 0
    });
    s.addText(p.sub, {
      x: bx, y: 2.2, w: 2.8, h: 0.35, fontSize: 12, fontFace: "Calibri",
      color: C.muted, align: "center", margin: 0
    });
    s.addText(p.desc, {
      x: bx + 0.25, y: 2.7, w: 2.3, h: 1.8, fontSize: 14, fontFace: "Calibri",
      color: C.text, align: "left", valign: "top", margin: 0
    });
  });

  s.addText("Everything connects through one equation:  w* = (1/γ) × E[rᵉ] / Var(r)", {
    x: 0.6, y: 5.0, w: 9, h: 0.4, fontSize: 13, fontFace: "Calibri",
    color: C.midBlue, italic: true, margin: 0
  });
  addSlideNumber(s, sn, TOTAL);
}

// ════════════════════════════════════════════════
//  SLIDE 3 — THE BIG PICTURE: ESTIMATION UNCERTAINTY
// ════════════════════════════════════════════════
{
  sn++;
  let s = pres.addSlide();
  darkSlide(s);

  s.addText("The Big Picture", {
    x: 0.5, y: 0.15, w: 9, h: 0.5, fontSize: 26, fontFace: "Georgia",
    color: C.white, bold: true, margin: 0
  });

  // ── THE IDEAL ──
  s.addShape(pres.shapes.RECTANGLE, { x: 1.5, y: 0.7, w: 7.0, h: 1.05, fill: { color: "1B5E20", transparency: 20 }, line: { color: C.green, width: 1.5 } });
  s.addText([
    { text: "THE IDEAL:  ", options: { fontSize: 13, fontFace: "Georgia", color: C.green, bold: true } },
    { text: "If you knew E[R] and Σ, the answer is one equation:", options: { fontSize: 12, fontFace: "Calibri", color: C.ice, breakLine: true } },
    { text: "W* = (1/γ) Σ⁻¹ E[Rᵉ]     →  Tangency portfolio  →  Max Sharpe  →  Done.", options: { fontSize: 13, fontFace: "Calibri", color: C.white, bold: true } },
  ], { x: 1.65, y: 0.72, w: 6.7, h: 1.0, valign: "middle", margin: 0 });

  // ── DISRUPTION ARROW ──
  s.addShape(pres.shapes.LINE, { x: 5.0, y: 1.75, w: 0, h: 0.35, line: { color: C.coral, width: 2.5, endArrowType: "triangle" } });

  // ── THE PROBLEM ──
  s.addShape(pres.shapes.RECTANGLE, { x: 2.0, y: 2.15, w: 6.0, h: 0.55, fill: { color: C.coral }, shadow: mkShadow() });
  s.addText("REALITY:  You don't know E[R] or Σ.  Estimation uncertainty changes everything.", {
    x: 2.1, y: 2.15, w: 5.8, h: 0.55, fontSize: 12, fontFace: "Calibri",
    color: C.white, bold: true, valign: "middle", margin: 0
  });

  // ── RESPONSE BRANCHES ──
  // Left branch: Estimate E[R]
  s.addShape(pres.shapes.LINE, { x: 3.2, y: 2.7, w: 0, h: 0.3, line: { color: C.accent, width: 1.5, endArrowType: "triangle" } });
  // Right branch: Estimate Σ
  s.addShape(pres.shapes.LINE, { x: 6.8, y: 2.7, w: 0, h: 0.3, line: { color: C.teal, width: 1.5, endArrowType: "triangle" } });

  // LEFT: Estimate E[R]
  s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: 3.05, w: 5.4, h: 0.45, fill: { color: C.accent, transparency: 15 }, line: { color: C.accent, width: 1 } });
  s.addText("Estimate E[Rᵉ]  —  the hard part", {
    x: 0.5, y: 3.05, w: 5.1, h: 0.45, fontSize: 12, fontFace: "Georgia",
    color: C.accent, bold: true, valign: "middle", margin: 0
  });

  // RIGHT: Estimate Σ
  s.addShape(pres.shapes.RECTANGLE, { x: 5.95, y: 3.05, w: 3.7, h: 0.45, fill: { color: C.teal, transparency: 15 }, line: { color: C.teal, width: 1 } });
  s.addText("Estimate Σ  —  easier but still hard", {
    x: 6.1, y: 3.05, w: 3.4, h: 0.45, fontSize: 12, fontFace: "Georgia",
    color: C.teal, bold: true, valign: "middle", margin: 0
  });

  // Response boxes under E[R]
  const erBoxes = [
    { label: "Ch 5.1", desc: "Timing:\nforecast E[R]\nwith signals", x: 0.35 },
    { label: "Ch 6", desc: "Factor E[R]:\nE[Rᵢ] = Σₖ βᵢₖ λₖ\nK premia not N means", x: 2.05 },
    { label: "Ch 10", desc: "Characteristics:\nsort → long/short\ncross-section signals", x: 3.75 },
  ];

  erBoxes.forEach(b => {
    s.addShape(pres.shapes.RECTANGLE, { x: b.x, y: 3.6, w: 1.55, h: 1.25, fill: { color: C.accent, transparency: 75 }, line: { color: C.accent, width: 0.8 } });
    s.addText(b.label, {
      x: b.x + 0.08, y: 3.63, w: 1.4, h: 0.28, fontSize: 10, fontFace: "Georgia",
      color: C.accent, bold: true, margin: 0
    });
    s.addText(b.desc, {
      x: b.x + 0.08, y: 3.92, w: 1.4, h: 0.88, fontSize: 9, fontFace: "Calibri",
      color: C.ice, valign: "top", margin: 0
    });
  });

  // Response boxes under Σ
  const sigBoxes = [
    { label: "Ch 5.2", desc: "Vol timing:\nRV predictable\nscale by 1/RVₜ", x: 5.95 },
    { label: "Ch 6", desc: "Factor risk:\nΣ = BΣ_FB'+Σ_ε\nfewer parameters", x: 7.65 },
  ];

  sigBoxes.forEach(b => {
    s.addShape(pres.shapes.RECTANGLE, { x: b.x, y: 3.6, w: 1.55, h: 1.25, fill: { color: C.teal, transparency: 75 }, line: { color: C.teal, width: 0.8 } });
    s.addText(b.label, {
      x: b.x + 0.08, y: 3.63, w: 1.4, h: 0.28, fontSize: 10, fontFace: "Georgia",
      color: C.teal, bold: true, margin: 0
    });
    s.addText(b.desc, {
      x: b.x + 0.08, y: 3.92, w: 1.4, h: 0.88, fontSize: 9, fontFace: "Calibri",
      color: C.ice, valign: "top", margin: 0
    });
  });

  // Bottom bar: managing the uncertainty
  s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: 5.0, w: 9.3, h: 0.5, fill: { color: C.gold, transparency: 15 }, line: { color: C.gold, width: 1 } });
  s.addText([
    { text: "Managing Uncertainty:  ", options: { fontSize: 11, fontFace: "Georgia", color: C.gold, bold: true } },
    { text: "Ch 7 Diversification reduces risk from Σ errors  •  Ch 9 Shrinkage & factor structure tame estimation  •  Ch 11 Heuristics when MV fails  •  Ch 12 Detect overfitting  •  Ch 13 Regularization (Lasso, etc.)", options: { fontSize: 9.5, fontFace: "Calibri", color: C.ice } },
  ], { x: 0.5, y: 5.0, w: 9.0, h: 0.5, valign: "middle", margin: 0 });

  addSlideNumber(s, sn, TOTAL);
}

// ════════════════════════════════════════════════
//  SLIDE 4 — CONNECTIONS TABLE (from the uncertainty lens)
// ════════════════════════════════════════════════
{
  sn++;
  let s = pres.addSlide();
  darkSlide(s);

  s.addText("Every Chapter Is a Response to Estimation Uncertainty", {
    x: 0.5, y: 0.2, w: 9.0, h: 0.55, fontSize: 22, fontFace: "Georgia",
    color: C.white, bold: true, margin: 0
  });

  const rows = [
    { ch: "Ch 4", topic: "Returns", response: "Define the object: excess returns, Sharpe ratio — the scoreboard before estimation begins", col: C.accent },
    { ch: "Ch 5", topic: "Timing", response: "Forecast E[R] with signals (hard: OOS R² < 0) or scale by 1/RV (easier: vol is persistent)", col: C.accent },
    { ch: "Ch 6", topic: "Factor Models", response: "Reduce E[R] to K factor premia (not N means).  Reduce Σ to factor structure (not N² covariances)", col: C.teal },
    { ch: "Ch 7", topic: "Portfolios", response: "Diversification protects you: errors in individual covariances wash out in W'ΣW", col: C.teal },
    { ch: "Ch 8", topic: "Capital Alloc I", response: "The ideal: MVE = Σ⁻¹E[Rᵉ].  Two-fund separation holds if you trust your estimates", col: C.teal },
    { ch: "Ch 9", topic: "Estimation", response: "The problem quantified: ±2σ perturbation in E[R] flips MVE weights.  Shrink toward simpler models", col: C.teal },
    { ch: "Ch 10", topic: "Strategies", response: "Side-step: rank stocks on characteristics instead of estimating E[R] directly.  Long top, short bottom", col: C.gold },
    { ch: "Ch 11", topic: "Capital Alloc II", response: "When MV fails: 1/N, risk parity, shrinkage.  Simpler heuristics often win out-of-sample", col: C.gold },
    { ch: "Ch 12", topic: "Evaluation", response: "Detect overfitting: SR degrades >50% OOS.  Multiple testing, hold-out discipline, publication bias", col: C.coral },
    { ch: "Ch 13", topic: "ML", response: "Regularize: Lasso beats complex models in low-SNR.  Bias-variance tradeoff favors simplicity", col: C.coral },
  ];

  rows.forEach((r, i) => {
    const by = 0.9 + i * 0.46;
    const bgT = i % 2 === 0 ? 85 : 90;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: by, w: 9.3, h: 0.42, fill: { color: r.col, transparency: bgT } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: by, w: 0.06, h: 0.42, fill: { color: r.col } });
    s.addText(r.ch, {
      x: 0.55, y: by, w: 0.65, h: 0.42, fontSize: 10, fontFace: "Georgia",
      color: r.col, bold: true, valign: "middle", margin: 0
    });
    s.addText(r.topic, {
      x: 1.2, y: by, w: 1.3, h: 0.42, fontSize: 10, fontFace: "Georgia",
      color: C.white, bold: true, valign: "middle", margin: 0
    });
    s.addText(r.response, {
      x: 2.55, y: by, w: 6.9, h: 0.42, fontSize: 9.5, fontFace: "Calibri",
      color: C.ice, valign: "middle", margin: 0
    });
  });

  addSlideNumber(s, sn, TOTAL);
}

// ════════════════════════════════════════════════
//  CH 4 — RETURNS
// ════════════════════════════════════════════════
chapterTitleSlide(4, "Introduction to Asset Returns",
  "Big idea: We care about excess returns — compensation for bearing risk.\nThe Sharpe Ratio is the universal scoreboard.", C.accent);

{
  let s = contentSlide("Returns: The Building Blocks");

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 4.3, h: 3.6, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Key Definitions", {
    x: 0.7, y: 1.2, w: 3.9, h: 0.4, fontSize: 16, fontFace: "Georgia", color: C.navy, bold: true, margin: 0
  });
  s.addText([
    { text: "Total Return", options: { bold: true, fontSize: 13, color: C.text, breakLine: true } },
    { text: "Rₜ = (Pₜ + Dₜ) / Pₜ₋₁ − 1", options: { fontSize: 13, color: C.midBlue, breakLine: true } },
    { text: "", options: { fontSize: 8, breakLine: true } },
    { text: "Excess Return", options: { bold: true, fontSize: 13, color: C.text, breakLine: true } },
    { text: "Rᵉₜ = Rₜ − Rᶠₜ", options: { fontSize: 13, color: C.midBlue, breakLine: true } },
    { text: "", options: { fontSize: 8, breakLine: true } },
    { text: "Sharpe Ratio", options: { bold: true, fontSize: 13, color: C.text, breakLine: true } },
    { text: "SR = E[Rᵉ] / σ(Rᵉ)", options: { fontSize: 13, color: C.midBlue, breakLine: true } },
    { text: "", options: { fontSize: 8, breakLine: true } },
    { text: "Annualization", options: { bold: true, fontSize: 13, color: C.text, breakLine: true } },
    { text: "μ_A = 12 × μ_M    σ_A = √12 × σ_M", options: { fontSize: 13, color: C.midBlue } },
  ], { x: 0.7, y: 1.7, w: 3.9, h: 3.0, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.1, w: 4.3, h: 3.6, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Why Excess Returns?", {
    x: 5.4, y: 1.2, w: 3.9, h: 0.4, fontSize: 16, fontFace: "Georgia", color: C.navy, bold: true, margin: 0
  });
  s.addText([
    { text: "Returns (not prices) are scale-free and comparable across assets.", options: { fontSize: 13, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 8, breakLine: true } },
    { text: "Excess returns strip out the time value of money — what remains is ", options: { fontSize: 13, color: C.text } },
    { text: "compensation for risk.", options: { fontSize: 13, color: C.text, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 8, breakLine: true } },
    { text: "Example (UNH, daily data):", options: { fontSize: 12, color: C.muted, breakLine: true } },
    { text: "Ann. mean: 22.4%   Vol: 43.3%", options: { fontSize: 12, color: C.midBlue, breakLine: true } },
    { text: "Sharpe Ratio ≈ 0.45", options: { fontSize: 14, color: C.accent, bold: true } },
  ], { x: 5.4, y: 1.7, w: 3.9, h: 3.0, valign: "top", margin: 0 });

  s.addText("Key takeaway: Sharpe ≈ 0.5 is a good benchmark for an annual Sharpe ratio.", {
    x: 0.6, y: 4.85, w: 9, h: 0.4, fontSize: 12, color: C.muted, italic: true, fontFace: "Calibri", margin: 0
  });
}

// ════════════════════════════════════════════════
//  CH 5 — TIMING
// ════════════════════════════════════════════════
chapterTitleSlide(5, "Timing Strategies",
  "Big idea: Optimal weight depends on expected return AND variance.\nYou can time on either — but expected returns are much harder to predict.", C.accent);

{
  let s = contentSlide("The Timing Framework");

  s.addShape(pres.shapes.RECTANGLE, { x: 1.5, y: 1.1, w: 7.0, h: 1.2, fill: { color: C.navy } });
  s.addText("w* = E[rᵉ] / (γ × Var(r))", {
    x: 1.5, y: 1.1, w: 7.0, h: 0.7, fontSize: 28, fontFace: "Georgia",
    color: C.white, bold: true, align: "center", margin: 0
  });
  s.addText("The optimal weight is the risk–return tradeoff scaled by risk aversion", {
    x: 1.5, y: 1.75, w: 7.0, h: 0.45, fontSize: 12, fontFace: "Calibri",
    color: C.ice, align: "center", italic: true, margin: 0
  });

  const colW = 4.0, colH = 2.6;
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.6, w: colW, h: colH, fill: { color: C.white }, shadow: mkShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.6, w: colW, h: 0.06, fill: { color: C.accent } });
  s.addText("Expected Return Timing (Ch 5.1)", {
    x: 0.7, y: 2.7, w: 3.6, h: 0.4, fontSize: 14, fontFace: "Georgia", color: C.accent, bold: true, margin: 0
  });
  s.addText([
    { text: "Signal: dividend yield → forecast rₜ₊ₕ", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "rₜ→ₜ₊ₕ = a + b × DPₜ + uₜ₊ₕ", options: { fontSize: 12, color: C.midBlue, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Pitfalls:", options: { bold: true, fontSize: 12, color: C.text, breakLine: true } },
    { text: "• Overlapping returns → use HAC (Newey-West)", options: { fontSize: 11, color: C.text, breakLine: true } },
    { text: "• In-sample SR = 0.75, but OOS R² < 0!", options: { fontSize: 11, color: C.coral, breakLine: true } },
    { text: "• Structural breaks (buybacks) weaken signal", options: { fontSize: 11, color: C.text } },
  ], { x: 0.7, y: 3.15, w: 3.6, h: 2.0, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.5, y: 2.6, w: colW, h: colH, fill: { color: C.white }, shadow: mkShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.5, y: 2.6, w: colW, h: 0.06, fill: { color: C.teal } });
  s.addText("Volatility Timing (Ch 5.2)", {
    x: 5.7, y: 2.7, w: 3.6, h: 0.4, fontSize: 14, fontFace: "Georgia", color: C.teal, bold: true, margin: 0
  });
  s.addText([
    { text: "wₜ = c / RVₜ  (scale down when vol is high)", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Why it works:", options: { bold: true, fontSize: 12, color: C.text, breakLine: true } },
    { text: "• Volatility is highly predictable (persistent)", options: { fontSize: 11, color: C.text, breakLine: true } },
    { text: "• Price of risk falls when vol is high", options: { fontSize: 11, color: C.text, breakLine: true } },
    { text: "• SR improvement: 0.45 → 0.52 (+15%)", options: { fontSize: 11, color: C.teal, bold: true, breakLine: true } },
    { text: "• Must lag signal & cap leverage!", options: { fontSize: 11, color: C.text } },
  ], { x: 5.7, y: 3.15, w: 3.6, h: 2.0, valign: "top", margin: 0 });
}

// ════════════════════════════════════════════════
//  CH 6 — FACTOR MODELS
// ════════════════════════════════════════════════
chapterTitleSlide(6, "Factor Models",
  "Big idea: Factor models serve two distinct purposes —\npredicting expected returns (fewer parameters) and modeling risk (structured Σ).", C.teal);

// ── NEW: Factor Models as Expected Return Models ──
{
  let s = contentSlide("Factor Models as Expected Return Models");

  // Top equation box
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 9.0, h: 1.6, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("From Regression to Expected Returns", {
    x: 0.7, y: 1.15, w: 8.6, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.navy, bold: true, margin: 0
  });
  s.addText([
    { text: "Start:  ", options: { fontSize: 13, color: C.muted } },
    { text: "rᵉᵢ = αᵢ + βᵢ₁ f₁ + βᵢ₂ f₂ + ⋯ + βᵢₖ fₖ + εᵢ", options: { fontSize: 14, color: C.midBlue, bold: true, breakLine: true } },
    { text: "Take E[·]:  ", options: { fontSize: 13, color: C.muted } },
    { text: "E[rᵉᵢ] = αᵢ + βᵢ₁ λ₁ + βᵢ₂ λ₂ + ⋯ + βᵢₖ λₖ", options: { fontSize: 14, color: C.midBlue, bold: true, breakLine: true } },
    { text: "where λₖ = E[fₖ] is the risk premium for factor k", options: { fontSize: 12, color: C.muted } },
  ], { x: 0.7, y: 1.55, w: 8.6, h: 1.1, valign: "top", margin: 0 });

  // Two insight cards
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 4.3, h: 2.15, fill: { color: C.white }, shadow: mkShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 0.08, h: 2.15, fill: { color: C.accent } });
  s.addText("The Dimension Reduction", {
    x: 0.75, y: 3.05, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.accent, bold: true, margin: 0
  });
  s.addText([
    { text: "Without factors: estimate N expected returns", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "(5,000 stocks = 5,000 noisy means!)", options: { fontSize: 11, color: C.coral, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "With factors: estimate K risk premia + N×K betas", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "(6 factors + betas from regression — much easier)", options: { fontSize: 11, color: C.teal, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Betas estimated from time-series regressions.\nRisk premia λ from factor portfolio returns.", options: { fontSize: 11, color: C.muted } },
  ], { x: 0.75, y: 3.45, w: 3.9, h: 1.6, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 3.0, w: 4.3, h: 2.15, fill: { color: C.white }, shadow: mkShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 3.0, w: 0.08, h: 2.15, fill: { color: C.teal } });
  s.addText("Alpha = What's Left Over", {
    x: 5.45, y: 3.05, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.teal, bold: true, margin: 0
  });
  s.addText([
    { text: "If the model is correct:  αᵢ = 0", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Expected returns fully explained by factor betas.", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "If αᵢ ≠ 0:  mispricing or missing factor.", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "\"Bonuses only for alpha\" — the industry mantra.", options: { fontSize: 12, color: C.midBlue, italic: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Example: MSFT daily α = 0.06% (annualized ~15%)\nβ_mkt = 1.19 → E[rᵉ] = 1.19 × 8% ≈ 9.5% from β", options: { fontSize: 11, color: C.muted } },
  ], { x: 5.45, y: 3.45, w: 3.9, h: 1.6, valign: "top", margin: 0 });
}

// ── NEW: Factor Models as Risk Models ──
{
  let s = contentSlide("Factor Models as Risk Models");

  // Top equation box
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 9.0, h: 1.6, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("From Betas to a Structured Covariance Matrix", {
    x: 0.7, y: 1.15, w: 8.6, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.navy, bold: true, margin: 0
  });
  s.addText([
    { text: "Σ = B Σ_F B' + Σ_ε", options: { fontSize: 18, fontFace: "Georgia", color: C.midBlue, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 4, breakLine: true } },
    { text: "B = N×K beta matrix     Σ_F = K×K factor covariance     Σ_ε = N×N diagonal (residual variances)", options: { fontSize: 11, color: C.muted, breakLine: true } },
    { text: "Portfolio risk:  Var(Rₚ) = ", options: { fontSize: 13, color: C.text } },
    { text: "(w'B)", options: { fontSize: 13, color: C.accent, bold: true } },
    { text: " Σ_F ", options: { fontSize: 13, color: C.text } },
    { text: "(B'w)", options: { fontSize: 13, color: C.accent, bold: true } },
    { text: " + w' Σ_ε w", options: { fontSize: 13, color: C.teal } },
    { text: "     where ", options: { fontSize: 12, color: C.text } },
    { text: "β_p = B'w", options: { fontSize: 13, color: C.accent, bold: true } },
    { text: " is the portfolio's factor exposure", options: { fontSize: 12, color: C.text } },
  ], { x: 0.7, y: 1.55, w: 8.6, h: 1.1, valign: "top", margin: 0 });

  // Two insight cards
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 4.3, h: 2.15, fill: { color: C.white }, shadow: mkShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 0.08, h: 2.15, fill: { color: C.accent } });
  s.addText("The Parameter Savings", {
    x: 0.75, y: 3.05, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.accent, bold: true, margin: 0
  });
  s.addText([
    { text: "Full Σ: N(N+1)/2 parameters", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "500 stocks → 125,250 covariances!", options: { fontSize: 12, color: C.coral, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Factor Σ: NK betas + K(K+1)/2 + N", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "500 stocks, 6 factors → 3,521 parameters", options: { fontSize: 12, color: C.teal, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "35× fewer parameters → far more stable\ncovariance estimates → better portfolios", options: { fontSize: 12, color: C.midBlue, bold: true } },
  ], { x: 0.75, y: 3.45, w: 3.9, h: 1.6, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 3.0, w: 4.3, h: 2.15, fill: { color: C.white }, shadow: mkShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 3.0, w: 0.08, h: 2.15, fill: { color: C.teal } });
  s.addText("Strategy Risk Decomposition", {
    x: 5.45, y: 3.05, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.teal, bold: true, margin: 0
  });
  s.addText([
    { text: "Your portfolio w has factor exposure β_p = B'w", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Systematic risk: β_p' Σ_F β_p", options: { fontSize: 13, color: C.accent, bold: true, breakLine: true } },
    { text: "→ risk from factor movements (not diversifiable)", options: { fontSize: 11, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Idiosyncratic risk: w' Σ_ε w", options: { fontSize: 13, color: C.teal, bold: true, breakLine: true } },
    { text: "→ diversifiable with many stocks", options: { fontSize: 11, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "R² = systematic / total variance", options: { fontSize: 12, color: C.midBlue, breakLine: true } },
    { text: "MSFT vs SPY: R² = 0.42 → 42% factor risk", options: { fontSize: 11, color: C.muted } },
  ], { x: 5.45, y: 3.45, w: 3.9, h: 1.6, valign: "top", margin: 0 });
}

// ── Hedging & Portable Alpha (kept) ──
{
  let s = contentSlide("Hedging, Portable Alpha & Appraisal Ratio");

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 4.3, h: 3.8, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Hedged Portfolio", {
    x: 0.7, y: 1.2, w: 3.9, h: 0.4, fontSize: 16, fontFace: "Georgia", color: C.teal, bold: true, margin: 0
  });
  s.addText([
    { text: "Hedge = Remove factor exposure:", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "rʰᵉᵈᵍᵉᵈ = rᵉ − β × f = α + ε", options: { fontSize: 14, color: C.midBlue, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Why hedge?", options: { bold: true, fontSize: 12, color: C.text, breakLine: true } },
    { text: "Lower vol → bigger position within risk budget", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Example (MSFT, $1M vol budget):", options: { fontSize: 12, color: C.muted, breakLine: true } },
    { text: "Unhedged position: ~$94M", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Hedged position: ~$136M (1.4× larger!)", options: { fontSize: 12, color: C.teal, bold: true } },
  ], { x: 0.7, y: 1.7, w: 3.9, h: 3.0, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.1, w: 4.3, h: 3.8, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Appraisal Ratio", {
    x: 5.4, y: 1.2, w: 3.9, h: 0.4, fontSize: 16, fontFace: "Georgia", color: C.teal, bold: true, margin: 0
  });
  s.addText([
    { text: "AR = α / σ(ε)", options: { fontSize: 16, color: C.midBlue, bold: true, breakLine: true } },
    { text: "= Sharpe ratio of hedged portfolio", options: { fontSize: 13, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Connection to overall Sharpe:", options: { bold: true, fontSize: 12, color: C.text, breakLine: true } },
    { text: "SR²_total = SR²_market + AR²", options: { fontSize: 14, color: C.midBlue, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Alpha and market are orthogonal bets.", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Portable alpha = sell β, keep α.", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Pod shops require factor-neutral positions\nacross multiple factors (zero net β).", options: { fontSize: 11, color: C.muted } },
  ], { x: 5.4, y: 1.7, w: 3.9, h: 3.0, valign: "top", margin: 0 });
}

// ════════════════════════════════════════════════
//  CH 7 — PORTFOLIO MATH
// ════════════════════════════════════════════════
chapterTitleSlide(7, "Portfolio Mathematics",
  "Big idea: Portfolio variance is NOT the weighted average of variances.\nCovariances dominate. Diversification is the only free lunch.", C.accent);

{
  let s = contentSlide("Portfolio Algebra");

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 9.0, h: 1.5, fill: { color: C.white }, shadow: mkShadow() });
  s.addText([
    { text: "Portfolio return:  ", options: { fontSize: 14, color: C.text } },
    { text: "Rₚ = W'R = Σ wⱼ rⱼ", options: { fontSize: 14, color: C.midBlue, bold: true, breakLine: true } },
    { text: "Expected return:  ", options: { fontSize: 14, color: C.text } },
    { text: "E[Rₚ] = W'E[R]", options: { fontSize: 14, color: C.midBlue, bold: true, breakLine: true } },
    { text: "Portfolio variance:  ", options: { fontSize: 14, color: C.text } },
    { text: "Var(Rₚ) = W'ΣW = Σᵢ Σⱼ wᵢwⱼ Cov(rᵢ,rⱼ)", options: { fontSize: 14, color: C.midBlue, bold: true } },
  ], { x: 0.7, y: 1.15, w: 8.6, h: 1.4, valign: "middle", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.9, w: 4.3, h: 2.2, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Diversification in Action", {
    x: 0.7, y: 3.0, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.navy, bold: true, margin: 0
  });
  s.addText([
    { text: "50-asset portfolio:", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "50 variance terms vs. 2,450 covariance terms", options: { fontSize: 12, color: C.accent, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Adding a MORE volatile asset can REDUCE\nportfolio vol if correlation is low enough.", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "US + Intl (70/30): lower vol than 100% US", options: { fontSize: 12, color: C.teal, bold: true } },
  ], { x: 0.7, y: 3.4, w: 3.9, h: 1.6, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 2.9, w: 4.3, h: 2.2, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Weight Constraints", {
    x: 5.4, y: 3.0, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.navy, bold: true, margin: 0
  });
  s.addText([
    { text: "Σ wⱼ = 1  (fully invested)", options: { fontSize: 12, color: C.midBlue, breakLine: true } },
    { text: "wⱼ ≥ 0  (long-only constraint)", options: { fontSize: 12, color: C.midBlue, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "With risk-free asset:", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Σ wⱼ + w_rf = 1", options: { fontSize: 12, color: C.midBlue, breakLine: true } },
    { text: "Short = negative w, Leverage = Σ|wⱼ| > 1", options: { fontSize: 12, color: C.text } },
  ], { x: 5.4, y: 3.4, w: 3.9, h: 1.6, valign: "top", margin: 0 });
}

// ════════════════════════════════════════════════
//  CH 8 — CAPITAL ALLOCATION I
// ════════════════════════════════════════════════
chapterTitleSlide(8, "Capital Allocation I",
  "Big idea: Two-Fund Separation — all investors hold the same risky portfolio (MVE);\nthey differ only in how much risk-free asset to mix in.", C.teal);

{
  let s = contentSlide("Mean-Variance Efficient Portfolio");

  s.addShape(pres.shapes.RECTANGLE, { x: 1.0, y: 1.1, w: 8.0, h: 1.3, fill: { color: C.navy } });
  s.addText([
    { text: "W* = (1/γ) Σ⁻¹ E[Rᵉ]", options: { fontSize: 26, fontFace: "Georgia", color: C.white, bold: true, breakLine: true } },
    { text: "MVE weights: inverse covariance × expected excess returns", options: { fontSize: 12, fontFace: "Calibri", color: C.ice, italic: true } },
  ], { x: 1.0, y: 1.1, w: 8.0, h: 1.3, align: "center", valign: "middle", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.7, w: 4.3, h: 2.4, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Two-Fund Separation", {
    x: 0.7, y: 2.8, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.teal, bold: true, margin: 0
  });
  s.addText([
    { text: "Optimal portfolio vol:", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "w* × σ(rₚ) = (1/γ) × SR", options: { fontSize: 13, color: C.midBlue, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Conservative investor: small w*, more cash", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Aggressive investor: large w*, same risky mix", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "\"All you need is Sharpe\" — the MVE portfolio\nmaximizes SR, everyone just scales it.", options: { fontSize: 12, color: C.teal, italic: true } },
  ], { x: 0.7, y: 3.2, w: 3.9, h: 1.8, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 2.7, w: 4.3, h: 2.4, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Empirical Example (FF6)", {
    x: 5.4, y: 2.8, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.teal, bold: true, margin: 0
  });
  s.addText([
    { text: "Factor Sharpe Ratios (annual):", options: { fontSize: 12, color: C.text, bold: true, breakLine: true } },
    { text: "Mkt: 0.46   SMB: 0.17   HML: 0.33", options: { fontSize: 12, color: C.midBlue, breakLine: true } },
    { text: "RMW: 0.41  CMA: 0.40  MOM: 0.49", options: { fontSize: 12, color: C.midBlue, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "MVE portfolio (in-sample):", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "SR ≈ 1.17", options: { fontSize: 16, color: C.accent, bold: true, breakLine: true } },
    { text: "⚠ But: massive overfitting risk (Ch 12)!", options: { fontSize: 11, color: C.coral } },
  ], { x: 5.4, y: 3.2, w: 3.9, h: 1.8, valign: "top", margin: 0 });
}

// ════════════════════════════════════════════════
//  CH 9 — ESTIMATION
// ════════════════════════════════════════════════
chapterTitleSlide(9, "Factor Model Estimation",
  "Big idea: Estimation risk is the silent killer. Small perturbations in inputs\ncause wild swings in MVE weights. Regularization is essential.", C.teal);

{
  let s = contentSlide("Estimation Risk & Hedged Portfolios");

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 9.0, h: 1.5, fill: { color: C.white }, shadow: mkShadow() });
  s.addText([
    { text: "The Problem:  ", options: { fontSize: 14, color: C.coral, bold: true } },
    { text: "MVE weights = Σ⁻¹E[Rᵉ].  Small errors in E[R] or Σ → extreme, unstable weights.", options: { fontSize: 13, color: C.text, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "The Fix:  ", options: { fontSize: 14, color: C.green, bold: true } },
    { text: "Shrink toward simpler models. Use factor structure to reduce the number of parameters.", options: { fontSize: 13, color: C.text, breakLine: true } },
    { text: "Factor model covariance:  Σ = β Var(F) β' + Var(ε)      (far fewer parameters than full Σ)", options: { fontSize: 12, color: C.midBlue } },
  ], { x: 0.7, y: 1.15, w: 8.6, h: 1.4, valign: "middle", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.9, w: 4.3, h: 2.2, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Alpha Portfolio (Hedged)", {
    x: 0.7, y: 3.0, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.teal, bold: true, margin: 0
  });
  s.addText([
    { text: "With uncorrelated residuals:", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Wᵢ = αᵢ / σ²(εᵢ)", options: { fontSize: 14, color: C.midBlue, bold: true, breakLine: true } },
    { text: "Weight proportional to alpha,\ninversely proportional to residual variance.", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Bet big on high-alpha, low-noise stocks.", options: { fontSize: 12, color: C.teal, italic: true } },
  ], { x: 0.7, y: 3.4, w: 3.9, h: 1.6, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 2.9, w: 4.3, h: 2.2, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Combining Bets", {
    x: 5.4, y: 3.0, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.teal, bold: true, margin: 0
  });
  s.addText([
    { text: "Orthogonal strategies combine via:", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "SR² = SR²_mkt + AR²", options: { fontSize: 16, color: C.midBlue, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "N independent pods with AR = a:", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "SR_combined = √N × a", options: { fontSize: 14, color: C.accent, bold: true, breakLine: true } },
    { text: "→ Diversification across strategies!", options: { fontSize: 12, color: C.teal } },
  ], { x: 5.4, y: 3.4, w: 3.9, h: 1.6, valign: "top", margin: 0 });
}

// ════════════════════════════════════════════════
//  CH 10 — CROSS-SECTIONAL STRATEGIES
// ════════════════════════════════════════════════
chapterTitleSlide(10, "Cross-Sectional Equity Strategies",
  "Big idea: Sort stocks on a characteristic → long the top, short the bottom.\nThis is how every major factor (value, momentum, quality) is constructed.", C.gold);

{
  let s = contentSlide("The Portfolio Construction Recipe");
  const steps = [
    { num: "1", label: "Compute\ncharacteristic", desc: "Book/Market,\n12m return, etc." },
    { num: "2", label: "Lag the\nsignal", desc: "Avoid look-\nahead bias" },
    { num: "3", label: "Sort into\ndeciles", desc: "Cross-section\neach month" },
    { num: "4", label: "Form\nportfolios", desc: "VW or EW\nwithin deciles" },
    { num: "5", label: "Long top\nShort bottom", desc: "R^LS = R₁₀ − R₁" },
  ];
  steps.forEach((st, i) => {
    const bx = 0.3 + i * 1.95;
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 1.2, w: 1.7, h: 1.8, fill: { color: C.white }, shadow: mkShadow() });
    s.addShape(pres.shapes.OVAL, { x: bx + 0.6, y: 1.05, w: 0.5, h: 0.5, fill: { color: C.gold } });
    s.addText(st.num, { x: bx + 0.6, y: 1.05, w: 0.5, h: 0.5, fontSize: 16, fontFace: "Georgia", color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(st.label, { x: bx + 0.1, y: 1.6, w: 1.5, h: 0.7, fontSize: 12, fontFace: "Georgia", color: C.navy, bold: true, align: "center", valign: "top", margin: 0 });
    s.addText(st.desc, { x: bx + 0.1, y: 2.3, w: 1.5, h: 0.6, fontSize: 10, fontFace: "Calibri", color: C.muted, align: "center", valign: "top", margin: 0 });
    if (i < steps.length - 1) {
      s.addShape(pres.shapes.LINE, { x: bx + 1.7, y: 2.0, w: 0.25, h: 0, line: { color: C.gold, width: 2, endArrowType: "triangle" } });
    }
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.4, w: 9.0, h: 1.8, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Signal–Diversification Tradeoff", {
    x: 0.7, y: 3.5, w: 8.6, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.gold, bold: true, margin: 0
  });
  s.addText([
    { text: "Fewer groups (5): weaker signal, more diversified, lower vol.", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Many groups (100): extreme signal, but concentrated, higher vol.", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Sweet spot: 10–20 groups typically optimal.", options: { fontSize: 12, color: C.gold, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Market-cap weighting preferred: auto-rebalances, minimizes turnover, easy to trade.", options: { fontSize: 12, color: C.muted } },
  ], { x: 0.7, y: 3.9, w: 8.6, h: 1.2, valign: "top", margin: 0 });
}

// Factor Zoo
{
  let s = contentSlide("The Factor Zoo — Key Factors");
  const factors = [
    { name: "Value", signal: "Book / Market", idea: "Cheap stocks outperform\n(contrarian / distress risk)", sr: "0.33" },
    { name: "Momentum", signal: "Past 12m return\n(skip last month)", idea: "Winners keep winning\n(6–12 month horizon)", sr: "0.49" },
    { name: "Profitability", signal: "Revenue − COGS\n/ Assets", idea: "Profitable firms earn more\n(quality signal)", sr: "0.41" },
    { name: "Low Vol", signal: "Historical\nvolatility", idea: "Low-vol beats high-vol\n(leverage constraints)", sr: "—" },
    { name: "Investment", signal: "Asset growth", idea: "Low investment firms\noutperform (empire building)", sr: "0.40" },
    { name: "Size", signal: "Market cap", idea: "Small caps earn premium\n(weakest factor)", sr: "0.17" },
  ];
  factors.forEach((f, i) => {
    const row = Math.floor(i / 3), col = i % 3;
    const bx = 0.4 + col * 3.15, by = 1.15 + row * 2.1;
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: by, w: 2.95, h: 1.85, fill: { color: C.white }, shadow: mkShadow() });
    s.addText(f.name, { x: bx + 0.15, y: by + 0.1, w: 1.6, h: 0.3, fontSize: 14, fontFace: "Georgia", color: C.navy, bold: true, margin: 0 });
    s.addText(`SR: ${f.sr}`, { x: bx + 1.9, y: by + 0.1, w: 0.9, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.accent, bold: true, align: "right", margin: 0 });
    s.addText(f.signal, { x: bx + 0.15, y: by + 0.45, w: 2.65, h: 0.5, fontSize: 10, fontFace: "Calibri", color: C.teal, margin: 0 });
    s.addText(f.idea, { x: bx + 0.15, y: by + 1.0, w: 2.65, h: 0.75, fontSize: 11, fontFace: "Calibri", color: C.text, margin: 0 });
  });
}

// Momentum
{
  let s = contentSlide("Momentum: The Details");
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 9.0, h: 0.8, fill: { color: C.white }, shadow: mkShadow() });
  s.addText([
    { text: "Mom signal:  ", options: { fontSize: 14, color: C.text } },
    { text: "Momᵢ,ₜ₋₂ = Pₜ₋₂ / Pₜ₋₁₄ − 1", options: { fontSize: 14, color: C.midBlue, bold: true } },
    { text: "     (12-month cumulative, skip most recent month)", options: { fontSize: 12, color: C.muted } },
  ], { x: 0.7, y: 1.15, w: 8.6, h: 0.7, valign: "middle", margin: 0 });

  const insights = [
    { title: "Return Horizons", body: "Short-term (<1m): Reversal\nIntermediate (3–12m): Momentum\nLong-term (3–5yr): Reversal\n\nMomentum is the intermediate effect.", col: C.accent },
    { title: "Skip Month", body: "Jegadeesh (1990): short-term\nreversal contaminates signal.\nSkipping last month removes\nmicrostructure noise.", col: C.teal },
    { title: "Crashes", body: "Daniel & Moskowitz (2015):\nMomentum crashes hard in\nhigh-vol periods (2008, 2020).\nHighly profitable but risky.", col: C.coral },
  ];
  insights.forEach((ins, i) => {
    const bx = 0.4 + i * 3.15;
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 2.2, w: 2.95, h: 2.7, fill: { color: C.white }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: 2.2, w: 2.95, h: 0.06, fill: { color: ins.col } });
    s.addText(ins.title, { x: bx + 0.15, y: 2.35, w: 2.65, h: 0.35, fontSize: 14, fontFace: "Georgia", color: ins.col, bold: true, margin: 0 });
    s.addText(ins.body, { x: bx + 0.15, y: 2.75, w: 2.65, h: 2.0, fontSize: 11, fontFace: "Calibri", color: C.text, valign: "top", margin: 0 });
  });
}

// ════════════════════════════════════════════════
//  CH 11 — CAPITAL ALLOCATION II
// ════════════════════════════════════════════════
chapterTitleSlide(11, "Capital Allocation II",
  "Big idea: When MVE is unreliable, use bet-sizing heuristics.\nSimpler models often beat optimal ones out-of-sample.", C.gold);

{
  let s = contentSlide("Bet-Sizing Heuristics");
  const heuristics = [
    { name: "Mean-Variance", formula: "wᵢ ∝ αᵢ / σ²(εᵢ)", note: "Optimal in theory; fragile in practice" },
    { name: "1/N", formula: "wᵢ = (1/N) × sign(αᵢ)", note: "Equal weight; ignores signal strength" },
    { name: "Proportional", formula: "wᵢ ∝ αᵢ", note: "Weight by alpha; ignores risk" },
    { name: "Risk Parity", formula: "wᵢ ∝ 1/σ(εᵢ)", note: "Equal vol contribution; robust" },
    { name: "Min Variance", formula: "wᵢ ∝ 1/σ²(εᵢ)", note: "Assumes equal alphas; uses risk only" },
    { name: "Shrinkage", formula: "wᵢ ∝ αᵢ / [(1−τ)σ² + τσ̄²]", note: "Blend MV toward simpler model" },
  ];
  heuristics.forEach((h, i) => {
    const by = 1.1 + i * 0.65;
    const bgCol = i % 2 === 0 ? C.offWhite : C.white;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: by, w: 9.0, h: 0.6, fill: { color: bgCol } });
    s.addText(h.name, { x: 0.7, y: by, w: 2.0, h: 0.6, fontSize: 13, fontFace: "Georgia", color: C.navy, bold: true, valign: "middle", margin: 0 });
    s.addText(h.formula, { x: 2.8, y: by, w: 3.2, h: 0.6, fontSize: 13, fontFace: "Calibri", color: C.midBlue, valign: "middle", margin: 0 });
    s.addText(h.note, { x: 6.2, y: by, w: 3.2, h: 0.6, fontSize: 11, fontFace: "Calibri", color: C.muted, valign: "middle", margin: 0 });
  });
  s.addText("Rule of thumb: small universe → 1/N or risk parity.  Large universe → shrinkage or MV with regularization.", {
    x: 0.5, y: 5.05, w: 9.0, h: 0.4, fontSize: 12, color: C.teal, italic: true, fontFace: "Calibri", margin: 0
  });
}

// ════════════════════════════════════════════════
//  CH 12 — PERFORMANCE EVALUATION
// ════════════════════════════════════════════════
chapterTitleSlide(12, "Performance Evaluation",
  "Big idea: Overfitting is the #1 enemy. If you didn't hold out a test sample,\nyour backtest is a fairy tale. Multiple testing makes it worse.", C.coral);

{
  let s = contentSlide("Alpha Testing & Overfitting");

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 4.3, h: 2.0, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Alpha Test", { x: 0.7, y: 1.2, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.coral, bold: true, margin: 0 });
  s.addText([
    { text: "rᵉₜ = α + β rᵐᵏᵗₜ + εₜ", options: { fontSize: 15, color: C.midBlue, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Appraisal Ratio = α / σ(ε) = t_α / √T", options: { fontSize: 13, color: C.midBlue, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Minimum AR to be p-confident true AR > target:", options: { fontSize: 11, color: C.text, breakLine: true } },
    { text: "AR_thresh = AR_target + z_p / √(T/12)", options: { fontSize: 12, color: C.coral, bold: true } },
  ], { x: 0.7, y: 1.6, w: 3.9, h: 1.4, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.1, w: 4.3, h: 2.0, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Overfitting in Action (MVE)", { x: 5.4, y: 1.2, w: 3.9, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.coral, bold: true, margin: 0 });
  s.addText([
    { text: "In-sample (1963–2012):", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "SR = 1.34, α = 12.3%/yr, t = 9.07", options: { fontSize: 13, color: C.green, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "Out-of-sample (2013–2025):", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "SR = 0.54, α = 3.2%/yr, t = 0.95", options: { fontSize: 13, color: C.coral, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "SR degrades by >50% out of sample.", options: { fontSize: 12, color: C.coral } },
  ], { x: 5.4, y: 1.6, w: 3.9, h: 1.4, valign: "top", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.35, w: 9.0, h: 1.9, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Diagnostics Toolkit", { x: 0.7, y: 3.45, w: 8.6, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.navy, bold: true, margin: 0 });
  s.addText("1. Sharpe Ratio & t-stat     2. Alpha & Appraisal Ratio     3. Cumulative returns & drawdown     4. Tail behavior (±3σ frequency)     5. Fraction to Half (robustness)     6. OOS test efficiency     7. Multiple testing correction", {
    x: 0.7, y: 3.85, w: 8.6, h: 0.5, fontSize: 11, fontFace: "Calibri", color: C.text, margin: 0
  });
  s.addText([
    { text: "Multiple testing: ", options: { bold: true, fontSize: 12, color: C.coral } },
    { text: "100 noise strategies, t > 1.64 → expect ~4 false positives. With 1 real signal (SR=1), 48-month test, t > 2:", options: { fontSize: 12, color: C.text, breakLine: true } },
    { text: "Hit rate = 15.9%  |  Detection rate = 48.5%", options: { fontSize: 13, color: C.coral, bold: true, breakLine: true } },
    { text: "Publication bias: HML SR ≈ 0.6 in-sample → ≈ 0 post-publication.", options: { fontSize: 12, color: C.muted } },
  ], { x: 0.7, y: 4.35, w: 8.6, h: 0.85, valign: "top", margin: 0 });
}

// Sample splitting
{
  let s = contentSlide("Sample Splitting: The Golden Rules");
  const rules = [
    { rule: "Never estimate and evaluate on the same sample.", icon: "1" },
    { rule: "Never use future data (lag everything).", icon: "2" },
    { rule: "Keep a hold-out sample. Don't peek until done tuning.", icon: "3" },
    { rule: "Document all discarded ideas (affects multiple testing).", icon: "4" },
  ];
  rules.forEach((r, i) => {
    const by = 1.2 + i * 0.85;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: by, w: 9.0, h: 0.7, fill: { color: C.white }, shadow: mkShadow() });
    s.addShape(pres.shapes.OVAL, { x: 0.65, y: by + 0.1, w: 0.5, h: 0.5, fill: { color: C.coral } });
    s.addText(r.icon, { x: 0.65, y: by + 0.1, w: 0.5, h: 0.5, fontSize: 16, fontFace: "Georgia", color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
    s.addText(r.rule, { x: 1.4, y: by, w: 7.8, h: 0.7, fontSize: 15, fontFace: "Calibri", color: C.text, valign: "middle", margin: 0 });
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.7, w: 9.0, h: 0.7, fill: { color: C.navy } });
  s.addText("Three-Way Split:  Estimation (fit model) → Tuning (select hyperparams) → Hold-out (final test)", {
    x: 0.7, y: 4.7, w: 8.6, h: 0.7, fontSize: 14, fontFace: "Calibri", color: C.white, valign: "middle", margin: 0
  });
}

// ════════════════════════════════════════════════
//  CH 13 — MACHINE LEARNING
// ════════════════════════════════════════════════
chapterTitleSlide(13, "Machine Learning in Finance",
  "Big idea: Signal-to-noise is destiny. In low-SNR domains like finance,\nregularized simple models often beat complex ones.", C.coral);

{
  let s = contentSlide("The Central Challenge");
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 9.0, h: 1.2, fill: { color: C.navy } });
  s.addText([
    { text: "Rᵢ,ₜ₊₁ = F(Xᵢ,ₜ) + εᵢ,ₜ", options: { fontSize: 22, fontFace: "Georgia", color: C.white, bold: true } },
    { text: "     Signal ≈ 0.1–0.5%/month  •  Noise ≈ 10%  •  SNR ≈ 0.01", options: { fontSize: 13, fontFace: "Calibri", color: C.ice } },
  ], { x: 0.7, y: 1.15, w: 8.6, h: 1.1, valign: "middle", margin: 0 });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.6, w: 9.0, h: 2.6, fill: { color: C.white }, shadow: mkShadow() });
  s.addText("Model Comparison (29 characteristics, ~200K stock-months)", {
    x: 0.7, y: 2.7, w: 8.6, h: 0.35, fontSize: 14, fontFace: "Georgia", color: C.navy, bold: true, margin: 0
  });
  const methods = [
    { name: "Lasso (L1)", sr: "1.03", note: "Baseline — hard to beat!" },
    { name: "Elastic Net", sr: "1.10", note: "Handles correlated features" },
    { name: "Lasso + interactions", sr: "2.40", note: "435 features, marginal gain" },
    { name: "Random Forest", sr: "1.47", note: "Auto interactions, shallow" },
    { name: "Gradient Boosted Trees", sr: "1.82", note: "Sequential residual fitting" },
    { name: "Neural Net (regularized)", sr: "2.61", note: "Dropout + early stopping" },
  ];
  methods.forEach((m, i) => {
    const by = 3.15 + i * 0.32;
    const bgCol = i % 2 === 0 ? C.lightBg : C.white;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: by, w: 8.8, h: 0.3, fill: { color: bgCol } });
    s.addText(m.name, { x: 0.8, y: by, w: 2.5, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.navy, bold: true, valign: "middle", margin: 0 });
    s.addText(`SR: ${m.sr}`, { x: 3.4, y: by, w: 1.2, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.accent, bold: true, valign: "middle", margin: 0 });
    s.addText(m.note, { x: 4.8, y: by, w: 4.4, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.muted, valign: "middle", margin: 0 });
  });
}

// ML lessons
{
  let s = contentSlide("ML Lessons for Finance");
  const lessons = [
    { title: "Start simple", body: "Lasso/Elastic Net are hard to beat, interpretable, and robust. Complexity rarely pays in low-SNR.", col: C.accent },
    { title: "Regularize everything", body: "Dropout + weight decay + early stopping for NNs. Keep trees shallow (depth ≤ 3). Shrink covariances.", col: C.teal },
    { title: "Respect the time series", body: "Never use future data. Three-way split. Learning curves matter more than architecture.", col: C.gold },
    { title: "Double descent", body: "Overparameterized models can recover signal if it exists — but CANNOT create signal from noise.", col: C.coral },
  ];
  lessons.forEach((l, i) => {
    const row = Math.floor(i / 2), col = i % 2;
    const bx = 0.5 + col * 4.7, by = 1.1 + row * 2.1;
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: by, w: 4.4, h: 1.8, fill: { color: C.white }, shadow: mkShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: bx, y: by, w: 0.08, h: 1.8, fill: { color: l.col } });
    s.addText(l.title, { x: bx + 0.25, y: by + 0.1, w: 4.0, h: 0.35, fontSize: 16, fontFace: "Georgia", color: l.col, bold: true, margin: 0 });
    s.addText(l.body, { x: bx + 0.25, y: by + 0.5, w: 4.0, h: 1.2, fontSize: 13, fontFace: "Calibri", color: C.text, valign: "top", margin: 0 });
  });
}

// ════════════════════════════════════════════════
//  SYNTHESIS — CONNECTIONS
// ════════════════════════════════════════════════
{
  sn++;
  let s = pres.addSlide();
  darkSlide(s);
  s.addText("Connecting Everything", {
    x: 0.6, y: 0.25, w: 9, h: 0.65, fontSize: 30, fontFace: "Georgia",
    color: C.white, bold: true, margin: 0
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.1, w: 9.0, h: 1.3, fill: { color: C.midBlue, transparency: 30 } });
  s.addText([
    { text: "The Golden Thread: One Equation Runs Through It All", options: { fontSize: 16, fontFace: "Georgia", color: C.white, bold: true, breakLine: true } },
    { text: "", options: { fontSize: 6, breakLine: true } },
    { text: "w* = (1/γ) × E[rᵉ] / Var(r)", options: { fontSize: 22, fontFace: "Georgia", color: C.ice, bold: true, breakLine: true } },
    { text: "Every chapter addresses a piece: measuring rᵉ (4), forecasting E[rᵉ] or Var (5), decomposing via factors (6–9), constructing strategies (10–11), evaluating honestly (12–13).", options: { fontSize: 12, fontFace: "Calibri", color: C.ice } },
  ], { x: 0.7, y: 1.15, w: 8.6, h: 1.2, valign: "middle", margin: 0 });

  const connections = [
    { from: "Factor model (6)", to: "Capital allocation (8)", link: "α → what to buy; β → what to hedge" },
    { from: "Hedging (6)", to: "Appraisal ratio (9)", link: "SR² = SR²_mkt + AR²" },
    { from: "Cross-sectional (10)", to: "ML (13)", link: "Characteristics → features → prediction" },
    { from: "Estimation risk (9)", to: "Bet sizing (11)", link: "When MV fails → heuristics" },
    { from: "Timing (5)", to: "Evaluation (12)", link: "OOS R² < 0 → overfitting!" },
  ];
  connections.forEach((c, i) => {
    const by = 2.7 + i * 0.52;
    s.addText(c.from, { x: 0.5, y: by, w: 2.4, h: 0.45, fontSize: 11, fontFace: "Calibri", color: C.accent, bold: true, valign: "middle", margin: 0 });
    s.addText("→", { x: 2.9, y: by, w: 0.3, h: 0.45, fontSize: 14, color: C.ice, align: "center", valign: "middle", margin: 0 });
    s.addText(c.to, { x: 3.2, y: by, w: 2.6, h: 0.45, fontSize: 11, fontFace: "Calibri", color: C.gold, bold: true, valign: "middle", margin: 0 });
    s.addText(c.link, { x: 5.8, y: by, w: 3.8, h: 0.45, fontSize: 11, fontFace: "Calibri", color: C.ice, valign: "middle", margin: 0 });
  });
  addSlideNumber(s, sn, TOTAL);
}

// ════════════════════════════════════════════════
//  EQUATIONS CHEAT SHEET (updated)
// ════════════════════════════════════════════════
{
  sn++;
  let s = pres.addSlide();
  lightSlide(s);
  s.addText("Key Equations — Cheat Sheet", {
    x: 0.6, y: 0.25, w: 9, h: 0.6, fontSize: 26, fontFace: "Georgia",
    color: C.navy, bold: true, margin: 0
  });

  const eqs = [
    { name: "Sharpe Ratio", eq: "SR = E[Rᵉ] / σ(Rᵉ)" },
    { name: "Optimal weight", eq: "w* = (1/γ) E[rᵉ] / Var(r)" },
    { name: "Factor model", eq: "rᵉ = α + βf + ε" },
    { name: "Factor E[R] model", eq: "E[rᵉᵢ] = αᵢ + Σₖ βᵢₖ λₖ    (λₖ = E[fₖ])" },
    { name: "Factor risk model", eq: "Σ = B Σ_F B' + Σ_ε" },
    { name: "MVE portfolio", eq: "W* = (1/γ) Σ⁻¹ E[Rᵉ]" },
    { name: "Portfolio variance", eq: "Var(Rₚ) = W'ΣW  =  β_p' Σ_F β_p + w'Σ_ε w" },
    { name: "Combined Sharpe", eq: "SR² = SR²_mkt + AR²" },
    { name: "Appraisal Ratio", eq: "AR = α / σ(ε) = t_α / √T" },
    { name: "Vol-managed weight", eq: "wₜ = c / RVₜ" },
    { name: "Lasso objective", eq: "min (1/2n)Σ(yᵢ − X'β)² + λ‖β‖₁" },
  ];

  eqs.forEach((e, i) => {
    const by = 0.95 + i * 0.41;
    const bgCol = i % 2 === 0 ? C.white : C.lightBg;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: by, w: 9.0, h: 0.38, fill: { color: bgCol } });
    s.addText(e.name, { x: 0.7, y: by, w: 2.8, h: 0.38, fontSize: 11, fontFace: "Georgia", color: C.navy, bold: true, valign: "middle", margin: 0 });
    s.addText(e.eq, { x: 3.6, y: by, w: 5.7, h: 0.38, fontSize: 12, fontFace: "Calibri", color: C.midBlue, valign: "middle", margin: 0 });
  });
  addSlideNumber(s, sn, TOTAL);
}

// ════════════════════════════════════════════════
//  FINAL SLIDE
// ════════════════════════════════════════════════
{
  sn++;
  let s = pres.addSlide();
  darkSlide(s);
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 1.5, w: 10, h: 2.8, fill: { color: C.midBlue, transparency: 25 } });

  s.addText("Five Things to Remember", {
    x: 0.6, y: 0.3, w: 9, h: 0.7, fontSize: 32, fontFace: "Georgia",
    color: C.white, bold: true, margin: 0
  });

  const takeaways = [
    "Excess returns are the fundamental object — risk premium is compensation for bearing risk.",
    "Factor models decompose returns: α is skill, β is exposure. Hedge β to isolate α.",
    "Diversification is the only free lunch: Var(portfolio) ≪ avg(Var) when correlations < 1.",
    "Estimation risk is real: MVE looks great in-sample, degrades out-of-sample. Regularize.",
    "Signal-to-noise is low in finance: simple regularized models beat complex ones. Always validate OOS.",
  ];
  takeaways.forEach((t, i) => {
    s.addText(`${i + 1}.`, { x: 0.6, y: 1.6 + i * 0.52, w: 0.35, h: 0.48, fontSize: 16, fontFace: "Georgia", color: C.gold, bold: true, valign: "top", margin: 0 });
    s.addText(t, { x: 1.0, y: 1.6 + i * 0.52, w: 8.3, h: 0.48, fontSize: 14, fontFace: "Calibri", color: C.white, valign: "top", margin: 0 });
  });

  s.addText("Good luck on the exam!", {
    x: 0.6, y: 4.8, w: 9, h: 0.5, fontSize: 18, fontFace: "Georgia",
    color: C.ice, italic: true, margin: 0
  });
  addSlideNumber(s, sn, TOTAL);
}

// ════════════════════════════════════════════════
//  WRITE
// ════════════════════════════════════════════════
const outPath = "/sessions/nice-confident-thompson/mnt/UG54/BigPictureReview.pptx";
pres.writeFile({ fileName: outPath }).then(() => {
  console.log(`Created: ${outPath} with ${sn} slides`);
}).catch(err => console.error("Error:", err));
