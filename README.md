# Amazon DSP Program Manager — Mock Interview Studio (Hostable Version)
A self-contained, single-page web app for rehearsing your Amazon interview. It records
your spoken answers, times them, shows STAR structure + tailored talking points +
model answers, and lets you self-score against the Amazon bar-raiser rubric.
Everything is stored **locally in your browser** (localStorage) — nothing is uploaded.
## What's in this folder
| File | Purpose |
|------|---------|
| `index.html` | The entire app. This is the only file that actually matters. |
| `staticwebapp.config.json` | Config for **Azure Static Web Apps** (sets microphone permission + 
routing). |
| `netlify.toml` | Config for **Netlify** (sets microphone permission). |
| `.nojekyll` | Tells **GitHub Pages** to serve files as-is. |
| `README.md` | This file. |
> ⚠️ **Why hosting matters:** browsers only grant microphone access on pages served
> over **https://** (or from `localhost`). Opening `index.html` by double-clicking it
> (a `file://` path) will block recording. Any of the options below fixes that.--
## Option A — GitHub Pages (free, ~5 min, easiest to share a link)
1. Create a free account at github.com, then create a new **public** repository, e.g. `mock-interview`.
2. Click **Add file → Upload files**, drag in **all** the files from this folder
 (including the hidden `.nojekyll`), and commit.
3. Go to **Settings → Pages**. Under *Build and deployment → Source*, choose **Deploy from a branch**,
 pick branch **main** and folder **/ (root)**, and **Save**.
4. Wait ~1 minute. Your live app will be at:
 `https://<your-username>.github.io/mock-interview/`
5. Open that URL, allow the microphone when prompted, and you're recording.
## Option B — Netlify (free, drag-and-drop, no Git needed)
1. Go to app.netlify.com and sign up (free).
2. On the **Sites** page, drag this **entire folder** onto the "deploy" drop zone.
3. Netlify gives you a live `https://random-name.netlify.app` URL instantly.
4. (Optional) Rename the site under **Site settings → Change site name**.
## Option C — Azure Static Web Apps (best if you want it in your Microsoft tenant)
1. Push this folder to a GitHub repo (see Option A steps 1–2).
2. In the Azure Portal, create a **Static Web App** → **Free** plan.
3. Connect it to your GitHub repo. For build settings choose:
 - **App location:** `/`
 - **Api location:** *(leave blank)*
 - **Output location:** *(leave blank)*
4. Azure builds and gives you a live `https://<name>.azurestaticapps.net` URL.
 The included `staticwebapp.config.json` already enables microphone access.
## Option D — Run locally for a quick test (no hosting)
From inside this folder, run one of these, then open the printed URL:
```bash
# Python (already on most machines)
python -m http.server 8000
# then open http://localhost:8000
# or Node
npx serve .
```
`localhost` counts as a secure origin, so the microphone works.--
## Embedding in SharePoint / a Teams tab
Once it's live at an `https://` URL (Options A–C), you can embed it:
**SharePoint page:** Edit page → add the **Embed** web part → paste:
```html
<iframe src="https://YOUR-LIVE-URL/" width="100%" height="900"
```
 allow="microphone" style="border:0"></iframe>
The `allow="microphone"` attribute is required or recording is blocked inside the frame.
**Teams:** Add a **Website** tab and point it at your live URL.
--
## Privacy note
All recordings, scores, and notes live only in *your* browser's localStorage on the
device you use. They are never sent anywhere. Clearing your browser data — or clicking
**Reset session** in the app — erases them. If you deploy publicly, anyone with the link
can *use* the practice tool, but they cannot see *your* saved recordings
