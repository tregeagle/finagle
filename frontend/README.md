# Finagle Frontend

React SPA for the Finagle personal finance & CGT tracker.

## Tech Stack

- React 19 + TypeScript (Vite)
- Tailwind CSS v4
- React Router

## Setup

```bash
npm install
npm run dev
```

Dev server runs at http://localhost:5173 and expects the backend at http://localhost:8000.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |
| `VITE_API_KEY` | API key (must match `FINAGLE_API_KEY` on backend) | _(empty)_ |

Example:

```bash
VITE_API_KEY=your-key VITE_API_URL=https://api.example.com/api/v1 npm run dev
```

## Production Build

```bash
VITE_API_KEY=your-key VITE_API_URL=https://api.example.com/api/v1 npm run build
```

Outputs static files to `dist/` for deployment to any static hosting (Netlify, Vercel, Cloudflare Pages, etc.).
