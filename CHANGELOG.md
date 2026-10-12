# Changelog

## 2026-10-11

- Add automatic dark mode that follows the visitor's system setting,
  with no toggle or JavaScript. daisyUI's `business` theme is paired
  with `bumblebee` as `--prefersdark`; `data-theme="bumblebee"` is
  removed from `<html>`, since it locked the page to light mode, and
  a `color-scheme` meta tag is added. In dark mode the ping button
  uses a darker navy primary instead of `business`'s orange accent
  (text 8.30:1 on the button), and `bumblebee`'s rounder corners
  replace `business`'s nearly square ones
  (`services/web/project/styles/app.css`, `templates/home.html`,
  `CLAUDE.md`).
- Build the CSS locally instead of loading Tailwind and daisyUI from
  jsDelivr at page load. The Docker builder stage downloads the
  Tailwind 4.3.3 standalone CLI (checked against per-architecture
  SHA-256s) and compiles `project/styles/app.css` into
  `project/assets/app.css`, which the final stage copies in and
  `home.html` loads from `/assets/app.css`. daisyUI 5.7.46 is vendored
  as `project/styles/daisyui-5.7.46.mjs` (SHA-256 checked against the
  release). This removes the runtime dependency on a third-party CDN,
  pins versions that were floating (`daisyui@5`,
  `@tailwindcss/browser@4`), and drops the in-browser Tailwind
  compiler. The built file is
  gitignored (`services/web/Dockerfile`, `.gitignore`,
  `services/web/project/styles/`, `templates/home.html`, `CLAUDE.md`).
  The untracked dev setup installs the same CLI and runs
  `tailwindcss --watch=always` next to Flask's debug server, as
  described in `CLAUDE.md`.
- Add `CLAUDE.md` with the commands, the dev/prod switching workflow,
  and an architecture overview, so AI assistants can work in the repo
  without rediscovering them.
- Expand `CLAUDE.md`: note that `to-dev.sh` and `to-prod.sh` are
  untracked too, so a fresh clone has no dev setup; add the dev run
  command and port 5000; list how the dev image differs from prod
  (no lint, `dnsutils`, runs as root); and explain that prod pings
  as non-root through unprivileged ICMP sockets, which rely on
  Docker's default `net.ipv4.ping_group_range` (the repo doesn't set
  it), so a failing host gets that sysctl (in the compose file, or on
  the host for rootless Docker) rather than `NET_RAW` or root.
- Update the copyright notice in `LICENSE` and `README.md` to
  `Copyright (c) 2025-2026 Greg Chetcuti <greg@chetcuti.com>`, covering
  the current year and adding a contact address.
- Fix the README install step to load `http://IP_ADDRESS:8102`. It
  said `https://` and port 8101 (ptr's port, likely copied from that
  repo); the app serves plain HTTP on 8102, matching
  `docker-compose.yml` and the live deployment.
- Fix a reflected XSS in the ping result. `check_ping()` built its
  messages with f-strings that put the user-supplied address straight
  into HTML, and `home.html` rendered them with `|safe`, so a URL like
  `/<img src=x onerror=alert(1)>` ran script. The messages now use
  `Markup(...).format(...)`, which escapes the address and resolved IP,
  and the template no longer needs `|safe`
  (`services/web/project/__init__.py`, `templates/home.html`).
- Fix an open redirect in `POST /`. `home()` returned
  `redirect("/" + address)`, so submitting `/evil.example` produced
  `Location: //evil.example`, which browsers follow to another site.
  The address is now URL-encoded with `quote(address, safe="")`, so
  the redirect always stays on this site
  (`services/web/project/__init__.py`).
- Stop pinging the visitor's own IP when they open `/`. `GET /`
  redirected straight to `/<visitor IP>`, and an IP that doesn't
  answer takes the full 5-second timeout, so the site seemed to freeze
  on the first visit. `GET /` now shows the form with the visitor's IP
  filled in and selected, so typing replaces it and pressing Enter
  pings it. An empty submit would now just reload the form with the
  visitor's IP, so the address field is `required` and the browser
  asks for an address instead. The loading spinner now starts from
  the form's `onsubmit` rather than the button's `onclick`, so it
  doesn't spin when the browser blocks an empty submit
  (`services/web/project/__init__.py`, `templates/home.html`).
- Upgrade Flask from 2.3.0 to 3.1.3 and pin `Werkzeug==3.1.8` in
  `services/web/requirements.txt`. Werkzeug was unpinned, so each
  image build pulled the newest release, and Flask 2.3.0 predates
  Werkzeug 3 (its test client crashed on the missing
  `werkzeug.__version__`). 3.1.8 is what the live container already
  runs, and Flask 3.1.3 supports it and Python 3.9.
- Use only the first address in `X-Forwarded-For` to find the
  visitor's IP. The whole header was used, so behind a chain of
  proxies a value like `203.0.113.8, 10.0.0.1` was treated as one
  address. An empty first entry now falls back to the connecting
  address; before, an empty header made `GET /` redirect to itself in
  a loop. The current Caddy setup sends a single address, so it isn't
  affected (`services/web/project/__init__.py`).
- Pin pip to 26.0.1 in both stages of `services/web/Dockerfile`.
  `pip install --upgrade pip` took whatever pip was newest, so
  identical commits could build with different toolchains. 26.0.1 is
  the last release that supports Python 3.9 and is what the live
  container already runs.
- Show a clear "IPv6 addresses aren't supported" message instead of
  "There was a problem". ping3 4.0.8 and `socket.gethostbyname()` are
  IPv4-only, and the container's Docker network has IPv6 disabled, so
  IPv6 pings could never succeed (`services/web/project/__init__.py`).
- Add `ACR.md` with the project's AI Code Rating, B1b (Maintainer:
  Experienced, AI Share: 1-25%, Oversight: Reviewed), and an ACR badge
  in `README.md`, so readers can see how much of the code AI wrote and
  how it was checked.
- Add this changelog.
