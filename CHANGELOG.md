# Changelog

## 2026-10-12

- Upgrade Python from 3.13 to 3.14 (`python:3.14.8-slim`), in both
  stages of the `Dockerfile`. 3.14.8 is an expedited security release
  (fixes for SSL and tarfile bugs, among others), and 3.14 gets bug
  fixes for longer than 3.13. Dependabot's PR #1
  proposed 3.14.7; this goes straight to 3.14.8 instead. All four
  pinned packages install on it (Flask 3.1.3, gunicorn 26.2.0, ping3
  5.1.6, Werkzeug 3.1.9). Tested in the production image: flake8 and
  the CSS build pass, the page and its assets load, public addresses
  reply, an unresponsive one times out after 5 seconds, and private,
  IPv6, and unresolvable addresses get their usual messages
  (`Dockerfile`, `CLAUDE.md:57`). The locally excluded
  `Dockerfile.DEV` isn't in the repo; it was moved to 3.14.8 by hand
  to match.
- Upgrade ping3 from 4.0.8 to 5.1.6. 5.0 added IPv6 pinging and 5.1
  IPv6 hop limits; the 5.1.x fixes match ICMP time-exceeded and
  destination-unreachable replies to the ping that was sent. `ping()`
  still returns the delay as a float, `None` on a timeout, and `False`
  on an error, and still falls back to an unprivileged datagram socket
  for the non-root user, so `check_ping()` needs no changes. The site
  stays IPv4-only, since `socket.gethostbyname()` only returns IPv4
  and the Docker network has IPv6 off; the code comment and
  `CLAUDE.md` now give those as the reasons instead of ping3. Tested
  in the production image: public addresses reply, an unresponsive
  one times out after 5 seconds, and private, documentation, and IPv6
  addresses are refused as before. Same change as Dependabot's PR #4,
  made here so it has a changelog entry (`requirements.txt`,
  `project/__init__.py:56`, `CLAUDE.md:49`).
- Upgrade Werkzeug from 3.1.8 to 3.1.9, the security release for
  GHSA-g6x2-hccm-hh4m (Dependabot alert #1, medium): `safe_join()`
  let Windows special device names through. That only matters on
  Windows, and the app runs in a Linux container, so it wasn't
  exposed. Werkzeug says the release fixes bugs but doesn't otherwise
  change behaviour. Same change as Dependabot's PR #3, made here so it
  has a changelog entry; Dependabot should close the PR once it sees
  the new pin, and if it doesn't, it can be closed by hand
  (`requirements.txt`).
- Add Dependabot version updates. Dependabot alerts and security fix
  PRs (set in the GitHub repo's settings, not in this file) only cover
  known vulnerabilities; nothing kept the pinned packages or the
  Python base image current otherwise. Dependabot now checks
  `requirements.txt` and the `Dockerfile`'s Python base image once a
  month, with all pip updates grouped into one PR. It only proposes
  versions that have been out for at least 7 days, so a bad or
  hijacked release has time to be caught and pulled first; security
  fix PRs aren't delayed. The versions pinned inside the
  `Dockerfile`'s build steps (pip, flake8, and the Tailwind CLI)
  aren't covered and still need updating by hand. GitHub Actions
  isn't included because the repo has no workflows
  (`.github/dependabot.yml`, new).

## 2026-10-11

- Refuse to ping addresses that aren't public. Any address the
  server could reach was pinged, including loopback, private,
  link-local, and CGNAT ranges, so a visitor could map which hosts
  on the server's own networks were up. The address is now resolved
  first and refused unless `ipaddress` counts it as global, and the
  ping goes to that resolved IP rather than the name, so a second
  DNS lookup can't swap in a private address
  (`project/__init__.py`).
- Remove jQuery. It was only used to show the loading spinner on
  submit, which a line of inline JavaScript now does, so every page
  load skips an 87 KB script (`templates/home.html`,
  `assets/jquery-3.7.1.min.js`).
- Remove `FLASK_ENV=production` from `docker-compose.yml`. Flask
  2.3 removed `FLASK_ENV`, so the setting did nothing.
- Upgrade gunicorn from 20.1.0 to 26.2.0. 20.1.0 dates from 2021 and
  misses the request-smuggling fixes in 22.0 and 23.0, which matter
  for an app behind a reverse proxy (`requirements.txt`).
- Upgrade Python from 3.9 to 3.13 (`python:3.13.16-slim`). 3.9
  reached end of life in October 2025 and no longer gets security
  fixes, and gunicorn 24+ needs Python 3.10 or later (`Dockerfile`).
- Run gunicorn with 2 workers and 4 threads each. With the default
  single sync worker, one ping to an unresponsive address held the
  only worker for the full 5-second timeout, so every other visitor
  waited behind it. `--no-control-socket` turns off the unused
  control socket gunicorn 25.1+ creates by default, which would go
  under the `app` user's home directory, a directory it doesn't own
  (`docker-compose.yml`).
- Show the round-trip time in milliseconds to two decimal places
  (`9.93 ms`) instead of seconds to twenty (`0.00993...`). The
  `try/except` around the formatting could never fail and is gone,
  and a reply is now recognised by `ping3.ping()` returning a float,
  so a 0.0 delay no longer counts as no reply
  (`project/__init__.py`).
- Add `<!doctype html>`, `lang="en"`, and a viewport meta tag, and
  remove three classes that did nothing. Without a doctype the browser
  rendered the page in quirks mode, which Tailwind's base styles don't
  expect; without `lang` screen readers had to guess the language; and
  without a viewport tag phones showed a zoomed-out desktop layout.
  `form` and `loading-circle` aren't daisyUI classes and
  `justify-left` isn't a Tailwind class (it's `justify-start`), so
  none of them was in the built CSS (`templates/home.html`,
  `CLAUDE.md`).
- Update the AI Code Rating from B1b to B2b. With the CSS build,
  dark mode, and input label, AI-written lines are about a third of
  the code (80 of 243 lines; the vendored daisyUI and jQuery files
  don't count), which moves the AI Share from 1–25% to 26–50%
  (`ACR.md`, `README.md` badge).
- Add `aria-label="Address"` to the address input, so screen readers
  announce the field by name instead of relying on the placeholder,
  which isn't a reliable accessible name and disappears once the
  field has a value (`templates/home.html`).
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
