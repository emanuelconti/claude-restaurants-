#!/usr/bin/env python3
"""What the day's Sincronia carousel says: the slides, the last slide, the caption.

The page is a daily push for your head, your routine and your drive, told
through everyday life, in English. Topics are human first; Sincronia is
mentioned only on the rare topic where it is genuinely the subject, and never
with a link. STYLE.md is the brief a run writes from.
"""

from __future__ import annotations

import re
import datetime as _dt
import random as _random

EPOCH = _dt.date(2026, 10, 31)

# Photos without faces, the same sets the brand's other feeds use.
PHOTO_SETS = {
    "life": [
        "1470252649378-9c29740c9fa8",  # sunrise over a valley
        "1501139083538-0139583c060f",  # hourglass
        "1495364141860-b0d03eccd065",  # a hand holding an alarm clock
        "1484480974693-6ca0a78fb36b",  # an open notebook
        "1506784983877-45594efa4cbe",  # a planner and a coffee
        "1434030216411-0b793f4b4173",  # a hand writing
        "1488190211105-8b0e65b80b4e",  # a desk, a coffee, a journal
        "1506126613408-eca07ce68773",  # a silhouette at sunrise
        "1447752875215-b2761acb3c5d",  # a bridge into the woods
        "1511920170033-f8396924c348",  # latte art, from above
        "1509042239860-f550ce710b93",  # three cappuccinos
        "1442975631115-c4f7b05b8a2c",  # a cafe inside, morning light
    ],
    "work": [
        "1519389950473-47ba0277781c",  # a desk full of laptops, from above
        "1486312338219-ce68d2c6f44d",  # hands typing
        "1516321318423-f06f85e504b3",  # a hand at a laptop
        "1484480974693-6ca0a78fb36b",  # an open notebook
        "1434030216411-0b793f4b4173",  # a hand writing
        "1488190211105-8b0e65b80b4e",  # a desk, a coffee, a journal
        "1554224155-6726b3ff858f",  # hands with receipts
        "1520607162513-77705c0f0d4a",  # a card terminal, from above
    ],
    "city": [
        "1583422409516-2895a77efded",  # a city from above
        "1511527661048-7fe73d85e9a4",  # a hill at dusk
        "1517248135467-4c7edcad34c4",  # a restaurant inside
        "1554118811-1e0d58224f24",  # a cafe, empty chairs
        "1521017432531-fbd92d768814",  # a cafe counter
        "1493857671505-72967e2e2760",  # a cafe with a menu board and a bike
        "1524758631624-e2822e304c36",  # a lounge with armchairs
        "1510812431401-41d2bd2722f3",  # glasses raised
        "1528712306091-ed0763094c98",  # hands at the stove
    ],
}

HANDLE = "@sincronia.live"
CAPTION_FOLLOW = (f"Follow {HANDLE} for a push like this every day. "
                  "Save it for the day you need it, and send it to someone who does.")
HASHTAGS = "#mindset #motivation #habits #focus #discipline #smallwins #realtalk"

# The last slide of every carousel.
FOLLOW = dict(
    title="A push for your day, every day.",
    lines=["Short ideas for your head, your routine and your drive."],
    pill=f"Follow {HANDLE}",
    small="Save it for the day you need it.",
)

SLOTS = 3  # carousels a day


def check_topic(topic: dict) -> list:
    """What is wrong with a topic written for a run, in words a writer can fix; empty if nothing."""
    errors = []

    def text(value, name, most):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name} is missing")
        elif len(value) > most:
            errors.append(f"{name} has {len(value)} characters, at most {most}: {value!r}")
        elif "—" in value or "–" in value:
            errors.append(f"{name} has a dash; use a colon, a full stop or a comma: {value!r}")

    text(topic.get("title"), "title", 90)
    text(topic.get("hook"), "hook", 120)
    points = topic.get("points")
    if not isinstance(points, list) or not 5 <= len(points) <= 8:
        errors.append("points must be a list of 5 to 8 points")
        points = []
    for i, point in enumerate(points, 1):
        if not (isinstance(point, (list, tuple)) and len(point) == 3 and isinstance(point[1], list)):
            errors.append(f"point {i} must be [heading, [line, line], closing line]")
            continue
        heading, lines, punch = point
        text(heading, f"point {i} heading", 52)
        if not 1 <= len(lines) <= 2:
            errors.append(f"point {i} needs 1 or 2 lines")
        for j, line in enumerate(lines, 1):
            text(line, f"point {i} line {j}", 95)
        text(punch, f"point {i} closing line", 75)
    if "hashtags" in topic and not (isinstance(topic["hashtags"], str)
                                    and topic["hashtags"].startswith("#") and len(topic["hashtags"]) <= 200):
        errors.append("hashtags must be one string of up to 200 characters, starting with #")
    if topic.get("photos", "life") not in PHOTO_SETS:
        errors.append(f"photos must be one of {sorted(PHOTO_SETS)}")
    ids = topic.get("photo_ids")
    if ids is not None and not (isinstance(ids, list) and ids and all(isinstance(p, str) and re.fullmatch(r"\d{10,13}-[0-9a-f]{12}", p) for p in ids)):
        errors.append("photo_ids must be a list of Unsplash photo ids like 1544982560-63ad67a35c23 (the part after images.unsplash.com/photo-)")
    return errors


def bank_topic(date: _dt.date, slot: int = 1) -> dict:
    """A written topic for a date and slot, when a run has none of its own."""
    n = (date - EPOCH).days * SLOTS + (slot - 1)
    return EVERYDAY[n % len(EVERYDAY)]


def carousel(date: _dt.date, slot: int = 1, topic: dict | None = None) -> dict:
    """The slides' content for a date and slot, with one photo per slide, the same every time."""
    topic = topic or bank_topic(date, slot)
    rng = _random.Random(date.toordinal() * 10 + slot)
    pool = list(PHOTO_SETS.get(topic.get("photos", "life"), PHOTO_SETS["life"]))
    rng.shuffle(pool)
    need = 1 + len(topic["points"])
    picks = (pool * (need // len(pool) + 1))[:need]
    # The owner (31 October): the photos must change from post to post. A topic can name its own,
    # one per slide (cover first), chosen fresh for it; the set fills in any that are missing.
    if topic.get("photo_ids"):
        own = list(dict.fromkeys(topic["photo_ids"]))
        picks = (own + [p for p in pool if p not in own])[:need]
    # The title opens the caption, so later runs can see what was already posted.
    caption = f"{topic['title']}\n\n{topic['hook']}\n\n{CAPTION_FOLLOW}\n\n{topic.get('hashtags') or HASHTAGS}"
    count = len(topic["points"])
    numbers = list(range(count, 0, -1)) if topic.get("countdown") else list(range(1, count + 1))
    return dict(date=date.isoformat(), slot=slot, title=topic["title"], points=topic["points"],
                numbers=numbers, photos=picks, caption=caption)


# The written bank: used when a run writes nothing of its own, so a post always
# goes out. Everyday life, motivation and mindset, nothing about the brand.
EVERYDAY = [
    dict(
        title="8 signs you are further along than you think",
        hook="Number 3 is the one nobody claps for.",
        photos="life",
        points=[
            ["Things that used to scare you", ["You do them now without the build up.",
                                               "The nerves moved somewhere else."], "That is growth, quietly."],
            ["You recover faster", ["A bad day used to take a week.", "Now it takes an evening."],
             "Resilience is a skill, not a mood."],
            ["You say no on time", ["Not after three days of drafting the message."],
             "Your calendar started to look like your priorities."],
            ["You stopped explaining yourself", ["A short answer is a full answer."],
             "Peace is quieter than people expect."],
            ["You ask better questions", ["Less what should I do, more what am I actually solving."],
             "Clarity beats effort."],
            ["Boring progress stopped bothering you", ["You can do the unglamorous version.",
                                                       "Day after day."], "That is the whole trick."],
            ["You compare less", ["Not never. Less.", "And you catch yourself faster when you do."],
             "The scoreboard was never real."],
            ["You keep promises to yourself", ["Small ones. Most days."], "This is where trust in yourself comes from."],
        ],
        hashtags="#growth #mindset #progress #selfworth #realtalk",
    ),
    dict(
        title="7 things to do before you check your phone",
        hook="The first twenty minutes set the tone for the whole day.",
        photos="life",
        points=[
            ["Stand up before you scroll", ["Feet on the floor, curtains open."], "Your head follows your body."],
            ["Drink water first", ["You are not tired. You are dehydrated and horizontal."], "Start with the easy win."],
            ["Name the one thing", ["If today only one thing gets done, which one?"], "One. Not five."],
            ["Move for two minutes", ["Stretch, walk the hallway, go outside."], "Two minutes counts."],
            ["Write the day in one line", ["Not a system. One line on paper."], "Clarity is cheap when it is short."],
            ["Eat something real", ["Coffee is not breakfast, it is a personality."], "Fuel before input."],
            ["Then open the phone", ["On purpose, with a reason."], "You are the one deciding."],
        ],
        hashtags="#morningroutine #habits #focus #discipline #mindset",
    ),
    dict(
        title="The 6 stages of starting something new",
        hook="Everyone pretends they skipped stage 4.",
        photos="life",
        countdown=False,
        points=[
            ["The idea is perfect", ["In your head it already works.", "Nothing has been tested yet."],
             "This stage is free. Enjoy it."],
            ["The first attempt", ["It is worse than you imagined.", "Much worse."], "It is supposed to be."],
            ["The research hole", ["Twelve tabs, two courses, zero progress."], "Learning can be hiding."],
            ["The quiet doubt", ["Maybe you are not the kind of person who does this."],
             "Everyone meets this voice. It lies."],
            ["The boring middle", ["No applause, no milestone, just the work."], "This is where most people stop."],
            ["It works a little", ["Not a breakthrough. A sign."], "Signs are enough to keep going."],
        ],
        hashtags="#startingout #discipline #mindset #progress #motivation",
    ),
    dict(
        title="8 small things that fix a bad day",
        hook="None of them are expensive. Number 6 takes ten seconds.",
        photos="city",
        points=[
            ["Change the room", ["A different chair is a different brain."], "Move before you think harder."],
            ["Finish one tiny thing", ["The dish, the email, the bed."], "Momentum is physical."],
            ["Go outside without a goal", ["Ten minutes. No podcast."], "Your head needs the silence."],
            ["Text someone first", ["You do not need a reason."], "Connection is a reset button."],
            ["Lower the bar for today", ["Not quitting. Resizing."], "A small day is still a day."],
            ["Put the phone in another room", ["Ten seconds to carry it there."], "Distance works better than willpower."],
            ["Eat properly", ["Half of the mood was hunger."], "Check the basics first."],
            ["Go to bed early", ["Tomorrow is a genuinely different day."], "Some problems are just tiredness."],
        ],
        hashtags="#badday #selfcare #mindset #reset #mentalhealth",
    ),
    dict(
        title="7 lies your brain tells you at 11pm",
        hook="It sounds so reasonable in the dark.",
        photos="life",
        points=[
            ["You have wasted the year", ["It counts months you cannot even remember."], "Memory is not an audit."],
            ["Everyone else figured it out", ["You are comparing your inside to their outside."], "You always lose that one."],
            ["You should decide this tonight", ["Big decisions at midnight are a trap."], "Nothing is due before morning."],
            ["One more episode", ["It is never one."], "Tomorrow pays for it."],
            ["You are behind", ["Behind whom? On whose schedule?"], "There is no official timetable."],
            ["You will remember this idea", ["You will not. Write it down."], "Paper beats confidence."],
            ["Tomorrow you will feel different", ["This one is true, actually."], "Go to sleep."],
        ],
        hashtags="#overthinking #night #mindset #mentalhealth #realtalk",
    ),
    dict(
        title="6 things discipline actually looks like",
        hook="It is quieter and more boring than the internet says.",
        photos="work",
        points=[
            ["Starting badly", ["Not waiting for the good mood or the right setup."], "Motion first, mood second."],
            ["Short sessions, often", ["Twenty honest minutes beats a heroic Sunday."], "Frequency builds skill."],
            ["Stopping on time", ["Finishing while you still have something left."], "Tomorrow starts easier."],
            ["Doing it at 60 percent", ["On tired days, the smaller version still counts."], "Never zero."],
            ["Protecting one block", ["One hour nobody gets to book."], "Defend it like a meeting."],
            ["Coming back after breaking it", ["Missing once is an accident. Missing twice is a new habit."],
             "The comeback is the discipline."],
        ],
        hashtags="#discipline #habits #focus #consistency #mindset",
    ),
    dict(
        title="7 things that are not laziness",
        hook="Number 2 gets mistaken for it constantly.",
        photos="life",
        points=[
            ["Being tired", ["Your body is reporting, not rebelling."], "Rest is information."],
            ["Not knowing where to start", ["That is a planning problem wearing a laziness costume."],
             "Shrink the first step."],
            ["Avoiding something scary", ["Fear looks a lot like procrastination."], "Name the fear and it shrinks."],
            ["Needing more information", ["Sometimes the pause is correct."], "Not every delay is avoidance."],
            ["Recovering", ["After a hard stretch, slow is the point."], "You are not a machine with a bad month."],
            ["Doing the invisible work", ["Thinking, deciding, waiting on someone else."], "It does not look like output."],
            ["Resting on purpose", ["Chosen rest is not the same as collapse."], "Plan it before you need it."],
        ],
        hashtags="#rest #burnout #mentalhealth #mindset #selfcompassion",
    ),
    dict(
        title="8 ways to stop comparing yourself to everyone",
        hook="Number 5 is the one that actually sticks.",
        photos="life",
        points=[
            ["Check the timeline", ["You are seeing year five of their work in a ten second clip."],
             "Different starting lines."],
            ["Mute, do not unfollow", ["You can protect your head without a confrontation."], "Quietly is fine."],
            ["Compare to last month", ["The only honest comparison is your own."], "Same person, different data."],
            ["Ask what you actually want", ["Half of envy is wanting something you never chose."], "Check the wish first."],
            ["Make something today", ["Envy dies in the middle of work."], "Hands busy, head quiet."],
            ["Follow fewer, closer", ["A smaller feed is a calmer head."], "Curate like it matters, because it does."],
            ["Say it out loud to a friend", ["Envy loses most of its power when spoken."], "It shrinks in daylight."],
            ["Let someone be ahead", ["Their win costs you nothing."], "There is no fixed number of good lives."],
        ],
        hashtags="#comparison #socialmedia #mindset #mentalhealth #selfworth",
    ),
    dict(
        title="The 7 phases of a Sunday evening",
        hook="Phase 4 arrives without warning, every week.",
        photos="city",
        points=[
            ["Still technically the weekend", ["It is 4pm. Plenty of time."], "Famously plenty of time."],
            ["The small clean up", ["One cupboard, suddenly, with great energy."], "Procrastination in a nice outfit."],
            ["The plan for the week", ["Gym, cooking, early nights, a new person entirely."], "Ambition peaks on Sundays."],
            ["The quiet dread", ["Nothing happened. The mood just walked in."], "Everyone gets this one."],
            ["The scroll", ["Forty minutes gone, nothing gained."], "You know. You keep going."],
            ["The late dinner", ["Whatever is in the fridge, standing up."], "A classic."],
            ["The one more episode", ["Tomorrow is a problem for tomorrow you."], "Be kind to them anyway."],
        ],
        hashtags="#sunday #weekend #realtalk #relatable #mondayprep",
    ),
]
