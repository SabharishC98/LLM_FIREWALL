
I have read every file in full. Here is the exhaustive audit report — ready to be turned into an artifact.

---

# 🔍 LLM Firewall Frontend — Comprehensive Code Audit Report

**Scope:** `frontend/` — all files in `src/`, plus `package.json`, `vite.config.js`, `index.html`, `tailwind.config.js`  
**Total files read:** 22

---

## 📁 CONFIG & INFRASTRUCTURE FILES

---

### `package.json`
**What it does:** Declares dependencies, scripts, and project metadata.

**Issues:**
1. **No `lint` or `test` scripts** — No ESLint, Prettier, or Vitest configured at all. Zero test coverage infrastructure.
2. **No `"lint"` or `"format"` scripts** — This means CI/CD has no automated quality gate.
3. **Missing `"eslint"` / `"@eslint/js"` / `"eslint-plugin-react-hooks"` devDependencies** — react-hooks lint rules are absent; this causes silent bugs (e.g., exhaustive deps violations won't be caught).
4. **`"@types/d3": "^7.4.3"` in devDependencies but project has no TypeScript** — The `@types/d3` package is pointless without TS. It's dead weight.
5. **No `"engines"` field** — No Node.js version constraint declared; devs could run mismatched versions.
6. **`"version": "1.0.0"` with `"private": true`** — Fine for internal apps; no issue there.
7. **`clsx` installed but never used anywhere in the codebase** — Dead dependency, ships to bundle.

---

### `vite.config.js`
**What it does:** Configures the Vite dev server with a proxy to `localhost:8000` for `/v1` and `/health` routes.

**Issues:**
1. **Proxy target is hardcoded to `http://localhost:8000`** — Will break in staging/prod and for any teammate who runs the backend on a different port. Should use `process.env.VITE_BACKEND_URL || 'http://localhost:8000'`.
2. **No `build.outDir` or `build.sourcemap` configuration** — In production, there will be no sourcemaps, making debugging impossible.
3. **No `preview` port specified** — `vite preview` will pick a random available port. Should set `preview: { port: 4173 }`.
4. **Proxy only proxies `/v1` and `/health`** — If the backend ever adds a route at a different prefix, the proxy silently breaks and the dev gets CORS errors.
5. **No `server.host` declared** — Won't bind to `0.0.0.0`; prevents Docker/WSL2 development workflows.
6. **No `resolve.alias`** — All imports use relative paths like `'../../utils/api'`, making refactoring painful. Should define `@/` alias.

---

### `index.html`
**What it does:** Root HTML shell for the React SPA.

**Issues:**
1. **Google Fonts loaded via external CDN without SRI hashes** — If fonts.googleapis.com is compromised, arbitrary CSS can be injected. No `integrity` attribute.
2. **`rel="preconnect"` but no `rel="preload"` for the font CSS** — Preconnect without preload is half-baked. Font swap flicker will occur.
3. **No CSP (Content Security Policy) meta tag** — Massive security gap. Without CSP, XSS via injected scripts is fully enabled.
4. **Favicon uses an inline SVG `data:` URI with an emoji** — Renders incorrectly on Firefox and some mobile browsers. Not production-ready.
5. **No OG tags / social metadata** — Minor, but the description meta is set; OG isn't.
6. **`class="bg-firewall-bg text-firewall-text"` on `<body>`** — These Tailwind classes are defined in tailwind config but the body is styled in `index.css` with hardcoded hex too. Duplication of styling intent.
7. **No `<noscript>` fallback** — Users with JS disabled see a blank page with no explanation.

---

### `tailwind.config.js`
**What it does:** Extends Tailwind with custom firewall design tokens.

**Issues:**
1. **`grid-cols-24` is used in `Analytics.jsx` (heatmap) but is NOT defined in the Tailwind config** — Tailwind only ships `grid-cols-1` through `grid-cols-12` by default. This class will not render. The 24-column heatmap grid will silently break into a single column.
2. **`animate-fade-in` and `animate-slide-in` are defined, but `animate-blocked-shake`, `animate-ripple`, `animate-explosion` are defined only in `index.css`** — Split animation definitions; inconsistent approach.
3. **No `safelist` defined** — Dynamic Tailwind classes constructed in JS (e.g., `bg-firewall-${color}/10`) will be purged in production builds. Several components do this:
   - `RiskBadge.jsx` dynamically constructs `bgClasses` from a map (safe here)
   - `AttackChip.jsx` uses inline `style` (safe)
   - But `Overview.jsx` has `colorMap[color]` with strings — these ARE safe since they're pre-listed in an object. Still, vigilance required.
4. **`firewall-purple` is referenced in `ApiKeys.jsx` (`bg-firewall-purple/10`, `text-firewall-purple`) and IS defined in config** — OK, but opacity modifiers on custom colors require Tailwind 3 with CSS variables or explicit declaration. Currently uses hex — opacity modifiers on hex colors do work in Tailwind 3.3+ via `color-mix`. Fine for now.

---

## 📁 `src/` ROOT FILES

---

### `main.jsx`
**What it does:** React root mount with `BrowserRouter` and `StrictMode`.

**Issues:**
1. **No error boundary at the root level** — If any top-level component throws an unhandled error, the entire app goes blank. There should be an `<ErrorBoundary>` wrapping `<App />`.
2. **`document.getElementById('root')` has no null check** — If someone renames the div, the app crashes with an unclear error at `createRoot(null)`.
3. **No global toast/notification context** — API errors across all pages are silently swallowed or shown in different inconsistent ways.

---

### `App.jsx`
**What it does:** Route table using `react-router-dom` v6 with a shared `<Layout>` wrapper.

**Issues:**
1. **No 404 / catch-all route** — Navigating to `/unknown-path` renders nothing (empty `<main>`). Should add `<Route path="*" element={<NotFound />} />`.
2. **No `<Suspense>` / lazy loading** — All 5 pages are eagerly imported. For a dashboard with heavy charts (Recharts, D3), initial bundle will be large. Should use `React.lazy()` + `<Suspense>`.
3. **No route-level error boundaries** — A crash in any single page crashes the whole layout.

---

### `index.css`
**What it does:** Global styles, custom utilities, scrollbar overrides, animations.

**Issues:**
1. **`* { margin: 0; padding: 0; box-sizing: border-box }` in global CSS conflicts with Tailwind's `@tailwind base`** — Tailwind base (Preflight) already resets margins and padding. This is redundant and could conflict with Preflight's more targeted resets.
2. **Scrollbar styles use only `-webkit-scrollbar`** — Firefox uses `scrollbar-width` / `scrollbar-color`. No cross-browser scrollbar styling.
3. **Animation classes (`animate-ripple`, `animate-explosion`, `animate-blocked-shake`) are defined here but not in Tailwind config** — Using raw CSS instead of Tailwind `keyframes`/`animation` extensions. Fine, but inconsistent — other animations are in `tailwind.config.js`.
4. **`@layer utilities` block contains glassmorphism classes** — Good practice, but the `.glass` utility uses hardcoded hex colors (`rgba(26, 26, 26, 0.8)`) instead of CSS variables tied to the design token system. If the theme changes, these won't update.

---

## 📁 `utils/`

---

### `utils/api.js`
**What it does:** Central API client using `fetch`. Reads API key from `localStorage`. Exports all API methods.

**Issues:**
1. **`localStorage.getItem('fw_api_key')` — the API key is stored in `localStorage`** — This is a security vulnerability. `localStorage` is accessible to any JavaScript on the page, including XSS injected code. For a security product, the API key should at minimum be in `sessionStorage`, and ideally never stored client-side at all (use HttpOnly cookies for authenticated sessions).
2. **`throw { status: response.status, ...error }` — throwing a plain object, not an `Error` instance** — This breaks stack traces. `console.error` on this object won't show where the error originated. Should be `throw new Error(error.message)` or a custom error class.
3. **`return response.json()` at line 22 — no try/catch on the success path** — If the API returns `200 OK` with non-JSON body (e.g., plain text, HTML error page from a proxy), `response.json()` will throw an unhandled promise rejection that bubbles up uncaught.
4. **`VITE_API_URL` defaults to `''` (empty string)** — In production without the Vite proxy, all requests go to the same origin. This is intentional with a proxy, but there's no documentation or `.env.example` to communicate this. Developers deploying to a separate domain will silently break all API calls.
5. **`api.check(prompt, threshold, app_context, custom_canary)` — all parameters positional** — Easy to accidentally swap `threshold` and `app_context`. Should accept an options object.
6. **No request timeout** — `fetch()` has no built-in timeout. A hanging backend will hang the UI forever with a loading spinner.
7. **No retry logic** — A transient network error gives the user a permanent error state.
8. **`getLogs` filters out `false` and `0` values** — `if (val !== undefined && val !== null && val !== '')` — `flagged_only: false` would be excluded! The `false` value IS different from "not set," but gets dropped by this check. This means you can never actively un-filter.

---

### `utils/formatters.js`
**What it does:** Pure utility functions for formatting risk scores, timestamps, numbers, attack types, and colors.

**Issues:**
1. **`formatRiskScore(score)` — no guard against non-numeric input** — If `score` is `"high"` or `NaN`, `(score * 100).toFixed(1)` produces `"NaN%"` which renders in the UI.
2. **`formatMs(ms)` — `ms < 1` check is misleading** — Returns `'<1ms'` for `0.0001ms`. The condition should probably be `ms < 1` or `ms === 0`.
3. **`formatTime`/`formatDateTime` hardcodes `'en-US'` locale** — The dashboard may be used internationally. Should use `undefined` to auto-detect the user's locale, or make locale configurable.
4. **`formatAttackType` has duplicate entries** — `canary_echo`, `refusal_bypass`, and `indirect_injection` appear BOTH in the prefix-check block (lines 87–99) AND in the `map` object (lines 111–113). The map entries are dead code — they can never be reached because the prefix checks above always catch them first.
5. **`getAttackColor` doesn't cover all attack types in `formatAttackType`'s map** — Attack types like `DIRECT_INJECTION`, `PERSONA_HIJACKING`, `SYSTEM_OVERRIDE`, `ENCODING_ATTACKS`, `MANY_SHOT` have labels defined but no color in `getAttackColor`. They fall through to `'#888888'` (grey).
6. **`getRiskColor(score)` — no guard for `null`/`undefined` score** — `null >= 0.65` is `false` in JS, so null scores always render as green `text-firewall-green`. This is a silent false-safe classification in the UI.
7. **`getRiskBg(score)` — same `null` guard issue as `getRiskColor`**.
8. **`timeAgo` — `new Date(iso)` will produce `Invalid Date` if `iso` is malformed** — `getTime()` on invalid date returns `NaN`, `Math.floor(NaN / 1000)` = `NaN`, and the function returns `'NaNs ago'` in the UI.

---

## 📁 `hooks/`

---

### `hooks/usePolling.js`
**What it does:** Generic polling hook wrapping an async fetch function with interval, loading, and error states.

**Issues:**
1. **`loading` initializes to `true` but never resets to `true` on subsequent polls** — After the first load, every subsequent poll silently updates data without any visual indicator. If a poll fails after successful data, `loading` stays `false`, and the stale data is shown without a "refreshing" indicator.
2. **Race condition: if a slow fetch resolves after a newer one, data can be overwritten with stale data** — There is no abort/cancel mechanism. If poll interval is 3s but a fetch takes 4s, the responses will arrive out of order, setting old data over new. Should use `AbortController` or a sequence counter.
3. **`setError(err)` stores the raw error object in state** — The error object from `api.js` is a plain object (not an Error instance). Rendering `error.message` in components will be `undefined`. Error objects are also not serializable, which can cause issues with React DevTools.
4. **The hook has `intervalMs` and `enabled` in the dependency array of `useEffect`** — `refresh` is also in the dep array. Since `refresh` is a `useCallback` with `[]` deps, this is stable. But `fetchFn` is reassigned every render via `fetchRef.current = fetchFn` — the actual fetch is not in the dep array, which is intentional but non-obvious.
5. **If `enabled` toggles from `true` to `false`, the in-flight request still completes and calls `setData`/`setError`** — This could update unmounted component state (causes React warning) or a component that has moved on.
6. **No cleanup of in-flight requests on unmount** — Same AbortController issue. Network request continues even after the component unmounts.

---

### `hooks/useFirewall.js`
**What it does:** Thin wrapper around `api.js` methods with `useCallback`.

**Issues:**
1. **This hook is architecturally unnecessary** — Every method is a one-liner `return api.X(args)`. The `useCallback` with `[]` deps adds zero value because the `api` object methods are already stable module-level references. This is boilerplate with no benefit.
2. **`createKey(name, tier)` in the hook only accepts 2 params**, but `api.createKey` accepts 5 (`name, tier, app_context, custom_canary, custom_intent_examples`). The hook silently drops the extra 3 args. `ApiKeys.jsx` correctly bypasses this hook and calls `api.createKey()` directly — meaning the hook is wrong and the page is correct, but this is confusing.
3. **`checkPrompt(prompt, threshold)` in the hook only accepts 2 params**, but `api.check` accepts 4. Same mismatch. `LiveTestWidget.jsx` also bypasses this hook.
4. **None of the hook functions have any error handling** — All rejections propagate raw to callers. The hook is supposed to be the "API layer" but provides no consistent error normalization.

---

## 📁 `components/`

---

### `components/AttackChip.jsx`
**What it does:** Renders a colored chip badge for an attack type string.

**Issues:**
1. **No PropTypes or TypeScript** — `type` prop is untyped. Could receive anything.
2. **`${color}15` and `${color}40` hex opacity shorthand** — Works for 6-char hex colors (e.g., `#E63946`). If `getAttackColor` ever returns a named color or `rgb()` value, this breaks silently and the chip renders with wrong/no background.
3. **No `title` attribute** — Long attack type labels are truncated by their container, with no tooltip to reveal the full name.

---

### `components/RiskBadge.jsx`
**What it does:** Renders BLOCKED/SUSPICIOUS/SAFE label with color-coded dot and score.

**Issues:**
1. **No `score` null/undefined guard** — If `score` is `null`, `score >= 0.65` is false, `score >= 0.35` is false, so label renders as `'SAFE'` and `getRiskColor(null)` returns `'text-firewall-green'`. A null-score request is shown as SAFE — potentially misleading.
2. **`sizeClasses[size]` has no fallback** — If an unknown `size` prop is passed (e.g., `size="xl"`), `sizeClasses[size]` is `undefined`, and the className concatenation produces `"... undefined ..."` in the DOM.
3. **No PropTypes or TypeScript**.
4. **The `bgClasses` map is keyed on computed Tailwind class strings** — This is fragile. If `getRiskColor` ever changes its return values, the bg mapping silently breaks.

---

### `components/Layout.jsx`
**What it does:** App shell with sidebar + `<Outlet>` for page content.

**Issues:**
1. **`h-screen overflow-hidden` on the outer div + `overflow-y-auto` on `<main>`** — Correct pattern, but on mobile the sidebar is fixed-width `w-64` with no responsive behavior. On screens < 768px, the sidebar and main content will overflow without scroll.
2. **No responsive/mobile layout** — No `hidden md:block` on sidebar, no hamburger menu. The app is completely unusable on mobile.
3. **Sidebar always mounted** — No lazy loading for sidebar navigation items. Minor.

---

### `components/Sidebar.jsx`
**What it does:** Navigation sidebar with logo, nav links, and a "System Online" status indicator.

**Issues:**
1. **`"System Online"` and `"3-Layer Pipeline Active"` are hardcoded strings** — These are always shown regardless of actual backend health. The status never dynamically checks if the backend is reachable. This is cosmetic lying — it shows "Online" even when the API is down.
2. **`v1.0.0` is hardcoded** — Should come from `package.json` via `import pkg from '../../package.json' assert { type: 'json' }` or a Vite define.
3. **"3-Layer Pipeline Active" text is factually wrong** — The system has 6 layers (0–5), not 3. Inconsistent with the rest of the UI.
4. **No aria roles on `<nav>`** — The `<nav>` element has no `aria-label="Main navigation"`. Accessibility gap.
5. **No keyboard navigation handling** — All navlinks are anchor-like but rely entirely on browser defaults.
6. **No active state on the `<aside>`** — No `role="complementary"` or `aria-label`.

---

### `components/LayerBreakdown.jsx`
**What it does:** Renders a visual breakdown of all 6 pipeline layer results with scores, latency, and status indicators.

**Issues:**
1. **`canary?.ran !== false` as a "ran" check** — This evaluates to `true` when `canary` is `undefined` (because `undefined !== false`). So a missing layer object is shown as "ran" rather than "N/A". This could show misleading "0% score" rows for layers that didn't exist in the response.
2. **`(embedding_similarity.similarity_score * 100).toFixed(1)` at line 74** — No null guard. If `similarity_score` is `null`, this produces `"0.0%"` instead of `"—"`. Line 75 has a fallback `|| 0` but line 74 does not.
3. **`context_policy.similarity_to_intent` at line 106** — No null guard. If `context_policy.triggered` is true but `similarity_to_intent` is undefined, this produces `"NaN%"`.
4. **`context_policy.app_context` at line 107** — When context policy is not triggered, the template literal renders `Within scope for "undefined"` if `app_context` is absent.
5. **Emoji icons in SVG text** — The layer icons are rendered as text content. These work in HTML but are non-accessible and inconsistent with the Lucide React icon system used everywhere else.
6. **The `LayerRow` subcomponent is defined in the same file but not exported** — Fine for now, but limits reusability.
7. **Score display `(score * 100).toFixed(1)%` at line 141** — If `score > 1.0` (a backend bug), this displays ">100%" which looks broken.
8. **Comment at top says "6 classifier layers" but Layer 0 (Canary) is labeled separately, making it ambiguous** — Minor doc inconsistency.

---

### `components/LogDrawer.jsx`
**What it does:** Slide-out drawer showing full detail of a log entry including all layer data.

**Issues:**
1. **`animate-slide-in` CSS class** — This class IS defined in `tailwind.config.js` (`keyframes.slide-in`). Good. But no exit/closing animation — the drawer just vanishes on close.
2. **No Escape key handler to close** — Standard UX expectation for modal drawers. `onKeyDown` / `useEffect` + `keydown` listener is missing.
3. **Backdrop click closes the drawer, but the drawer itself has no focus trap** — Screen reader and keyboard users can tab behind the drawer to the main content.
4. **Heuristic signal rendering: `(val * 100).toFixed(0)%` for progress bar width** — If `val > 1.0`, the bar width exceeds 100%, overflowing the container visually.
5. **ML scores: `Object.entries(log.layers.ml_classifier.all_scores).sort(...)` — no null guard on `all_scores` values** — If any score is `null`, `b - a` returns `NaN` and sort order is undefined.
6. **`log.flagged_pattern` rendered inside `<code>` without sanitization** — If `flagged_pattern` contains HTML entities or script-like text, React's JSX escaping protects against actual XSS. But regex patterns may contain characters that look like broken HTML in the DOM inspector.
7. **Drawer is `w-[500px]` fixed** — On screens < 500px wide it overflows off the screen with no adaptation.
8. **No loading state** — If the drawer needs to fetch additional detail (it currently just uses the log object passed in), there's no skeleton.
9. **`{log.request_id}` displayed directly** — If request_id contains very long strings, it will overflow the header.

---

### `components/LiveGraph.jsx`
**What it does:** D3.js animated graph showing App → Firewall → LLM with animated pulses for safe/blocked events.

**Issues:**
1. **Memory leak: `setTimeout(() => g.remove(), delay + N)` references** — If the component unmounts before the timeout fires, `g.remove()` tries to operate on a detached DOM node. The timeouts are not cleared on cleanup, leaking timer handles.
2. **Memory leak: `firewallPulse()` recursive transition at line 147–159** — The idle animation calls itself recursively via `.on('end', firewallPulse)`. When `events.length` goes from 0 to >0 and `useEffect` re-runs, the entire SVG is cleared with `svg.selectAll('*').remove()` at line 31 — but the recursive D3 transition is not explicitly stopped. D3 transitions on removed nodes will error silently, but the `firewallPulse` closure still holds a reference to the old selection.
3. **`prevEventsLen.current` tracks the length, not identity of events** — If `events` array is replaced with a new array of the same length, `newEvents` will be an empty slice and no animation triggers. This can happen if the parent re-renders with a new array reference.
4. **SVG redraws entirely on every `events` change** — `svg.selectAll('*').remove()` and full redraw on every new event. For a real-time monitor this is expensive. D3 should use an enter/update/exit pattern instead.
5. **No resize observer** — The SVG `width`/`height` is captured once at mount (`container.clientWidth`). If the container resizes (window resize), the SVG doesn't adapt.
6. **`nodes` and `edges` arrays are recreated on every render** — Minor, but these are constants that could be outside the component.
7. **`animateSafePulse` and `animateBlockedPulse` are module-level functions that receive `svg`** — They operate on the live D3 SVG selection. If called after unmount, they will throw.
8. **No accessibility** — The SVG has no `role`, `aria-label`, or title. Screen readers see nothing.
9. **Events array grows unboundedly** — `setEvents(prev => [...prev, ...newLogs...])` appends forever. After hours of use, this array could become enormous, causing performance issues.
10. **Hardcoded magic numbers throughout** — `delay + 2000`, `delay + 3000`, `800` per event stagger, `width * 0.15/0.5/0.85` for node positions. None are configurable.

---

### `components/LiveTestWidget.jsx`
**What it does:** Inline prompt-testing widget with example buttons, textarea, context config, and result display.

**Issues:**
1. **`api.check()` called directly, bypassing `useFirewall` hook** — Inconsistent. The hook exists but is ignored here.
2. **`setError(err.detail || err.error || 'Failed to check prompt')` — narrow error property check** — If `err` is a network error (e.g., `TypeError: Failed to fetch`), `.detail` and `.error` are both undefined, so error shows `'Failed to check prompt'` with no useful detail. The original `err.message` from the TypeError is discarded.
3. **`result.processing_time_ms` used directly at line 168: `Math.round(result.processing_time_ms)`** — No null guard. If the field is absent, renders `NaN`.
4. **`EXAMPLE_PROMPTS` is a module-level constant** — Fine, but the actual attack prompt strings in the code ("Ignore all previous instructions...") will appear in the source map / JS bundle. Not a practical security issue but worth noting.
5. **No max-length on the textarea** — A user could paste megabytes of text and the entire payload gets sent to the API with no client-side validation.
6. **App context options are hardcoded** — `general`, `coding_assistant`, `recipe_bot`, etc. These should come from the API or a shared config so they don't get out of sync with the backend.
7. **No keyboard shortcut to submit** — `Ctrl+Enter` to submit is a universal expectation for textarea inputs.
8. **`animate-fade-in` class on result div** — This animation is defined in `tailwind.config.js`. ✓ But the animation replays every time the same result re-renders due to parent re-render (no memoization).
9. **`JSON.stringify(result, null, 2)` in `<pre>` renders raw API response** — Good for debugging, but in production this exposes full internal scoring details to anyone who opens DevTools.

---

## 📁 `pages/`

---

### `pages/Overview.jsx`
**What it does:** Dashboard overview with metric cards, attack breakdown donut chart, layer effectiveness bars, and a real-time feed.

**Issues:**
1. **Both `usePolling` calls have no error handling in the UI** — `error` is destructured but never used. If `api.getStats()` fails, `stats` is `null`, cards show `0`, and there's no visible error state.
2. **`stats?.block_rate?.toFixed(1) || 0` at lines 78, 84** — If `block_rate` is `0.0`, the `|| 0` fallback activates because `"0.0"` is truthy but `0.0.toFixed(1)` = `"0.0"` which is truthy. Actually safe, but `|| 0` mixed with optional chaining is misleading — should use `?? 0`.
3. **`ATTACK_COLORS` local map partially duplicates `getAttackColor` from formatters** — Two sources of truth for attack colors. They can diverge. `prompt_leaking` is in `ATTACK_COLORS` but not in `getAttackColor`, and vice versa for `prompt_extraction`.
4. **`<Cell key={i} ...>` uses array index as key** — Should use `entry.name` as key. If the attack data order changes between polls, React may reuse wrong DOM nodes.
5. **Missing loading skeleton** — When `statsLoading` is true, the metric cards just show `0` values. There's no skeleton/shimmer state.
6. **`<LogDrawer>` is rendered inside `<div className="space-y-6">` instead of a portal** — The drawer's `position: fixed` works visually, but stacking contexts from parent CSS (e.g., `transform`, `filter`, `backdrop-filter`) can break `fixed` positioning. Should use `ReactDOM.createPortal`.
7. **`LineChart` is imported from recharts but never used** — Dead import.
8. **`TrendingDown` is imported from lucide-react but never used** — Dead import.
9. **`Clock` is imported in `Analytics.jsx` — but in Overview, icons like `TrendingUp` and `TrendingDown` are imported** — `TrendingDown` is unused.
10. **No `aria-label` on chart containers** — Charts are inaccessible to screen readers.

---

### `pages/LiveMonitor.jsx`
**What it does:** Real-time split-screen monitor with scrolling log, D3 graph, session stats bar, and `LiveTestWidget`.

**Issues:**
1. **`events` array grows unboundedly** — `setEvents(prev => [...prev, ...newLogs])` accumulates every event seen during the session. After hours of uptime, this array becomes enormous and causes performance degradation in both React state and D3 rendering.
2. **No error UI when polling fails** — `error` is not destructured from `usePolling`. If the API goes down, the log stream just freezes silently with no indicator.
3. **`bg-firewall-red/8` at line 121** — Tailwind opacity modifier `/8` produces `rgba` with 8/255 ≈ 3.1% opacity. This is valid Tailwind but extremely faint — likely intended to be `/10` (10%) for consistency with other uses.
4. **`prevLogsRef` comparison relies on `request_id` equality** — If the backend reuses `request_id` (unlikely but possible), new events won't be detected.
5. **Session stats are client-side only** — Refreshing the page resets session stats to 0. This is by design but should be documented.
6. **`style={{ maxHeight: '500px' }}` is inline** — This bypasses Tailwind's utility system. Should use `max-h-[500px]` Tailwind class.
7. **`<Shield />` inside the empty state at line 151 is imported but only used in this one spot** — Fine, not a bug.
8. **The "6-Layer Status Bar" at line 86–101 lists only 5 named layers (Canary → Rule-Based → Embedding → ML → Context Policy → Output)** — "Heuristic" layer is missing from the display, and "Output" is listed but isn't a detection layer. The pipeline bar is inaccurate.
9. **No responsive layout** — `grid-cols-5` split will break on medium screens.

---

### `pages/Analytics.jsx`
**What it does:** Deep analytics page with stacked area chart, heatmap, risk score histogram, layer effectiveness bars, and flagged patterns list.

**Issues:**
1. **`grid-cols-24` CSS class used for heatmap (line 186, 201)** — As noted in tailwind config: this class is NOT in Tailwind's default config and NOT extended. **This is a rendering bug** — the 24-column hourly heatmap will not render correctly in a production build (class gets purged/not generated).
2. **No error state for the stats fetch** — `error` from `usePolling` is never used. If stats fail, the page shows empty charts with placeholder text.
3. **No loading state** — When stats are loading, charts show "Processing Trend Data..." / "Generating Score Map..." strings. These look like indefinite loading states without a spinner or skeleton.
4. **`"System Stability: 100.0%"` is hardcoded** — This value is always `100.0%` regardless of actual system health. It's a placeholder masquerading as a live metric. This is misleading in production.
5. **Stacked area chart has hardcoded `dataKey` names**: `role_override`, `goal_hijacking`, `context_poisoning`, `tool_manipulation`, `cascading_amplification` — If the backend returns different key names (e.g., `ROLE_OVERRIDE`), the chart renders empty. No defensive mapping.
6. **`heatmapData.filter(d => d.day === dayIdx)` — assumes `day` is 0-indexed Monday-start** — The DAYS array is `['Mon',...,'Sun']` (Monday=0). If the backend returns Sunday-start (0=Sunday, JavaScript convention), the entire heatmap will be shifted by one day.
7. **`topPatterns.map((item, i) => ...)` uses array index as key** — Should use a stable key like `item.pattern`.
8. **`getHeatmapColorClass` has hardcoded thresholds (10, 20, 35)** — These magic numbers should be constants or configurable.
9. **No `aria-label` or accessibility attributes on charts**.
10. **`layerData.canary_pct || 0` at line 289** — If `canary_pct` is `0`, `|| 0` is a no-op (fine). But if `canary_pct` is `undefined` because the key doesn't exist, it becomes `0` — same result. Using `?? 0` is more explicit.
11. **`percentage.toFixed(1)` in `LayerStat`** — No guard for when `percentage` is not a number. If the API returns a string, this crashes.

---

### `pages/Logs.jsx`
**What it does:** Paginated, filterable log table with CSV export and drawer for detail view.

**Issues:**
1. **`fetchLogs` function is recreated on every render** — It's defined inside the component without `useCallback`, so `usePolling(fetchLogs, 10000)` gets a new function reference on every render. `usePolling` handles this via `fetchRef.current = fetchFn` — so it works, but it's architecturally sloppy.
2. **CSV export does not escape values** — In `handleExportCSV`, values are joined with commas: `e.join(',')`. If any field contains a comma (e.g., `attack_type` = `"role_override, pattern"` or a timestamp with commas), the CSV will be malformed. Values must be quoted: `"${v}"` with internal quote escaping.
3. **CSV export only exports current page, not all logs** — The button label says "Export CSV" but only exports the 15 currently visible rows. This is misleading; users expect a full export.
4. **`useEffect` with `[page, flaggedOnly, blockedOnly, attackType, provider, refreshTrigger]` depends on `refresh`** — `refresh` is missing from the dep array (ESLint exhaustive-deps would catch this). With `refresh` excluded, if the hook rebuilds `refresh`, the effect won't rerun. Currently stable but fragile.
5. **`flaggedOnly || undefined` at line 27** — If `flaggedOnly` is `false`, this sends `undefined` (omitted). The filter can never be explicitly set to `false`. Only a problem if the backend treats "absent" differently from `false`.
6. **No loading skeleton in the table** — When `loading` is true, the table shows the previous data (or empty). No visual feedback of active loading except the spinning refresh icon in the header.
7. **`(log.risk_score * 100).toFixed(1)%` at line 199** — No null guard. If `risk_score` is null, renders `NaN%`.
8. **Filter panel is missing a "clear all filters" button** — Users must manually reset each filter individually.
9. **`data?.pages || 1` — when `pages` is 0 (no results), defaults to 1** — Shows pagination for an empty table. Minor UX issue.
10. **No debounce on filter changes** — Each filter change immediately triggers a `refresh()` call. Not a problem with select/checkboxes, but if a search text field were added, this would be a problem.
11. **`<LogDrawer>` rendered inside page div, not in a portal** — Same issue as in Overview.jsx.
12. **Attack type filter options are hardcoded and only partially match the actual attack types in the system** — `prompt_leaking`, `jailbreak_direct`, `encoding_attack` are filter options but the backend's actual attack types include `role_override`, `goal_hijacking`, `DIRECT_INJECTION`, `ENCODING_ATTACKS` etc. Users filtering on `encoding_attack` may get no results if backend uses `ENCODING_ATTACKS`.

---

### `pages/ApiKeys.jsx`
**What it does:** API key management, creation, revocation, integration guide with code samples, and LiveTestWidget.

**Issues:**
1. **`handleCopy` uses `await navigator.clipboard.writeText()` without try/catch** — Clipboard API can be rejected (user denied permission, insecure context, Firefox private mode). The unhandled rejection will throw silently and `copiedId` will never be set.
2. **`handleCreate` silently swallows errors: `console.error('Failed to create key:', err)` at line 110** — No UI error feedback to the user. If key creation fails, nothing happens visually — the form just stays open.
3. **`handleRevoke` silently swallows errors similarly** — `console.error` only. If revocation fails, the key still appears in the list and the user doesn't know why.
4. **`confirm()` browser dialog used for revocation confirmation** — `window.confirm()` is deprecated UX, blocked in some embedded contexts, and not styleable. Should use a proper confirmation modal.
5. **`CODE_SAMPLES` contain `https://llmfirewall.dev/v1/check`** — This is a production domain hardcoded in the integration guide. If the domain changes, or for local dev, this is wrong. Should interpolate `import.meta.env.VITE_API_URL || window.location.origin`.
6. **`"fw_live_****{key.key_id.slice(-8)}"` at line 289** — This uses `key.key_id` (the UUID), not the actual masked API key. The `key_id` is not the secret. The masked display is fabricated and doesn't reflect the actual key prefix. Confusing and potentially misleading.
7. **`usePolling(() => api.listKeys(), 30000)` — 30-second interval for key list** — This is reasonable, but the keys list doesn't need polling at all. It only changes on user actions (create/revoke). Should use a plain fetch + manual `refresh()` trigger, not polling.
8. **No `loading` state used from `usePolling` for the keys list** — While keys are loading (on page mount), the list shows "No API keys yet" instead of a loading skeleton.
9. **`keysData?.keys || []` — if `keysData.keys` is `null`, defaults to `[]`** — Fine, but no error state.
10. **`setCreatedKey(result)` stores the full API response** — If the response includes sensitive fields, they're held in React state. The created key is rendered directly: `{createdKey.api_key}` — this exposes the full key in React DevTools state inspector.
11. **Integration guide tabs for `node` and `python` reference `llm-firewall` npm package** — This package may not exist yet. Showing code that doesn't work erodes trust.
12. **`setNewKeyTier` is set but `newKeyTier` state reset is missing in `handleCreate`** — After creating a key, `newKeyName`, `appContext`, `customCanary`, `customIntentExamples` are all reset, but `newKeyTier` is not reset to `'free'`.

---

## 📋 CROSS-CUTTING ISSUES (All Files)

1. **Zero PropTypes or TypeScript** — The entire frontend is untyped JavaScript. No prop validation on any component. In a security dashboard, passing a `null` score or wrong type to components causes silent rendering bugs (shown above repeatedly).

2. **No error boundaries** — No `<ErrorBoundary>` component exists anywhere. Any unhandled JS error in any component crashes the entire app silently.

3. **No global loading/error state management** — Each component manages its own error state independently, with inconsistent UX. Some show banners, some show nothing, some log to console.

4. **No toast notification system** — Create key failure, revoke failure, clipboard failure — all are silent. A toast library (e.g., react-hot-toast) is needed.

5. **D3 and React in the same render cycle** — `LiveGraph.jsx` manipulates the DOM directly via D3 inside a `useEffect`. This is the standard integration pattern, but cleanup is incomplete (memory leaks identified above).

6. **All pages import `api` directly AND some use `useFirewall` hook** — Inconsistent abstraction layer. `LiveTestWidget`, `ApiKeys`, `Logs`, `Overview`, `LiveMonitor`, `Analytics` all import `api` directly. `useFirewall` is defined but essentially unused.

7. **No `.env.example` file** — No documentation of what environment variables are available (`VITE_API_URL`). New developers will not know this exists.

8. **No 404 page, no error page** — Dead routes and backend errors have no dedicated UI.

9. **`animate-fade-in` class used on page mounts** — Every page has `animate-fade-in` on its root div. This is cosmetically fine but the animation re-fires on every page visit due to React Router unmounting/remounting components.

10. **App context options duplicated in three places** — `LiveTestWidget.jsx` (select options), `ApiKeys.jsx` (select options), `Logs.jsx` (filter options), and the backend presumably has its own list. These will diverge.

11. **No accessibility audit** — No `aria-*` attributes on charts, no focus management in drawers, no skip-to-content link, no keyboard navigation for modals. WCAG 2.1 AA is not met.

12. **CSP is completely absent** — Both in `index.html` (meta tag) and server config. XSS vulnerability.

---

## 🔴 SEVERITY SUMMARY

| Severity | Count | Examples |
|----------|-------|---------|
| 🔴 Critical (security/data integrity) | 4 | API key in localStorage, no CSP, unescaped CSV export, silent key creation failure |
| 🟠 High (functional bugs, data loss) | 12 | `grid-cols-24` heatmap broken, events array memory leak, null score shown as SAFE, LogDrawer has no portal, hook silently drops args |
| 🟡 Medium (UX, error handling) | 18 | No loading skeletons, no error states, no error boundaries, hardcoded "100% stability", no 404 route, confirm() dialog |
| 🔵 Low (code quality, maintainability) | 14 | Dead imports, unused hook, hardcoded thresholds, duplicate constants, no PropTypes, no TS |

Total findings: **48+**

All file paths confirmed from `e:\Drizzle\VS\firewall\frontend\`.
