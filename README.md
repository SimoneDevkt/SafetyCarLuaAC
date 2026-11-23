# Race Control - Safety Car (CSP Online Script)

A **testing prototype** for Assetto Corsa race-control announcements:

| Admin action | Driver HUD | Driver audio |
| --- | --- | --- |
| **SC ON** | SAFETY CAR DEPLOYED | Rising alert (`sc_on.wav`) |
| **SC LIGHTS OFF** | SAFETY CAR LIGHTS OFF | Different falling alert (`sc_lights_off.wav`) |
| **GREEN FLAG** | GREEN FLAG - TRACK CLEAR | None |

The banner appears for about 5.5 seconds. After SC ON or SC LIGHTS OFF, a small SC indicator remains until GREEN FLAG.

## Prerequisites

- Assetto Corsa and compatible **Custom Shaders Patch (CSP)** on the driver PCs (CSP 0.2.5 or later is **recommended for testing**, not a verified minimum for this prototype).
- An Assetto Corsa Server Manager installation with **CSP Extra Options** enabled.
- A GitHub repository with **GitHub Pages** enabled under **Settings > Pages > Build and deployment > Source: GitHub Actions**.
- A race administrator who can access the admin tools in CSP's new chat interface.

## Publish to GitHub Pages

1. Create a GitHub repository (a public repository is the easiest setup for free Pages hosting).
2. Upload **all files and folders** from this project into the root of the repository, including the hidden `.github/workflows/deploy-pages.yml` file.
3. Set the default branch to **`main`**. This workflow deploys on pushes to `main`, or manually with **Actions > Deploy Race Control Assets to GitHub Pages > Run workflow**.
4. In the repository, open **Settings > Pages** and set **Source** to **GitHub Actions**.
5. Push a commit to `main`, or run the deployment workflow manually. Wait for GitHub Actions to report a successful deployment.
6. Open the GitHub Pages site. It will list the deployed script, both audio files, and a generated `extra_options.ini` file.

**No manual URL editing is needed.** During deployment, `scripts/build_site.py` reads the URL supplied by `actions/configure-pages`, injects it into the published `safetycar.lua`, and generates a CSP Extra Options snippet pointing to the correct script URL. This handles project Pages (`https://USERNAME.github.io/REPOSITORY`) and custom domains automatically.

Published URLs for this repository (a fork will get its own URLs, shown on its Pages site):

```text
https://simonedevkt.github.io/SafetyCarLuaAC/safetycar.lua
https://simonedevkt.github.io/SafetyCarLuaAC/sc_on.wav
https://simonedevkt.github.io/SafetyCarLuaAC/sc_lights_off.wav
https://simonedevkt.github.io/SafetyCarLuaAC/extra_options.ini
```

## Configure Emperor Servers / ACSM

1. Enable **Enable Extra Custom Shaders Patch Options** in the server settings (the exact label may vary by ACSM version).
2. Open your published **`extra_options.ini`** URL and copy its entire contents.
3. Paste the section into the race's **CSP Extra Options**; do not replace unrelated extra-options sections.
4. For an initial test, leave **`REQUIRED = 0`** so a script download failure does not block entry. Once tested, **`REQUIRED = 1`** can make the online script mandatory for compatible clients.
5. Save, restart the session if required by your server manager, and join with two CSP-equipped clients.
6. Log in as a server administrator, open CSP's **new chat app**, and find **Race Control - Safety Car** in its admin tools. Use the three actions and verify the result on the second client.

If your version of ACSM generates or manages the extra-options block automatically, use its own supported input area; avoid creating duplicate `[SCRIPT_RACE_CONTROL_SAFETY_CAR]` sections.

## Local preview build

You can verify the generated static files without deploying to GitHub:

```bash
python3 scripts/build_site.py --base-url https://example.github.io/race-control
python3 -m unittest discover -s tests -v
```

The `_site/` directory is created automatically and ignored by Git.

## Important limitations

- This is a **prototype that has not been tested in Assetto Corsa/CSP**. The exact CSP version needed for WAV playback, remote media fetching, and the HUD must be verified with real clients.
- Online Lua scripts execute on player clients. Drivers need compatible CSP, but this package is designed so they **do not manually install** the script or audio files.
- **CSP OnlineEvents are client-originated**, and the admin UI flag does not authenticate broadcasted events server-side. A malicious client may forge messages. For public/competitive use, add a server-authoritative plugin that verifies admin identity and owns race-control state.
- The current status exists only on connected clients. A driver joining after SC deployment might miss the current state until another announcement. Persisting/synchronizing state needs a server component or a vetted synchronization strategy.
- Alerts do not enforce speed limits, overtaking rules, safety-car vehicle behavior, or actual vehicle light states.
- Both WAVs are original simple tone signals. Playback depends on CSP's online script and audio support.
- GitHub Pages is **public web hosting**; do not include tokens, passwords, or private keys in the deployed files.

## Structure

```text
.github/workflows/deploy-pages.yml  GitHub Actions deployment workflow
site/index.html                   Landing page listing downloadable assets
site/safetycar.lua                CSP Online Lua script (base URL templated)
site/sc_on.wav                    Audio for SC deployed
site/sc_lights_off.wav            Audio for lights off
extra_options.example.ini         Manual configuration fallback
scripts/build_site.py             Static site build and URL injection
tests/test_build.py               Static build checks
.gitignore                        Ignore local build output
README.md                         Project setup and limitations
```

## References

- [CSP server extra options (online script configuration)](https://github-wiki-see.page/m/AssettoCN/acc-extension-config/wiki/Misc-%E2%80%93-Server-extra-options)
- [GitHub Pages custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Assetto Corsa Server Manager Wiki](https://wiki.emperorservers.com/en/assetto-corsa-server-manager)
