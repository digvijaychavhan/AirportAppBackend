# Project Rules and Guidelines

## Git & Remote Push Policy
- **CRITICAL: NEVER run `git push` autonomously, automatically, or as part of a general commit/save task.**
- You must **ONLY** execute `git push` when the user **explicitly commands** you to push in that specific conversation turn (e.g. "push to git", "push to github", "git push").
- If the user asks to commit, only run `git commit` locally. Do NOT push unless "push" is explicitly stated.
- Always ask for confirmation or wait for explicit instruction before publishing any code to remote repositories.

## Network & API Architecture Policy: Hybrid Routing & Direct Backend Calls
- **Direct Backend Calls for Independent Workloads**: Frontend components and services (such as Socket.IO/WebSockets, WebRTC signaling, high-frequency telemetry, media uploads/recordings, and domain APIs) are permitted and encouraged to communicate directly with the backend server.
- **Backend CORS Management**: The FastAPI backend is configured to allow CORS requests originating from the production frontend (e.g. `https://airport-app-mocha.vercel.app`), local environments (`http://localhost:3000`), and Electron apps.
- **Production HTTPS & Security Compliance**: When deployed on Vercel (`https://`), direct backend endpoints must use valid `https://` URLs (via custom domain, SSL certificate, or cloud proxy) to ensure the browser does not block requests due to mixed content or SSL mismatch.
- **Local & Electron Environments**: For local development and Electron desktop kiosk applications, direct communication to `localhost`, LAN IP addresses, or configured remote URLs is fully supported.
