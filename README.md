# Tweeter - A Twitter Clone

A full-featured Twitter clone built with Django. Users can sign up, create posts ("Twits"), like and comment on others' posts, and manage their profiles -- all styled with Bootstrap 5.

## Overview

Tweeter is a social media web app inspired by Twitter. It's built entirely with Django class-based views and follows a two-app architecture:

- **accounts** - Handles user registration, authentication, and profile management using a custom user model that extends Django's `AbstractUser`.
- **tweeter** - The core social functionality: creating/editing/deleting Twits, commenting, and liking.

Users land on a home page and are prompted to sign up or log in. Once authenticated, they can browse a dashboard feed of all Twits (newest first), create their own Twits with text and optional image URLs, like/unlike posts via AJAX, and leave comments. Each user has a private profile they can edit and a public profile page that displays all of their Twits.

### How It Works

- **Authentication** is handled through Django's built-in auth system with custom sign-up and profile forms rendered using crispy-forms. Password reset works via SMTP email.
- **Twits** are created, updated, and deleted through class-based views (`CreateView`, `UpdateView`, `DeleteView`). Edit and delete actions are restricted to the Twit's author using `UserPassesTestMixin`.
- **Comments** use a compound view pattern -- `TwitDetailView` dispatches GET requests to render the Twit with its comments, and POST requests to handle comment form submissions.
- **Likes** are implemented as a `ManyToManyField` on the Twit model. The like button sends an AJAX GET request (via jQuery) to a toggle endpoint, which adds or removes the user from the relationship and returns JSON. The UI updates the button style, icon, and count without a page reload.
- **Profiles** come in two flavors: `ProfileDetailView` shows the logged-in user their own info, while `PublicProfileView` displays any user's profile along with all their Twits in reverse chronological order.

## Features

- **User Authentication** - Sign up, login, password change and reset via email
- **Custom User Model** - Extended with date of birth and profile details
- **Twits** - Create, edit, and delete posts with text and image URLs
- **Likes** - Like/unlike Twits with AJAX (no page reload)
- **Comments** - Add comments on any Twit (140 character limit)
- **Profiles** - Private profile editing and public profile pages showing a user's Twits
- **Dashboard** - Feed of all Twits, newest first
- **Authorization** - Only Twit authors can edit or delete their own posts

## Development Progression

1. **Project Initialization**
   - Created Django project (`django_project/`) and two apps: `accounts/` and `tweeter/`
   - Configured `settings.py` with custom user model, crispy-forms, and Bootstrap 5 template pack
   - Set up root URL routing in `django_project/urls.py`

2. **Custom User Model**
   - Defined `CustomUser` in `accounts/models.py`, extending `AbstractUser` with a `date_of_birth` DateField
   - Created `CustomUserCreationForm` and `CustomUserChangeForm` in `accounts/forms.py`
   - Registered the custom model in `accounts/admin.py` with `CustomUserAdmin`

3. **Database Models**
   - Defined `Twit` model in `tweeter/models.py` with `author` (ForeignKey), `body` (TextField), `image_url` (URLField), `likes` (ManyToManyField), and `created`/`updated` timestamps
   - Defined `Comment` model with `twit` (ForeignKey to Twit), `author` (ForeignKey to CustomUser), and a 140-character `body`
   - Added `__str__()`, `get_absolute_url()`, and `get_like_url()` methods to models

4. **User Authentication**
   - Built `SignUpView` (CreateView) in `accounts/views.py` with the custom creation form
   - Created `signup.html` and `login.html` templates with crispy-form rendering
   - Configured `LOGIN_REDIRECT_URL` and `LOGOUT_REDIRECT_URL` in `settings.py`

5. **Password Management**
   - Integrated Django's built-in password change and reset views via `django.contrib.auth.urls`
   - Created templates: `password_change_form.html`, `password_change_done.html`, `password_reset_form.html`, `password_reset_done.html`, `password_reset_confirm.html`, `password_reset_complete.html`
   - Configured SMTP email backend in `settings.py` for sending reset emails

6. **Twit CRUD**
   - Built `TwitListView` (ListView) and `TwitCreateView` (CreateView) in `tweeter/views.py`, auto-assigning `request.user` as author via `form_valid()`
   - Built `TwitUpdateView` (UpdateView) and `TwitDeleteView` (DeleteView) with `UserPassesTestMixin` to restrict actions to the Twit's author
   - Created templates: `twit_list.html`, `twit_create.html`, `twit_update.html`, `twit_delete.html`
   - Wired up URL patterns in `tweeter/urls.py` (`/twits/`, `/twits/new/`, `/twits/<pk>/edit/`, `/twits/<pk>/delete/`)

7. **Comment System**
   - Created `CommentForm` (ModelForm) in `tweeter/forms.py` with a single `body` field
   - Built a compound `TwitDetailView` in `tweeter/views.py` that dispatches GET to `CommentGetView` (DetailView) and POST to `CommentPostView` (FormView + SingleObjectMixin)
   - `CommentPostView.form_valid()` uses `commit=False` to attach the `twit` and `author` before saving
   - Created `twit_detail.html` to display the Twit, its comments, and the comment form

8. **Like System with AJAX**
   - Added `TwitLikeView` in `tweeter/views.py` — a toggle endpoint that adds/removes the user from the Twit's `likes` ManyToMany field and returns `{"success": true}` as JSON
   - Wrote `static/js/base.js` with jQuery click handler on `.like_button` elements that sends an AJAX GET request, then updates the button style, icon, and like count without a page reload

9. **User Profiles**
   - Built `ProfileDetailView` (DetailView) and `ProfileUpdateView` (UpdateView) in `accounts/views.py` for viewing/editing the logged-in user's own profile
   - Built `PublicProfileView` (DetailView) with overridden `get_context_data()` to include all of a user's Twits in reverse chronological order
   - Created `profile_detail.html`, `profile_update.html`, and `public_profile.html` templates
   - Added URL patterns in `accounts/urls.py` (`/profile/`, `/profile/update/`, `/public_profile/<pk>/`)

10. **Automated Tests**
    - Wrote `ProfilePageTests` and `SignupPageTests` in `accounts/tests.py` covering profile access, redirects for unauthenticated users, sign-up with all custom fields
    - Wrote `TwitTests` in `tweeter/tests.py` covering model creation, `__str__` output, comment relationships, like toggling, list/detail view rendering, comment posting, and 403 responses on unauthorized edit/delete

11. **Deployment Prep**
    - Configured WhiteNoise middleware and `CompressedManifestStaticFilesStorage` in `settings.py` for production static file serving
    - Added `Procfile` (Gunicorn), `runtime.txt` (Python 3.13), and environment variable config via `python-dotenv`
    - Set `ALLOWED_HOSTS` for both localhost and production

## Database ERD

![Database Entity Relationship Diagram](https://barnesbrothers.net/cis218/assignment_images/assignment_4/cis218_assignment_4_erd.png "Database Entity Relationship Diagram")

### Models

- **CustomUser** - Extends `AbstractUser` with an optional `date_of_birth` field.
- **Twit** - A post with `body`, optional `image_url`, timestamps, an `author` foreign key, and a `likes` many-to-many relationship to users.
- **Comment** - Linked to a Twit and an author, with a 140-character `body` and timestamps.

## Project Structure

```
Tweeter/
├── accounts/          # Custom user model, auth views, profile views
├── tweeter/           # Twit/Comment models, CRUD views, like endpoint
├── django_project/    # Settings, root URL config, WSGI/ASGI
├── templates/         # All HTML templates (base, home, twits, profiles, auth)
├── static/js/         # AJAX like functionality (jQuery)
├── manage.py
├── requirements.txt
└── Procfile           # Gunicorn config for deployment
```

## Tech Stack

- Python 3.13
- Django 4.2
- Bootstrap 5 (via django-crispy-forms)
- jQuery (AJAX like functionality)
- WhiteNoise (static file serving)
- SQLite (default) / PostgreSQL (production)
- Gunicorn (WSGI server)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ArriZa-Wi/Tweeter_Twitter_Clone.git
   cd Tweeter_Twitter_Clone
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file (see `.env.example` for reference):
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   ```

4. Run migrations and start the server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

5. Visit `http://127.0.0.1:8000/` and create an account to get started.

## Running Tests

```bash
python manage.py test
```

Tests cover user profile access, sign-up with custom fields, Twit CRUD operations, comment posting, like/unlike toggling, and permission enforcement (403 on unauthorized edit/delete).
