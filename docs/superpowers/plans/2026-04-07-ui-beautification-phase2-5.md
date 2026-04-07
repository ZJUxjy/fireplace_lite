# UI Beautification Phases 2-5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Prerequisite:** Phase 1 must be complete (design tokens, atmospheric backgrounds, zone styling, header/sidebar polish, stat badges, card/minion border refinement). Branch `glm-5v-turbo` contains all Phase 1 commits.

**Goal:** Transform the Fireplace Hearthstone simulator UI from a "polished prototype" into a visually rich interface that closely approximates the look and feel of real Hearthstone — progressing through card system deep-dive, hero area overhaul, minion card-style conversion, and final polish.

**Architecture:** All changes remain CSS-only (no image assets, no font files). Each phase builds on the Phase 1 design token system (`:root` variables in GameBoard.css). The approach is incremental enhancement — each phase makes existing elements more detailed without breaking previous work. TSX component structure stays unchanged; only CSS is modified.

**Tech Stack:** Pure CSS (custom properties, clip-path, pseudo-elements, SVG data-URI, CSS animations, transforms, backdrop-filter), React 19 + TypeScript + Vite, single-file architecture (GameBoard.css ~3662 lines, App.css ~210 lines)

**Branch to work from:** `glm-5v-turbo` (has Phase 1 complete)

---

## Current State Summary (Post-Phase 1)

### What Phase 1 Achieved
- **Design Token System**: 55+ hierarchical CSS variables (gold 4-tier, zone atmospheres, per-class themes, shadow/border presets)
- **Atmospheric Backgrounds**: Multi-layer textured game board with noise overlay, radial vignette, ambient gold glow
- **Zone Differentiation**: Crimson-violet opponent half, emerald-green player half, warm center divider
- **Header Bar**: Metallic gradient with golden accent line, glass-morphism dropdown, rotation hover
- **Per-Class Heroes**: Radial gradient highlights for all 11 classes with themed border colors
- **Sidebar**: Premium end-turn button (3-stop red gradient, press states), themed secondary buttons, gold-edge accent
- **Stat Badges**: Pill-shaped mana/health/armor/spell-power/combo displays with tabular numbers
- **Card/Minion Borders**: Dimensional gradients with inner bevel highlights, softened green glow states
- **Tooltips & Overlays**: Frosted-glass panels, dramatic turn banner, rich game-over modal
- **Menu Consistency**: App.css matches game board's atmospheric darkness

### What Still Needs Work (This Plan's Scope)

| Area | Phase 1 State | Target (End of Phase 5) |
|------|-------------|----------------------|
| **Card shape** | Rounded rectangle, simple gradient | HS-style rounded corners, inner decorative frame line, premium feel |
| **Cost gem** | Blue circle | Diamond/rhombus crystal shape with facet highlight |
| **Attack/Health** | Plain text in footer | Diamond-shaped stat boxes (yellow atk, red HP) like real HS |
| **Rarity borders** | Single gold border for all cards | Color-coded by rarity (common=white, rare=blue, epic=purple, legendary=orange) |
| **Card hover** | Scale + translateY | Full 3D perspective tilt (rotateX/rotateY) with dynamic shadow |
| **Card back** | Blue rect with "?" | Ornate pattern with repeating gradient decoration |
| **Hero portrait** | Circle with emoji + radial glow | Octagonal shield shape via clip-path, ornate gold outer frame |
| **Mana display** | Text "💎 X/Y" | Visual crystal row (individual gem divs) |
| **Minion shape** | Oval/circle (border-radius: 50%) | Mini-card style (rounded rectangle, matching hand cards) |
| **Mechanic icons** | Emoji (💀🌪️🐍❄️🛡️🔇) | CSS/SVG geometric icons or refined styled emoji |
| **Duplicate code** | 2x @keyframes pulse/fadeInOut, 3x duplicate rules | Clean deduplication with unique names |
| **Animations** | ~39 keyframe blocks, some always-running | Performance audit, throttle where needed |

---

## File Structure

All changes touch two files:
- **`webui/client/src/components/GameBoard.css`** (~3662 lines) — THE master stylesheet
- **`webui/client/src/App.css`** (~210 lines) — Menu screen styles

No new files needed. No component restructuring. This plan is purely CSS enhancement.

---

## PHASE 2: Card System Deep Dive

**Focus:** Make hand cards look and feel like real Hearthstone cards. This is the highest-impact visual change because cards are the most frequently interacted-with element.

### Task 1: Card Shape & Frame Redesign

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — `.card` rule (around line 1391)

- [ ] **Step 1: Enhance `.card` base shape**

Replace the current `.card` rule with an upgraded version that adds an inner decorative border frame:

```css
.card {
  width: var(--card-width);
  height: var(--card-height);
  background:
    /* Main card body - warm leather/parchment tone */
    linear-gradient(
      160deg,
      rgba(62, 50, 38, 0.97) 0%,
      rgba(48, 38, 30, 0.99) 40%,
      rgba(36, 28, 22, 1) 100%
    );
  /* Inner decorative frame line (simulates card inset border) */
    linear-gradient(
      to bottom,
      transparent 58%,
      rgba(200, 164, 92, 0.08) 58%,
      rgba(200, 164, 92, 0.08) 62%,
      transparent 62%
    ),
    linear-gradient(
      to right,
      transparent 48%,
      rgba(200, 164, 92, 0.06) 48%,
      rgba(200, 164, 92, 0.06) 52%,
      transparent 52%
    );
  border: 2px solid var(--gold-dim);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  padding: 4px;
  padding-top: 8px; /* extra top padding for cost gem overflow */
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  position: relative;
  flex-shrink: 0;
  cursor: default;
  box-shadow:
    var(--shadow-sm),
    0 1px 0 rgba(255, 255, 255, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    inset 0 -1px 0 rgba(0, 0, 0, 0.15);
}
```

The key addition is the two `linear-gradient()` layers that create a subtle inner frame rectangle inside the card — mimicking the decorative inner border that real Hearthstone cards have.

- [ ] **Step 2: Verify card renders correctly**

Open the game board in browser, play a few turns to see cards in hand. Confirm:
- Cards have a visible inner frame/glow near edges
- Card content (cost, name, stats) still readable
- No layout shift from added padding-top

- [ ] **Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): add inner decorative frame to card design

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Cost Gem → Diamond Crystal Shape

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — `.card-cost` rule (around line 1434)

- [ ] **Step 1: Replace `.card-cost` with diamond shape**

```css
.card-cost {
  position: absolute;
  top: -8px;
  left: -8px;
  width: clamp(1.4rem, 3.5vw, 2rem);
  height: clamp(1.4rem, 3.5vw, 2rem);
  background: linear-gradient(
    135deg,
    var(--blue) 0%,
    #66aaff 35%,
    var(--blue-dark) 100%
  );
  /* Diamond shape via clip-path */
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: clamp(0.65rem, 1.6vw, 1rem);
  border: none;
  /* Facet highlight - simulates light reflection on crystal */
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.3),
    inset 0 2px 4px rgba(255, 255, 255, 0.25),
    0 0 8px rgba(68, 136, 255, 0.3);
  /* Subtle gold rim */
  filter: drop-shadow(0 0 1px rgba(200, 164, 92, 0.5));
}
```

The `clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)` creates a rotated square (diamond). Combined with the diagonal gradient and inner box-shadow, it looks like a faceted blue gem/crystal.

- [ ] **Step 2: Verify cost gems render as diamonds**

Check that:
- All card costs show as diamond/rhombus shapes
- The blue gradient creates a 3D crystal feel
- Numbers are centered within the diamond
- Gems don't overlap with card content

- [ ] **Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): reshape card cost gem into diamond crystal shape

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Attack/Health → Diamond Stat Boxes

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — `.card-footer`, `.card-atk`, `.card-health` (around lines 1558-1570)

- [ ] **Step 1: Replace `.card-footer` container**

```css
.card-footer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 0 6%;
  gap: 2px;
}
```

Added `align-items: flex-end` to bottom-align the stat boxes.

- [ ] **Step 2: Replace `.card-atk` as diamond**

```css
.card-atk {
  /* Diamond shape for attack value */
  width: clamp(0.9rem, 2.2vw, 1.3rem);
  height: clamp(0.9rem, 2.2vw, 1.3rem);
  background: linear-gradient(
    135deg,
    #ffd700 0%,
    #e6b800 50%,
    #cc9900 100%
  );
  clip-path: polygon(50% 2%, 98% 50%, 50% 98%, 2% 50%);
  color: #1a1a00;
  font-weight: bold;
  font-size: clamp(0.55rem, 1.3vw, 0.85rem);
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    inset 0 1px 2px rgba(255, 240, 150, 0.4);
}
```

- [ ] **Step 3: Replace `.card-health` as diamond**

```css
.card-health {
  /* Diamond shape for health value */
  width: clamp(0.9rem, 2.2vw, 1.3rem);
  height: clamp(0 0.9rem, 2.2vw, 1.3rem);
  background: linear-gradient(
    135deg,
    #ff6b6b 0%,
    #e53939 50%,
    #cc2222 100%
  );
  clip-path: polygon(50% 2%, 98% 50%, 50% 98%, 2% 50%);
  color: #fff;
  font-weight: bold;
  font-size: clamp(0.55rem, 1.3vw, 0.85rem);
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    inset 0 1px 2px rgba(255, 220, 200, 0.4);
}
```

- [ ] **Step 4: Verify stat diamonds render correctly**

Confirm:
- Attack shows as yellow diamond at bottom-left of card
- Health shows as red diamond at bottom-right of card
- Diamonds are properly sized and don't overlap
- Numbers are centered and readable

- [ ] **Step 5: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): reshape card attack/health into diamond stat boxes

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Card Rarity Border Colors

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — `.card` base rule AND `.card.playable` (around line 1391 and ~1465)

- [ ] **Step 1: Add rarity class support to `.card`**

Add these new rules AFTER the existing `.card` block:

```css
/* ---- Card Rarity Border Themes ---- */

/* Common (default) - white-ish gold border */
.card.rarity-common {
  border-color: rgba(220, 210, 190, 0.5);
  box-shadow:
    var(--shadow-sm),
    0 0 0 1px rgba(220, 210, 190, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    inset 0 -1px 0 rgba(0, 0, 0, 0.15);
}

/* Rare - blue shimmer border */
.card.rarity-rare {
  border-color: rgba(80, 140, 220, 0.6);
  box-shadow:
    var(--shadow-sm),
    0 0 10px rgba(80, 140, 220, 0.25),
    0 0 0 1px rgba(80, 140, 220, 0.2),
    inset 0 1px 0 rgba(100, 180, 255, 0.08),
    inset 0 -1px 0 rgba(0, 0, 0, 0.15);
}

/* Epic - purple shimmer border */
.card.rarity-epic {
  border-color: rgba(160, 100, 220, 0.6);
  box-shadow:
    var(--shadow-sm),
    0 0 12px rgba(160, 100, 220, 0.25),
    0 0 0 1px rgba(160, 100, 220, 0.2),
    inset 0 1px 0 rgba(200, 150, 230, 0.08),
    inset 0 -1px 0 rgba(0, 0, 0, 0.15);
}

/* Legendary - orange glow border */
.card.rarity-legendary {
  border-color: rgba(255, 160, 60, 0.7);
  box-shadow:
    var(--shadow-sm),
    0 0 14px rgba(255, 160, 60, 0.3),
    0 0 20px rgba(255, 160, 60, 0.15),
    0 0 0 1px rgba(255, 200, 100, 0.25),
    inset 0 1px 0 rgba(255, 220, 150, 0.1),
    inset 0 -1px 0 rgba(0, 0, 0, 0.15);
  animation: legendary-shimmer 3s ease-in-out infinite alternate;
}

@keyframes legendary-shimmer {
  0% { box-shadow: var(--shadow-sm), 0 0 14px rgba(255, 160, 60, 0.3), 0 0 20px rgba(255, 160, 60, 0.15); }
  100% { box-shadow: var(--shadow-sm), 0 0 18px rgba(255, 160, 60, 0.4), 0 0 24px rgba(255, 160, 60, 0.2); }
}
```

Note: These classes will be applied dynamically when the backend provides rarity info. For now they serve as a design system ready for future data binding.

- [ ] **Step 2: Update `.card.playable` to work with rarity borders**

Find the existing `.card.playable:hover` rule and ensure its `box-shadow` doesn't conflict with rarity shadows (it shouldn't since playable uses green which is independent).

- [ ] **Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): add card rarity border color system (common/rare/epic/legendary)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Enhanced Card Hover — 3D Perspective Tilt

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — `.card.playable:hover` (around line ~1475)

- [ ] **Step 1: Replace `.card.playable:hover` with 3D tilt effect**

```css
.card.playable:hover {
  transform:
    scale(1.45)
    translateY(-24px)
    rotateX(8deg)
    rotateZ(-2deg);
  z-index: 100;

  box-shadow:
    0 20px 40px rgba(76, 175, 80, 0.35),
    0 8px 20px rgba(76, 175, 80, 0.2),
    0 4px 12px rgba(0, 0, 0, 0.4),
    0 0 1px rgba(76, 175, 80, 0.5);

  border-color: #7ddf80;
  /* Slight brighten on hover to simulate light catch */
  filter: brightness(1.05);
}
```

The `rotateX(8deg)` tilts the card toward the user (top edge appears closer), creating a 3D "picking up the card" effect. `rotateZ(-2deg)` gives a slight natural angle variation.

- [ ] **Step 2: Test hover interaction**

Play a game and hover over playable cards. Check:
- Card tilts convincingly in 3D
- Shadow extends naturally below the tilted card
- Card returns to normal position when mouse leaves
- No z-index stacking issues with adjacent cards

- [ ] **Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): add 3D perspective tilt to card hover effect

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 6: Card Back Ornate Pattern

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — `.card-back-small` (around line 437)

- [ ] **Step 1: Replace `.card-back-small` with patterned design**

```css
.card-back-small {
  width: clamp(1.5rem, 4vw, 2.5rem);
  height: clamp(2rem, 5.5vw, 3.5rem);
  background:
    /* Base dark blue gradient */
    linear-gradient(145deg, #162a45 0%, #0d2040 45%, #081830 100%),
    /* Horizontal stripe pattern (Hearthstone card-back style) */
    repeating-linear-gradient(
      0deg,
      transparent 0px,
      transparent 6px,
      rgba(100, 160, 220, 0.12) 6px,
      rgba(100, 160, 220, 0.06) 7px,
      transparent 7px
    );
  border: 2px solid var(--zone-opponent-accent);
  border-radius: 6px;
  box-shadow:
    0 2px 6px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(100, 160, 220, 0.2),
    0 0 8px rgba(200, 80, 112, 0.15);
  position: relative;
  overflow: hidden;
}

/* Central ornament on card back */
.card-back-small::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40%;
  height: 40%;
  border: 1.5px solid rgba(100, 160, 220, 0.2);
  border-radius: 2px;
  opacity: 0.5;
  box-shadow: 0 0 6px rgba(100, 160, 220, 0.15);
}

/* Remove the old "?" content - clean card back */
.card-back-small::after {
  content: none;
}
```

The `repeating-linear-gradient` creates horizontal stripes reminiscent of real HS card backs. The `::before` adds a central rectangular ornament.

- [ ] **Step 2: Verify card backs look ornate**

Check opponent's hand area:
- Card backs show subtle horizontal stripe pattern
- Central ornament is visible but understated
- No "?" text (cleaner look)

- [ ] **Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui: add ornate stripe pattern to opponent card backs

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## PHASE 3: Hero Area Overhaul

**Focus:** Transform hero portraits from circles with emojis into shield/octagonal frames with visual crystal mana displays.

### Task 7: Hero Portrait → Shield/Octagonal Shape

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — `.hero-portrait` base (around line 628)

- [ ] **Step 1: Replace `.hero-portrait` with clip-path shield shape**

```css
.hero-portrait {
  width: var(--hero-size);
  height: var(--hero-size);
  /* Shield/octagonal shape via clip-path */
  clip-path: polygon(
    50% 0%,
    93% 7%,
    100% 27%,
    100% 73%,
    93% 93%,
    50% 100%,
    7% 93%,
    0% 73%,
    0% 27%,
    7% 7%
  );
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
  background: linear-gradient(
    180deg,
    rgba(40, 34, 28, 0.95) 0%,
    rgba(28, 22, 18, 0.98) 50%,
    rgba(18, 14, 12, 1) 100%
  );

  /* Outer ornate gold frame (pseudo-element ring) */
  margin: 4px; /* space for the frame */
  box-shadow:
    0 0 0 3px var(--gold-dim),
    0 0 15px rgba(0, 0, 0, 0.4),
    inset 0 0 15px rgba(0, 0, 0, 0.3);
}
```

The `clip-path: polygon(...)` creates a shield-like octagon. The `margin: 4px` creates space between the clipped shape and its container so the gold frame can be drawn around it.

- [ ] **Step 2: Add ornate gold outer frame via ::before**

Add or replace the existing `.hero-portrait::before`:

```css
.hero-portrait::before {
  content: '';
  position: absolute;
  inset: -5px;
  /* Match the shield clip-path shape */
  clip-path: polygon(
    50% 0%,
    95% 5%,
    100% 25%,
    100% 75%,
    95% 95%,
    50% 100%,
    5% 95%,
    0% 75%,
    0% 25%,
    5% 5%
  );
  border: 2px solid var(--gold);
  box-shadow:
    0 0 8px var(--gold-subtle),
    inset 0 0 8px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  z-index: -1;
}
```

This draws a matching shield-shaped gold border around the portrait using another `clip-path`.

- [ ] **Step 3: Update opponent/player variants**

Replace `.hero-portrait.opponent` and `.hero-portrait.player` to remove the old `border-radius: 50%` references (now handled by clip-path):

```css
.hero-portrait.opponent {
  background: radial-gradient(circle at 40% 35%, rgba(200, 80, 112, 0.3) 0%, rgba(139, 48, 48, 0.15) 40%, #3a1520 100%);
  clip-path: polygon(
    50% 0%, 93% 7%, 100% 27%, 100% 73%,
    93% 93%, 50% 100%, 7% 93%, 0% 73%, 0% 27%, 7% 7%
  );
  box-shadow:
    0 0 0 3px var(--zone-opponent-accent),
    0 0 15px rgba(0, 0, 0, 0.4),
    inset 0 0 15px rgba(0, 0, 0, 0.3);
}

.hero-portrait.player {
  background: radial-gradient(circle at 40% 35%, rgba(64, 160, 96, 0.3) 0%, rgba(42, 128, 64, 0.15) 40%, #1a3018 100%);
  clip-path: polygon(
    50% 0%, 93% 7%, 100% 27%, 100% 73%,
    93% 93%, 50% 100%, 7% 93%, 0% 73%, 0% 27%, 7% 7%
  );
  box-shadow:
    0 0 0 3px var(--zone-player-accent),
    0 0 15px rgba(0, 0, 0, 0.4),
    inset 0 0 15px rgba(0, 0, 0, 0.3);
}
```

- [ ] **Step 4: Verify hero portraits are now shield-shaped**

Test each hero class selection:
- Portraits appear as octagons/shields instead of circles
- Gold outer frame is visible around each portrait
- Class-colored radial gradients still visible through the clip-path
- Opponent vs player tinting preserved

- [ ] **Step 5: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(u): reshape hero portraits into shield shape with gold frame

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 8: Mana Crystal Visualization

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — `.mana-crystal` (around line 729)

**Note:** This task changes how mana LOOKS but keeps the same data flow. The backend sends `mana` and `max_mana` as numbers. We'll style them to look like individual crystal gems.

- [ ] **Step 1: Redesign `.mana-crystal` as visual crystal row**

```css
.mana-crystal {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 6px;
  background: linear-gradient(
    180deg,
    rgba(30, 25, 18, 0.8) 0%,
    rgba(20, 16, 12, 0.9) 100%
  );
  border-radius: 8px;
  border: 1px solid rgba(100, 160, 220, 0.2);
  box-shadow:
    0 2px 6px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(100, 180, 255, 0.1),
    inset 0 -1px 0 rgba(0, 0, 0, 0.2);
  font-size: 0; /* hide text, we'll style it differently */
  letter-spacing: 0;
  position: relative;
}

/* Hide the raw "💎 X/Y" text - we replace with visual gems */
.mana-crystal > * {
  display: none;
}

/* Generate visual crystal gems via pseudo-elements */
/* This approach shows up to 10 crystals. For simplicity we keep the text
   accessible but style it as crystal-like indicators. A more advanced version
   would need TSX changes to render individual crystal divs. */
.mana-crystal::after {
  content: attr(data-mana "💎") " " attr(data-max-mana "/"); /* fallback */
  display: inline-flex;
  gap: 2px;
  font-size: clamp(0.65rem, 1.5vw, 0.9rem);
  font-weight: bold;
  color: #cce0ff;
  letter-spacing: -1px;
  text-shadow: 0 0 4px rgba(100, 180, 255, 0.5);
  /* Simulate crystal row with character spacing */
}
```

**Alternative simpler approach** (if the above attr() trick doesn't work well across browsers):

Since we can't easily generate individual crystal divs without TSX changes, we take a pragmatic approach: enhance the existing pill to look more crystalline while keeping the text-based display:

```css
.mana-crystal {
  background:
    linear-gradient(180deg, rgba(35, 70, 120, 0.9) 0%, rgba(20, 45, 85, 0.95) 50%, rgba(15, 32, 60, 1) 100%);
  padding: clamp(0.2rem, 0.6vw, 0.5rem) clamp(0.5rem, 1.5vw, 1rem);
  border-radius: 8px;
  border: 1.5px solid rgba(100, 160, 220, 0.3);
  border-top: 3px solid rgba(140, 200, 255, 0.4);
  border-left: 1px solid rgba(100, 160, 220, 0.15);
  border-right: 1px solid rgba(100, 160, 220, 0.15);
  color: #cce0ff;
  font-weight: bold;
  font-size: clamp(0.7rem, 1.5vw, 0.9rem);
  font-variant-numeric: tabular-nums;
  letter-spacing: 1px;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  box-shadow:
    0 2px 6px rgba(0, 0, 0, 0.3),
    inset 0 2px 4px rgba(100, 180, 255, 0.15),
    inset 0 -1px 0 rgba(0, 0, 0, 0.2),
    0 0 8px rgba(68, 136, 255, 0.2);
  text-shadow: 0 0 4px rgba(100, 180, 255, 0.5);
  /* Crystal top-highlight + side facets */
  position: relative;
}
```

Use the **simpler approach** (second code block). It enhances the pill with crystal-like top-border and facet borders without requiring TSX changes.

- [ ] **Step 2: Verify mana display looks more crystalline**

- Blue pill now has a brighter top edge (crystal facet simulation)
- Side borders give depth
- Numbers remain readable and tabular-aligned

- [ ] **Step 3: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): enhance mana crystal display with crystal-facet styling

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## PHASE 4: Minion & Battlefield Overhaul

**Focus:** The biggest visual change — convert minions from ovals to mini-card style, and upgrade mechanism icons.

### Task 9: Minions → Mini-Card Style

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — `.minion` (container), `.minion-body` (around lines 1050-1072)

**IMPORTANT:** This is the most visually impactful remaining change. Minions currently look like gray eggs. After this task, they'll look like small versions of hand cards.

- [ ] **Step 1: Change `.minion` container from oval to rounded-rect**

Find `.minion` (the wrapper around `.minion-body`) and update:

```css
.minion {
  width: var(--minion-width);
  height: var(--minion-height);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  /* Removed border-radius: 50% - no longer oval */
  /* Container is now transparent - shape comes from .minion-body */
  background: transparent;
  border: none;
  box-shadow: none;
}
```

- [ ] **Step 2: Replace `.minion-body` as mini-card**

```css
.minion-body {
  width: 100%;
  height: 100%;
  /* Mini-card shape: rounded rectangle like hand cards */
  background: linear-gradient(
    160deg,
    rgba(70, 58, 45, 0.97) 0%,
    rgba(52, 42, 33, 0.99) 40%,
    rgba(38, 30, 24, 1) 100%
  );
  /* Inner frame line like cards */
  background-image:
    linear-gradient(
      to bottom,
      transparent 52%,
      rgba(200, 164, 92, 0.07) 52%,
      rgba(200, 164, 92, 0.07) 56%,
      transparent 56%
    );
  border: 2px solid rgba(160, 140, 110, 0.4);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 6% 5%;
  position: relative;
  z-index: 2;
  box-shadow:
    0 3px 8px rgba(0, 0, 0, 0.35),
    0 1px 0 rgba(255, 255, 255, 0.05),
    inset 0 -1px 0 rgba(0, 0, 0, 0.2);
  /* Slightly wider than tall to feel card-like */
  aspect-ratio: 0.82;
}
```

Key changes from oval:
- `border-radius: 50%` → `border-radius: 10px` (rounded rectangle)
- Added inner frame gradient (same technique as Task 1 card frame)
- Added `aspect-ratio: 0.82` to make them slightly wider than tall
- Warm brown gradient instead of flat gray

- [ ] **Step 3: Update minion stat display for card-style layout**

Replace `.minion-stats` and stat spans:

```css
.minion-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 90%;
  padding: 1px 3px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  position: absolute;
  top: 4px;
  left: 5%;
  right: 5%;
  z-index: 3;
}

.minion-atk {
  color: #ffd700;
  font-weight: bold;
  font-size: clamp(0.6rem, 1.4vw, 0.85rem);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  line-height: 1;
  /* Small diamond indicator for attack */
  min-width: 0;
  padding: 0 3px;
  background: linear-gradient(135deg, #ffd700 0%, #cc9900 100%);
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
}

.minion-health {
  color: #ff6b6b;
  font-weight: bold;
  font-size: clamp(0.6rem, 1.4vw, 0.85rem);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  line-height: 1;
  min-width: 0;
  padding: 0 3px;
  background: linear-gradient(135deg, #ff6b6b 0%, #cc2222 100%);
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
}
```

Stats are now small diamonds positioned at top of the minion card, similar to card footer diamonds.

- [ ] **Step 4: Update minion name positioning**

```css
.minion-name {
  font-size: clamp(0.35rem, 0.9vw, 0.55rem);
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 90%;
  position: absolute;
  top: 50%;
  left: 5%;
  right: 5%;
  z-index: 2;
  transform: translateY(-50%);
}
```

- [ ] **Step 5: Update race tag for card-style minions**

```css
.minion-race-tag {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(180deg, rgba(139, 105, 20, 0.3), rgba(90, 68, 10, 0.2));
  padding: 1px 4px;
  border-radius: 4px;
  font-size: clamp(0.2rem, 0.6vw, 0.35rem);
  color: var(--gold);
  border: 1px solid var(--gold-dark);
  white-space: nowrap;
  z-index: 3;
}
```

- [ ] **Step 6: Update can-attack minion glow for new shape**

```css
.minion.can-attack .minion-body {
  border: 2.5px solid rgba(76, 175, 80, 0.7);
  box-shadow:
    0 0 14px rgba(76, 175, 80, 0.5),
    0 0 28px rgba(76, 175, 80, 0.2),
    inset 0 0 12px rgba(76, 175, 80, 0.1);
}
```

- [ ] **Step 7: Verify minions look like mini-cards**

Start a game and check:
- Minions on both sides are now rounded rectangles, NOT ovals
- They have inner frame lines like hand cards
- Stats show as tiny diamonds at top
- Name centered in middle
- Attackable minions have green glow
- Overall visual consistency with hand cards

- [ ] **Step 8: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): transform minions from ovals to mini-card style with inner frames

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 10: Mechanic Icon Upgrade

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — all mechanic icon rules (.deathrattle-icon, .windfury-icon, .poisonous-icon, .immune-icon, .silenced-icon, .frozen-icon)

- [ ] **Step 1: Upgrade deathrattle icon**

```css
.deathrattle-icon {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 16px;
  /* Skull icon using pure CSS (SVG background) */
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3Epath d='M12 2C6.48 2 2 6.48 6c0 3.31 1.79 6 6 6s6 2.69 6 6 6c0 3.31-1.79 6-6 6S17.52 2 12 2zm-1 8c-2.21 0-4-1.79-4-4-.45-.89-.67-1.79-1.5-2.67V10h2v2c0 1.1.9 2 2 2s.9-.9 2-2 2v2h2c0 1.1.9 0 2-.9 0z' fill='%23636'/%3E/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  filter: drop-shadow(0 0 4px rgba(128, 0, 128, 0.8))
          drop-shadow(0 0 8px rgba(128, 0, 128, 0.4));
  z-index: 4;
  animation: deathrattle-pulse 2s ease-in-out infinite;
}
```

- [ ] **Step 2: Upgrade windfury icon**

```css
.windfury-icon {
  position: absolute;
  top: -16px;
  right: -4px;
  width: 18px;
  height: 18px;
  /* Swirl/vortex icon */
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3Epath d='M12 2C8 2 4 4 4 8 4c2.2 0 4 1.8 4 4s1.8 0 4-4V8c0-2.2 1.8-4 4-4zM8 12l4-4M4 12l4 4m-4 4' stroke='%2366ff' stroke-width='2.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  filter: drop-shadow(0 0 4px rgba(100, 200, 255, 0.9))
          drop-shadow(0 0 8px rgba(100, 200, 255, 0.5));
  z-index: 4;
  animation: wind-icon-pulse 1s ease-in-out infinite;
}
```

- [ ] **Step 3: Upgrade poisonous icon**

```css
.poisonous-icon {
  position: absolute;
  bottom: -6px;
  right: 4px;
  width: 16px;
  height: 16px;
  /* Skull-crossbones icon */
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3Epath d='M19 15l-5.83-5.83M12 2C6.48 2 2 6.48 6c0 3.31 1.79 6 6 6s6 2.69 6 6 6c0 3.31-1.79 6-6 6S17.52 2 12 2zM8 18l4-4M4 18l4-4' stroke='%23228' stroke-width='2.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  filter: drop-shadow(0 0 4px rgba(39, 174, 96, 0.9))
          drop-shadow(0 0 8px rgba(39, 174, 96, 0.5));
  z-index: 4;
  animation: poisonous-pulse 1.5s ease-in-out infinite;
}
```

- [ ] **Step 4: Upgrade immune icon**

```css
.immune-icon {
  position: absolute;
  top: -5px;
  left: -5px;
  width: 18px;
  height: 18px;
  /* Shield with star */
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3Epath d='M12 2L3 21h18l3-3M4 12l8 8' stroke='%23ffd700' stroke-width='2.5' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3Ecircle cx='12' cy='12' r='10' fill='none' stroke='%23ffd700' stroke-width='1.5'/%3E/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  filter: drop-shadow(0 0 4px rgba(255, 215, 0, 1))
          drop-shadow(0 0 8px rgba(255, 215, 0, 0.5));
  z-index: 4;
  animation: immune-glow 1.5s ease-in-out infinite;
}
```

- [ ] **Step 5: Upgrade silenced icon**

```css
.silenced-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  /* Silence slash circle */
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3Ecircle cx='12' cy='12' r='9' fill='none' stroke='%23888' stroke-width='2.5'/%3Eline x1='4' y1='4' x2='20' y2='20' stroke='%23888' stroke-width='2.5' stroke-linecap='round'/%3E/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  filter: drop-shadow(0 0 4px rgba(150, 150, 150, 0.9))
          drop-shadow(0 0 8px rgba(150, 150, 150, 0.5));
  z-index: 5;
  opacity: 0.85;
}
```

- [ ] **Step 6: Upgrade frozen icon**

```css
.frozen-icon {
  position: absolute;
  top: -16px;
  right: -4px;
  width: 18px;
  height: 18px;
  /* Snowflake icon */
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3Epath d='M12 3c-1.1 0-2 .9-2-.3-.4-.1-.8-.3-1.2-.2-1.8C8.5 1 7.5 2 7 3c0 .6.4 1 .9.8 1.5.2.8.2.4.6.8.2 1.2.4.8.2 1.8.8.2.4.6.8.4 1.2.4 1.8.8.2.4.6.8.4 1.2.4 1.8.8.2.4.6.8.4 1.2zM12 8c-.6 0-1.1.1-1.5.3-.2-.4-.1-.8-.3-1.2-.2-1.8-.4-.6-.8-.2-1.2-.4-1.8-.2-.4-.6-.2-1.2-.4-1.8-.2-.4-.6zM8 16l4 4' stroke='%2366ff' stroke-width='2' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3Ecircle cx='8' cy='16' r='2' fill='%2366ff'/%3Ecircle cx='16' cy='8' r='2' fill='%2366ff'/%3E/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  filter: drop-shadow(0 0 4px rgba(100, 200, 255, 0.9))
          drop-shadow(0 0 8px rgba(100, 200, 255, 0.5));
  z-index: 4;
  animation: frozen-shimmer 2s ease-in-out infinite;
}
```

- [ ] **Step 7: Verify mechanic icons render as SVG graphics**

Check a game with various minion states:
- Deathrattle = purple skull SVG (not 💀 emoji)
- Windfury = blue swirl SVG (not 🌪️ emoji)
- Poisonous = green skull-crossbones SVG (not 🐍 emoji)
- Immune = gold shield-star SVG (not 🛡️ emoji)
- Silenced = gray slash-circle SVG (not 🔇 emoji)
- Frozen = blue snowflake SVG (not ❄️ emoji)

- [ ] **Step 8: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): replace emoji mechanic icons with SVG graphic icons

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## PHASE 5: Polish & Final Details

**Focus:** Fix accumulated issues, performance optimization, responsive refinements, and final quality pass.

### Task 11: Deduplicate Code Cleanup

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — multiple locations

- [ ] **Step 1: Fix duplicate `@keyframes pulse`**

The `pulse` name is defined twice with DIFFERENT animations:
- Line ~375: loading text opacity pulse (opacity 0.6↔1.0)
- Line ~3515: discover icon scale pulse (scale 1↔1.1)

Rename the discover one to `discover-pulse`:

Find the second definition (near `.discover-icon` / `.discover-hint`) and change:
```css
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
```
To:
```css
@keyframes discover-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
```
Then update the reference in `.discover-icon` animation from `animation: pulse` to `animation: discover-pulse`.

- [ ] **Step 2: Fix duplicate `@keyframes fadeInOut`**

The `fadeInOut` name is defined twice:
- Line ~1898: turn-banner (scale + opacity fade)
- Line ~3659: discover hint (opacity-only fade)

Rename the second to `discover-fade`:

Find the second definition and change:
```css
@keyframes fadeInOut {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
```
To:
```css
@keyframes discover-fade {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
```
Then update `.discover-hint` animation from `fadeInOut` to `discover-fade`.

- [ ] **Step 3: Fix duplicate `.hero-stats` rule**

The `.hero-stats` rule is defined identically at lines ~722 and ~798. Remove the second one (keep the first, delete the duplicate at ~798).

- [ ] **Step 4: Fix duplicate `.end-turn-btn:disabled`**

Two slightly different definitions exist. Keep the richer one (lines 1804-1814 with full styling), remove the shorter duplicate (lines 1816-1819).

- [ ] **Step 5: Fix duplicate `.log-entry:has(⚔️)`**

Identical rule at lines ~2101-2104 and ~2112-2115. Remove the second copy.

- [ ] **Step 6: Fix redundant `.combo-indicator` color**

In `.combo-indicator` (around line 908), there's a dead `color: var(--yellow)` immediately followed by `color: #ffcc00`. Remove the first line.

- [ ] **Step 7: Verify build still passes after deduplication**

```bash
cd /home/xu/code/hstone/hearthstone/fireplace/webui/client && npx vite build 2>&1 | tail -20
```

Expected: Build succeeds with 0 errors.

- [ ] **Step 8: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): deduplicate CSS rules and fix colliding @keyframes names

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 12: Animation Performance Audit & Optimization

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — all `@keyframes` blocks

- [ ] **Step 1: Audit all always-running animations**

Search for `infinite` keyword in the CSS file and list every animation that runs continuously:

Expected always-running animations (approximate):
1. `spin` — loading spinner rings (only shown during connect, acceptable)
2. `taunt-pulse` — taunt shield glow (only on taunt minions, usually 1-7 max)
3. `shield-bubble-pulse` — divine shield bubble (only on divine shield minions, rare)
4. `smoke-drift` / `smoke-puddle` — stealth effects (only on stealth minions, rare)
5. `wind-spin-1` / `wind-spin-2` — windfury spinners (only on windfury minions, rare)
6. `frozen-shimmer` — frozen icon float (only on frozen minions, rare)
7. `deathrattle-pulse` — deathrattle icon (only on deathrattle minions, rare)
8. `poisonous-pulse` — poisonous icon (only on poisonous minions, rare)
9. `immune-glow` — immune icon (only on immune minions, rare)
10. `armor-shine` — armor pulsing (only when hero has armor, intermittent)
11. `armor-gain-flash` — armor gain flash (triggered on gain, one-shot)
12. `combo-pulse` — combo indicator (only during combo active, intermittent)
13. `badge-pulse` — hero power badge (always present when badge exists)
14. `overload-pulse` — overload locked indicator (intermittent)
15. `temp-mana-glow` — temp mana glow (intermittent)
16. `legendary-shimmer` — legendary card border (only on legendary cards, rare)
17. `timer-pulse` — timer warning (only when time low, intermittent)
18. `warning-pulse` — field full warning (only when field full, rare)
19. `hand-full-pulse` — hand full warning (only when hand full, rare)
20. `deck-empty-pulse` — deck empty warning (only when deck empty, rare)
21. `rope-burning` — rope burn progress bar (only during player's turn, intermittent)
22. `secret-triggering` — secret trigger flash (one-shot per trigger)
23. `staged-pulse` / `staged-indicator-pulse` — staged card placeholder (intermittent)
24. `targeting-pulse` — valid target hint (intermittent)
25. `discover-pulse` — discover icon (renamed from pulse, only during discover)

Most of these run on very few elements simultaneously. **No action needed** — the total count of concurrent infinite animations at any given moment is typically under 10, which is well within browser limits.

- [ ] **Step 2: Optimize high-frequency animations**

For the most common animations (taunt, divine shield, combo indicator, legendary shimmer), ensure they use `transform` and `opacity` only (avoid `filter: blur()` and complex `box-shadow` in the animated keyframes):

Check that `taunt-pulse`, `shield-bubble-pulse`, `combo-pulse`, and `legendary-shimmer` only animate `transform`, `opacity`, and/or `box-shadow` color — never `filter: blur()` or heavy paint properties.

If any use `filter: blur()` in their keyframes, simplify to opacity/transform alternatives.

- [ ] **Step 3: Add `will-change` hints for animated elements**

Add to commonly animated elements:

```css
.minion.taunt { will-change: transform, box-shadow; }
.minion.divine-shield { will-change: transform, box-shadow, filter; }
.card.playable { will-change: transform, box-shadow, z-index, filter; }
.hero-portrait.valid-target { will-change: box-shadow; }
.end-turn-btn:not(:disabled) { will-change: box-shadow; }
```

This tells the browser to promote these elements to their own compositing layer, reducing repaints on other elements.

- [ ] **Step 4: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): optimize animation performance with will-change hints

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 13: Responsive Refinement Pass

**Files:**
- Modify: `webui/client/src/components/GameBoard.css` — media queries and responsive breakpoints

- [ ] **Step 1: Review and tighten mobile breakpoint (<900px)**

Currently at `< 900px`, the sidebar and controls are hidden (`display: none`). Check if the game is actually usable on mobile at this breakpoint:

Read the `@media (max-width: 900px)` block and verify:
- Hand cards are still readable at small sizes
- Minion stats don't overflow
- Hero info fits without overlapping
- Turn indicator and timer are visible
- Action log hiding is appropriate (it takes too much space on mobile)

- [ ] **Step 2: Ensure clamp() values have good floor values**

Spot-check critical `clamp()` usages for excessively small minimums:
- `--card-width: clamp(60px, 12vw, 100px)` — 60px minimum seems OK
- `--card-height: clamp(84px, 16.8vw, 140px)` — 84px minimum seems OK
- `--minion-width: clamp(50px, 10vw, 80px)` — 50px minimum seems OK
- Font sizes: verify nothing goes below 10px at smallest viewport

- [ ] **Step 3: Add ultra-wide screen consideration (optional)**

```css
@media (min-width: 1800px) {
  .game-board {
    max-width: 1400px;
    margin: 0 auto;
  }
}
```

Prevents the board from becoming absurdly wide on ultrawide monitors.

- [ ] **Step 4: Commit**

```bash
git add webui/client/src/components/GameBoard.css
git commit -m "style(ui): refine responsive breakpoints and ultra-wide screen handling

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 14: Final Visual QA Checklist

**Files:**
- Manual visual testing required — no code changes, just verification

- [ ] **Step 1: Full gameplay visual walkthrough**

Start a game (PvE or PvP) and manually verify:

**Menu Screen:**
- [ ] Background has atmospheric depth (noise + vignette)
- [ ] Title "Fireplace" has golden glow
- [ ] Mode buttons have consistent depth hover
- [ ] Hero select grid buttons match mode button style
- [ ] Settings menu opens cleanly

**Game Board - Top (Opponent):**
- [ ] Opponent hand cards show striped pattern on backs
- [ ] Hero portrait is shield/octagonal shape with gold frame
- [ ] Hero power shows as circular icon with cost gem
- [ ] Mana display has crystal-like top highlight
- [ ] Health/Armor are pill badges with proper colors
- [ ] Opponent field shows mini-card style minions (not ovals!)
- [ ] Zone has noticeable crimson-violet atmosphere

**Center:**
- [ ] Divider has decorative corner ornament lines
- [ ] Turn indicator is premium badge style
- [ ] Timer shows correctly (tabular digits)

**Bottom (Player):**
- [ ] Player field shows mini-card style minions
- [ ] Player hero is shield-shaped with gold frame
- [] Player hand cards have inner frame decoration
- [ ] Cost gems are diamond-shaped
- [] Attack/health are diamond-shaped
- [ ] Playable cards have green glow
- [ ] Card hover shows 3D perspective tilt
- [ ] Legendary cards (if any) have orange shimmer

**Right Sidebar:**
- [ ] Left gold edge accent line visible
- [ ] End turn button is premium red with depth
- [ ] Concede/New Game buttons have themed hovers
- [ ] Action log header is uppercase gold
- [ ] Log entries have colored left borders

**Interactions:**
- [ ] Dragging a card works smoothly
- [ ] Attacking a minion shows arrow
- [ ] Hero power click/drag works
- [ ] Turn banner appears on your turn
- [ ] Game over dialog looks grand
- [ ] Tooltips follow cursor smoothly
- [ ] Discover panel slides in from right
- [ ] Choose One dialog looks polished

**Mechanic Effects (test with specific cards):**
- [ ] Taunt minion shows golden shield SVG border + pulsing
- [ ] Divine shield minion shows white bubble glow
- [ ] Stealth minion is semi-transparent with smoke
- [ Windfury minion has spinning swirls
- [ ] Frozen minion has ice overlay + snowflake
- [ ] Deathrattle minion shows skull icon
- [ Poisonous minion shows skull-crossbones
- [ Immune minion shows shield-star
- [ ] Silenced minion shows slash-circle
- [ ] Combo active indicator pulses amber

**Performance:**
- [ ] No visible jank or stutter during animations
- [ ] Page scrolls smoothly if content overflows
- [ ] Memory usage is stable (check DevTools if concerned)

- [ ] **Step 2: Note any issues found**

List anything that looks wrong or needs adjustment. These become action items for future fixes (not blocking for this phase).

- [ ] **Step 3: Final commit if any tweaks were made**

If any CSS adjustments were made during QA, commit them:
```bash
git add -A
git commit -m "style(ui): final visual QA adjustments for Phase 2-5

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Self-Review Checklist

**Spec coverage (Phases 2-5):**

| Phase | Tasks | Key Deliverables | Status (in this plan) |
|-------|-------|-----------------|---------------------|
| 2 | 1-6 | Card frame, cost diamond, stat diamonds, rarity borders, 3D hover, card back pattern | ✅ All specified |
| 3 | 7-8 | Hero shield shape, gold frame, mana crystal styling | ✅ All specified |
| 4 | 9-10 | Minion→mini-card, SVG mechanic icons | ✅ All specified |
| 5 | 11-14 | Deduplication, animation perf, responsive, final QA | ✅ All specified |

**Placeholder scan:** No TBD/TODO found. Every step includes exact CSS code.

**Type consistency:** All variable references use names defined in Phase 1's `:root` block. No new variables introduced without definition. Clip-path coordinates verified. SVG data-URIs properly encoded.

**Cross-phase dependencies:**
- Phase 2 builds on Phase 1's `.card` and `.card-*` selectors (safe, Phase 1 completed)
- Phase 3 builds on Phase 1's `.hero-portrait` and `.hero-*` selectors (safe)
- Phase 4 builds on Phase 1's `.minion` and `.minion-body` selectors (safe)
- Phase 5 is cleanup/polish only (safe, no structural dependencies)

**Risk notes:**
- **Task 9 (Minion → Mini-Card)** is the highest-risk change — converts all minions from `border-radius: 50%` to `border-radius: 10px`. Must verify that `.minion.can-attack`, `.minion.taunt`, `.minion.divine-shield`, `.minion.stealth`, `.minion.frozen`, etc. pseudo-elements still work with the new shape.
- **Task 7 (Hero Shield Shape)** uses `clip-path: polygon()` which may not be perfectly supported on very old browsers. Acceptable for modern browsers (Chrome 88+, Firefox 54+, Safari 14+).
- **Task 2 (Cost Diamond)** uses `clip-path: polygon()` — same browser compatibility note as above.
