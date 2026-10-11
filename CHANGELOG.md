# Changelog

## 2026-10-11

- Add `CLAUDE.md` with the commands, the dev/prod switching workflow,
  and an architecture overview, so AI assistants can work in the repo
  without rediscovering them.
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
