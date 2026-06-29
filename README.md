# px-sandbox-android

A sandbox of small Android apps. On every push to `main`, GitHub Actions
builds an APK for each app and publishes a GitHub Pages site listing them
all for download.

## Layout

```
apps/
  hello-world/        # one Gradle module per app
    app-info.json     # name / description shown on the download page
    build.gradle.kts
    src/...
scripts/
  generate_site.py    # builds index.html from the compiled APKs
.github/workflows/
  build-and-deploy.yml
```

## Adding a new app

1. Create a new folder under `apps/<your-app>/` containing an Android
   application Gradle module (`build.gradle.kts` applying
   `com.android.application`).
2. Add an `app-info.json` with `name`, `description` and `package`.

That's it — `settings.gradle.kts` auto-includes every app folder, the
workflow builds them all with `./gradlew assembleDebug`, and
`generate_site.py` lists every produced APK on the download page.

## Building locally

```bash
./gradlew assembleDebug
python3 scripts/generate_site.py --apps-dir apps --output-dir site
# open site/index.html
```

## GitHub Pages setup

In the repository settings, set **Pages → Build and deployment → Source**
to **GitHub Actions**. The `build-and-deploy.yml` workflow does the rest.
