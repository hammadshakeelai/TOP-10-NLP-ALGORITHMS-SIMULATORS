# Backend-Free Static Deployment

The frontend can be built as a self-contained static site with no FastAPI
backend, no Python, and no network calls at all. This is what gets published to
GitHub Pages.

## How it works

Every algorithm ships a pre-computed snapshot under `apps/web-ui/src/mocks/`:

- `catalog.json` — the 13-entry algorithm catalog
- `demos/<id>.json` — demo metadata per algorithm
- `runs/<id>.json` — a full reference run (traces, visualizations, warnings)

`apps/web-ui/src/api/client.ts` has two backend-free modes:

| Mode | Trigger | Behaviour |
|---|---|---|
| **static** | `VITE_STATIC_MODE=true` at build time | No request is ever attempted. The UI reads snapshots directly and shows a "Static demo" badge. |
| **offline** | A live backend was expected but is unreachable | Same snapshots, but the user gets a one-time toast explaining the backend is down. |

The distinction matters: without static mode a deployed site would fire a
doomed request at `http://localhost:8000`, wait for it to fail, and greet every
visitor with an "API unreachable" toast.

### Limitation

In static mode, custom input **replays the pre-computed reference run** for that
algorithm rather than simulating the text you typed. Each result carries a
`STATIC_MODE` warning saying so. Run the platform locally with the backend
(see `docs/RUNBOOK.md`) to simulate your own inputs.

## Build-time environment variables

| Variable | Default | Purpose |
|---|---|---|
| `VITE_STATIC_MODE` | unset (live) | `"true"` builds the backend-free bundle. |
| `VITE_BASE_PATH` | `/` | Sub-path the site is served from. GitHub Pages project sites need `/<repo>/`. |
| `VITE_API_URL` | `http://localhost:8000` | Gateway URL. Ignored when static mode is on. |

Leaving all three unset produces the normal backend-connected build, so local
development is unchanged. See `apps/web-ui/.env.example`.

## Build it locally

PowerShell:

```powershell
cd apps/web-ui
$env:VITE_STATIC_MODE = "true"
$env:VITE_BASE_PATH = "/TOP-10-NLP-ALGORITHMS-SIMULATORS/"
npm run build
```

> On Git Bash, setting `VITE_BASE_PATH=/TOP-10-.../` inline gets mangled by MSYS
> path conversion into `/Program Files/Git/TOP-10-.../`. Use PowerShell, or
> prefix the command with `MSYS_NO_PATHCONV=1`.

The build always writes two extra files, on every host:

- `dist/404.html` — a copy of `index.html`, so deep links like
  `/simulate/tfidf` render instead of hitting a bare Pages 404
- `dist/.nojekyll` — stops Pages running Jekyll over the output

Deep links return an HTTP **404 status** while serving the app shell. Users see
the correct page; crawlers see a 404. Switching `BrowserRouter` to `HashRouter`
would give clean 200s at the cost of `#/`-style URLs.

## GitHub Pages

Already set up and live:

**https://hammadshakeelai.github.io/TOP-10-NLP-ALGORITHMS-SIMULATORS/**

`.github/workflows/deploy-pages.yml` builds and publishes on every push to
`main` that touches `apps/web-ui/**`, and on manual dispatch
(`gh workflow run deploy-pages.yml --ref main`).

The repository deliberately keeps **one branch**. Pages deploys from `main`
alone, so a second long-lived branch would mean whichever pushed last won the
deployment.

Pages is configured with `build_type: workflow`. If it ever needs re-enabling:

```powershell
gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow
```

or **Settings → Pages → Build and deployment → Source: GitHub Actions**.
Without it the workflow fails at `configure-pages` with "Get Pages site failed".

## CI must run Node 24

`npm ci` fails on Node 20 with `Missing: yaml@2.9.0 from lock file`. `yaml@2`
is an *optional peer* of `postcss-load-config`; npm 11 omits it from the
lockfile and npm 10 (bundled with Node 20) demands it. Any new workflow that
runs `npm ci` needs `node-version: 24`.

## Other hosts

Vercel and Netlify serve from the root, so they need `VITE_STATIC_MODE=true`
only — leave `VITE_BASE_PATH` unset. Both hosts ignore `404.html` and
`.nojekyll`; the build still emits them, harmlessly. Netlify needs a
`public/_redirects` containing `/* /index.html 200` for deep links, and Vercel
rewrites SPA routes on its own.
