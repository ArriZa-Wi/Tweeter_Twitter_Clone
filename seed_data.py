"""Seed dummy data for screenshots. Run with: python seed_data.py"""
import os
import random
import django
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
django.setup()

from django.utils import timezone
from accounts.models import CustomUser
from tweeter.models import Twit, Comment

USERS = [
    ("ada",       "Ada",       "Lovelace",  "ada@tweeter.dev"),
    ("torvalds",  "Linus",     "Torvalds",  "linus@tweeter.dev"),
    ("grace",     "Grace",     "Hopper",    "grace@tweeter.dev"),
    ("dhh",       "David",     "Heinemeier","dhh@tweeter.dev"),
    ("guido",     "Guido",     "van Rossum","guido@tweeter.dev"),
    ("antirez",   "Salvatore", "Sanfilippo","antirez@tweeter.dev"),
]

TWITS = [
    {
        "author": "ada",
        "body": "first commit on a new project. clean `git init`, fresh repo smell. nothing beats it.",
    },
    {
        "author": "torvalds",
        "body": "spent 3 hours debugging only to find a missing semicolon. classic.\n\n```c\nfor (int i = 0; i < n; i++)\n    printf(\"%d\\n\", arr[i]);\n```\n\nthe fix was satisfying though.",
    },
    {
        "author": "grace",
        "body": "**hot take:** the best programming language is the one your team can actually maintain at 3am during an incident.",
        "image_url": "https://picsum.photos/seed/server-room/600/400",
    },
    {
        "author": "dhh",
        "body": "ship it. iterate. you're not gonna predict what users actually want from inside your head.",
    },
    {
        "author": "guido",
        "body": "today's python tip — use `pathlib` instead of `os.path`:\n\n```python\nfrom pathlib import Path\n\nconfig = Path.home() / '.config' / 'myapp.toml'\nif config.exists():\n    print(config.read_text())\n```\n\nso much cleaner.",
    },
    {
        "author": "antirez",
        "body": "redis lookups in under a millisecond never gets old. ✨",
        "image_url": "https://picsum.photos/seed/redis-dashboard/600/350",
    },
    {
        "author": "ada",
        "body": "spent the morning rewriting our htmx integration. _no more_ jquery anywhere. the diff is glorious.",
    },
    {
        "author": "torvalds",
        "body": "rebased a feature branch with 47 commits. now it's 6. squash early, squash often.",
    },
    {
        "author": "grace",
        "body": "morning standup:\n\n- ✅ deployed v2.4.1\n- 🔥 investigating cache miss spike\n- ⏳ pairing with @ada on the auth refactor at 2pm\n\nlet's go team.",
    },
    {
        "author": "dhh",
        "body": "controversial opinion: **delete more code than you write.** the best PR i've reviewed this month was -342 / +12.",
        "image_url": "https://picsum.photos/seed/code-on-screen/600/380",
    },
    {
        "author": "guido",
        "body": "TIL `dict | dict` syntax for merging in python 3.9+. been writing `{**a, **b}` for years out of habit.\n\n```python\na = {'x': 1, 'y': 2}\nb = {'y': 3, 'z': 4}\nprint(a | b)  # {'x': 1, 'y': 3, 'z': 4}\n```",
    },
    {
        "author": "antirez",
        "body": "the most underrated debugging tool is *printf*. fight me.",
    },
    {
        "author": "ada",
        "body": "finally got the dark theme dialed in. monospace everything, neon green accents, blinking caret in the navbar. it just feels right.",
        "image_url": "https://picsum.photos/seed/terminal-screenshot/700/420",
    },
    {
        "author": "grace",
        "body": "if your test suite takes longer to run than your lunch break, you have a test suite problem, not a productivity problem.",
    },
    {
        "author": "torvalds",
        "body": "git log --oneline | wc -l  →  18,447\n\nstill counting.",
    },
]

COMMENTS = [
    ("torvalds", 0, "fresh repos are sacred. don't pollute it with a README on the first commit."),
    ("grace",    0, "agreed. the `git init` -> first push is the best moment in software."),
    ("ada",      1, "the semicolon strikes again. i've lost weeks of my life to that."),
    ("dhh",      1, "and yet rust would have caught it at compile time. just sayin'."),
    ("guido",    2, "this is the most accurate thing posted on this site today."),
    ("antirez",  2, "+1. boring tech wins on-call rotations."),
    ("ada",      4, "pathlib is genuinely one of the best stdlib additions in the last decade."),
    ("grace",    4, "i still mix up `/` for joining paths. muscle memory dies hard."),
    ("dhh",      6, "the htmx + server-rendered approach is so refreshing after 5 years of SPA fatigue."),
    ("torvalds", 7, "interactive rebase is a superpower. people are afraid of it for no reason."),
    ("antirez",  9, "342 lines deleted. chef's kiss."),
    ("ada",      11, "printf debugging is the great equalizer. doesn't matter your seniority."),
    ("guido",    12, "looks great. send me the CSS, i want to steal it for my blog."),
    ("dhh",      13, "if your test suite is fast, you actually run it. that's the entire trick."),
]


def run():
    # Wipe prior seed data so re-running is idempotent
    Twit.objects.filter(author__username__in=[u[0] for u in USERS]).delete()

    users = {}
    for username, first, last, email in USERS:
        u, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={"first_name": first, "last_name": last, "email": email},
        )
        if created:
            u.set_password("password123")
            u.save()
        users[username] = u

    twit_objs = []
    now = timezone.now()
    for i, t in enumerate(TWITS):
        # Stagger created times so timesince renders varied "X minutes/hours ago"
        offset = timedelta(minutes=(len(TWITS) - i) * 17 + random.randint(0, 7))
        twit = Twit.objects.create(
            author=users[t["author"]],
            body=t["body"],
            image_url=t.get("image_url"),
        )
        # Force the created timestamp (auto_now_add doesn't allow at create)
        Twit.objects.filter(pk=twit.pk).update(created=now - offset)
        twit.refresh_from_db()
        twit_objs.append(twit)

    # Likes — random distribution
    for twit in twit_objs:
        likers = random.sample(list(users.values()), k=random.randint(0, len(users)))
        for u in likers:
            twit.likes.add(u)

    # Comments
    for author_username, twit_idx, body in COMMENTS:
        if twit_idx >= len(twit_objs):
            continue
        Comment.objects.create(
            author=users[author_username],
            twit=twit_objs[twit_idx],
            body=body,
        )

    print(f"seeded: {len(users)} users, {len(twit_objs)} twits, {len(COMMENTS)} comments")
    print("login with any of:")
    for u in USERS:
        print(f"  username={u[0]}  password=password123")


if __name__ == "__main__":
    run()
