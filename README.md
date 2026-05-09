# Anteritus · 전생

Past-life reading + soul network — single-page app, served as a static site behind nginx.

## Local

Just open `index.html` in a browser, or run any static server.

## Deploy (GCP Cloud Run via Cloud Build)

```sh
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_REGION=asia-northeast3,_REPO=anteritus,_SERVICE=anteritus
```

The build:
1. Builds the nginx image (Dockerfile + nginx.conf + index.html).
2. Pushes to Artifact Registry (`<region>-docker.pkg.dev/<project>/anteritus/anteritus`).
3. Deploys to Cloud Run as a public service on port 8080.

## Stack
- nginx 1.27-alpine, gzip on text payloads
- Single HTML file (`index.html`); browser-side JS only
- localStorage persists `souls[]` and `bonds[]`
