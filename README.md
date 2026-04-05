# 💸 SpendWise — Personal Finance Tracker

> **A full-stack PWA that lets users track income, expenses, and savings goals — synced in real-time across devices, installable on any phone, and built entirely without a framework.**

🔗 **[Live Demo](https://project-4o1eq.vercel.app)** &nbsp;|&nbsp; 📋 **[Test Cases (29 scenarios)](./SpendWise_TestCases.xlsx)** &nbsp;|&nbsp; 🤖 **[Selenium Test Suite](./spendwise_selenium_tests.py)**

---

## Why This Project Stands Out

Most beginner finance apps are todo-list clones in disguise. SpendWise is different — it integrates **Google OAuth**, **Firestore real-time sync**, **live currency conversion**, and **PWA installability** into a single, dependency-free HTML/CSS/JS file. No React. No bundler. No backend server. Just clean, deliberate engineering.

---

## What It Does

**Transaction Management**
- Log income and expenses with category, date, and description
- Month-by-month summary showing balance, total income, and total expenses
- Filter transaction history by type (all / in / out)
- Supports both Bangladeshi (৳ 35,00,000) and international (3,500,000) number formatting

**Savings Goals**
- Create named savings goals with a target amount
- Auto-calculates progress based on a percentage or fixed amount drawn from real income transactions
- Configurable income category filters (e.g. only count 💼 Work income toward a goal)
- Animated progress bar with live saved/remaining breakdown

**Multi-Currency Support**
- 26 supported currencies with live exchange rates via ExchangeRate API
- Toggle a conversion overlay that shows every amount in a secondary currency in real-time
- Currency preference persists across sessions

**Authentication & Sync**
- Google Sign-In via the GSI client — no password, no friction
- All data synced to **Cloud Firestore** with a debounced write strategy to minimize API calls
- Offline-first: data is read from `localStorage` instantly while Firebase catches up in the background
- Visual sync indicator dot in the header

**PWA — Works Like a Native App**
- Installable on iOS and Android via `manifest.json`
- Service worker for offline capability
- Safe area insets, splash screen, and mobile-optimised touch targets

---

## Technical Highlights

| Area | Implementation |
|---|---|
| Auth | Google Identity Services (GSI), JWT verified via `tokeninfo` endpoint |
| Database | Cloud Firestore with `onSnapshot` real-time listener |
| Offline | `localStorage` cache + Service Worker (`sw.js`) |
| Currency API | ExchangeRate API v6 with graceful degradation |
| Security | All user-generated content escaped via `esc()` before DOM injection — XSS-safe |
| Performance | Debounced Firestore saves (800ms) to batch rapid state changes |
| Formatting | Custom Bangladeshi lakh/crore number formatter with live input masking |

**Stack:** Vanilla JS · HTML · CSS · Firebase Firestore · Google OAuth 2.0 · ExchangeRate API · Vercel

---

## Testing

This project was built with quality assurance as a first-class concern, not an afterthought.

**Manual Test Cases**
- 29 scenarios across 7 modules designed for TestRail
- Covers: authentication, transaction CRUD, goal logic, currency switching, filtering, and PWA behaviour

**Selenium Automation Suite**
- 18 automated end-to-end tests covering critical user paths
- Run locally in 2 steps:

```bash
pip install selenium webdriver-manager
python spendwise_selenium_tests.py
```

---

## Getting Started

No setup required — it's a static app deployed on Vercel.

**To run locally:**
```bash
git clone https://github.com/tasfii567/SpendWise.git
cd SpendWise
# Open index.html in your browser, or serve with any static file server
npx serve .
```

> Note: Google Sign-In requires the app to be served over HTTP/HTTPS (not `file://`).

---

## Project Structure

```
SpendWise/
├── index.html                  # Entire frontend — UI, logic, Firebase init
├── sw.js                       # Service worker for PWA offline support
├── manifest.json               # PWA manifest (icons, theme, display)
├── icon-192.png                # App icon
├── icon-512.png                # App icon (large)
├── SpendWise_TestCases.xlsx    # 29 manual test cases (TestRail-ready)
└── spendwise_selenium_tests.py # Selenium automation suite (18 tests)
```

---

## Skills Demonstrated

- Building a **production-ready PWA** from scratch with zero dependencies
- **OAuth integration** with secure server-side token verification
- **Real-time database** design with Firestore and optimistic UI updates
- Writing a complete **QA test plan** — both manual and automated — alongside the feature code
- Deploying and shipping to a live URL via Vercel

---

*Built by [@tasfii567](https://github.com/tasfii567)*
