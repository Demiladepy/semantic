# Deploy to Streamlit Cloud

## Prerequisites
1. GitHub account
2. Repository pushed to GitHub (public)
3. Streamlit Cloud account (free at share.streamlit.io)

## Deployment Steps

### Step 1: Push Code to GitHub

Make sure these files are committed:
```bash
git add dashboard.py
git add requirements-dashboard.txt
git add .streamlit/config.toml
git commit -m "Add Streamlit dashboard for PNP demo"
git push origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository**: `Demiladepy/semantic` (your repo)
   - **Branch**: `main`
   - **Main file path**: `dashboard.py`
5. Click **"Advanced settings"**
   - Under **Python version**, select `3.11`
   - Under **Secrets**, leave empty (no secrets needed)
6. For **Custom subdomain**, enter: `pnp-ai-agent`
7. Click **"Deploy!"**

### Step 3: Custom Requirements (Important!)

By default, Streamlit Cloud uses `requirements.txt`. To use minimal dependencies:

**Option A: Rename files**
```bash
mv requirements.txt requirements-full.txt
mv requirements-dashboard.txt requirements.txt
git add .
git commit -m "Use minimal requirements for Streamlit Cloud"
git push
```

**Option B: Create packages.txt** (if system dependencies needed)
Not required for this dashboard.

### Step 4: Verify Deployment

After deployment, your app will be available at:
```
https://pnp-ai-agent.streamlit.app
```

Or similar URL assigned by Streamlit Cloud.

## Troubleshooting

### "Module not found" errors
- The dashboard only needs: `streamlit`, `plotly`, `pandas`, `numpy`
- Make sure `requirements.txt` contains only these

### App crashes on load
- Check Streamlit Cloud logs (click "Manage app" > "Logs")
- Usually a dependency issue

### App loads but shows errors
- Check browser console for JavaScript errors
- May be a Plotly version issue

## Local Testing

Run locally before deploying:
```bash
python -m streamlit run dashboard.py
```

Then visit: http://localhost:8501

## Dashboard Features

The deployed dashboard shows:
- **AI Agent Tab**: Create markets from prompts
- **Privacy Tokens Tab**: ELUSIV, LIGHT, PNP collateral info
- **Markets Tab**: Active markets and charts
- **Activity Log**: Agent operations

## URL to Share with Judges

Once deployed, share this URL:
```
https://pnp-ai-agent.streamlit.app
```

This gives judges a live, interactive demo without needing to run any code!
