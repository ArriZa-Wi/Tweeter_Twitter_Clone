# Tweeter - A Twitter Clone

A Django-based microblog inspired by Twitter, restyled with a dark "coder" theme and powered by [htmx](https://htmx.org) for SPA-style interactivity. Users can sign up, post Twits (with Markdown + syntax-highlighted code blocks), like, comment, and manage their profiles — all without full page reloads.

> [!NOTE]
> This repo only has a single original commit because the project was developed as a final project for a class, hosted on a private GitHub organization. This is a clean copy brought over to my personal GitHub, with a styling and interactivity overhaul on top.

## Overview

Tweeter is a social media web app inspired by Twitter, built entirely with Django class-based views. It has a two-app architecture:

- **accounts** - User registration, authentication, profile management. Uses a custom user model extending Django's `AbstractUser`.
- **tweeter** - Core social functionality: creating/editing/deleting Twits, comments, likes.

After logging in users land on a dashboard feed showing all Twits (newest first), with an inline composer at the top, live character counter, Markdown rendering, code-block syntax highlighting, animated like counts, toast notifications, and an SPA-style flow where every action swaps a partial fragment in place rather than reloading the page.

### How It Works

- **Server-rendered partials with htmx** - Every mutating action (create/edit/delete a Twit, like, comment) hits a regular Django view that, when called from htmx, returns just the relevant HTML fragment (`partials/_twit_card.html`, `partials/_comment.html`). The browser swaps it into place. When called from a vanilla form submit, the same view returns a normal redirect, so the site degrades gracefully without JavaScript.
- **`HX-Trigger` events** drive client-side UI updates — e.g. on like, the server returns an empty body and an `HX-Trigger: {"twit:liked": {...}}` header which the client uses to animate the count (CountUp.js) and fire a particle burst.
- **Markdown + Prism** - Tweet bodies are rendered through `marked → DOMPurify → Prism.highlightAllUnder` so users can post fenced code blocks (```` ```python `, ```` ```c `, etc.) and they show up syntax-highlighted in the GitHub-dark palette.
- **Alpine.js** handles small client-side state (dropdown menu, char counter, CRT-mode toggle persisted in `localStorage`).
- **NProgress** shows a green top progress bar tied to htmx requests; **Notyf** fires toast notifications when an `HX-Trigger` event arrives.

## Features

- **User Authentication** - Sign up, login, password change and reset via email
- **Custom User Model** - Extended with date of birth and profile fields
- **Twits with Markdown** - Create, edit, delete posts with text, optional image URL, and fenced code blocks
- **htmx everywhere** - Like, comment, post, and delete all swap partials without full reloads
- **Animated like counts** with CountUp.js + particle burst on click
- **Toast notifications** on every successful action
- **CRT scanline mode** toggleable from the user menu (persisted to `localStorage`)
- **Dark coder theme** - JetBrains Mono + Inter, GitHub-dark palette, neon accents, blinking caret logo
- **Comments** - 140 char limit, posted inline via htmx
- **Profiles** - Private profile editing and public profile pages
- **Authorization** - Only Twit authors can edit or delete their own posts
- **Graceful degradation** - Every htmx flow has a non-JS fallback path

## Tech Stack

- Python 3.13
- Django 4.2
- [htmx 2.0](https://htmx.org) + [django-htmx](https://django-htmx.readthedocs.io)
- [Alpine.js 3](https://alpinejs.dev) for client-side state
- [marked](https://marked.js.org) + [DOMPurify](https://github.com/cure53/DOMPurify) for safe Markdown
- [Prism.js](https://prismjs.com) for code syntax highlighting
- [Notyf](https://carlosroso.com/notyf/), [CountUp.js](https://inorganik.github.io/countUp.js/), [NProgress](https://ricostacruz.com/nprogress/) for micro-interactions
- WhiteNoise (static file serving)
- SQLite (default) / PostgreSQL (production)
- Gunicorn (WSGI server)

No npm/build step — every frontend library is loaded via CDN. Custom CSS lives in `static/css/`.

## Project Structure

```
Tweeter/
├── accounts/                  # Custom user model, auth views, profile views
├── tweeter/                   # Twit/Comment models, htmx-aware views, like endpoint
├── django_project/            # Settings, root URL config, WSGI/ASGI
├── templates/
│   ├── base.html              # Master layout (htmx, Alpine, Prism, etc.)
│   ├── partials/
│   │   ├── _twit_card.html    # Single tweet card (rendered standalone for htmx swaps)
│   │   └── _comment.html      # Single comment row
│   ├── home.html, twit_list.html, twit_detail.html, ...
│   └── registration/          # Auth templates
├── static/
│   ├── css/
│   │   ├── theme.css          # Design tokens + components (dark coder theme)
│   │   └── animations.css     # Keyframes (slide-in, heart-pop, particle burst)
│   └── js/
│       └── app.js             # Markdown rendering, NProgress/Notyf wiring, like animations
├── seed_data.py               # Populate the DB with demo users, twits, comments
├── manage.py
├── requirements.txt
└── Procfile                   # Gunicorn config for deployment
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ArriZa-Wi/Tweeter_Twitter_Clone.git
   cd Tweeter_Twitter_Clone
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   # source .venv/bin/activate     # macOS / Linux
   pip install -r requirements.txt
   ```

3. Create a `.env` file (see `.env.example`):
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ```

   > Note: a `DATABASE_URL` env var is **optional**. If unset, the app falls back to a local SQLite file at `db.sqlite3`. If you do set it, make sure it's a valid URL (e.g. `postgres://user:pass@host:5432/dbname`). If your shell has a leftover `DATABASE_URL` set globally (some Anaconda installs do), unset it before running the server or override it in `.env`.

4. Run migrations and start the server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Visit `http://127.0.0.1:8000/` and create an account.

### (Optional) Seed demo data

Populate the DB with 6 demo users, 15 Twits (including some with images and fenced code blocks), and a bunch of comments — useful for screenshots or demos:

```bash
python seed_data.py
```

All demo accounts use password `password123`. Usernames: `ada`, `torvalds`, `grace`, `dhh`, `guido`, `antirez`.

## Running Tests

```bash
python manage.py test
```

Tests cover user profile access, sign-up with custom fields, Twit CRUD operations, comment posting, like/unlike toggling, and permission enforcement (403 on unauthorized edit/delete).

## Database ERD

![Database Entity Relationship Diagram](https://barnesbrothers.net/cis218/assignment_images/assignment_4/cis218_assignment_4_erd.png "Database Entity Relationship Diagram")

### Models

- **CustomUser** - Extends `AbstractUser` with an optional `date_of_birth` field.
- **Twit** - A post with `body`, optional `image_url`, timestamps, an `author` foreign key, and a `likes` many-to-many relationship to users.
- **Comment** - Linked to a Twit and an author, with a 140-character `body` and timestamps.

## Original Development Progression

The original class project (Bootstrap + jQuery version) followed this build order. The current code on `main` includes the dark-theme / htmx overhaul layered on top.

1. **Project Initialization** — Created Django project (`django_project/`) and two apps: `accounts/` and `tweeter/`. Configured `settings.py` with custom user model, crispy-forms, and Bootstrap 5 template pack.
2. **Custom User Model** — Defined `CustomUser` extending `AbstractUser` with a `date_of_birth` field. Created `CustomUserCreationForm` / `CustomUserChangeForm`. Registered in admin.
3. **Database Models** — Defined `Twit` (author, body, image_url, likes, timestamps) and `Comment` (twit, author, 140-char body) with `__str__`, `get_absolute_url`, `get_like_url`.
4. **User Authentication** — Built `SignUpView` with crispy-form templates. Configured `LOGIN_REDIRECT_URL` / `LOGOUT_REDIRECT_URL`.
5. **Password Management** — Integrated Django's built-in password change/reset views. Created all six registration templates. Configured SMTP email backend.
6. **Twit CRUD** — Built `TwitListView`, `TwitCreateView`, `TwitUpdateView`, `TwitDeleteView` with `UserPassesTestMixin` for ownership checks.
7. **Comment System** — Created `CommentForm` and a compound `TwitDetailView` that dispatches GET to `CommentGetView` (DetailView) and POST to `CommentPostView` (FormView + SingleObjectMixin).
8. **Like System with AJAX (original)** — `TwitLikeView` returned JSON; `static/js/base.js` used jQuery to toggle the button and count. *(Both replaced in the modernization pass — see below.)*
9. **User Profiles** — `ProfileDetailView`, `ProfileUpdateView`, `PublicProfileView` with templates.
10. **Automated Tests** — `accounts/tests.py` and `tweeter/tests.py`.
11. **Deployment Prep** — WhiteNoise + `CompressedManifestStaticFilesStorage`, `Procfile`, `runtime.txt`, env config via `python-dotenv`.

## Modernization Pass (Dark Theme + htmx Interactivity)

After the class submission, the site was rebuilt around a dark "coder" aesthetic and a partial-rendering interaction model:

- **Stripped Bootstrap and jQuery** — replaced with a custom CSS design system (`static/css/theme.css`, `static/css/animations.css`) using GitHub-dark colors, JetBrains Mono + Inter fonts, neon accents, and a blinking caret logo.
- **Added htmx + django-htmx** — every mutating view (`TwitCreate/Update/Delete`, `Comment`, `TwitLike`) now returns a rendered partial fragment when `request.htmx` is true, along with an `HX-Trigger` header that the client uses to fire toasts and animations. The same views still serve normal full-page responses for the JS-disabled path.
- **Created partial templates** — `templates/partials/_twit_card.html` and `_comment.html` so the feed and detail views share rendering logic with htmx responses.
- **Added Alpine.js** for local state (user dropdown menu, live character counter on the composer, CRT-mode toggle persisted to `localStorage`).
- **Added Markdown + syntax highlighting** — tweet bodies render through `marked → DOMPurify → Prism.highlightAllUnder`, so fenced code blocks display with Prism's "Tomorrow Night" palette.
- **Added animation libraries** — CountUp.js animates like counts, NProgress shows a green progress bar at the top of the page during htmx requests, Notyf fires top-right toast notifications for every successful action.
- **CSS-only particle burst** when a tweet is liked (five particles fly outward in randomized directions, no JS library needed).

## Demo Accounts

After running `python seed_data.py`, you can sign in as any of:

| Username   | Password      |
|------------|---------------|
| `ada`      | `password123` |
| `torvalds` | `password123` |
| `grace`    | `password123` |
| `dhh`      | `password123` |
| `guido`    | `password123` |
| `antirez`  | `password123` |
