"""What Sowld's Instagram carousels say, and which day says what.

The profile posts carousels only: a cover with a big title over a photo, then
one numbered point per slide, text on white with a photo fading in under it,
the mark on every slide, no faces. The last slide is Sowld, and only when the
topic earns it.

English: @sowld.ai posts in English, unlike SocialPerks which is Spanish.

The topics are everyday life around the stuff we own, buy, keep and finally
let go of: the wardrobe, the drawer of cables, moving house, a market find,
the thing you regret selling. People like them because they recognise
themselves, and save them because they are about something they keep putting
off. Nothing here is a sales pitch; see STYLE.md for why that is the rule and
not a preference.

Every topic is a title for the cover, a line for the caption, and points: a
heading, the lines under it, and the closing line set in bold. `photos` names
the set its slides draw from (PHOTO_SETS); `countdown` numbers the points from
the highest down, for a ranking; `cta` adds the Sowld slide at the end.
"""

from __future__ import annotations

import datetime as _dt
import random as _random

# The first day of the bank's rotation.
EPOCH = _dt.date(2026, 10, 30)

PHOTO_SETS = {
    # Wardrobes, shelves, boxes: the stuff a topic about owning things sits on.
    "stuff": [
        "1489274495757-95c7c837b101",  # a rail of clothes
        "1558769132-cb1aea458c5e",  # folded clothes on a shelf
        "1445205170230-053b83016050",  # a wardrobe from above
        "1591047139829-d91aecb6caea",  # a bag on a chair
        "1595341888016-a392ef81b7de",  # shoes lined up
        "1586528116311-ad8dd3c8310d",  # cardboard boxes, moving day
        "1600585154340-be6161a56a0c",  # an empty room, moving day
        "1484101403633-562f891dc89a",  # a desk with cables and a lamp
    ],
    # Markets, second-hand shops, flea stalls: the hunt.
    "market": [
        "1441986300917-64674bd600d8",  # a shopfront
        "1556742049-0cfed4f6a45d",  # a market stall
        "1472851294608-062f824d29cc",  # a shop interior
        "1513519245088-0e12902e5a38",  # vintage furniture
        "1555041469-a586c61ea9bc",  # a vintage table
        "1538688525198-9b88f6f53126",  # an armchair
        "1493663284031-b7e3aefcae8e",  # a lamp and a chair
        "1550009158-9ebf69173e03",  # old electronics on a table
    ],
    # Mornings, coffee, notebooks: for the topics that are just life.
    "life": [
        "1470252649378-9c29740c9fa8",  # sunrise over a valley
        "1484480974693-6ca0a78fb36b",  # an open notebook
        "1506784983877-45594efa4cbe",  # a planner and a coffee
        "1488190211105-8b0e65b80b4e",  # a desk, a coffee, a journal
        "1495364141860-b0d03eccd065",  # a hand holding an alarm clock
        "1511920170033-f8396924c348",  # latte art from above
        "1442975631115-c4f7b05b8a2c",  # a café inside, morning light
        "1434030216411-0b793f4b4173",  # a hand writing
    ],
    # People-shaped scenes without faces: hands, desks, walks, windows. For the
    # topics that are about a life rather than about objects.
    "human": [
        "1499750310107-5fef28a66643",  # a laptop and a notebook by a window
        "1499209974431-9dddcece7f88",  # someone walking, from behind
        "1517842645767-c639042777db",  # hands and a notebook
        "1506485338023-6ce5f36692df",  # a window, plants, light
        "1517836357463-d25dfeac3438",  # a gym floor
        "1524178232363-1fb2b075b655",  # a lecture hall from behind
        "1476304884326-cd2c88572c5f",  # a path through trees
        "1518457607834-6e8d80c183c5",  # a quiet room with a chair
    ],
    # Receipts, cards, laptops: money topics without a single figure invented.
    "money": [
        "1554224155-6726b3ff858f",  # hands with receipts
        "1563013544-824ae1b704d3",  # a card in a hand
        "1520607162513-77705c0f0d4a",  # a card terminal from above
        "1486312338219-ce68d2c6f44d",  # hands typing
        "1516321318423-f06f85e504b3",  # a hand at a laptop
        "1554224154-26032ffc0d07",  # a calculator and papers
    ],
}

# The bank: what a run posts when writing a fresh topic fails. Everyday life
# first, Sowld only where the topic walks into it on its own.
EVERYDAY = [
    dict(
        title="The 7 stages of finally clearing out your wardrobe",
        hook="Stage 4 is where everyone gets stuck.",
        photos="stuff",
        points=[
            ("The burst of energy", ["You pull everything out onto the bed.", "You feel like a different person."], "That feeling lasts about fifteen minutes."),
            ("The first doubt", ["\"This might come back in style.\"", "You bought it in 2017."], "Styles come back. You, in that size, maybe not."),
            ("The maybe pile", ["Not a keep, not a throw.", "It grows faster than the other two."], "The maybe pile is where decluttering goes to die."),
            ("The guilt", ["\"But it was expensive.\"", "It has not moved in three years."], "The money is already spent. The space you are still paying for."),
            ("The surrender", ["Everything goes back in.", "Except two t-shirts, so you can say you did something."], "The wardrobe wins again."),
            ("The bed problem", ["It is eleven at night.", "You have to sleep there."], "The most effective deadline ever invented."),
            ("One drawer", ["Not the whole wardrobe. Not Sunday.", "One drawer, tonight, twenty minutes."], "Everyone who cleared out a house started with one drawer."),
        ],
    ),
    dict(
        title="Things everyone owns and nobody has used in years",
        hook="You have at least five of these. Probably six.",
        photos="stuff",
        countdown=True,
        points=[
            ("The box of cables", ["You no longer know what charges what.", "Throwing them out feels reckless."], "There is definitely a cable in there for something you no longer own."),
            ("The exercise machine", ["Bought in January with real conviction.", "Currently holding a jumper."], "The best clothes rail anyone ever paid for."),
            ("The bread maker", ["Used twice.", "Weighs as much as a small child."], "The gift that quietly becomes furniture."),
            ("The CDs and DVDs", ["Nothing in the house can play them.", "You keep them anyway."], "Those are not objects. They are memories in a cracked case."),
            ("The clothes from the other size", ["In both directions.", "Just in case."], "A wardrobe should not be a backup plan for your own body."),
            ("The second set of pans", ["You use one. The rest, never.", "But you do not throw out a pan."], "There is only ever one favourite pan, and you know which."),
        ],
    ),
    dict(
        title="What we tell ourselves right before buying something we do not need",
        hook="You have said at least three of these out loud.",
        photos="money",
        points=[
            ("\"It is an investment\"", ["It is not.", "It almost never is."], "An investment is something you could sell. An excuse is not."),
            ("\"It was on sale\"", ["You saved forty per cent.", "On something you were not going to buy."], "A discount on something you did not need is not a saving."),
            ("\"I will use it all the time\"", ["You say it with total confidence.", "You genuinely believe it in that moment."], "Count how often you used it last month. Not how often you can picture it."),
            ("\"I deserve it\"", ["Often you do.", "But a checkout page is a strange place to reward yourself."], "Deserving it and needing it are two different things."),
            ("\"If I wait it will be gone\"", ["The fear of missing it decides instead of you.", "It is usually still there next week."], "Urgency is a technique, not information."),
            ("\"I can always resell it\"", ["The intention is real.", "The photo for the listing never happens."], "Reselling is work. Buying takes ten seconds."),
        ],
    ),
    dict(
        title="The 6 stages of moving house, by someone who has done it",
        hook="Stage 3 changes how you see your own stuff forever.",
        photos="stuff",
        points=[
            ("Optimism", ["\"One weekend and we are done.\"", "You bought ten boxes."], "You will need thirty two."),
            ("The reckoning", ["You find out how much you actually own.", "You were not prepared for this information."], "You were living in a storage unit and nobody told you."),
            ("Ruthlessness", ["At some point you stop deciding with your heart.", "You decide with the arm that has to carry it."], "Nothing frees you like having to take it up three flights of stairs."),
            ("The miscellaneous box", ["Batteries, one sock, a key, some birthday candles.", "Labelled: \"various\"."], "Every move has one box that will never be opened."),
            ("The empty flat", ["You stand in it for a minute.", "It looks bigger and smaller at once."], "Empty rooms make a sound you remember for years."),
            ("A month later", ["You cannot recall half of what you brought.", "And you are completely fine."], "Maybe it was never thirty two boxes' worth."),
        ],
    ),
    dict(
        title="Things you only learn once you start buying second hand",
        hook="Number 5 you remember for good.",
        photos="market",
        cta=True,
        points=[
            ("The photos say more than the description", ["The description is written to sell.", "The photos are not."], "One blurry shot of exactly the part that matters is never an accident."),
            ("The lowest price is rarely the deal", ["It is usually the listing with something wrong.", "Or something left unsaid."], "The real find sits in the middle of the list, not at the bottom."),
            ("You learn to ask", ["\"Does everything work? Any faults the photos miss?\"", "How they answer matters as much as what."], "Silence is an answer too."),
            ("Retail price means nothing", ["\"It was £900 new\" tells you nothing about today.", "Only similar listings on sale right now do."], "What a used thing is worth is set by its market, not by its receipt."),
            ("Your first bad buy", ["It happens to everyone.", "It costs little and teaches a lot."], "Nobody gets good at this without getting burned once."),
            ("The feeling is different", ["It is not only about spending less.", "It is about having found it."], "Buying is easy. Finding is something else."),
        ],
    ),
    dict(
        title="7 things we hide from our families about what we bought",
        hook="You have used the first one this month.",
        photos="money",
        points=[
            ("\"I have had this for ages\"", ["Delivered with complete calm.", "While removing the tag."], "The tag is always the detail that gives you away."),
            ("\"It was so cheap\"", ["The real number stays classified.", "You round down. Heavily."], "Nobody in history has ever rounded a price up."),
            ("\"A friend gave it to me\"", ["The friend does not exist.", "Nobody will ever check."], "Every family has one imaginary friend who is extremely generous."),
            ("\"It is for work\"", ["Technically it could be useful.", "Technically."], "The word \"technically\" is holding up entire household budgets."),
            ("\"It is second hand\"", ["This one is sometimes true.", "And it works every time."], "The only one you do not have to make up."),
            ("\"I did not order that\"", ["Said while standing next to a parcel with your name on it.", "With conviction."], "Sometimes boldness is all you have left."),
            ("\"This is the last thing\"", ["It is not the last thing.", "It is never the last thing."], "We all believe it, every single time."),
        ],
    ),
    dict(
        title="The things you regret selling",
        hook="There is always one. You are thinking of it right now.",
        photos="stuff",
        points=[
            ("The console from your childhood", ["Sold to fund the newer one.", "You do not remember the newer one."], "You did not sell a box. You sold a few hundred afternoons."),
            ("The bike", ["\"I never use it anyway.\"", "Every spring, without fail, you think about it."], "Bikes are regretted seasonally."),
            ("The book with your notes in it", ["You can find the book again.", "Your pencil notes, no."], "Some things are one of a kind only because you used them."),
            ("The jacket", ["It did not even fit that well.", "But it is in every photo from those years."], "Clothes hold entire evenings inside them."),
            ("The instrument", ["\"I do not play any more anyway.\"", "It was a promise, not an object."], "Selling it was saying out loud that you had stopped."),
            ("The one you sold in a hurry", ["Not for money, not for space.", "Just because that day you wanted it done."], "The opposite of impulse buying exists, and it stings the same."),
        ],
    ),
    dict(
        title="Signs you have become the person who resells everything",
        hook="Four of these and it is already too late.",
        photos="market",
        points=[
            ("You price everything", ["You walk into a friend's flat and think \"that would sell well\".", "You do not say it. But you think it."], "Once the brain learns to look, it does not switch off."),
            ("You have a packing corner", ["Boxes, tape, a tape measure.", "It assembled itself."], "Nobody decides to have a shipping area. It appears."),
            ("You know the good light", ["You worked out which window.", "And what time."], "The difference between a photo and a listing is the light."),
            ("You check prices for fun", ["Even for things you would never sell.", "Just to know."], "Curiosity is the first symptom."),
            ("You have your own condition scale", ["\"Good\" means something precise to you.", "Far more precise than it does to anyone else."], "People who actually sell describe the flaws first."),
            ("Throwing things out bothers you", ["Not for environmental reasons.", "Because you can see value others cannot."], "Once you learn to look, there is no going back."),
        ],
    ),
    dict(
        title="The 6 stages of a Sunday that was supposed to be productive",
        hook="Stage 4 arrives no matter what you planned.",
        photos="life",
        points=[
            ("The 8am alarm", ["Set on Saturday night, full of ambition.", "Cancelled at 8:01."], "Saturday night you has never met Sunday morning you."),
            ("The list", ["Six things.", "Written neatly, in order."], "Writing the list absolutely counts as doing the first thing."),
            ("The long coffee", ["It was meant to take ten minutes.", "It is half past eleven."], "No coffee has ever taken as long as planned."),
            ("The black hole", ["Videos, messages, an article about something you do not need.", "You look up and an hour is gone."], "Free time does not get spent. It evaporates."),
            ("The 7pm burst", ["Suddenly you are reorganising a drawer nobody asked about.", "With enormous energy."], "We will do anything rather than the thing on the list."),
            ("The 10pm peace", ["You did two things out of six.", "That is genuinely fine."], "Not every Sunday has to produce something."),
        ],
    ),
    dict(
        title="What a used item is really worth: 5 things to know",
        hook="Number 2 is where almost everyone goes wrong.",
        photos="market",
        cta=True,
        points=[
            ("Retail price is the wrong anchor", ["A four year old item at half price is not a bargain.", "That is just what four year old items cost."], "Comparing to new tells you nothing about now."),
            ("What others are asking today", ["Same model, same condition, listed right now.", "Five listings is enough to see where you stand."], "An item's market is made of similar items, not of a price list."),
            ("Condition changes everything", ["\"Like new\" and \"visible wear\" are not the same item.", "Only compare like for like."], "Two prices cannot be compared if they describe different things."),
            ("The price is not the cost", ["Add shipping, fees, the trip if you collect it.", "And the missing part you will have to buy."], "Compare the real cost, not the number in the listing."),
            ("A huge discount is a warning", ["70 per cent below is not luck.", "It is a question you have not answered yet."], "Look harder, not faster."),
        ],
    ),
    dict(
        title="7 things that make a home feel dated (and it is not the furniture)",
        hook="Number 5 you can fix in an afternoon.",
        photos="stuff",
        points=[
            ("Cold white light", ["It lights everything like an office.", "Nobody relaxes in an office."], "Warm light changes a room more than a new sofa does."),
            ("Visible cables", ["You stop seeing them after a week.", "Anyone walking in sees them instantly."], "Tidiness is noticed when it is missing, not when it is there."),
            ("Bare walls", ["It does not have to be expensive art.", "It has to be yours."], "A room with nothing on the walls always looks like it is waiting."),
            ("Everything from one shop", ["Coordinated, but with no story.", "Like a catalogue page."], "Good rooms always have one thing that does not match."),
            ("Short curtains", ["The detail you cannot name.", "But you can feel it."], "Curtains to the floor: the most underrated trick there is."),
            ("Flat surfaces", ["Tables and shelves collect everything.", "They fill themselves."], "Every clear surface is one fewer place for things to pile up."),
            ("Things you no longer use", ["They take up room and attention.", "Even when you are not looking at them."], "A home breathes when something leaves, not when something arrives."),
        ],
    ),
    dict(
        title="Things you say every single time you walk into a charity shop",
        hook="You say the third one out loud. Always.",
        photos="market",
        points=[
            ("\"Just a quick look\"", ["Announced at the door.", "With total sincerity."], "It has never once been a quick look."),
            ("\"Who buys this?\"", ["Said in front of something unexplainable.", "Someone will buy it. Someone always does."], "There is a buyer for everything. That is the best part of second hand."),
            ("\"My gran had this exact one\"", ["Mandatory.", "At least once per visit."], "These shops are museums where you are allowed to touch."),
            ("\"If I just fixed it up a bit\"", ["The most dangerous sentence in the building.", "You will not fix it up."], "\"I'll fix it myself\" has filled entire garages."),
            ("\"I'll come back if it is still here\"", ["It will not be.", "You know that as you say it."], "In a second hand shop, coming back later is a polite way of saying no."),
            ("\"One more lap and we go\"", ["The second final lap.", "Of the four planned."], "Nobody has ever left on the first attempt."),
        ],
    ),
    dict(
        title="6 habits of people whose homes never fill up with stuff",
        hook="They are not tidier. They decide earlier.",
        photos="stuff",
        points=[
            ("They decide at the door", ["The moment to say no is before it comes in.", "After that it is yours and it weighs more."], "Your front door is the best filter you own."),
            ("One in, one out", ["Not a strict rule.", "A reminder."], "The space is fixed. The stuff is not."),
            ("They do not shop for their future self", ["The one who will run, cook, read more.", "They shop for who they are now."], "Imaginary you has a wardrobe full of things never worn."),
            ("They keep the moment, not the object", ["A photo takes less room than a box.", "And you can actually find it again."], "It is not the memory that takes up space. It is the container."),
            ("They set a deadline", ["\"If it is still untouched in six months, it goes.\"", "No drama."], "A date decides for you when you cannot decide yourself."),
            ("They do not wait for the right moment", ["It does not come.", "The house move comes."], "Better to choose calmly than to decide in a rush."),
        ],
    ),
    dict(
        title="The 8 worst feelings of a Monday morning",
        hook="Number 6 nobody ever talks about.",
        photos="life",
        countdown=True,
        points=[
            ("The alarm that does not sound like yours", ["It goes off like a mistake.", "It is not a mistake."], "Monday has a sound all of its own."),
            ("Darkness at seven", ["From October onwards.", "It feels like getting up in the night."], "Half an hour more daylight changes the mood more than we admit."),
            ("The emails lined up", ["They piled up over the weekend.", "None are urgent. Together they look enormous."], "The number frightens us more than the contents."),
            ("Coffee drunk too fast", ["You do not taste it.", "You use it."], "A rushed coffee is not a coffee. It is fuel."),
            ("The packed train", ["Everyone with the same face.", "A strange silent solidarity."], "The one moment of the week when we are all honest."),
            ("The weekend you cannot account for", ["It happened and you do not know where.", "And you did not rest either."], "Resting and doing nothing are not the same thing."),
            ("The first meeting", ["Ten minutes of something that could have been a message.", "Everybody is thinking it."], "Nobody ever says it."),
            ("Counting what is left", ["You do it at nine on Monday.", "Four and a half days."], "Knowing how long is left has never once helped anyone."),
        ],
    ),
    dict(
        title="Things people do not know about what is sitting in their loft",
        hook="Number 3 is worth more than you would guess.",
        photos="market",
        cta=True,
        points=[
            ("Old electronics are not rubbish", ["Discontinued models, spare parts.", "People search for these on purpose."], "There is a buyer even for a board from a model nobody makes any more."),
            ("Cane and rattan furniture came back", ["What looked dated ten years ago.", "Is now looked for."], "Ugly and old are different things, and time sorts out which is which."),
            ("Instruments hold their value", ["Better than almost anything else.", "Even used, even after years."], "Wood ages better than plastic, in every sense."),
            ("The toys from your childhood", ["Not all of them. Some."], "The box is half the value. Almost nobody keeps the box."),
            ("Books, almost never", ["Unless they are rare or first editions.", "Better to pass them on."], "A book's value is nearly always in whoever reads it next."),
            ("But your time costs too", ["Photographing, writing, replying, shipping.", "For fifteen pounds it is not worth it."], "Before selling, count the minutes it costs you as well."),
        ],
    ),
    dict(
        title="The 6 stages of being asked \"how much did that cost?\"",
        hook="We all do number 5 and none of us admits it.",
        photos="money",
        points=[
            ("The calculation", ["You decide in half a second whether to be honest.", "It depends entirely on who is asking."], "The same figure changes depending on the person."),
            ("The rounding", ["Downwards, naturally.", "\"About a hundred\", from a hundred and forty."], "\"About\" is the most flexible word in the language."),
            ("The unrequested explanation", ["Nobody asked for one.", "You give it anyway."], "Over-explaining is always a confession."),
            ("The \"it was second hand\"", ["If it is true, you say it with pride.", "And you should."], "Paying less for the same thing is not an excuse. It is a skill."),
            ("Checking the price afterwards", ["The moment you are alone.", "To see whether you did well."], "Nobody resists looking it up later. Nobody."),
            ("The peace", ["If you used it a lot, it was fine anyway.", "The price matters less than the use."], "The real bargain is the thing you reach for every day."),
        ],
    ),
    dict(
        title="6 things that change when you stop putting off one single thing",
        hook="You do not need a new life. You need to close one open loop.",
        photos="life",
        points=[
            ("The invisible list", ["It is not the written tasks that weigh.", "It is the five open ones you carry everywhere."], "What you put off does not sit still. It follows you."),
            ("The cost of thinking about it", ["You have thought about it twenty times in two months.", "Doing it took twenty minutes."], "Putting it off always costs more than doing it."),
            ("The smallest one", ["Not the important one: the one that irritates you most.", "Usually it is something ridiculous."], "Start with the ridiculous one. You need momentum, not heroism."),
            ("The disproportionate first step", ["Closing something small unlocks something big.", "It is not motivation. It is momentum."], "Nobody tidies one drawer and then stops there."),
            ("What you get back", ["Room in the house, room in your head.", "They always arrive together."], "You clear your head with your hands."),
            ("Tonight", ["Not Sunday. Not next month.", "One thing, twenty minutes, tonight."], "Next week already has too much in it."),
        ],
    ),
    dict(
        title="What nobody tells you about letting things go",
        hook="It is not discipline. It is understanding what you are actually holding.",
        photos="stuff",
        cta=True,
        points=[
            ("You are not keeping the object", ["You are keeping the person you were when you used it.", "Or the one you thought you would become."], "Wardrobes are full of versions of us that never arrived."),
            ("The money is already gone", ["\"It was expensive\" does not bring it back.", "Keeping it still costs you, every day, in space."], "Spent money is spent. The space you are paying for right now."),
            ("The guilt is not yours", ["An unused gift is not a lack of respect.", "The gesture already happened, years ago."], "You can keep the thought without keeping the object."),
            ("It ends up somewhere better", ["What is dead weight to you is exactly what someone was looking for.", "This happens every day."], "A thing you never use is worth nothing. In someone else's hands, it is."),
            ("The lightness afterwards", ["Nobody has ever cleared a room and regretted it.", "Not once."], "You will not miss it. That is the part you cannot believe beforehand."),
            ("One box", ["Not the whole house. Not the whole wardrobe.", "One box, today."], "Everyone who emptied a house started with one box."),
        ],
    ),
    dict(
        title="7 signs you are further along than you think",
        hook="You already do number 5 without noticing.",
        photos="life",
        points=[
            ("You compare yourself to last year", ["Not to other people's lives on a screen.", "That is a rare skill."], "The only comparison that tells you anything true is you, before."),
            ("You say no faster", ["To objects, to plans, to things that are not for you.", "Without explaining for half an hour."], "Saying no quickly is a form of respect, including for yourself."),
            ("You ask the price without flinching", ["And what it really costs, not what it cost once.", "Nobody finds it rude."], "Asking is not stinginess. It is knowing what you are doing."),
            ("You put things off less", ["Not never. Less."], "Real progress is boring and does not photograph well."),
            ("You buy less and choose better", ["Not to save money.", "Because you worked out what you actually use."], "Owning fewer but better things is an achievement, not a sacrifice."),
            ("You trust your own judgement", ["You look at something and know whether you need it.", "Without having to ask anyone."], "That took time. It is worth more than you think."),
            ("You stopped waiting for the right moment", ["It does not arrive.", "You just start."], "The right moment is an excuse with a nice name."),
        ],
    ),
    dict(
        title="The 6 stages of finally selling the thing that sat there for years",
        hook="Stage 5 you will not expect, and it beats the money.",
        photos="market",
        cta=True,
        points=[
            ("The hesitation", ["\"I might use it one day.\"", "You have been saying that for three years."], "Three years of \"one day\" is an answer."),
            ("The photo", ["The part that stops everyone.", "Ten minutes, light from the window, done."], "The barrier is not selling. It is starting."),
            ("The price", ["You look at what others are asking for the same thing today.", "Not at what you paid."], "What a thing is worth is set by its market, not by your memory of it."),
            ("The first message", ["It comes sooner than you expect.", "Someone was actually looking for it."], "What was clutter to you was a saved search to someone else."),
            ("The empty space", ["You look at where it used to stand.", "You feel oddly lighter."], "It was never the money. It was the thing watching you every day."),
            ("The second one", ["The moment the first is gone, you spot the next.", "There is no going back."], "It always starts with one object."),
        ],
    ),
    dict(
        title="Things you only learn when you are forced to choose",
        hook="Number 4 applies to wardrobes and to everything else.",
        photos="stuff",
        points=[
            ("Choosing is more tiring than working", ["That is why we put it off.", "It is not laziness. It is real effort."], "Deciding once costs less than thinking about it twenty times."),
            ("Maybe is not an answer", ["It is the decision moved further along.", "With interest."], "Every \"maybe\" is an appointment with yourself that you will miss."),
            ("Fewer options, more peace", ["Four jumpers you love beat twenty that are fine.", "You know this every morning."], "Choice stops being freedom when there is too much of it."),
            ("What you keep says who you are now", ["Not who you were, not who you hoped to be.", "Now."], "Look at what is around you: it is the most honest version of you there is."),
            ("You are allowed to get it wrong", ["You will give away something you miss.", "One thing in a hundred."], "Getting it wrong sometimes costs far less than never deciding."),
            ("It gets easy", ["The first ten decisions are hard.", "From the twentieth, they take two seconds."], "You do not need to be decisive to start. You become decisive by starting."),
        ],
    ),
    dict(
        title="7 things nobody tells you about starting something new",
        hook="Number 3 is why most people stop in week two.",
        photos="human",
        points=[
            ("The first week is a lie", ["Everything is easy because everything is novel.", "You mistake excitement for ability."], "What you build in week one tells you nothing about week six."),
            ("Week two is the real start", ["The novelty is gone and nothing has improved yet.", "This is where almost everyone quits."], "The boring middle is not a sign you chose wrong."),
            ("You will be bad at it", ["Visibly, embarrassingly bad.", "For longer than feels reasonable."], "Being bad at something is the entry fee, not a verdict."),
            ("Nobody is watching as closely as you think", ["The audience you are afraid of is busy with their own week.", "Nobody remembers your first attempt."], "The fear of looking stupid costs more than looking stupid ever does."),
            ("Progress is invisible from inside", ["You only see the gap between you and good.", "You never see the distance from where you began."], "Keep something from day one. It is the only honest mirror you will have."),
            ("Small and daily beats big and rare", ["Twenty minutes most days wins.", "Four hours once a month does not."], "Consistency is not discipline. It is just a lower bar, kept."),
            ("The only real requirement", ["Not talent, not a plan, not the right moment.", "Showing up again after the week it got boring."], "Everyone who is good at something was once two weeks in and unimpressive."),
        ],
    ),
    dict(
        title="The 8 lies we tell ourselves about time",
        hook="You have told yourself number 6 this week.",
        photos="life",
        countdown=True,
        points=[
            ("\"I do not have time\"", ["Usually it means it is not the priority.", "Which is allowed. It is just a different sentence."], "Saying what you actually chose is more honest than blaming the clock."),
            ("\"I will do it when things calm down\"", ["Things do not calm down.", "A quieter month has never once arrived on its own."], "If it only happens in the calm, it does not happen."),
            ("\"I work better under pressure\"", ["You work *faster* under pressure.", "Those are not the same."], "Deadlines do not improve work. They just end it."),
            ("\"It will only take a minute\"", ["It takes eleven.", "Every single time."], "Everything takes longer than the version of it in your head."),
            ("\"I am just checking one thing\"", ["Forty minutes later.", "You cannot name what you read."], "The phone does not steal hours. It borrows minutes and never returns them."),
            ("\"I am too tired to start\"", ["Often you are too undecided to start.", "Starting is what makes the tiredness lift."], "Energy comes after the first five minutes, not before."),
            ("\"Next week will be different\"", ["Next week already has a shape.", "And it looks like this one."], "Next week is this week with a different name."),
            ("\"There is still time\"", ["There is. That is the point.", "Not infinite, but more than you think today."], "Start badly today rather than perfectly in a year that never comes."),
        ],
    ),
    dict(
        title="Signs you are quietly doing better than you were",
        hook="Nobody claps for these. They count anyway.",
        photos="human",
        points=[
            ("You recover faster", ["A bad day used to cost a week.", "Now it costs a day."], "Resilience is not feeling less. It is coming back sooner."),
            ("You apologise less for existing", ["Fewer sorries in messages.", "Fewer explanations nobody asked for."], "You stopped treating your own needs as an inconvenience."),
            ("You can sit with a no", ["Yours or someone else's.", "Without rewriting it six times."], "A no you can say calmly is a kind of freedom."),
            ("Fewer people, more real ones", ["It looks like a smaller life.", "It is a heavier one."], "A shrinking circle is often a sign of better aim."),
            ("You ask instead of assuming", ["One awkward question.", "Instead of a week of imagining."], "Most of what we worry about dies the moment we ask."),
            ("You rest without earning it", ["Not as a reward for a productive day.", "Just because you are tired."], "You stopped needing a receipt to be allowed to stop."),
        ],
    ),
    dict(
        title="6 things that change when you stop waiting to feel ready",
        hook="Ready is not a feeling you get. It is one you build.",
        photos="human",
        points=[
            ("Ready arrives after, not before", ["You do not feel ready and then act.", "You act, badly, and ready catches up."], "Confidence is a receipt, not a ticket."),
            ("The research becomes hiding", ["Another video, another list, another plan.", "It feels like progress and costs nothing."], "At some point reading about it is how you avoid doing it."),
            ("You find out in a week", ["What you could have spent three months deciding.", "The real thing answers questions the plan cannot."], "One attempt teaches more than a month of thinking about attempting."),
            ("The first version is supposed to be bad", ["Everyone's was.", "You only ever saw their tenth."], "You are comparing your draft to someone else's final."),
            ("You stop needing permission", ["From a qualification, a person, a better moment.", "Nobody was ever going to give it."], "The permission you are waiting for is yours to sign."),
            ("One small, scary, today thing", ["Send the message. Post the thing. Book it.", "Ten minutes, not ten weeks."], "Do the smallest version of it before you talk yourself out of it."),
        ],
    ),
    dict(
        title="The 7 stages of a habit that actually sticks",
        hook="Most people quit at 3 and think they failed.",
        photos="life",
        points=[
            ("Day one is easy", ["Pure motivation, zero evidence.", "Enjoy it, it is not coming back."], "Motivation starts things. It has never finished one."),
            ("The first miss", ["You skip a day. Nothing collapses.", "But something in your head calls it over."], "Missing once is a day off. Missing twice is a decision."),
            ("The boredom", ["No visible progress, no novelty left.", "This is the stage people call failure."], "Boredom is not a sign it is wrong. It is a sign it is working."),
            ("Making it smaller", ["Twenty minutes becomes five.", "Five you will actually do."], "A habit you keep badly beats a habit you quit perfectly."),
            ("It stops needing a decision", ["You notice you did not argue with yourself about it.", "First time in weeks."], "A habit is just a decision you stopped having to make."),
            ("Someone notices", ["Not the result. The change in you.", "That lands harder than any number."], "Other people see the difference before the mirror does."),
            ("You would miss it now", ["Skipping feels worse than doing.", "That is the whole finish line."], "It stuck the moment it stopped feeling like effort."),
        ],
    ),
    dict(
        title="Things that are not laziness (even though they feel like it)",
        hook="Number 4 gets mistaken for it constantly.",
        photos="human",
        points=[
            ("Not starting because it is unclear", ["Your brain will not move without a first step.", "It is waiting for instructions, not for willpower."], "Write the next physical action, not the goal."),
            ("Too many open loops", ["Nine half-finished things, none done.", "Everything feels heavy because everything is still on."], "Close one small thing and the rest get lighter immediately."),
            ("Being tired in a way sleep does not fix", ["Decisions, noise, people, screens.", "Different tiredness needs different rest."], "Doing nothing and resting are not the same thing."),
            ("Avoiding something that scares you", ["It looks identical to laziness from outside.", "It is fear wearing a disguise."], "Name the thing you are avoiding. It shrinks about half."),
            ("Burnout mistaken for a character flaw", ["You did too much for too long.", "Then blamed yourself for stopping."], "You cannot discipline your way out of being depleted."),
            ("Needing the task to be smaller", ["Not more motivation.", "A smaller first step."], "If you cannot start, the task is too big, not you too weak."),
        ],
    ),
    dict(
        title="8 small things that fix a bad day faster than anything else",
        hook="Number 7 takes four minutes and nobody does it.",
        photos="life",
        countdown=True,
        points=[
            ("Going outside for ten minutes", ["No destination, no podcast.", "Just outside."], "Almost nothing survives a walk unchanged."),
            ("Water, then food", ["Half of a bad afternoon is a skipped lunch.", "Check that before anything else."], "Fix the body before you interrogate the mood."),
            ("Finishing one tiny thing", ["The email. The dish. The reply.", "Anything that moves to done."], "One closed loop changes the whole day's weather."),
            ("Putting the phone in another room", ["Not face down. Another room.", "The difference is enormous."], "Distance beats willpower, every time."),
            ("Making the bed, even at 6pm", ["It is absurd and it works.", "One surface in order."], "Order in one square metre spreads further than it should."),
            ("Telling one person the truth", ["\"Today was rough.\" That is the whole message.", "No analysis required."], "Said out loud, most things get about thirty per cent smaller."),
            ("Writing down what is actually wrong", ["Four minutes, by hand.", "Usually it is one thing, not eleven."], "Worry feels huge until it has to fit in a sentence."),
            ("Letting the day be bad", ["Not every day gets rescued.", "Some just end."], "A day you survive is not a day you failed."),
        ],
    ),
    dict(
        title="Things worth doing even when nobody sees them",
        hook="Especially when nobody sees them.",
        photos="human",
        points=[
            ("The work before the work", ["The reps, the drafts, the practice.", "None of it photographs."], "Everything that looks effortless had a boring part nobody posted."),
            ("Keeping a promise to yourself", ["The smallest one counts.", "You are the only witness and the only one affected."], "Self-trust is built from promises nobody else would notice you breaking."),
            ("Being kind with no audience", ["To a stranger, to a tired waiter, to yourself.", "No one is counting."], "Who you are when it earns you nothing is who you are."),
            ("Finishing what bores you", ["The last twenty per cent, the unglamorous part.", "This is where most things die."], "Finished and imperfect beats perfect and abandoned."),
            ("Doing it properly when nobody would know", ["The shortcut was available.", "You did not take it."], "Standards you keep in private are the only real ones."),
            ("Starting again, quietly", ["No announcement, no fresh start on a Monday.", "Just again, today."], "Beginning again is not failure. It is the actual skill."),
        ],
    ),
]

CAPTION_SAVE = "Save it, and send it to whoever needs to read it."
CAPTION_SHARE = "What is the stuff in your house actually worth? getsowld.com"
HASHTAGS = "#secondhand #declutter #thrifting #reselling #minimalism #homeorganisation"

# The last slide, only for topics with "cta": what Sowld actually does.
CTA = dict(
    title="What is that thing actually worth?",
    lines=["Sowld compares a second hand listing to similar items on sale right now and estimates what it is worth."],
    small="Free, 15 checks a month. Estimates are indicative.",
    url="getsowld.com",
)

# The site is off the profile's link in bio while it is not ready, so the
# Sowld slide is off too: sending someone to a URL they cannot tap from the
# bio wastes the last slide and makes the post read as an ad for nothing.
# One line to turn back on the day the link returns.
CTA_ENABLED = False

SLOTS = 5  # carousels a day


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
        if not 1 <= len(lines) <= 6:
            errors.append(f"point {i} needs 1 to 6 lines")
        for j, line in enumerate(lines, 1):
            text(line, f"point {i} line {j}", 95)
        text(punch, f"point {i} closing line", 75)
    if "hashtags" in topic and not (isinstance(topic["hashtags"], str) and topic["hashtags"].startswith("#") and len(topic["hashtags"]) <= 200):
        errors.append("hashtags must be one string of up to 200 characters, starting with #")
    if "cta" in topic and not isinstance(topic["cta"], bool):
        errors.append("cta must be true or false")
    if topic.get("photos", "stuff") not in PHOTO_SETS:
        errors.append(f"photos must be one of {sorted(PHOTO_SETS)}")
    return errors


def bank_topic(date: _dt.date, slot: int = 1) -> dict:
    """A written topic for a date and slot, when a run has none of its own."""
    n = (date - EPOCH).days * SLOTS + (slot - 1)
    return EVERYDAY[n % len(EVERYDAY)]


def carousel(date: _dt.date, slot: int = 1, topic: dict | None = None) -> dict:
    """The slides' content for a date and slot, one photo per slide (cover first), the same every time."""
    topic = topic or bank_topic(date, slot)
    rng = _random.Random(date.toordinal() * 10 + slot)
    pool = list(PHOTO_SETS.get(topic.get("photos", "stuff"), PHOTO_SETS["stuff"]))
    rng.shuffle(pool)
    need = 1 + len(topic["points"])
    picks = (pool * (need // len(pool) + 1))[:need]
    # The title opens the caption, so the next runs can see what was already posted.
    cta = bool(topic.get("cta")) and CTA_ENABLED
    tail = CAPTION_SHARE if cta else CAPTION_SAVE
    caption = f"{topic['title']}\n\n{topic['hook']}\n\n{tail}\n\n{topic.get('hashtags') or HASHTAGS}"
    count = len(topic["points"])
    numbers = list(range(count, 0, -1)) if topic.get("countdown") else list(range(1, count + 1))
    return dict(date=date.isoformat(), slot=slot, title=topic["title"], points=topic["points"],
                numbers=numbers, photos=picks, caption=caption, cta=cta)
