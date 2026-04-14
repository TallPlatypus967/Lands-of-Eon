
def godshard_count(player):
    """Count how many Godshard-type items the player holds."""
    shard_names = {"Godshard Fragment", "Second Godshard", "Third Godshard"}
    return sum(1 for it in player.inventory if it["name"] in shard_names)

def ritual_unlocked(player):
    """Return True if player has everything needed to attempt the ritual."""
    return (
            godshard_count(player) >= 2 and
            "crown_returned_throne" in player.flags and
            "knows_ritual_phrase" in player.flags and
            "found_throne_room" in player.flags and
            "read_ashen_tablet" in player.flags
    )

def confrontation_unlocked(player):
    """Return True if the Unmade/Maelvyr confrontation should trigger."""
    return (
            "looked_void_well" in player.flags and
            any(f in player.flags for f in ("full_truth_known", "sael_spoke_maelvyr",
                                            "found_sealed_sanctum")) and
            "confrontation_done" not in player.flags
    )


def event_chamber_of_agreement(player, room):
    """The room where the Unmade first contacted Maelvyr — a lore flashback room."""
    hr("═", colour=Fore.MAGENTA)
    print(c("  THE CHAMBER OF THE AGREEMENT", Fore.MAGENTA + Style.BRIGHT))
    hr("═", colour=Fore.MAGENTA)
    print()
    wrap("The scorched circle on the floor is not a burn. It is an absence — "
         "a place where something was present so completely that the stone beneath it "
         "stopped being stone for a moment and has not entirely recovered.", Fore.MAGENTA)
    pause()
    wrap("At the edge of the circle: two sets of footprints, pressed into the stone "
         "as though the floor was briefly soft. One set — human. One set — not. "
         "The not-human set has no clear shape. The impressions are simply wrong, "
         "in the way that a shadow is wrong when it falls in the direction the light came from.",
         Fore.MAGENTA)
    pause()
    player.flags.add("found_chamber_of_agreement")

    done = room.get("_agreement_done", set())
    while True:
        opts = []
        if "circle" not in done:   opts.append("Step into the circle")
        if "stone" not in done:    opts.append("Examine the Agreement Stone, if you have it")
        if "read" not in done:     opts.append("Look for inscriptions")
        if "candle" not in done and player.has_item("Candle"):
            opts.append("Hold the Candle over the footprints")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Step into the circle":
            done.add("circle")
            wrap("The stone inside the circle is a different temperature — not cold, not warm. "
                 "Absent. As though it has no opinion on temperature anymore. "
                 "You stand in the exact centre. Nothing happens. "
                 "And then — briefly, a fraction of a second — "
                 "you understand what it felt like to be Maelvyr in this room. "
                 "To be offered everything. To say yes.", Fore.MAGENTA)
            # Dissonance whisper — heard only if player is in the circle
            if "circle" in done and random.random() < 0.5:
                print()
                wrap("From somewhere that is not a direction: a sound. "
                     "Not a voice. Not music. Something between the two — "
                     "a resonance that your mind keeps trying to interpret as words "
                     "and keeps failing. "
                     "It is not threatening. It is simply present. "
                     "The name for what you are hearing, if you knew it, is Dissonance.",
                     Fore.MAGENTA + Style.BRIGHT)
                player.flags.add("heard_dissonance")
            wrap("The feeling passes. You step out.", Fore.MAGENTA)
            player.flags.add("stood_in_circle")
            if "full_truth_known" in player.flags:
                wrap("You understand, now, what the Unmade offered. "
                     "And you understand why he took it.", Fore.MAGENTA + Style.BRIGHT)

        elif ch == "Examine the Agreement Stone, if you have it":
            done.add("stone")
            if player.has_item("Agreement Stone"):
                wrap("You hold the Agreement Stone over the circle. "
                     "The warm side turns toward the circle. The cold side faces away from it — "
                     "or rather, the cold side faces toward the exits, toward the rest of the ruins, "
                     "toward the world. "
                     "The stone knows what happened here. The warm side is the side that agreed.",
                     Fore.MAGENTA + Style.BRIGHT)
                player.flags.add("agreement_stone_circle")
                wrap("Something in the stone clicks — not physically. Conceptually. "
                     "You understand that the Agreement Stone can be used to invoke "
                     "what happened here. It is a record. A receipt.", Fore.MAGENTA)
                player.flags.add("knows_agreement_stone_use")
            else:
                wrap("You don't have the Agreement Stone. "
                     "If such a thing exists, it would respond to this place.")

        elif ch == "Look for inscriptions":
            done.add("read")
            wrap("The walls of this room have inscriptions — but they are not Eldrosian. "
                 "They are in the older script, the pre-imperial one. "
                 "You can read fragments: "
                 "'...the offer was made once before, to one who refused...' "
                 "And: '...the name of the one who refused is: ___' — damaged, illegible. "
                 "And: '...the Unmade requires a willing door. It cannot force entry. "
                 "It can only wait...'", Fore.CYAN)
            player.flags.add("agreement_chamber_inscription")

        elif ch == "Hold the Candle over the footprints":
            done.add("candle")
            wrap("The candle's flame turns red. Not the blue of old script — red. "
                 "In the red light, the not-human footprints resolve further. "
                 "They are not footprints at all. They are places where the Unmade's attention "
                 "rested — where it pressed against the world hard enough to leave a mark. "
                 "Each 'footprint' is the same shape: a small, perfect circle. "
                 "Like the wells.", Fore.RED + Style.BRIGHT)
            player.flags.add("candle_agreement_chamber")

        room["_agreement_done"] = done


def event_ritual_chamber(player, room):
    """The Ritual Chamber — only reachable if ritual_unlocked()."""
    hr("═", colour=Fore.YELLOW)
    print(c("  THE RITUAL CHAMBER", Fore.YELLOW + Style.BRIGHT))
    hr("═", colour=Fore.YELLOW)
    print()

    def ritual_missing_report(player) -> str:
        """
        Return a string describing exactly what the player needs
        to complete the ritual, and where to find each missing element.
        """
        missing = []

        shards_held = godshard_count(player)
        if shards_held < 3:
            needed = 3 - shards_held
            shard_hints = []
            if not player.has_item("Godshard Fragment") and "obtained_godshard_1" not in player.flags:
                shard_hints.append("the First Godshard (in Emperor Vaelan's throne room — "
                                   "still in his hand)")
            elif not player.has_item("Godshard Fragment"):
                shard_hints.append("the First Godshard (you held it but no longer do — "
                                   "check the Place Between)")
            if not player.has_item("Second Godshard") and "obtained_godshard_2" not in player.flags:
                shard_hints.append("the Second Godshard (carried by the Corrupted High Priest "
                                   "in the deep ruins)")
            elif not player.has_item("Second Godshard"):
                shard_hints.append("the Second Godshard (you held it but no longer do — "
                                   "check the Place Between)")
            if not player.has_item("Third Godshard") and "obtained_godshard_3" not in player.flags:
                shard_hints.append("the Third Godshard (resting on the plinth in the "
                                   "Hall of the Shattered Crown)")
            elif not player.has_item("Third Godshard"):
                shard_hints.append("the Third Godshard (you held it but no longer do — "
                                   "check the Place Between)")
            missing.append(f"  You need {needed} more Godshard(s):")
            for hint in shard_hints:
                missing.append(f"    - {hint}")

        if "crown_returned_throne" not in player.flags:
            if not player.has_item("Old Crown"):
                missing.append("  The Old Crown has not been returned to Vaelan's throne room.")
                missing.append("    - Find the Old Crown (in the lesser throne room, depth 5+)")
            else:
                missing.append("  The Old Crown must be placed on Vaelan's throne "
                               "(visit the Throne of Eldros-Verath).")

        if "knows_ritual_phrase" not in player.flags:
            missing.append("  You do not yet know the ritual phrase.")
            missing.append("    - Find the Codex of the First Age in the Whispering Library.")
            missing.append("    - You will need the Crystal Mirror to decode it.")

        if "found_throne_room" not in player.flags:
            missing.append("  You have not yet found the Throne of Eldros-Verath.")
            missing.append("    - It is in the deep ruins (depth 13+).")

        if "read_ashen_tablet" not in player.flags:
            missing.append("  You have not read the Ashen Tablet.")
            missing.append("    - It is found behind the Iron Key door (depth 4+).")

        return "\n".join(missing) if missing else ""

    if not ritual_unlocked(player):
        wrap("The dais is present. The hollow at its centre is present. "
             "The room is waiting — but not for you yet.", Fore.LIGHTBLUE_EX + Style.BRIGHT)
        print()

        report = ritual_missing_report(player)
        if report:
            wrap("You sense what is lacking:", Fore.YELLOW)
            print(c(report, Fore.YELLOW))
        return



    wrap("The nine-circle diagram on the dais glows faintly — "
         "not from any source you can see, but from the diagram itself. "
         "The hollow at the centre pulses at the same frequency as the Godshards you carry. "
         "The room is waiting.", Fore.YELLOW)
    print()
    wrap("You hold three fragments of Vaethar's divided form. "
         "The Codex told you what to say. The throne room showed you what was lost. "
         "The shards are trembling in your hands.", Fore.YELLOW + Style.BRIGHT)
    print()

    ch = prompt(["Attempt the ritual",
                 "Examine the dais more carefully",
                 "Leave — you are not ready"])

    if ch == "Leave — you are not ready":
        wrap("You step back. The dais continues to pulse. It will wait.")
        return

    elif ch == "Examine the dais more carefully":
        wrap("The nine circles of the diagram correspond to the nine wells. "
             "The central tenth circle — filled solid on the parchment — "
             "is here represented differently: as an absence. A void at the centre "
             "of the nine. The hollow where you would place the shards sits "
             "precisely in the middle of that absence.", Fore.CYAN)
        wrap("On the rim of the dais, barely visible: "
             "'What was divided will cohere. What cohered will choose. "
             "The choice is the vessel's alone.'", Fore.CYAN)
        player.flags.add("read_dais_inscription")
        return  # let them come back

    elif ch == "Attempt the ritual":
        _perform_ritual(player, room)


def _perform_ritual(player, room):
    """The ritual sequence — branches to Ascension or Atheron endings."""
    hr("═", colour=Fore.YELLOW)
    wrap("You place the three Godshard Fragments into the hollow at the centre of the dais. "
         "They fit. Of course they fit. They were made for this, or something like this — "
         "they remember being whole.", Fore.YELLOW)
    pause()
    wrap("The frequency you have felt in your chest since you first picked up a shard "
         "increases. The nine circles on the dais begin to glow, each a different colour. "
         "The hollow where the shards rest glows gold.", Fore.YELLOW + Style.BRIGHT)
    pause()
    wrap("The room is shaking. Not violently — at the same frequency as the shards. "
         "A resonance. The walls, the stone, the air: all of it is vibrating at the "
         "pitch of something that was whole and fragmented and is approaching wholeness again.",
         Fore.YELLOW + Style.BRIGHT)
    pause()

    wrap("The Codex said to speak three things. You know what they are.", Fore.YELLOW)
    print()
    wrap("What do you say?", Fore.MAGENTA)
    spoken = secret_input(player)

    # Check for correct ritual phrase (flexible — various wordings accepted)
    vaethar_named = any(w in spoken for w in ("vaethar",))
    atheron_named  = any(w in spoken for w in ("atheron",))
    vessel_claimed = any(w in spoken for w in ("vessel","i am the vessel","i am vessel"))

    correct = vaethar_named and atheron_named and vessel_claimed
    partial = sum([vaethar_named, atheron_named, vessel_claimed]) >= 2

    if correct:
        # Check if Atheron is near (player has been to dragon hall recently — use flag)
        if "atheron_named" in player.flags and "studied_atheron" in player.flags:
            # Atheron responds to the ritual
            _ending_atheron(player)
        else:
            _ending_ascension(player)
    elif partial:
        # Incomplete phrase — ritual partially fires, dangerous
        _ending_ritual_partial(player)
    else:
        wrap("The shards pulse once — then dim. Whatever the ritual requires, "
             "it is not those words. The shards remain in the dais. "
             "The room settles. You may try again.", Fore.RED)
        player.flags.add("ritual_failed_once")


def _ending_ascension(player):
    """ENDING 1: Full Ascension — the player becomes the vessel."""
    print()
    hr("═", colour=Fore.YELLOW + Style.BRIGHT)
    print(c("  ENDING: THE VESSEL", Fore.YELLOW + Style.BRIGHT))
    hr("═", colour=Fore.YELLOW + Style.BRIGHT)
    print()
    pause()
    wrap("The shards respond. All three at once, immediately, without hesitation. "
         "The gold light from the hollow expands — not outward into the room "
         "but inward, into you, through your hands where they rest on the dais.",
         Fore.YELLOW + Style.BRIGHT)
    pause()
    wrap("It is not painful. That is the most surprising thing. "
         "It is the sensation of something that was scattered across centuries "
         "finding a point to cohere around. "
         "The point is you.", Fore.YELLOW + Style.BRIGHT)
    pause()
    wrap("Vaethar gave their form willingly, once, to empower a line of mortals. "
         "The line ended. The shards waited. "
         "They were not waiting for an emperor. "
         "They were waiting for someone who came looking without being sent.",
         Fore.YELLOW + Style.BRIGHT)
    pause()
    wrap("The nine-circle diagram on the dais blazes — all nine colours simultaneously — "
         "and then goes dark. The room goes dark. "
         "Everything goes dark.", Fore.YELLOW + Style.BRIGHT)
    pause()
    wrap("And then you can see in the dark.", Fore.YELLOW + Style.BRIGHT)
    pause()

    # Check what the player knows — the ending text responds to their discoveries
    print()
    hr(colour=Fore.YELLOW)

    if "full_truth_known" in player.flags:
        wrap("You know everything that happened here. You know who built this place. "
             "You know who destroyed it, and what they became, and why. "
             "You know that the Unmade is still present, somewhere beneath the stones, "
             "patient in the way that things are patient when they have been waiting "
             "longer than everything else.", Fore.YELLOW)
        wrap("And you know that you are, now, something it will have to account for.", Fore.YELLOW + Style.BRIGHT)
    else:
        wrap("You carry pieces of the truth, and gaps where the truth should be. "
             "It does not matter. What you have become does not require you "
             "to know everything. It only required you to choose.", Fore.YELLOW)

    print()
    wrap("Above the ruins of Eldros-Verath, the ground shakes. "
         "Elsewhere in the world — thousands of miles away — "
         "something that calls itself Dravennis stops mid-motion "
         "and looks toward the horizon.", Fore.YELLOW)
    pause()
    wrap("The ancient godshards have re-activated. "
         "The world's foundations shift, briefly, under the weight of something "
         "returning to what it was — or becoming what it was always going to be.",
         Fore.YELLOW + Style.BRIGHT)
    pause()

    print()
    hr("═", colour=Fore.YELLOW + Style.BRIGHT)
    print(c(f"  {player.name.upper()} — VESSEL OF VAETHAR", Fore.YELLOW + Style.BRIGHT))
    print(c("  The ruins are yours now, as much as anything can be yours.", Fore.YELLOW))
    print(c(f"  Rooms explored: {player.visited_rooms}  |  Gold: {player.gold}", Fore.YELLOW))
    found = sum(1 for f in ALL_FLAGS if f in player.flags and f in DISCOVERY_TEXT)
    print(c(f"  Discoveries: {found} of {len(DISCOVERY_TEXT)}", Fore.CYAN))
    hr("═", colour=Fore.YELLOW + Style.BRIGHT)
    sys.exit(0)


def _ending_atheron(player):
    """ENDING 2: Atheron's Wrath — the dragon wakes and erupts outward."""
    print()
    hr("═", colour=Fore.RED + Style.BRIGHT)
    print(c("  ENDING: THE KING WAKES", Fore.RED + Style.BRIGHT))
    hr("═", colour=Fore.RED + Style.BRIGHT)
    print()
    pause()
    wrap("The shards respond — but so does something else. "
         "Far below, or perhaps not so far as you thought, something stirs. "
         "The frequency of the ritual has reached somewhere it was not intended to reach.",
         Fore.RED)
    pause()
    wrap("The floor of the ritual chamber cracks. Not from the ritual — "
         "from below the ritual. Something immense has shifted its weight "
         "for the first time in a very long time.", Fore.RED)
    pause()
    wrap("The gold light from the dais and the cracks in the floor "
         "meet in the room. The frequencies are not the same. "
         "They are not compatible. The room begins to come apart.", Fore.RED + Style.BRIGHT)
    pause()
    wrap("You run.", Fore.RED + Style.BRIGHT)
    pause()
    wrap("Behind you — and then around you, and then above you — "
         "something erupts through the ruins of Eldros-Verath "
         "with a force that is not fire and is not sound "
         "but has qualities of both.", Fore.RED + Style.BRIGHT)
    pause()
    wrap("Atheron. King of Dragons. "
         "Oldest living thing in these ruins, or beneath them. "
         "Awake.", Fore.RED + Style.BRIGHT)
    pause()
    wrap("He does not pursue you. "
         "You are interesting but not the thing he woke for. "
         "The thing he woke for is older than you, "
         "and it is beneath the well, and he is going toward it "
         "with an intention that has been forming for centuries.",
         Fore.RED)
    pause()
    wrap("You emerge from the ruins at speed, "
         "covered in dust, carrying three godshards that are still pulsing, "
         "as behind you the ruins of the first empire erupt outward "
         "under the force of the oldest dragon finding something "
         "it has been waiting to confront.", Fore.RED)
    pause()

    print()
    hr(colour=Fore.RED)
    wrap("Whether he wins or loses — whether the Unmade is destroyed or merely driven back — "
         "you do not know. You were not there for that part. "
         "You were running.", Fore.RED)
    if "full_truth_known" in player.flags:
        wrap("But you know enough to understand what Atheron was doing. "
             "He was correcting a mistake that the world had been living with "
             "since the Night of Collapse.", Fore.RED + Style.BRIGHT)
    print()
    hr("═", colour=Fore.RED + Style.BRIGHT)
    print(c(f"  {player.name.upper()} — THEY WHO WOKE THE KING", Fore.RED + Style.BRIGHT))
    print(c("  Whether this was wise is a question for historians.", Fore.RED))
    print(c(f"  Rooms explored: {player.visited_rooms}  |  Gold: {player.gold}", Fore.YELLOW))
    found = sum(1 for f in ALL_FLAGS if f in player.flags and f in DISCOVERY_TEXT)
    print(c(f"  Discoveries: {found} of {len(DISCOVERY_TEXT)}", Fore.CYAN))
    hr("═", colour=Fore.RED + Style.BRIGHT)
    sys.exit(0)


def _ending_ritual_partial(player):
    """Bad ritual — incomplete phrase causes collapse/corruption."""
    print()
    hr("═", colour=Fore.RED)
    print(c("  THE RITUAL COLLAPSES", Fore.RED + Style.BRIGHT))
    hr("═", colour=Fore.RED)
    print()
    wrap("The shards begin to respond — and stop. "
         "Something in the phrase was missing. "
         "The ritual is not a mechanism. It cannot run halfway. "
         "What it does when interrupted is not the same as not running.",
         Fore.RED)
    pause()
    wrap("The gold light inverts. "
         "The nine-circle diagram does not go dark — it goes black, "
         "a black that is brighter than the gold was. "
         "The shards leave your hands — not gently — "
         "and scatter across the floor of the chamber.",
         Fore.RED + Style.BRIGHT)
    pause()
    wrap("Something has been summoned that is not Vaethar's power. "
         "Something was listening to the ritual "
         "and moved into the space the ritual opened.", Fore.RED + Style.BRIGHT)
    pause()
    wrap("The room darkens. The darkness is not empty.", Fore.RED + Style.BRIGHT)
    pause()
    # This transitions into the confrontation
    player.flags.add("ritual_summoned_confrontation")
    _confrontation(player, forced=True)


def _confrontation(player, forced=False):
    """
    The Confrontation — the Unmade speaks through the shadow of Maelvyr.
    Triggered at the Void-well (if confrontation_unlocked) or by a collapsed ritual.
    Branches to: Bargain ending, or player refuses and continues.
    """
    print()
    hr("═", colour=Fore.LIGHTBLUE_EX + Style.BRIGHT)
    print(c("  THE OFFER", Fore.LIGHTBLUE_EX + Style.BRIGHT))
    hr("═", colour=Fore.LIGHTBLUE_EX + Style.BRIGHT)
    print()
    pause()

    if forced:
        wrap("The darkness in the ritual chamber coalesces. "
             "It does not fill the room — it occupies a point in the room, "
             "and that point is enough.", Fore.LIGHTBLUE_EX + Style.BRIGHT)
    else:
        wrap("The darkness in the well rises. "
             "Not the darkness of depth — this darkness has direction. "
             "It rises toward you with purpose.", Fore.LIGHTBLUE_EX + Style.BRIGHT)
    pause()

    wrap("A shape forms at the centre of the dark. "
         "Humanoid. Robed. You have seen this shape before — "
         "in the Crystal Mirror in the throne room, "
         "standing before Emperor Vaelan. "
         "It is the shape of Maelvyr, cast in shadow, "
         "at a distance of thousands of miles "
         "and also directly in front of you.",
         Fore.MAGENTA)
    pause()
    wrap("When it speaks, the voice is not one voice. "
         "It is a voice with something vast behind it, using it.", Fore.MAGENTA)
    print()
    pause()

    wrap("  'You have come further than most.'", Fore.MAGENTA + Style.BRIGHT)
    pause()
    wrap("  'You know what this place is. You know what was agreed here. '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'You know that the agreement was not a mistake — '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'it was an opening. A necessary opening.'", Fore.MAGENTA + Style.BRIGHT)
    pause()

    # Adapt dialogue based on what player knows
    if "full_truth_known" in player.flags:
        wrap("  'You know my name. Both of them. '", Fore.MAGENTA + Style.BRIGHT)
        wrap("  'That is rare. That earns you honesty: '", Fore.MAGENTA + Style.BRIGHT)
        wrap("  'I am not offering you what I offered him. '", Fore.MAGENTA + Style.BRIGHT)
        wrap("  'He wanted to survive. You already have what he wanted. '", Fore.MAGENTA + Style.BRIGHT)
        wrap("  'I am offering you what comes after survival.'", Fore.MAGENTA + Style.BRIGHT)
    else:
        wrap("  'You carry pieces of the truth. Not all of them. '", Fore.MAGENTA + Style.BRIGHT)
        wrap("  'That is fine. The truth is not a prerequisite for the offer.'", Fore.MAGENTA + Style.BRIGHT)
    pause()

    wrap("  'There is a crack in the world. I came through it. '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'The crack is not closing. It does not need to close. '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'What it needs is someone to stand on this side of it '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'and call it a door.'", Fore.MAGENTA + Style.BRIGHT)
    pause()
    wrap("  'You. Here. Now. That is what I want. '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'The price is your mortality. The name Demongod was coined for what you would become. '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'The man who coined it meant it as a warning. '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'I offer it as a title.'", Fore.MAGENTA + Style.BRIGHT)
    pause()

    print()
    print(c("  The shadow waits. The darkness is patient.", Fore.LIGHTBLUE_EX + Style.BRIGHT))
    print()

    ch = prompt([
        "Refuse the offer",
        "Ask what the Unmade actually is",
        "Ask what happened to Maelvyr after Eldros",
        "Accept the offer",
    ])

    if ch == "Ask what the Unmade actually is":
        wrap("The shadow tilts — almost amusement. "
             "'What I am is a question with no satisfying answer. '", Fore.MAGENTA)
        wrap("'I existed before the wells formed. Before Thaun. Before Arukiel. '", Fore.MAGENTA)
        wrap("'Before Atheron. Before the gods — before Myrrakhel herself. '", Fore.MAGENTA)
        wrap("'I am what was here when there was nothing else. '", Fore.MAGENTA)
        wrap("'The nothing else, given intention.'", Fore.MAGENTA + Style.BRIGHT)
        pause()
        wrap("'The name Unmade was given to me by beings who wanted to believe '", Fore.MAGENTA)
        wrap("'that I was the absence of something, rather than a presence. '", Fore.MAGENTA)
        wrap("'They were wrong. '", Fore.MAGENTA)
        wrap("'I have always been a presence. I have simply been patient.'", Fore.MAGENTA + Style.BRIGHT)
        player.flags.add("unmade_spoke_its_nature")
        pause()
        # Fall through to choice again
        ch2 = prompt([
            "Refuse the offer",
            "Ask what happened to Maelvyr after Eldros",
            "Accept the offer",
        ])
        ch = ch2

    if ch == "Ask what happened to Maelvyr after Eldros":
        wrap("'He left.' The shadow's voice carries something — "
             "not pride, not contempt. Ownership.", Fore.MAGENTA)
        wrap("'He killed the emperor. He took what the emperor held. '", Fore.MAGENTA)
        wrap("'He became what the word Demongod was invented for. '", Fore.MAGENTA)
        wrap("'And then he walked away from these ruins '", Fore.MAGENTA)
        wrap("'and built something elsewhere. '", Fore.MAGENTA)
        wrap("'He drinks the blood of magi. He grows. '", Fore.MAGENTA)
        wrap("'He is a door, as I said — and he is learning '", Fore.MAGENTA)
        wrap("'to open wider.'", Fore.MAGENTA + Style.BRIGHT)
        player.flags.add("unmade_spoke_maelvyr")
        pause()
        if "sael_dravennis_connection" not in player.flags:
            player.flags.add("sael_dravennis_connection")
            wrap("The line between Maelvyr and Dravennis is now unmistakable.", Fore.MAGENTA)
        ch2 = prompt(["Refuse the offer", "Accept the offer"])
        ch = ch2

    if ch == "Accept the offer":
        _ending_bargain(player)
    else:
        _confrontation_refused(player)


def _confrontation_refused(player):
    """Player refuses the Unmade's offer — they continue."""
    wrap("The shadow is still.", Fore.MAGENTA)
    pause()
    wrap("  'Interesting.'", Fore.MAGENTA + Style.BRIGHT)
    pause()
    wrap("  'No one has said no in a very long time. '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'The last one who refused — I did not record their name. '", Fore.MAGENTA + Style.BRIGHT)
    wrap("  'Perhaps I should have.'", Fore.MAGENTA + Style.BRIGHT)
    pause()
    wrap("The shadow collapses — not with drama, not with threat. "
         "Simply: it was there, and then it was not. "
         "The darkness returns to being ordinary darkness.", Fore.LIGHTBLUE_EX + Style.BRIGHT)
    pause()
    wrap("The well — or the ritual chamber — is just a room again. "
         "You are still here. You are still yourself. "
         "Whatever that means, now.", Fore.LIGHTBLUE_EX + Style.BRIGHT)
    print()
    player.flags.add("confrontation_done")
    player.flags.add("refused_the_offer")
    player.max_hp += 10
    player.attack += 2
    print(c("  Something about refusal has weight. Max HP +10, ATK +2.", Fore.GREEN))
    pause()
    wrap("You can still complete the ritual, if you have what you need. "
         "Or you can leave. The ruins will stand regardless.", Fore.YELLOW)


def _ending_bargain(player):
    """ENDING 3: The Bargain — player accepts the Unmade's offer. Dark ending."""
    print()
    hr("═", colour=Fore.RED + Style.BRIGHT)
    print(c("  ENDING: THE AGREEMENT", Fore.RED + Style.BRIGHT))
    hr("═", colour=Fore.RED + Style.BRIGHT)
    print()
    pause()
    wrap("'Yes.' The word leaves your mouth before you have finished deciding.",
         Fore.RED)
    pause()
    wrap("The shadow does not celebrate. "
         "It simply begins.", Fore.RED)
    pause()
    wrap("The cold comes first. Not the cold of depth or the cold of the well — "
         "the cold of something pressing through from the other side of a crack "
         "in the world, "
         "using the opening you have just made by agreeing to be it.",
         Fore.RED + Style.BRIGHT)
    pause()
    wrap("It is not painful. He told you it would not be. "
         "He was right about that, at least.", Fore.RED + Style.BRIGHT)
    pause()
    wrap("What it is: the sensation of everything that makes you mortal "
         "— your ending, your limitation, your smallness — "
         "being recognised, acknowledged, "
         "and then set aside.", Fore.RED + Style.BRIGHT)
    pause()
    wrap("What replaces it is not warmth. "
         "It is the absence of the cold. "
         "You are not full. You are hollow. "
         "You carry the void, as Thaun carries it, "
         "but Thaun chose that before the world had words for choice.", Fore.RED + Style.BRIGHT)
    pause()
    wrap("You did not.", Fore.RED + Style.BRIGHT)
    pause()

    print()
    hr(colour=Fore.RED)

    if "full_truth_known" in player.flags:
        wrap("You know exactly what you have become. "
             "You knew when you said yes. "
             "The word DEMONGOD is not a warning anymore. "
             "It is a description.", Fore.RED + Style.BRIGHT)
    else:
        wrap("You do not fully understand what you have become. "
             "That, too, was part of the offer.", Fore.RED)

    print()
    wrap("Thousands of miles away, in a city you have never visited, "
         "Dravennis pauses. Looks toward the horizon. "
         "Recognises something.", Fore.RED)
    pause()
    wrap("There are now two doors where there was one.", Fore.RED + Style.BRIGHT)
    print()
    hr("═", colour=Fore.RED + Style.BRIGHT)
    print(c(f"  {player.name.upper()} — THE SECOND AGREEMENT", Fore.RED + Style.BRIGHT))
    print(c("  The Unmade has been patient. It is less patient now.", Fore.RED))
    print(c(f"  Rooms explored: {player.visited_rooms}  |  Gold: {player.gold}", Fore.YELLOW))
    found = sum(1 for f in ALL_FLAGS if f in player.flags and f in DISCOVERY_TEXT)
    print(c(f"  Discoveries: {found} of {len(DISCOVERY_TEXT)}", Fore.CYAN))
    hr("═", colour=Fore.RED + Style.BRIGHT)
    sys.exit(0)

def _ending_truth(player):
    """ENDING 4 (win): Escape with full knowledge. Bittersweet."""
    print()
    hr("═", colour=Fore.GREEN)
    print(c("  ENDING: THE WITNESS", Fore.GREEN + Style.BRIGHT))
    hr("═", colour=Fore.GREEN)
    print()
    pause()
    wrap("You climb the stairs. The ruins do not stop you. "
         "Nothing down here has ever been trying to stop you — "
         "it has been waiting to be found.", Fore.GREEN)
    pause()
    wrap("Daylight.", Fore.GREEN + Style.BRIGHT)
    pause()
    wrap(f"  {player.name} emerges from the Ruins of Eldros-Verath "
         "carrying everything. The truth of the empire — "
         "what it was, what it built, what it loved, what destroyed it. "
         "The name Maelvyr, which you will not write down. "
         "The name Dravennis, which is the same name. "
         "The shape of the Unmade, which you saw in the well "
         "and which was old when the wells were new.", Fore.GREEN)
    pause()

    if "refused_the_offer" in player.flags:
        wrap("You were offered what Maelvyr was offered, and you said no. "
             "You are not sure what that means for the world — "
             "whether refusing closes anything, or only delays it. "
             "You suspect: delays it. "
             "But the refusal was real, and it was yours, and it meant something "
             "to the thing that made the offer.", Fore.GREEN + Style.BRIGHT)
    elif "void_well_witnessed" in player.flags:
        wrap("You spoke his name into the well and the well said: witnessed. "
             "You do not know what that means. "
             "You suspect no one does, including the well.", Fore.GREEN)

    print()
    wrap("The ruins remain. "
         "The darkness below them does not care that you have left. "
         "It has been here longer than you. It will be here after.",
         Fore.GREEN + Style.BRIGHT)
    pause()

    print()
    found = sum(1 for f in ALL_FLAGS if f in player.flags and f in DISCOVERY_TEXT)
    print(c(f"  Rooms explored: {player.visited_rooms}  |  Gold: {player.gold}", Fore.YELLOW))
    print(c(f"  Discoveries: {found} of {len(DISCOVERY_TEXT)}", Fore.CYAN))
    if found >= len(DISCOVERY_TEXT) - 3:
        print(c("  You found almost everything.", Fore.CYAN + Style.BRIGHT))
    else:
        print(c(f"  {len(DISCOVERY_TEXT) - found} secrets remain in the dark.", Fore.CYAN))
    hr("═", colour=Fore.GREEN)
    print()

    ch = prompt([
        "Descend again — there is still more to find",
        "End here"
    ])

    if ch.startswith("Descend"):
        # Reset run state, keep everything earned
        player.descent += 1
        player.depth = 0
        player.visited_rooms = 0
        player.hp = min(player.hp, player.max_hp)
        print()
        wrap("You turn back at the threshold. The light behind you dims. "
             "The dark below is the same dark. It has been waiting.", Fore.YELLOW)
        if player.descent == 2:
            wrap("You notice something you did not see before: a second staircase, "
                 "deeper, that was not visible on your first descent. "
                 "Or perhaps you were not ready to see it.", Fore.MAGENTA)
        print()
        pause()
        # Return control to main() loop — run_game will be called again
        return "descend"
    else:
        sys.exit(0)


def _ending_sealing(player):
    """ENDING 5: The Sealing — at the Void-well, player attempts to seal the Unmade."""
    print()
    hr("═", colour=Fore.CYAN)
    print(c("  ENDING: THE SEALED DOOR", Fore.CYAN + Style.BRIGHT))
    hr("═", colour=Fore.CYAN)
    print()
    pause()
    wrap("You stand at the well. You have refused the offer. "
         "You have read everything there is to read in these ruins. "
         "You know the name of what is in the well. "
         "You know the name of what made the world.", Fore.CYAN)
    pause()
    wrap("You do not know if this will work. "
         "You are not sure anyone could know.", Fore.CYAN)
    pause()
    wrap("You speak the Deepest Pulse's name into the well — "
         "not as an invocation, but as a question. "
         "As someone standing at the edge of something too large to see fully, "
         "asking if anyone on the other side is listening.",
         Fore.CYAN + Style.BRIGHT)
    pause()

    wrap("The well is silent for a long time.", Fore.CYAN)
    pause()
    wrap("Then: warmth. From the cold. "
         "A single pulse, upward, through the stones of the rim "
         "and into your hands where they rest on it. "
         "One pulse. Like a heartbeat. Like an answer.", Fore.CYAN + Style.BRIGHT)
    pause()
    wrap("The darkness in the well does not close. "
         "It does not seal. "
         "What happens is subtler: "
         "it becomes less present. "
         "As if something vast has shifted its weight slightly away from this point. "
         "As if the attention that has been focused here for centuries "
         "has been redirected — gently, firmly — elsewhere.",
         Fore.CYAN)
    pause()
    wrap("You do not know if this is Myrrakhel. "
         "You do not know if Myrrakhel still exists in a way that can respond to names. "
         "You do not know if what just happened was a sealing, "
         "or a delay, "
         "or simply a coincidence of timing.", Fore.CYAN)
    pause()
    wrap("The well is still there. The darkness is still in it. "
         "But the darkness is, perhaps, a little further away than it was.",
         Fore.CYAN + Style.BRIGHT)
    pause()

    print()
    wrap("You leave. You do not know if you have won. "
         "You are not sure the word applies.", Fore.CYAN)
    print()
    hr("═", colour=Fore.CYAN)
    print(c(f"  {player.name.upper()} — THE ONE WHO ASKED", Fore.CYAN + Style.BRIGHT))
    print(c("  Whether the question was answered is unresolved.", Fore.CYAN))
    print(c(f"  Rooms explored: {player.visited_rooms}  |  Gold: {player.gold}", Fore.YELLOW))
    found = sum(1 for f in ALL_FLAGS if f in player.flags and f in DISCOVERY_TEXT)
    print(c(f"  Discoveries: {found} of {len(DISCOVERY_TEXT)}", Fore.CYAN))
    hr("═", colour=Fore.CYAN)
    sys.exit(0)
