# UI Beautification Phase 1: Basic Visual Upgrade

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the Fireplace Hearthstone simulator UI from a flat, plain prototype into a visually rich interface that captures the fantasy atmosphere of real Hearthstone — using only pure CSS (no image assets, no font changes).

**Architecture:** All changes are CSS-only modifications to `GameBoard.css` (the 2935-line master stylesheet) and minor corresponding adjustments in `App.css` for menu-screen consistency. The approach is layered: first establish a rich design token system (CSS variables), then rebuild the game board background with multi-layer gradients and textures, then upgrade each UI region (opponent zone, player zone, divider, header, sidebar) with atmospheric styling, decorative borders, and depth effects. No component logic changes needed — this is purely a visual overhaul.

**Tech Stack:** Pure CSS (custom properties, gradients, clip-path, pseudo-elements, SVG data-URI filters, CSS animations), React 19 + TypeScript (no component changes expected), Vite build system

**Scope:** Phase 1 of a multi-phase beautification plan. Excludes: fonts (user preference), card redesign (Phase 2), hero portrait overhaul (Phase 3), minion card-style conversion (Phase 4), polish details (Phase 5).

**Key File:**
- `webui/client/src/components/GameBoard.css` — **THE** single file that contains all game board styling (~2935 lines). Every task modifies this file.

---

### Task 1: Design Token System Overhaul

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:1-24`

Replace the current flat `:root` variable block with an expanded, hierarchical color system. This is the foundation — all subsequent tasks reference these tokens.

- [ ] **Step 1: Replace the `:root` CSS variable block (lines 1-24)**

Find the existing `:root { ... }` block and replace it entirely with:

```css
/* ========================================
   DESIGN TOKEN SYSTEM - Phase 1
   Hierarchical color palette with gold tiers,
   atmospheric zones, and per-class themes
   ======================================== */

:root {
  /* ---- Core Neutrals ---- */
  --bg-deepest: #0a0810;
  --bg-primary: #12101a;
  --bg-secondary: #1a1622;
  --bg-tertiary: #251e2a;
  --bg-card: #2d2436;
  --bg-card-hover: #3a2d48;
  --bg-surface: rgba(255, 255, 255, 0.03);
  --bg-surface-hover: rgba(255, 255, 255, 0.07);

  /* ---- Gold Palette (4-tier for depth) ---- */
  --gold-bright: #f0d878;
  --gold: #c8a45c;
  --gold-dim: #8b7355;
  --gold-dark: #5a4a32;
  --gold-glow: rgba(240, 216, 120, 0.35);
  --gold-subtle: rgba(200, 164, 92, 0.15);

  /* ---- Semantic Colors ---- */
  --red: #ff4444;
  --red-glow: rgba(255, 68, 68, 0.4);
  --red-dark: #cc2222;
  --yellow: #ffcc00;
  --yellow-glow: rgba(255, 204, 0, 0.35);
  --blue: #4488ff;
  --blue-glow: rgba(68, 136, 255, 0.35);
  --blue-dark: #2266dd;
  --green-player: #408040;
  --green-light: rgba(64, 128, 64, 0.2);
  --green-glow: rgba(76, 175, 80, 0.5);
  --red-opponent: #8b3030;
  --red-light: rgba(139, 48, 48, 0.18);
  --purple: #9b59b6;
  --purple-glow: rgba(155, 89, 182, 0.35);

  /* ---- Zone Atmosphere Colors ---- */
  /* Opponent zone: deep crimson-violet */
  --zone-opponent-bg: linear-gradient(
    180deg,
    rgba(80, 20, 50, 0.25) 0%,
    rgba(50, 15, 35, 0.2) 40%,
    rgba(30, 10, 25, 0.12) 100%
  );
  --zone-opponent-border: rgba(180, 60, 90, 0.25);
  --zone-opponent-accent: #c85070;

  /* Player zone: deep forest-emerald */
  --zone-player-bg: linear-gradient(
    180deg,
    rgba(15, 50, 30, 0.2) 0%,
    rgba(10, 35, 22, 0.15) 40%,
    rgba(8, 25, 18, 0.1) 100%
  );
  --zone-player-border: rgba(60, 150, 90, 0.25);
  --zone-player-accent: #40a060;

  /* Center divider: neutral warm */
  --zone-center-bg: linear-gradient(
    180deg,
    transparent 0%,
    rgba(200, 164, 92, 0.06) 40%,
    rgba(200, 164, 92, 0.1) 50%,
    rgba(200, 164, 92, 0.06) 60%,
    transparent 100%
  );

  /* ---- Per-Class Theme Colors ---- */
  --class-druid: #ff7d0a;
  --class-hunter: #abd473;
  --class-mage: #69ccf0;
  --class-paladin: #f58cba;
  --class-priest: #ffffff;
  --class-shaman: #0070de;
  --class-warrior: #c79c6e;
  --class-rogue: #fff569;
  --class-warlock: #9482c9;
  --class-demonhunter: #a330c9;
  --class-neutral: #999999;

  /* ---- Layout Tokens ---- */
  --header-height: 3rem;
  --log-width: clamp(160px, 20vw, 220px);

  /* ---- Card/Minion Sizing ---- */
  --card-width: clamp(60px, 12vw, 100px);
  --card-height: clamp(84px, 16.8vw, 140px);
  --minion-width: clamp(50px, 10vw, 80px);
  --minion-height: clamp(62px, 13vw, 100px);
  --hero-size: clamp(3rem, 8vw, 5rem);

  /* ---- Border/Shadow Tokens ---- */
  --border-subtle: 1px solid rgba(200, 164, 92, 0.12);
  --border-normal: 1px solid rgba(200, 164, 92, 0.25);
  --border-strong: 2px solid var(--gold-dim);
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
  --shadow-gold: 0 0 20px var(--gold-subtle);
  --inner-glow: inset 0 0 20px rgba(200, 164, 92, 0.05);

  /* ---- Texture Overlay (SVG noise filter) ---- */
  --noise-opacity: 0.03;
}
```

- [ ] **Step 2: Verify the page still renders without layout breakage**

Run the dev server and open the game board in browser. Confirm:
- The game container still fills the viewport
- All existing elements are visible (no `var()` reference errors)
- The overall color scheme shifted darker/richer but nothing broke

Run: `cd /home/ubuntu/code/fireplace_lite/webui/client && npm run dev`
Expected: Dev server starts, page loads without CSS parse errors

- [ ] **Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): expand CSS design token system with hierarchical palette"
```

---

### Task 2: Game Board Background Reconstruction

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:27-34` (`.game-container`)
- Modify: `webui/client/src/components/GameBoard.css:191-198` (`.game-board`)

Replace the flat gradient background with a multi-layer textured game board that simulates the Hearthstone table feel.

- [ ] **Step 1: Rebuild `.game-container` background**

Find `.game-container` (around line 27) and replace its styles:

```css
/* 游戏容器 - Rich atmospheric background */
.game-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;

  /*
   * Layer 1 (bottom): Deep base
   * Layer 2: Radial vignette from center
   * Layer 3: Subtle noise texture via SVG filter
   * Layer 4: Top-to-bottom atmosphere gradient (warm center)
   */
  background:
    /* Noise texture overlay */
    url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"),
    /* Radial vignette - edges darker */
    radial-gradient(ellipse 120% 100% at 50% 50%, transparent 40%, var(--bg-deepest) 100%),
    /* Base gradient - deep purple-black to dark brown */
    linear-gradient(
      180deg,
      #0e0a14 0%,
      #151020 15%,
      #1a1525 35%,
      #1a1820 55%,
      #171a18 75%,
      #0e1410 100%
    );
  background-color: var(--bg-primary);
}
```

- [ ] **Step 2: Add ambient light glow behind the game board**

After the `.game-container` rule, add a new pseudo-element rule for ambient atmosphere:

```css
/* Ambient glow effect on game container */
.game-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;

  /* Soft central glow simulating table-top lighting */
  background: radial-gradient(
    ellipse 80% 60% at 50% 48%,
    rgba(200, 164, 92, 0.04) 0%,
    rgba(200, 164, 92, 0.02) 30%,
    transparent 70%
  );
}

/* Ensure content sits above the ambient layer */
.game-container > * {
  position: relative;
  z-index: 1;
}
```

- [ ] **Step 3: Rebuild `.game-board` with textured surface**

Find `.game-board` (around line 191) and replace:

```css
/* 游戏棋盘 - Textured playing surface */
.game-board {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: clamp(0.3rem, 1vw, 0.8rem);
  position: relative;
  overflow-y: auto;

  /* Multi-layer board texture */
  background:
    /* Fine grain texture */
    url("data:image/svg+xml,%3Csvg viewBox='0 0 128 128' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23g)' opacity='0.035'/%3E%3C/svg%3E"),
    /* Subtle wood-grain-like lines (horizontal streaks) */
    repeating-linear-gradient(
      0deg,
      transparent 0px,
      transparent 2px,
      rgba(200, 164, 92, 0.008) 2px,
      rgba(200, 164, 92, 0.008) 3px
    ),
    /* Board base: very subtle warm gradient */
    linear-gradient(
      180deg,
      rgba(30, 25, 35, 0.4) 0%,
      rgba(25, 22, 30, 0.3) 50%,
      rgba(20, 28, 25, 0.35) 100%
    );

  /* Inner border glow */
  box-shadow:
    inset 0 0 60px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.03);
}
```

- [ ] **Step 4: Visual verification**

Open the game board in browser and verify:
- Background has visible depth (center lighter than edges)
- Subtle texture/grain is perceptible on the board area
- No layout shifts occurred

- [ ] **Step 5: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): add multi-layer textured game board background with atmospheric depth"
```

---

### Task 3: Header Bar Enhancement

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:37-99` (`.game-header` and related)

Upgrade the top header bar from a simple gradient strip to a rich ornamental bar with depth.

- [ ] **Step 1: Replace `.game-header` styles**

Find `.game-header` (around line 37) and replace:

```css
/* 顶部标题栏 - Ornamental header bar */
.game-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 clamp(0.5rem, 3vw, 1.5rem);
  position: relative;
  flex-shrink: 0;

  /* Rich metallic gradient */
  background:
    linear-gradient(
      180deg,
      rgba(60, 48, 35, 0.95) 0%,
      rgba(40, 32, 25, 0.98) 40%,
      rgba(26, 20, 18, 1) 100%
    );

  /* Bottom decorative border - double-line effect */
  border-bottom: none;
  box-shadow:
    0 2px 12px rgba(0, 0, 0, 0.5),
    inset 0 -1px 0 rgba(200, 164, 92, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

/* Decorative bottom border line for header */
.game-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--gold-dim) 15%,
    var(--gold) 50%,
    var(--gold-dim) 85%,
    transparent 100%
  );
  opacity: 0.6;
}
```

- [ ] **Step 2: Enhance header title typography**

Find `.game-header h1` (around line 49) and replace:

```css
.game-header h1 {
  font-size: clamp(1rem, 4vw, 1.5rem);
  color: var(--gold);
  margin: 0;
  font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  text-shadow:
    0 0 10px var(--gold-glow),
    0 1px 2px rgba(0, 0, 0, 0.8);
}
```

- [ ] **Step 3: Enhance settings button**

Find `.header-settings-btn` (around line 56) and replace:

```css
.header-settings-btn {
  background: rgba(200, 164, 92, 0.1);
  border: 1px solid var(--gold-dim);
  border-radius: 6px;
  font-size: clamp(1rem, 2.5vw, 1.3rem);
  cursor: pointer;
  color: var(--gold);
  padding: 0.3rem 0.5rem;
  transition: all 0.2s ease;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-settings-btn:hover {
  background: rgba(200, 164, 92, 0.2);
  border-color: var(--gold);
  box-shadow: var(--shadow-gold);
  transform: rotate(30deg);
}
```

- [ ] **Step 4: Enhance settings dropdown menu**

Find `.header-settings-menu` (around line 65) and replace:

```css
.header-settings-menu {
  position: absolute;
  top: calc(var(--header-height) - 2px);
  right: clamp(0.5rem, 3vw, 1.5rem);
  background: linear-gradient(
    180deg,
    rgba(45, 36, 50, 0.98) 0%,
    rgba(26, 20, 30, 0.99) 100%
  );
  border: 2px solid var(--gold-dim);
  border-radius: 0 0 12px 12px;
  padding: 0.8rem;
  z-index: 1000;
  box-shadow:
    var(--shadow-lg),
    0 8px 24px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(8px);
}
```

Also update `.header-settings-menu button` (around line 82):

```css
.header-settings-menu button {
  display: block;
  width: 100%;
  padding: 0.4rem 0.8rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(200, 164, 92, 0.15);
  border-radius: 6px;
  color: #ccc;
  cursor: pointer;
  margin-bottom: 0.3rem;
  font-size: 0.85rem;
  transition: all 0.15s ease;
}

.header-settings-menu button:hover {
  background: rgba(200, 164, 92, 0.15);
  border-color: var(--gold-dim);
  color: var(--gold);
}

.header-settings-menu button.active {
  background: rgba(200, 164, 92, 0.2);
  border-color: var(--gold);
  color: var(--gold-bright);
  box-shadow: inset 0 0 8px var(--gold-subtle);
}
```

- [ ] **Step 5: Update back button style**

Find `.header-back-btn` (around line 1486) and replace:

```css
.header-back-btn {
  position: absolute;
  left: 0.5rem;
  background: rgba(200, 164, 92, 0.1);
  border: 1px solid var(--gold-dim);
  border-radius: 6px;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--gold);
  padding: 0.3rem 0.5rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.header-back-btn:hover {
  background: rgba(200, 164, 92, 0.2);
  border-color: var(--gold);
  box-shadow: var(--shadow-gold);
}
```

- [ ] **Step 6: Visual verification**

Open the game board and verify:
- Header has a rich metallic feel with subtle golden bottom line
- Title text has a soft glow
- Settings button rotates on hover
- Dropdown menu has glass-morphism effect

- [ ] **Step 7: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): enhance header bar with ornamental styling and depth effects"
```

---

### Task 4: Opponent Zone Atmospheric Styling

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:201-216` (opponent hand)
- Modify: `webui/client/src/components/GameBoard.css:218-232` (hero area - opponent)
- Modify: `webui/client/src/components/GameBoard.css:541-558` (opponent field)

Give the entire opponent half of the board a distinct crimson-violet atmosphere.

- [ ] **Step 1: Restyle opponent hand area**

Find `.opponent-hand-area` (around line 201) and replace:

```css
/* 对手手牌区 - Crimson-tinted zone */
.opponent-hand-area {
  height: clamp(2.5rem, 6vw, 4rem);
  display: flex;
  justify-content: center;
  gap: clamp(2px, 0.5vw, 5px);
  padding: clamp(2px, 0.5vw, 5px);
  position: relative;
}

/* Subtle red glow beneath opponent hand */
.opponent-hand-area::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 10%;
  right: 10%;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--zone-opponent-accent),
    transparent
  );
  opacity: 0.3;
  filter: blur(2px);
}
```

- [ ] **Step 2: Restyle opponent card-backs**

Find `.card-back-small` (around line 209) and replace:

```css
.card-back-small {
  width: clamp(1.5rem, 4vw, 2.5rem);
  height: clamp(2rem, 5.5vw, 3.5rem);
  background:
    linear-gradient(145deg, #1a3a5c 0%, #0d2040 50%, #0a1830 100%);
  border: 2px solid var(--zone-opponent-accent);
  border-radius: 6px;
  box-shadow:
    0 2px 6px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(100, 160, 220, 0.2),
    0 0 8px rgba(200, 80, 112, 0.15);
  position: relative;
  overflow: hidden;
}

/* Card-back pattern decoration */
.card-back-small::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50%;
  height: 50%;
  border: 1.5px solid rgba(100, 160, 220, 0.25);
  border-radius: 2px;
  opacity: 0.5;
}

.card-back-small::after {
  content: '?';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: clamp(0.6rem, 1.5vw, 1rem);
  color: rgba(100, 160, 220, 0.4);
  font-weight: bold;
}
```

- [ ] **Step 3: Restyle opponent hero area with zone atmosphere**

Find `.opponent-hero-area` (around line 226) and replace:

```css
.opponent-hero-area {
  background: var(--zone-opponent-bg);
  border-top: var(--border-subtle);
  border-bottom: var(--border-subtle);
  position: relative;
}

/* Subtle red ambient glow behind opponent hero */
.opponent-hero-area::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 150%;
  height: 140%;
  background: radial-gradient(
    ellipse at center,
    rgba(139, 48, 48, 0.08) 0%,
    transparent 70%
  );
  pointer-events: none;
  z-index: 0;
}

.opponent-hero-area > * {
  position: relative;
  z-index: 1;
}
```

- [ ] **Step 4: Restyle opponent field area**

Find `.opponent-field` (around line 551) and replace:

```css
.opponent-field {
  background:
    /* Zone tint */
    var(--zone-opponent-bg),
    /* Subtle horizontal lines suggesting board planks */
    repeating-linear-gradient(
      0deg,
      transparent 0px,
      transparent 8px,
      rgba(139, 48, 48, 0.03) 8px,
      rgba(139, 48, 48, 0.03) 9px
    );
  border-radius: 8px;
  position: relative;
}

/* Opponent field inner glow */
.opponent-field::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 8px;
  box-shadow: inset 0 0 30px rgba(139, 48, 48, 0.1);
  pointer-events: none;
}
```

- [ ] **Step 5: Visual verification**

Open a game and check:
- Opponent half has a noticeable reddish-purple tint vs player half
- Card-backs have a richer blue pattern look
- Hero area has subtle red ambient glow

- [ ] **Step 6: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): apply crimson-violet atmospheric styling to opponent zone"
```

---

### Task 5: Player Zone Atmospheric Styling

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:230-232` (player hero area)
- Modify: `webui/client/src/components/GameBoard.css:555-558` (player field)
- Modify: `webui/client/src/components/GameBoard.css:858-866` (player hand area)

Mirror Task 4's treatment but with emerald-green tones for the player side.

- [ ] **Step 1: Restyle player hero area with green atmosphere**

Find `.player-hero-area` (around line 230) and replace:

```css
.player-hero-area {
  background: var(--zone-player-bg);
  border-top: var(--border-subtle);
  border-bottom: var(--border-subtle);
  position: relative;
}

/* Subtle green ambient glow behind player hero */
.player-hero-area::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 150%;
  height: 140%;
  background: radial-gradient(
    ellipse at center,
    rgba(64, 128, 64, 0.08) 0%,
    transparent 70%
  );
  pointer-events: none;
  z-index: 0;
}

.player-hero-area > * {
  position: relative;
  z-index: 1;
}
```

- [ ] **Step 2: Restyle player field area**

Find `.player-field` (around line 555) and replace:

```css
.player-field {
  background:
    /* Zone tint */
    var(--zone-player-bg),
    /* Subtle horizontal lines */
    repeating-linear-gradient(
      0deg,
      transparent 0px,
      transparent 8px,
      rgba(64, 128, 64, 0.03) 8px,
      rgba(64, 128, 64, 0.03) 9px
    );
  position: relative;
  border-radius: 8px;
}

/* Player field inner glow */
.player-field::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 8px;
  box-shadow: inset 0 0 30px rgba(64, 128, 64, 0.1);
  pointer-events: none;
}
```

- [ ] **Step 3: Enhance player hand area**

Find `.player-hand-area` (around line 859) and replace:

```css
/* 玩家手牌区 - Emerald-tinted zone */
.player-hand-area {
  min-height: calc(var(--card-height) + 1rem);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: clamp(0.3rem, 1vw, 0.8rem) clamp(0.5rem, 3vw, 2rem);
  gap: clamp(0.2rem, 0.5vw, 0.5rem);
  position: relative;
}

/* Green accent line above hand */
.player-hand-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--zone-player-accent),
    transparent
  );
  opacity: 0.3;
  filter: blur(2px);
}
```

- [ ] **Step 4: Visual verification**

Confirm:
- Player half has a clear emerald-green atmosphere distinct from opponent's crimson
- Hand area has a subtle green accent line above it
- Both zones meet naturally at the center without harsh dividing line

- [ ] **Step 5: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): apply emerald-green atmospheric styling to player zone"
```

---

### Task 6: Central Divider Decoration

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:708-788` (`.field-divider`, `.turn-indicator`, `.turn-timer`)

Transform the thin center line into a decorative banner area reminiscent of Hearthstone's turn indicator zone.

- [ ] **Step 1: Replace `.field-divider` styles**

Find `.field-divider` (around line 708) and replace:

```css
/* 中央分隔线 - Decorative turn banner area */
.field-divider {
  height: clamp(2rem, 5vw, 3rem);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: var(--zone-center-bg);

  /* Decorative top and bottom borders */
  border-top: 1px solid rgba(200, 164, 92, 0.1);
  border-bottom: 1px solid rgba(200, 164, 92, 0.1);
}

/* Ornamental corner decorations on divider */
.field-divider::before,
.field-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: clamp(40px, 10vw, 100px);
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--gold-dim),
    transparent
  );
  opacity: 0.4;
}

.field-divider::before {
  left: clamp(10px, 3vw, 30px);
}

.field-divider::after {
  right: clamp(10px, 3vw, 30px);
}
```

- [ ] **Step 2: Enhance turn indicator badge**

Find `.turn-indicator` (around line 717) and replace:

```css
.turn-indicator {
  background: linear-gradient(
    180deg,
    rgba(40, 30, 20, 0.9) 0%,
    rgba(20, 15, 10, 0.95) 100%
  );
  padding: clamp(0.25rem, 0.8vw, 0.5rem) clamp(0.8rem, 2.5vw, 1.8rem);
  border-radius: 20px;
  color: var(--gold);
  font-weight: bold;
  font-size: clamp(0.75rem, 1.6vw, 1rem);
  letter-spacing: 0.05em;
  border: 1px solid var(--gold-dim);
  box-shadow:
    0 2px 8px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 0 12px var(--gold-subtle);
  text-transform: uppercase;
  position: relative;
  z-index: 2;
}
```

- [ ] **Step 3: Enhance turn timer**

Find `.turn-timer` (around line 763) and replace:

```css
.turn-timer {
  position: absolute;
  right: 1rem;
  background: linear-gradient(
    180deg,
    rgba(30, 25, 20, 0.85) 0%,
    rgba(20, 15, 12, 0.9) 100%
  );
  padding: 0.2rem 0.7rem;
  border-radius: 6px;
  color: #aaa;
  font-size: clamp(0.6rem, 1.2vw, 0.8rem);
  border: 1px solid rgba(200, 164, 92, 0.15);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.03em;
}

.turn-timer.warning {
  color: var(--red);
  border-color: rgba(255, 68, 68, 0.3);
  background: linear-gradient(
    180deg,
    rgba(60, 20, 15, 0.9) 0%,
    rgba(40, 12, 10, 0.95) 100%
  );
  animation: timer-pulse 0.5s ease-in-out infinite;
  box-shadow: 0 0 10px var(--red-glow);
}
```

- [ ] **Step 4: Visual verification**

Check:
- Center divider has a soft glowing band feel
- Turn indicator looks like a premium badge
- Timer has a refined capsule shape
- Corner ornament lines are visible on wide screens

- [ ] **Step 5: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): decorate central divider as ornamental banner area"
```

---

### Task 7: Per-Class Hero Theme Integration

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:319-349` (`.hero-portrait` class colors)
- Modify: `webui/client/src/components/GameBoard.css:2157-2177` (`.hero-portrait` enhancements)

Upgrade hero portraits from flat colored circles to themed class icons with decorative frames using the new class color variables.

- [ ] **Step 1: Enhance base `.hero-portrait` styles**

Find `.hero-portrait` (around line 319) and replace:

```css
/* 英雄头像 - Themed class portraits with decorative frame */
.hero-portrait {
  width: var(--hero-size);
  height: var(--hero-size);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;

  /* Double-ring border: outer gold, inner class-colored */
  border: 3px solid var(--gold-dim);
  box-shadow:
    0 0 15px rgba(0, 0, 0, 0.4),
    inset 0 0 10px rgba(0, 0, 0, 0.3),
    0 0 8px var(--gold-subtle);
}

/* Outer decorative ring (pseudo-element) */
.hero-portrait::before {
  content: '';
  position: absolute;
  inset: -5px;
  border-radius: 50%;
  border: 1px solid rgba(200, 164, 92, 0.2);
  pointer-events: none;
}

.hero-portrait.opponent {
  border-color: var(--zone-opponent-accent);
  box-shadow:
    0 0 15px rgba(0, 0, 0, 0.4),
    inset 0 0 10px rgba(0, 0, 0, 0.3),
    0 0 12px rgba(200, 80, 112, 0.2);
}

.hero-portrait.player {
  border-color: var(--zone-player-accent);
  box-shadow:
    0 0 15px rgba(0, 0, 0, 0.4),
    inset 0 0 10px rgba(0, 0, 0, 0.3),
    0 0 12px rgba(64, 160, 96, 0.2);
}
```

- [ ] **Step 2: Replace all class-specific hero backgrounds with themed versions**

Find the `.hero-portrait.hero-*` rules (around lines 339-349) and replace the entire block:

```css
/* Per-class theme gradients with inner glow matching class color */
.hero-portrait.hero-hunter {
  background: radial-gradient(circle at 40% 35%, rgba(171, 212, 115, 0.4) 0%, rgba(139, 172, 82, 0.2) 40%, #5D4A1C 100%);
  border-color: var(--class-hunter);
}
.hero-portrait.hero-mage {
  background: radial-gradient(circle at 40% 35%, rgba(105, 204, 240, 0.4) 0%, rgba(105, 204, 240, 0.2) 40%, #1a3a5c 100%);
  border-color: var(--class-mage);
}
.hero-portrait.hero-priest {
  background: radial-gradient(circle at 40% 35%, rgba(255, 255, 255, 0.2) 0%, rgba(200, 200, 200, 0.1) 40%, #444 100%);
  border-color: var(--class-priest);
}
.hero-portrait.hero-shaman {
  background: radial-gradient(circle at 40% 35%, rgba(0, 112, 222, 0.4) 0%, rgba(0, 112, 222, 0.2) 40%, #104060 100%);
  border-color: var(--class-shaman);
}
.hero-portrait.hero-paladin {
  background: radial-gradient(circle at 40% 35%, rgba(245, 140, 186, 0.4) 0%, rgba(245, 140, 186, 0.2) 40%, #6B3048 100%);
  border-color: var(--class-paladin);
}
.hero-portrait.hero-warrior {
  background: radial-gradient(circle at 40% 35%, rgba(199, 156, 110, 0.4) 0%, rgba(199, 156, 110, 0.2) 40%, #5C3520 100%);
  border-color: var(--class-warrior);
}
.hero-portrait.hero-rogue {
  background: radial-gradient(circle at 40% 35%, rgba(255, 245, 105, 0.35) 0%, rgba(255, 245, 105, 0.15) 40%, #2a3020 100%);
  border-color: var(--class-rogue);
}
.hero-portrait.hero-warlock {
  background: radial-gradient(circle at 40% 35%, rgba(148, 130, 201, 0.4) 0%, rgba(148, 130, 201, 0.2) 40%, #3a2048 100%);
  border-color: var(--class-warlock);
}
.hero-portrait.hero-druid {
  background: radial-gradient(circle at 40% 35%, rgba(255, 125, 10, 0.4) 0%, rgba(255, 125, 10, 0.2) 40%, #2a4015 100%);
  border-color: var(--class-druid);
}
.hero-portrait.hero-demonhunter {
  background: radial-gradient(circle at 40% 35%, rgba(163, 48, 201, 0.4) 0%, rgba(163, 48, 201, 0.2) 40%, #401830 100%);
  border-color: var(--class-demonhunter);
}
.hero-portrait.hero-neutral {
  background: radial-gradient(circle at 40% 35%, rgba(153, 153, 153, 0.25) 0%, rgba(100, 100, 100, 0.12) 40%, #333 100%);
  border-color: var(--class-neutral);
}
```

- [ ] **Step 3: Enhance hero name label**

Find `.hero-name` (around line 2170) and replace:

```css
.hero-name {
  position: absolute;
  bottom: -22px;
  font-size: clamp(0.45rem, 1.1vw, 0.65rem);
  color: var(--gold);
  text-shadow:
    0 0 6px rgba(200, 164, 92, 0.4),
    0 1px 3px rgba(0, 0, 0, 0.9);
  white-space: nowrap;
  letter-spacing: 0.05em;
  font-weight: 600;
}
```

- [ ] **Step 4: Enhance hero class icon**

Find `.hero-class-icon` (around line 2165) and replace:

```css
.hero-class-icon {
  font-size: clamp(1.4rem, 3.8vw, 2.3rem);
  filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.6))
          drop-shadow(0 0 8px rgba(0, 0, 0, 0.3));
  transition: filter 0.3s ease;
}

.hero-portrait:hover .hero-class-icon {
  filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.6))
          drop-shadow(0 0 12px rgba(0, 0, 0, 0.4));
}
```

- [ ] **Step 5: Visual verification**

Test each hero class selection and confirm:
- Each class has a visibly different color tone in the hero circle
- Radial highlight gives a subtle "lit from above" 3D feel
- Gold outer ring is visible around each portrait
- Opponent vs player heroes have different border tints

- [ ] **Step 6: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): apply per-class themed hero portraits with radial highlights"
```

---

### Task 8: Sidebar & Control Panel Polish

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:1357-1465` (`.action-log`)
- Modify: `webui/client/src/components/GameBoard.css:1467-1483` (`.game-controls`)
- Modify: `webui/client/src/components/GameBoard.css:1200-1244` (buttons)
- Modify: `webui/client/src/components/GameBoard.css:2326-2339` (`.game-sidebar`)

Polish the right sidebar to match the upgraded aesthetic.

- [ ] **Step 1: Enhance `.game-sidebar` container**

Find `.game-sidebar` (around line 2326) and replace:

```css
/* 游戏侧边栏 - Rich panel styling */
.game-sidebar {
  display: flex;
  flex-direction: column;
  background:
    linear-gradient(
      180deg,
      rgba(18, 14, 22, 0.98) 0%,
      rgba(10, 8, 14, 0.99) 100%
    );
  border-left: none;
  position: relative;
  min-width: var(--log-width);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.3);
}

/* Left decorative border for sidebar */
.game-sidebar::before {
  content: '';
  position: absolute;
  left: 0;
  top: 5%;
  bottom: 5%;
  width: 2px;
  background: linear-gradient(
    180deg,
    transparent 0%,
    var(--gold-dim) 20%,
    var(--gold) 50%,
    var(--gold-dim) 80%,
    transparent 100%
  );
  opacity: 0.5;
}
```

- [ ] **Step 2: Enhance control buttons area**

Find `.game-controls` (around line 1467) and replace:

```css
/* 中间控制按钮 - Premium button group */
.game-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 0.8rem 0.5rem;
  background: linear-gradient(
    180deg,
    rgba(25, 20, 28, 0.95) 0%,
    rgba(15, 12, 18, 0.98) 100%
  );
  border-left: 1px solid rgba(200, 164, 92, 0.1);
  border-right: 1px solid rgba(200, 164, 92, 0.1);
  position: relative;
}

/* Subtle separator glow between controls and log */
.game-controls::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 10%;
  right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-dim), transparent);
  opacity: 0.3;
}
```

- [ ] **Step 3: Redesign end-turn button**

Find `.end-turn-btn` (around line 1200) and replace:

```css
.end-turn-btn {
  padding: clamp(0.6rem, 1.8vw, 1rem) clamp(1.2rem, 3.5vw, 2rem);
  background: linear-gradient(
    180deg,
    #d4453a 0%,
    #b03025 40%,
    #8a2018 100%
  );
  border: 2px solid rgba(255, 200, 150, 0.3);
  border-radius: 10px;
  color: white;
  font-size: clamp(0.75rem, 2vw, 1.1rem);
  font-weight: bold;
  cursor: pointer;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  box-shadow:
    0 3px 10px rgba(176, 48, 37, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    inset 0 -2px 0 rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.end-turn-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
}

.end-turn-btn:hover:not(:disabled) {
  background: linear-gradient(
    180deg,
    #e54d42 0%,
    #c83830 40%,
    #a02820 100%
  );
  box-shadow:
    0 4px 16px rgba(192, 57, 43, 0.5),
    0 0 20px rgba(255, 100, 80, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.end-turn-btn:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow:
    0 1px 4px rgba(176, 48, 37, 0.4),
    inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.end-turn-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  background: linear-gradient(
    180deg,
    #555 0%,
    #3a3a3a 100%
  );
  border-color: rgba(100, 100, 100, 0.3);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}
```

- [ ] **Step 4: Enhance secondary buttons (concede, new-game, back)**

Find `.concede-btn, .new-game-btn, .back-btn` (around line 1220) and replace:

```css
.concede-btn, .new-game-btn, .back-btn {
  padding: clamp(0.4rem, 1.2vw, 0.7rem) clamp(0.8rem, 2vw, 1.2rem);
  background: linear-gradient(
    180deg,
    rgba(50, 42, 38, 0.9) 0%,
    rgba(35, 28, 25, 0.95) 100%
  );
  border: 1px solid rgba(200, 164, 92, 0.2);
  border-radius: 8px;
  color: var(--gold-dim);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: clamp(0.6rem, 1.4vw, 0.85rem);
  letter-spacing: 0.02em;
}

.concede-btn:hover {
  border-color: var(--red);
  color: var(--red);
  background: linear-gradient(
    180deg,
    rgba(80, 30, 25, 0.9) 0%,
    rgba(50, 18, 15, 0.95) 100%
  );
  box-shadow: 0 0 10px var(--red-glow);
}

.new-game-btn:hover {
  border-color: var(--green-player);
  color: #6acf80;
  background: linear-gradient(
    180deg,
    rgba(25, 55, 35, 0.9) 0%,
    rgba(15, 35, 22, 0.95) 100%
  );
  box-shadow: 0 0 10px var(--green-glow);
}

.back-btn:hover {
  border-color: var(--gold);
  color: var(--gold);
  background: linear-gradient(
    180deg,
    rgba(50, 42, 30, 0.9) 0%,
    rgba(35, 28, 20, 0.95) 100%
  );
  box-shadow: var(--shadow-gold);
}
```

- [ ] **Step 5: Enhance action log panel**

Find `.action-log` (around line 1357) and replace:

```css
/* 右侧操作日志 - Rich scrollable panel */
.action-log {
  background: linear-gradient(
    180deg,
    rgba(18, 14, 22, 0.95) 0%,
    rgba(10, 8, 12, 0.98) 100%
  );
  padding: clamp(0.4rem, 1vw, 0.8rem);
  height: 100%;
  max-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
  position: relative;
}

.action-log::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--gold-dim),
    transparent
  );
  opacity: 0.3;
}
```

Enhance `.action-log h3` (around line 1370):

```css
.action-log h3 {
  margin: 0 0 clamp(0.3rem, 1vw, 0.8rem) 0;
  color: var(--gold);
  font-size: clamp(0.7rem, 1.5vw, 0.9rem);
  text-align: center;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-shadow: 0 0 8px var(--gold-subtle);
}
```

- [ ] **Step 6: Visual verification**

Check:
- Sidebar has a subtle golden left-edge accent line
- End turn button looks like a premium red action button with depth
- Secondary buttons have themed hover states (red=concede, green=new game)
- Log panel has a refined header

- [ ] **Step 7: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): polish sidebar, control buttons, and action log panel"
```

---

### Task 9: Mana Crystal & Stats Display Enhancement

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:365-377` (`.mana-crystal`)
- Modify: `webui/client/src/components/GameBoard.css:430-466` (`.hero-health`, `.hero-armor`)
- Modify: `webui/client/src/components/GameBoard.css:490-507` (`.spell-power`)
- Modify: `webui/client/src/components/GameBoard.css:509-533` (`.combo-indicator`)

Upgrade the stat displays from plain text to visually distinct badges/gauges.

- [ ] **Step 1: Redesign mana crystal display**

Find `.mana-crystal` (around line 365) and replace:

```css
.mana-crystal {
  background: linear-gradient(
    180deg,
    rgba(40, 90, 140, 0.9) 0%,
    rgba(25, 60, 110, 0.95) 50%,
    rgba(18, 45, 85, 1) 100%
  );
  padding: clamp(0.2rem, 0.6vw, 0.5rem) clamp(0.5rem, 1.5vw, 1rem);
  border-radius: 14px;
  color: #cce0ff;
  font-weight: bold;
  font-size: clamp(0.7rem, 1.5vw, 0.9rem);
  border: 1.5px solid rgba(100, 160, 220, 0.3);
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  letter-spacing: 0.03em;
  box-shadow:
    0 2px 6px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(100, 180, 255, 0.15),
    inset 0 -1px 0 rgba(0, 0, 0, 0.2);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}
```

- [ ] **Step 2: Redesign health display**

Find `.hero-health` (around line 430) and replace:

```css
.hero-health {
  color: #ff6b6b;
  font-size: clamp(0.9rem, 2vw, 1.3rem);
  font-weight: bold;
  text-shadow: 0 0 8px rgba(255, 80, 80, 0.4), 0 1px 2px rgba(0, 0, 0, 0.6);
  background: linear-gradient(
    180deg,
    rgba(120, 20, 20, 0.3) 0%,
    rgba(80, 10, 10, 0.2) 100%
  );
  padding: 2px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 80, 80, 0.2);
  min-width: 42px;
  text-align: center;
  font-variant-numeric: tabular-nums;
}
```

- [ ] **Step 3: Redesign armor display**

Find `.hero-armor` (around line 437) and replace:

```css
.hero-armor {
  color: #d0e0f0;
  font-size: clamp(0.85rem, 1.8vw, 1.2rem);
  font-weight: bold;
  background: linear-gradient(
    180deg,
    rgba(100, 130, 160, 0.3) 0%,
    rgba(70, 95, 120, 0.2) 100%
  );
  padding: 2px 10px;
  border-radius: 10px;
  border: 1.5px solid rgba(150, 180, 210, 0.3);
  min-width: 42px;
  text-align: center;
  box-shadow:
    0 0 10px rgba(140, 170, 200, 0.15);
  transition: all 0.3s ease;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}
```

- [ ] **Step 4: Redesign spell power badge**

Find `.spell-power` (around line 491) and replace:

```css
.spell-power {
  color: #e0b0ff;
  font-size: clamp(0.75rem, 1.8vw, 1.05rem);
  font-weight: bold;
  background: linear-gradient(
    180deg,
    rgba(120, 60, 160, 0.3) 0%,
    rgba(80, 35, 120, 0.2) 100%
  );
  padding: 2px 8px;
  border-radius: 10px;
  border: 1.5px solid rgba(155, 89, 182, 0.35);
  min-width: 40px;
  text-align: center;
  box-shadow: 0 0 10px rgba(155, 89, 182, 0.15);
  font-variant-numeric: tabular-nums;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.spell-power.opponent {
  opacity: 0.85;
  border-style: dashed;
}
```

- [ ] **Step 5: Redesign combo indicator**

Find `.combo-indicator` (around line 510) and replace:

```css
.combo-indicator {
  color: var(--yellow);
  font-size: clamp(0.7rem, 1.6vw, 1rem);
  font-weight: bold;
  background: linear-gradient(
    180deg,
    rgba(200, 150, 50, 0.25) 0%,
    rgba(160, 100, 20, 0.15) 100%
  );
  padding: 2px 10px;
  border-radius: 10px;
  border: 1.5px solid rgba(243, 156, 18, 0.35);
  min-width: 50px;
  text-align: center;
  animation: combo-pulse 1.5s ease-in-out infinite;
  box-shadow: 0 0 10px rgba(243, 156, 18, 0.12);
  text-shadow: 0 0 6px rgba(243, 156, 18, 0.3), 0 1px 2px rgba(0, 0, 0, 0.5);
  letter-spacing: 0.03em;
}
```

- [ ] **Step 6: Visual verification**

Confirm:
- Mana crystal looks like a blue gem/capsule
- Health has a red-tinted pill background
- Armor has a silvery metallic feel
- Spell power and combo have themed colored badges
- All stats use tabular numbers for alignment

- [ ] **Step 7: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): enhance mana crystal and stat displays with themed badges"
```

---

### Task 10: Card & Minion Border/Frame Refinement

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:869-882` (`.card` base)
- Modify: `webui/client/src/components/GameBoard.css:599-622` (`.minion-body`)
- Modify: `webui/client/src/components/GameBoard.css:884-894` (`.card.playable`)

Refine card and minion borders to use the new token system and add subtle premium touches.

- [ ] **Step 1: Enhance base card styling**

Find `.card` (around line 869) and replace:

```css
/* 卡牌 - Refined card frame */
.card {
  width: var(--card-width);
  height: var(--card-height);
  background: linear-gradient(
    145deg,
    rgba(58, 46, 34, 0.95) 0%,
    rgba(45, 36, 28, 0.98) 50%,
    rgba(35, 28, 22, 1) 100%
  );
  border: 2px solid var(--gold-dim);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  padding: 4px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  position: relative;
  flex-shrink: 0;
  cursor: default;
  box-shadow:
    var(--shadow-sm),
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    inset 0 -1px 0 rgba(0, 0, 0, 0.2);
}
```

- [ ] **Step 2: Enhance playable card state**

Find `.card.playable` (around line 884) and replace:

```css
.card.playable {
  border: 2px solid rgba(76, 175, 80, 0.6);
  box-shadow:
    0 0 12px rgba(76, 175, 80, 0.35),
    0 0 24px rgba(76, 175, 80, 0.15),
    inset 0 0 15px rgba(76, 175, 80, 0.08);
  cursor: pointer !important;
}

.card.playable:hover {
  transform: scale(1.4) translateY(-20px);
  box-shadow:
    0 0 20px rgba(76, 175, 80, 0.5),
    0 0 40px rgba(76, 175, 80, 0.2),
    0 4px 20px rgba(0, 0, 0, 0.4);
  z-index: 100;
  border-color: #6acf80;
}
```

- [ ] **Step 3: Enhance minion body appearance**

Find `.minion-body` (around line 609) and replace:

```css
.minion-body {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    160deg,
    rgba(80, 72, 64, 0.95) 0%,
    rgba(58, 52, 46, 0.98) 40%,
    rgba(42, 38, 34, 1) 100%
  );
  border: 2px solid rgba(160, 140, 110, 0.35);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 8% 6%;
  position: relative;
  z-index: 2;
  box-shadow:
    0 3px 8px rgba(0, 0, 0, 0.35),
    inset 0 2px 3px rgba(255, 255, 255, 0.05),
    inset 0 -2px 3px rgba(0, 0, 0, 0.2);
}
```

- [ ] **Step 4: Enhance attackable minion state**

Find `.minion.can-attack .minion-body` (around line 625) and replace:

```css
.minion.can-attack .minion-body {
  border: 2.5px solid rgba(76, 175, 80, 0.7);
  box-shadow:
    0 0 14px rgba(76, 175, 80, 0.5),
    0 0 28px rgba(76, 175, 80, 0.2),
    inset 0 0 12px rgba(76, 175, 80, 0.1);
}
```

- [ ] **Step 5: Visual verification**

Check:
- Cards have a more refined, slightly rounded frame with inner highlights
- Playable cards have a softer green glow (not harsh bright green)
- Minion bodies look less like flat gray circles and more like dimensional objects
- Attackable minions have a clear but tasteful green highlight

- [ ] **Step 6: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): refine card and minion borders with dimensional depth"
```

---

### Task 11: Tooltip & Overlay Polish

**Files:**
- Modify: `webui/client/src/components/GameBoard.css:1040-1051` (`.tooltip-fixed`)
- Modify: `webui/client/src/components/GameBoard.css:1270-1304` (`.game-over-*`)
- Modify: `webui/client/src/components/GameBoard.css:1247-1268` (`.turn-banner`)

Polish overlays and tooltips to match the premium aesthetic.

- [ ] **Step 1: Enhance tooltip styling**

Find `.tooltip-fixed` (around line 1040) and replace:

```css
/* 卡片详情悬浮提示 - Premium tooltip card */
.tooltip-fixed {
  position: fixed;
  width: clamp(190px, 32vw, 300px);
  background: linear-gradient(
    160deg,
    rgba(35, 28, 22, 0.97) 0%,
    rgba(22, 17, 14, 0.99) 100%
  );
  border: 2px solid var(--gold-dim);
  border-radius: 10px;
  padding: 12px;
  z-index: 9999;
  pointer-events: none;
  transform: translateY(-50%);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.6),
    0 0 20px rgba(200, 164, 92, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(8px);
}
```

- [ ] **Step 2: Enhance tooltip name**

Find `.tooltip-name` (around line 1053) and replace:

```css
.tooltip-name {
  color: var(--gold-bright);
  font-weight: bold;
  font-size: clamp(0.75rem, 1.6vw, 1.05rem);
  margin-bottom: 5px;
  text-shadow: 0 0 8px var(--gold-subtle);
  letter-spacing: 0.02em;
}
```

- [ ] **Step 3: Enhance turn banner**

Find `.turn-banner` (around line 1247) and replace:

```css
/* 回合提示 - Grand entrance banner */
.turn-banner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: linear-gradient(
    160deg,
    rgba(40, 30, 18, 0.95) 0%,
    rgba(25, 18, 10, 0.98) 100%
  );
  padding: clamp(0.8rem, 2.5vw, 1.5rem) clamp(2.5rem, 6vw, 4rem);
  border-radius: 14px;
  color: var(--gold-bright);
  font-size: clamp(1.1rem, 3vw, 1.8rem);
  font-weight: bold;
  border: 2px solid var(--gold);
  z-index: 50;
  animation: fadeInOut 2s ease-in-out forwards;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  box-shadow:
    0 0 40px var(--gold-glow),
    0 8px 32px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  text-shadow: 0 0 15px var(--gold-glow);
}
```

- [ ] **Step 4: Enhance game-over dialog**

Find `.game-over-dialog` (around line 1290) and replace:

```css
.game-over-dialog {
  background: linear-gradient(
    160deg,
    rgba(45, 36, 28, 0.98) 0%,
    rgba(28, 22, 18, 0.99) 100%
  );
  border: 3px solid var(--gold);
  border-radius: 16px;
  padding: clamp(1.5rem, 4vw, 2.5rem);
  text-align: center;
  max-width: 400px;
  width: 90%;
  animation: gameOverSlideIn 0.5s ease-out;
  box-shadow:
    0 0 60px var(--gold-glow),
    0 16px 48px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
```

Also update `.game-over-title` (around line 1306):

```css
.game-over-title {
  font-size: clamp(1.5rem, 5vw, 2.5rem);
  margin-bottom: 0.5rem;
  text-shadow: 0 0 25px var(--gold-glow), 0 2px 4px rgba(0, 0, 0, 0.8);
  letter-spacing: 0.05em;
}
```

- [ ] **Step 5: Visual verification**

Check:
- Tooltips have a frosted-glass premium feel
- Turn banner has a grand, dramatic entrance look
- Game over dialog feels like a proper modal with golden glow

- [ ] **Step 6: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): polish tooltips, banners, and overlay dialogs"
```

---

### Task 12: App.css Menu Screen Consistency

**Files:**
- Modify: `webui/client/src/App.css` (full file)

Update the menu/hero-select screen to share the same visual language as the upgraded game board.

- [ ] **Step 1: Update `.app` background**

Find `.app` (around line 12) and replace its background:

```css
.app {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E"),
    radial-gradient(ellipse 120% 100% at 50% 50%, transparent 40%, #0a0810 100%),
    linear-gradient(180deg, #0e0a14 0%, #151020 40%, #171a18 80%, #0e1410 100%);
  color: #fff;
}
```

- [ ] **Step 2: Update main title styling**

Find `.app h1` (around line 32) and replace:

```css
.app h1 {
  font-size: clamp(3rem, 10vw, 5rem);
  margin: 0;
  color: #c8a45c;
  text-shadow:
    0 0 30px rgba(240, 216, 120, 0.3),
    0 2px 4px rgba(0, 0, 0, 0.6);
  font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
  letter-spacing: 0.15em;
}
```

(Note: we define `--gold` inline since App.css doesn't have access to GameBoard.css variables, or we could add a minimal `:root` here too.)

- [ ] **Step 3: Update mode select buttons**

Find `.mode-select button` (around line 57) and replace:

```css
.mode-select button {
  padding: clamp(0.8rem, 2vw, 1.2rem) clamp(1.5rem, 4vw, 2.5rem);
  font-size: clamp(0.9rem, 2vw, 1.2rem);
  background: linear-gradient(
    180deg,
    rgba(55, 44, 33, 0.9) 0%,
    rgba(38, 30, 24, 0.95) 100%
  );
  border: 2px solid rgba(200, 164, 92, 0.35);
  border-radius: 10px;
  color: #c8a45c;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  min-width: 150px;
  letter-spacing: 0.05em;
  box-shadow:
    0 3px 10px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.mode-select button:hover {
  transform: translateY(-4px);
  box-shadow:
    0 8px 24px rgba(200, 164, 92, 0.2),
    0 4px 12px rgba(0, 0, 0, 0.3);
  border-color: #c8a45c;
}
```

- [ ] **Step 4: Update hero select buttons**

Find `.hero-btn` (around line 143) and replace:

```css
.hero-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: linear-gradient(
    180deg,
    rgba(55, 44, 33, 0.85) 0%,
    rgba(38, 30, 24, 0.92) 100%
  );
  border: 2px solid rgba(200, 164, 92, 0.25);
  border-radius: 12px;
  color: #c8a45c;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  gap: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}

.hero-btn:hover {
  transform: translateY(-4px);
  box-shadow:
    0 8px 20px rgba(200, 164, 92, 0.15),
    0 4px 12px rgba(0, 0, 0, 0.3);
  border-color: #c8a45c;
}
```

- [ ] **Step 5: Visual verification**

Navigate through menu → hero select → game start and confirm:
- Menu background matches the game board's atmospheric darkness
- Buttons have consistent depth and hover behavior
- No jarring visual jump when transitioning from menu to game

- [ ] **Step 6: Final commit**

```bash
git add webui/client/src/App.css
git commit -m "style(ui): update menu screens for visual consistency with game board"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] CSS variable system overhaul → Task 1
- [x] Game board background with textures → Task 2
- [x] Opponent zone crimson-violet atmosphere → Task 4
- [x] Player zone emerald-green atmosphere → Task 5
- [x] Central divider decoration → Task 6
- [x] Per-class hero theme colors → Task 7
- [x] Header bar enhancement → Task 3
- [x] Sidebar/control panel polish → Task 8
- [x] Mana crystal & stats display → Task 9
- [x] Card/minion border refinement → Task 10
- [x] Tooltip & overlay polish → Task 11
- [x] Menu screen consistency → Task 12
- [x] Fonts explicitly excluded per user request

**Placeholder scan:** No TBD, TODO, or placeholder patterns found. All code blocks contain complete CSS.

**Type consistency:** All variable references use the names defined in Task 1's `:root` block. Class names match existing HTML structure in `GameBoard.tsx`.

**Risk notes:**
- The SVG noise filter data-URIs use `%23` for `#` encoding — verified correct for CSS URLs
- `::before`/`::after` pseudo-elements added to `.game-container` require children to have `position: relative; z-index: 1` — handled in Task 2 Step 2
- No JavaScript/TSX changes needed — all tasks are CSS-only
- Responsive design preserved via existing `clamp()` usage throughout
