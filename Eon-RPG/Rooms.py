import random, textwrap, sys
import json, os, pathlib, copy

# ─── SHRINE ───────────────────────────────────────────────────────────────────
def event_shrine(player, room):
    wrap("The altar is cold to the touch, but the candles lean toward you. "
         "Ash in a hollow — and beneath the ash, faint warmth.")
    ch = prompt(["Kneel and pray", "Speak a name into the flame",
                 "Place an offering on the altar", "Leave"])

    if ch == "Kneel and pray":
        healed = random.randint(10, 18)
        player.hp = min(player.max_hp, player.hp + healed)
        if player.poisoned: player.poisoned = False; print(c("  The warmth draws the poison out.", Fore.GREEN))
        print(c(f"  Restored {healed} HP. ({player.hp}/{player.max_hp})", Fore.GREEN))

    elif ch == "Pay 30 gold for a full heal":
        if player.gold < 30:
            wrap("The shrine is patient, but not free.", Fore.YELLOW)
        else:
            player.gold -= 30
            player.hp = player.max_hp
            player.poisoned = False
            player.cursed = False
            wrap("The shrine accepts the gold without comment. "
                 "You are fully healed.", Fore.GREEN)
            print(c(f"  HP: {player.hp}/{player.max_hp}", Fore.GREEN))

    elif ch == "Speak a name into the flame":
        wrap("The flames lean close. What name do you speak?", Fore.MAGENTA)
        spoken = secret_input(player)
        _shrine_name_response(player, spoken)

    elif ch == "Place an offering on the altar":
        _shrine_offering(player)

    room["_shrine_used"] = room.get("_shrine_used", 0) + 1


def _shrine_name_response(player, spoken):
    if "atheron" in spoken:
        if "spoke_atheron_shrine" not in player.flags:
            player.flags.add("spoke_atheron_shrine")
            wrap("The flame turns blindingly gold. A vast exhalation — not threatening. Acknowledging. "
                 "Then ordinary light.", Fore.YELLOW)
            player.max_hp += 5; player.hp = min(player.hp + 5, player.max_hp)
            print(c("  Max HP +5.", Fore.GREEN))
        else:
            wrap("The flame flickers. It has already heard this name from you.", Fore.YELLOW)

    elif any(w in spoken for w in ("maelvyr","the betrayer","dravennis")):
        if "spoke_maelvyr_shrine" not in player.flags:
            player.flags.add("spoke_maelvyr_shrine")
            wrap("The candles die — all of them. Absolute dark. Then, one by one, they relight. "
                 "The warmth is gone. The ash has been disturbed — breathed on from the other side.",
                 Fore.RED)
            wrap("Scratched into the stone beneath the ash, newly visible: DEMONGOD.", Fore.RED + Style.BRIGHT)
        else:
            print(c("  The candles dim. Not again.", Fore.RED))

    elif any(w in spoken for w in ("thaun","the hollow")):
        wrap("The flames turn cold blue. The walls seem to dissolve — darkness shot through with "
             "something that might be stars or eyes. Then the shrine is just a shrine.", Fore.CYAN)

    elif any(w in spoken for w in ("arukiel","falling light")):
        wrap("The flames shoot upward as if reaching. A sound like distant impact. "
             "One pulse of brilliant white light. The shrine settles.", Fore.WHITE)

    elif any(w in spoken for w in ("myrrakhel","deepest pulse")):
        if "spoke_myrrakhel_shrine" not in player.flags:
            player.flags.add("spoke_myrrakhel_shrine")
            wrap("Every candle burns simultaneously brighter and colder. The ash rises and forms, "
                 "very briefly, a pattern you cannot name but feel you should know. Then scatters. "
                 "The warmth does not return.", Fore.YELLOW + Style.BRIGHT)
            player.max_hp += 3; player.hp = min(player.hp + 3, player.max_hp)
            print(c("  Max HP +3.", Fore.GREEN))
        else:
            wrap("The candles do not react further.", Fore.YELLOW)

    elif any(w in spoken for w in ("vaelan","emperor","the emperor")):
        if "spoke_vaelan_shrine" not in player.flags:
            player.flags.add("spoke_vaelan_shrine")
            wrap("The flame goes a deep, steady crimson. A sound — not a voice — passes through the "
                 "room like the echo of something that happened a long time ago in this exact place. "
                 "Then the flame returns to yellow. The ash, you notice, is slightly warm.", Fore.RED)
        else:
            wrap("The flame reddens, briefly. Then ordinary again.", Fore.RED)

    elif any(w in spoken for w in ("vaethar","chosen child","dragon's child")):
        if "spoke_vaethar_shrine" not in player.flags:
            player.flags.add("spoke_vaethar_shrine")
            wrap("Both flame and warmth increase simultaneously — "
                 "gold and warm, sustaining rather than sudden. The ash in the hollow reshapes "
                 "into something like wings, very briefly, before collapsing.", Fore.YELLOW)
            player.hp = min(player.max_hp, player.hp + 10)
            print(c("  +10 HP. The shrine knows this name.", Fore.GREEN))
        else:
            wrap("The flame glows warmly. It has given what it can for that name.", Fore.YELLOW)

    elif any(w in spoken for w in ("ysena","weaver of shadows")):
        wrap("The candles dim to a low, blue-grey. The shadows lengthen. "
             "Something — a warmth, or a presence — lingers for a moment where the shadow is "
             "deepest, then withdraws. Atheron's spouse. The shrine remembers.", Fore.CYAN)
        player.flags.add("spoke_ysena_shrine")

    else:
        wrap("The flames lean, consider, and return to stillness.")


def _shrine_offering(player):
    """Specific items have uses at the shrine."""
    offerable = [it for it in player.inventory
                 if it["name"] in ("Dawn Shard","Godshard Fragment","Vaethar's Tear",
                                   "Relic Coin","Dragon Scale","Old Crown")]
    if not offerable:
        wrap("You have nothing that seems right to place here. The altar waits.")
        return
    opts = [it["name"] for it in offerable] + ["Nothing"]
    ch = prompt(opts)
    if ch == "Nothing": return

    item = next(it for it in offerable if it["name"] == ch)
    player.remove_item(ch)

    if ch == "Dawn Shard":
        wrap("The shard begins to glow very brightly on the altar. The warmth spreads outward "
             "into the room itself. The candles burn higher. You feel restored — "
             "not just in body but in something harder to name.", Fore.YELLOW)
        player.hp = player.max_hp
        player.max_hp += 8
        player.hp = player.max_hp
        print(c("  Fully healed. Max HP +8.", Fore.GREEN))
        player.flags.add("dawn_shard_offered")

    elif ch == "Godshard Fragment":
        wrap("The fragment resonates with something in the altar — the frequency you felt in your "
             "chest becomes a frequency the altar feels too. The candles pulse in rhythm with it. "
             "Then the fragment is still. On the altar, beside it: something the altar has "
             "given back.", Fore.YELLOW + Style.BRIGHT)
        try_give_unique(player, "Vaethar's Tear")
        player.attack += 2; player.max_hp += 10
        player.hp = min(player.hp + 10, player.max_hp)
        print(c("  ATK +2, Max HP +10. The shrine exchanged one thing for another.", Fore.GREEN))
        player.flags.add("godshard_offered_shrine")

    elif ch == "Vaethar's Tear":
        wrap("The Tear dissolves on the altar's stone — not melting, simply becoming part of it. "
             "All the candles light at once, brighter than you have seen them. "
             "The warmth is overwhelming and then returns to normal. "
             "In the ash, a word has been pressed, in a language you cannot read. "
             "You feel, regardless: thank you.", Fore.YELLOW + Style.BRIGHT)
        player.max_hp += 15; player.hp = player.max_hp
        player.attack += 3
        print(c("  Max HP +15, fully healed, ATK +3. The shrine is grateful.", Fore.GREEN))
        player.flags.add("vaethar_tear_offered")

    elif ch == "Relic Coin":
        wrap("The coin rests on the altar. The face on it seems to look at the candles. "
             "Then the coin is gone. In its place, a small pile of coins — more than one.", Fore.YELLOW)
        player.gold += 25; print(c("  +25 gold.", Fore.YELLOW))

    elif ch == "Dragon Scale":
        wrap("The scale hisses on the altar stone and produces a single pulse of black-and-gold flame. "
             "Then it is simply a scale again — but it is warm now rather than merely warm to the touch. "
             "The altar has recognised what it is.", Fore.YELLOW)
        player.pick_up(item)  # give it back — it has been changed
        item["description"] = "Warm in a way that goes beyond temperature. The shrine has recognised it."
        player.flags.add("scale_shrine_blessed")

    elif ch == "Old Crown":
        wrap("You place the crown on the altar. The candles lean toward it. "
             "It sits there for a long moment, and then the altar does something: "
             "an inscription appears in the stone around the crown, brief and in common script: "
             "'WORN BY THOSE WHO CAME BEFORE VAELAN.' "
             "The crown is unchanged. But you know something now.", Fore.CYAN)
        player.pick_up(item)  # give it back
        player.flags.add("old_crown_shrine")
        if not player.has_item("Old Crown"):
            player.inventory.append(item)



def event_hall_of_the_nine(player, room):
    """
    Hall of the Nine — nine alcoves, each bearing a Sera's symbol.
    Interactive, lore-rich. Players can examine each alcove.
    """
    hr("═", colour=Fore.YELLOW)
    print(c("  THE HALL OF THE NINE", Fore.YELLOW + Style.BRIGHT))
    hr("═", colour=Fore.YELLOW)
    print()
    wrap(
        "A circular hall. Nine alcoves are set into the walls at equal intervals, "
        "each carved with a different symbol. The symbols are not Eldrosian — "
        "they predate the empire entirely. At the centre of the floor: "
        "a mosaic of nine circles arranged around a tenth, the tenth filled solid gold. "
        "Most of the gold has been pried out. The centre is hollow.",
        Fore.YELLOW)
    print()
    player.flags.add("found_hall_of_nine")

    ALCOVES = {
        "Myrrakhel": {
            "symbol": "A spiral that appears to turn inward forever.",
            "inscription": "'First. Godmaker. Giver. He who had will when there was nothing else to have it. '",
            "lore": "myrrakhel_alcove",
            "effect": lambda p: None,
            "effect_text": None,
        },
        "Kindrael": {
            "symbol": "A flame above a horizon line. The flame is larger than the horizon.",
            "inscription": "'The Flame at Dawn. Impatient. The first to make a Great Work. '",
            "lore": "kindrael_alcove",
            "effect": lambda p: None,
            "effect_text": None,
        },
        "Loria": {
            "symbol": "A tree whose roots are as large as its branches.",
            "inscription": "'The Verdant Bloom. Allseer. She moved through the new forests "
                           "and no one could know her mind. '",
            "lore": "loria_alcove",
            "effect": lambda p: None,
            "effect_text": None,
        },
        "Thalas": {
            "symbol": "A wave that is also a veil.",
            "inscription": "'She of the Endless Tides. She fed the rivers and the trees and the animals. '",
            "lore": "thalas_alcove",
            "effect": lambda p: None,
            "effect_text": None,
        },
        "Thar": {
            "symbol": "A crown of nine peaks.",
            "inscription": "'The Stonefather. Patient, and severe to those who broke his patience. "
                           "His burden is to lay beneath his Crown. '",
            "lore": "thar_alcove",
            "effect": lambda p: None,
            "effect_text": None,
        },
        "Ishak": {
            "symbol": "A forge above a storm cloud.",
            "inscription": "'Storm-Forge. He most enjoyed the early Chaos. "
                           "Of all the Sera, he alone felt against the near-mortals. '",
            "lore": "ishak_alcove",
            "effect": lambda p: None,
            "effect_text": None,
        },
        "Ysena": {
            "symbol": "A cloak draped over nothing. The nothing has a shape.",
            "inscription": "'Weaver of Shadows. She began to search deeper inside, "
                           "imagining creatures in her shadows — ones that eventually came to being. '",
            "lore": "ysena_alcove",
            "effect": lambda p: setattr(p, 'flags', p.flags | {"spoke_ysena_shrine"}),
            "effect_text": "The alcove of shadow grows briefly warmer. Something in it acknowledges you.",
        },
        "Vastino": {
            "symbol": "A cathedral reflected in ice.",
            "inscription": "'Frost-Child. She sits softly, remembering all that enters her ears. "
                           "Most beautiful is her Work — frost-covered cathedrals of stone and ice. '",
            "lore": "vastino_alcove",
            "effect": lambda p: None,
            "effect_text": None,
        },
        "Kelamaris": {
            "symbol": "Four lines radiating outward, each slightly curved, like wind made visible.",
            "inscription": "'Breath of the Heights. The youngest. Most brash. "
                           "He walked amongst the mortals from the very beginning, "
                           "believing that the chaos and volatility granted by wind was releasing. '",
            "lore": "kelamaris_alcove",
            "effect": lambda p: None,
            "effect_text": None,
        },
    }

    examined = room.get("_nine_examined", set())

    while True:
        unexamined = [name for name in ALCOVES if name not in examined]
        opts = [f"Examine the alcove of {name}" for name in unexamined]

        # Special interactions for players with specific items/knowledge
        if (player.has_item("Dawn Shard") and "dawn_nine_offered" not in examined
                and "Loria" in examined):
            opts.append("Place the Dawn Shard in Myrrakhel's alcove")
        if (player.has_item("Candle") and "candle_nine" not in examined):
            opts.append("Hold the Candle at the centre of the hall")

        opts.append("Leave the Hall")
        ch = prompt(opts)

        if ch == "Leave the Hall":
            break

        elif ch == "Hold the Candle at the centre of the hall":
            examined.add("candle_nine")
            wrap(
                "The candle's flame turns through every colour in sequence — "
                "gold, white, green, blue, grey, silver, red, black, pale orange — "
                "and then returns to yellow. Each colour corresponds to one alcove. "
                "The black corresponds to Ysena's. "
                "The pale orange is last, and it lingers longest.",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("candle_hall_of_nine")

        elif ch == "Place the Dawn Shard in Myrrakhel's alcove":
            examined.add("dawn_nine_offered")
            player.remove_item("Dawn Shard")
            wrap(
                "The shard rests in the spiral. For a moment the spiral seems to turn — "
                "actually turn, the stone moving — and then is still. "
                "The shard has been absorbed. "
                "In the hollow at the centre of the floor mosaic, "
                "a faint warmth now rises. Not gold. Something older than gold.",
                Fore.YELLOW + Style.BRIGHT)
            player.max_hp += 10; player.hp = min(player.hp + 10, player.max_hp)
            player.attack += 2
            print(c("  Max HP +10, ATK +2. The hall acknowledges the offering.", Fore.GREEN))
            player.flags.add("dawn_shard_nine")

        else:
            # Parse which alcove
            for name, data in ALCOVES.items():
                if f"Examine the alcove of {name}" == ch:
                    examined.add(name)
                    player.flags.add(data["lore"])
                    wrap(f"The symbol: {data['symbol']}", Fore.YELLOW)
                    wrap(f"Below it, the inscription: {data['inscription']}", Fore.CYAN)

                    # Atheron's connection to Ysena
                    if name == "Ysena" and "found_ysena" in player.flags:
                        print()
                        wrap(
                            "You have seen her name before — in the mural, beside Atheron. "
                            "The alcove's shadow seems to lean toward you very slightly.",
                            Fore.CYAN + Style.BRIGHT)

                    # Myrrakhel detail — only if player knows about Atraxis
                    if name == "Myrrakhel" and "atraxis_named" in player.flags:
                        print()
                        wrap(
                            "The spiral in the alcove is identical to the pattern "
                            "that appeared in the Agreement Chamber's footprints. "
                            "The shape of the Unmade's attention. "
                            "The shape of what Myrrakhel was made to counter.",
                            Fore.MAGENTA + Style.BRIGHT)

                    if data["effect_text"]:
                        print()
                        wrap(data["effect_text"], Fore.YELLOW)
                        data["effect"](player)
                    break

        room["_nine_examined"] = examined

    # Reward for examining all nine
    if len([k for k in ALCOVES if k in examined]) == 9 and "nine_completed" not in player.flags:
        player.flags.add("nine_completed")
        print()
        wrap(
            "You have stood before all nine. "
            "The hall is quiet. The nine symbols seem to orient toward one another — "
            "not physically, but in the way that things orient when they are part of a set "
            "and you have finally seen all of them. "
            "Something settles.",
            Fore.YELLOW + Style.BRIGHT)
        player.max_hp += 8; player.hp = min(player.hp + 8, player.max_hp)
        print(c("  Max HP +8.", Fore.GREEN))


def event_hall_of_shattered_crown(player, room):
    """
    Hall of the Shattered Crown — war memorial, holds the Third Godshard.
    Depicts the Wars of the Shattered Crown via murals.
    """
    hr("═", colour=Fore.RED)
    print(c("  THE HALL OF THE SHATTERED CROWN", Fore.RED + Style.BRIGHT))
    hr("═", colour=Fore.RED)
    print()
    wrap(
        "This room was built after the empire. That much is clear — "
        "the stonework is cruder than the rest of Eldros-Verath, "
        "the carvings rougher. Someone returned here after the fall "
        "and built this deliberately.",
        Fore.RED)
    print()
    wrap(
        "The walls depict a war. Multiple armies, multiple banners — "
        "you can identify the Eldrosian serpent-sun on some. "
        "The others bear symbols you do not recognise: "
        "a crown split into three pieces, "
        "and each army carrying one piece.",
        Fore.RED)
    pause()

    player.flags.add("found_shattered_crown_hall")

    done = room.get("_crown_done", set())

    while True:
        opts = []
        if "mural" not in done:   opts.append("Study the war murals")
        if "plinth" not in done:  opts.append("Examine the central plinth")
        if "names" not in done:   opts.append("Read the names on the walls")
        if "godshard" not in done and "plinth" in done:
            if not ("obtained_godshard_3" in player.flags):
                opts.append("Take what rests on the plinth")
        if "candle" not in done and player.has_item("Candle") and "mural" in done:
            opts.append("Hold the Candle to the damaged section of mural")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Study the war murals":
            done.add("mural")
            wrap(
                "The war depicted here lasted — the dates carved at the bottom suggest — "
                "for three generations after the fall of Eldros-Verath. "
                "It is called, in the caption, THE WARS OF THE SHATTERED CROWN. "
                "Vaelan had heirs. Each inherited one of the Godshards. "
                "Each believed that holding all three would restore the empire. "
                "None of them were right.",
                Fore.RED)
            wrap(
                "The final panel shows a figure — not a soldier, not a noble — "
                "placing three objects on a plinth in this exact room. "
                "The figure's face is not shown. "
                "Beneath the panel: 'HERE THEY REST UNTIL SOMEONE WORTHY COMES.'",
                Fore.RED + Style.BRIGHT)
            player.flags.add("read_shattered_crown_mural")

        elif ch == "Examine the central plinth":
            done.add("plinth")
            if "obtained_godshard_3" in player.flags:
                wrap(
                    "The plinth is empty now. You took what was here. "
                    "It was the right thing to do, or it was not. "
                    "The plinth does not have an opinion.",
                    Fore.LIGHTBLUE_EX + Style.BRIGHT)
            else:
                wrap(
                    "A stone plinth at the exact centre of the room. "
                    "On it: something that vibrates at a frequency you feel in your chest. "
                    "A Godshard. The third. "
                    "It has been here for a very long time, waiting for someone "
                    "who would recognise what it is.",
                    Fore.YELLOW + Style.BRIGHT)

        elif ch == "Take what rests on the plinth":
            done.add("godshard")
            try_give_unique(player, "Third Godshard")
            player.flags.add("found_third_godshard")
            wrap(
                "The moment you touch it, the other shards you carry respond. "
                "The three of them pulse together — once — and then settle "
                "into a shared frequency. They know each other.",
                Fore.YELLOW + Style.BRIGHT)

        elif ch == "Read the names on the walls":
            done.add("names")
            wrap(
                "The walls are covered in names — hundreds of them. "
                "The dead of the Wars of the Shattered Crown, "
                "listed without rank or title. "
                "Three names, at the top of the list, are larger than the others: "
                "CALYREN. VAELAN. TOLOS. "
                "Beneath Tolos's name, in different script: 'He tried.'",
                Fore.CYAN)
            player.flags.add("found_tolos_memorial")

        elif ch == "Hold the Candle to the damaged section of mural":
            done.add("candle")
            wrap(
                "The candle turns blue. In the blue light, the damaged section reveals itself: "
                "it was not damaged — it was covered over deliberately. "
                "Beneath the covering: a fourth figure in the final panel. "
                "Standing apart from the armies, watching. "
                "Robed. Face obscured. "
                "In the blue light you can read a caption that was painted over: "
                "'AND HE WATCHED FROM AFAR, AND WAS GLAD.'",
                Fore.MAGENTA + Style.BRIGHT)
            player.flags.add("candle_crown_hall")

        room["_crown_done"] = done


def event_veythari_sanctuary(player, room):
    """
    Veythari Sanctuary — quiet, silver-lit room.
    Starlight Shard can be offered here to unlock a memory of Arukiel.
    Crystal Mirror has a unique interaction.
    """
    hr("═", colour=Fore.WHITE)
    print(c("  THE VEYTHARI SANCTUARY", Fore.WHITE + Style.BRIGHT))
    hr("═", colour=Fore.WHITE)
    print()
    wrap(
        "The room is lit from within — not from torches or cracks in the ceiling, "
        "but from the walls themselves, a silver light that is steady and calm. "
        "At the centre: a pool of absolutely still water. "
        "At the pool's edge: a single pale tree, leafless, growing from the stone. "
        "Its branches hold what might be starlight — small points of cold light "
        "that do not flicker.",
        Fore.WHITE)
    print()
    player.flags.add("found_veythari_sanctuary")

    done = room.get("_sanctuary_done", set())

    while True:
        opts = []
        if "pool" not in done:   opts.append("Look into the pool")
        if "tree" not in done:   opts.append("Touch the pale tree")
        if "shard" not in done and player.has_item("Starlight Shard"):
            opts.append("Offer the Starlight Shard to the pool")
        if "mirror" not in done and player.has_item("Crystal Mirror"):
            opts.append("Hold up the Crystal Mirror in this room")
        if "candle" not in done and player.has_item("Candle"):
            opts.append("Hold the Candle near the tree")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Look into the pool":
            done.add("pool")
            wrap(
                "The pool reflects the silver walls and the tree. "
                "And then — very briefly — something else. "
                "A figure, falling. Not downward — outward, arms spread, "
                "face toward something bright above it. "
                "Falling in choice, not accident. "
                "Then the pool is just a pool.",
                Fore.WHITE)
            wrap("Arukiel. Of the Falling Light.", Fore.WHITE + Style.BRIGHT)
            player.flags.add("sanctuary_pool_vision")

        elif ch == "Touch the pale tree":
            done.add("tree")
            wrap(
                "The bark is cold. Not the cold of stone — the cold of something "
                "that has not been warm in a very long time, but was once. "
                "Where your hand rests on the bark, a small point of light brightens, "
                "then dims.",
                Fore.WHITE)
            if "met_sael" in player.flags:
                wrap(
                    "Sael is Veythari. This tree is not decoration — "
                    "it is something that was planted here deliberately, "
                    "by someone who expected to return.",
                    Fore.WHITE + Style.BRIGHT)
                player.flags.add("sanctuary_sael_tree")

        elif ch == "Offer the Starlight Shard to the pool":
            done.add("shard")
            player.remove_item("Starlight Shard")
            wrap(
                "The shard touches the surface of the pool and does not sink. "
                "It rests there, glowing. "
                "The pool brightens — the silver walls brighten — "
                "the tree's points of light flare, all of them, simultaneously.",
                Fore.WHITE + Style.BRIGHT)
            pause()
            wrap(
                "In the brightness: a memory. Not yours. "
                "A figure falling from a sky that is blindingly bright — "
                "the sun at its fullest and most furious — "
                "falling in a ring of silver light, arms spread, "
                "landing on a world that is not yet finished being made. "
                "Standing. Looking around at what the world is and what it will be. "
                "Deciding to be part of it.",
                Fore.WHITE + Style.BRIGHT)
            pause()
            wrap(
                "The brightness fades. The pool is still. "
                "The shard is gone — absorbed. "
                "On the surface of the pool, briefly: a reflection of a face you do not know "
                "but recognise from the mural. Arukiel. "
                "Then the reflection is yours again.",
                Fore.WHITE)
            player.flags.add("arukiel_memory")
            player.max_hp += 12; player.hp = min(player.hp + 12, player.max_hp)
            player.defence += 2
            print(c("  Max HP +12, DEF +2. You carry the memory now.", Fore.GREEN))

        elif ch == "Hold up the Crystal Mirror in this room":
            done.add("mirror")
            wrap(
                "In the Crystal Mirror, the room is identical — "
                "except the tree has leaves. Silver-white leaves, "
                "and sitting in the branches: a figure, legs dangling, "
                "watching you with silver eyes. "
                "When you meet the figure's gaze in the mirror, it raises a hand. "
                "Not threatening. Greeting. "
                "Then the leaves are gone and the tree is bare again.",
                Fore.WHITE + Style.BRIGHT)
            player.flags.add("sanctuary_mirror_figure")
            if "met_sael" in player.flags:
                wrap(
                    "You have met silver eyes before. "
                    "The figure in the mirror was not Sael — "
                    "but it was Veythari.",
                    Fore.WHITE)

        elif ch == "Hold the Candle near the tree":
            done.add("candle")
            wrap(
                "The candle's flame turns silver-white and very still. "
                "The tree's small lights brighten in response. "
                "For a moment the room is brighter than it has any right to be. "
                "Then the candle returns to yellow and the lights dim.",
                Fore.WHITE + Style.BRIGHT)
            player.hp = min(player.max_hp, player.hp + 8)
            print(c("  +8 HP. The sanctuary's light is healing.", Fore.GREEN))

        room["_sanctuary_done"] = done


def event_crystal_mirror_room(player, room):
    """
    The Mirror Room — fixed location for the Crystal Mirror.
    The mirror can be found here; the room has unique interactions.
    """
    hr(colour=Fore.CYAN)
    print(c("  THE CHAMBER OF REFLECTIONS", Fore.CYAN + Style.BRIGHT))
    hr(colour=Fore.CYAN)
    print()
    wrap(
        "A small chamber, perfectly square. "
        "Every surface is polished — walls, floor, ceiling — "
        "but only one surface reflects correctly. "
        "The others show the room from impossible angles. "
        "At the centre: a wooden stand, and on the stand, a mirror. "
        "It is face-down.",
        Fore.CYAN)
    print()

    done = room.get("_crystal_done", set())

    while True:
        opts = []
        if "turn" not in done:  opts.append("Turn the mirror over")
        if "take" not in done and "turn" in done and "obtained_crystal_mirror" not in player.flags:
            opts.append("Take the Crystal Mirror")
        if "walls" not in done: opts.append("Study the impossible reflections in the walls")
        if player.has_item("Crystal Mirror") and "use_here" not in done:
            opts.append("Use the Crystal Mirror you carry in this room")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Turn the mirror over":
            done.add("turn")
            wrap(
                "The mirror is face-down for a reason. "
                "When you turn it over, the reflection is — wrong. "
                "Not wrong in the way of a bad mirror. Wrong in the way of "
                "a window onto a place that is not this room. "
                "The reflection shows a corridor you have not visited. "
                "At the end of the corridor: a door. "
                "The door is open. Beyond it: darkness, and two points of gold light. "
                "Then the reflection settles and shows only the room.",
                Fore.CYAN + Style.BRIGHT)
            player.flags.add("mirror_room_vision")
            if "studied_atheron" in player.flags:
                wrap(
                    "Two points of gold light. The colour of Atheron's eyes.",
                    Fore.YELLOW)

        elif ch == "Take the Crystal Mirror":
            done.add("take")
            try_give_unique(player, "Crystal Mirror")
            wrap(
                "The mirror is heavier than it looks. "
                "In your hands, the reflection shows something that is not quite you — "
                "the same face, the same posture, "
                "but the expression is slightly different. "
                "More certain. Or less.",
                Fore.CYAN)

        elif ch == "Study the impossible reflections in the walls":
            done.add("walls")
            wrap(
                "One wall shows the room from above — you, looking down at yourself. "
                "One wall shows the room as it was — furnished, lit, occupied by someone "
                "who is not present. A scholar's room, papers on a desk. "
                "One wall shows the room as it will be — you cannot tell how you know this, "
                "but the room in that reflection is empty. "
                "The stand is there. The mirror is there. Face-down again.",
                Fore.CYAN)
            player.flags.add("studied_reflection_walls")

        elif ch == "Use the Crystal Mirror you carry in this room":
            done.add("use_here")
            wrap(
                "You hold up the Crystal Mirror. "
                "In it, the impossible reflections on the walls resolve — "
                "all of them, simultaneously, into a single image: "
                "the room as it was, the scholar at the desk, "
                "writing. The scholar looks up. "
                "Directly at you, through the mirror. "
                "Their mouth moves. You cannot hear them. "
                "Then the reflection is ordinary.",
                Fore.CYAN + Style.BRIGHT)
            player.flags.add("mirror_scholar_vision")
            if "read_talarion_chronicle" in player.flags:
                wrap(
                    "The scholar's face. You have read his name. "
                    "This was Talarion's room.",
                    Fore.CYAN + Style.BRIGHT)
                player.flags.add("talarion_room_found")

        room["_crystal_done"] = done


def event_dawn_shard_room(player, room):
    """
    The Dawn Chamber — fixed location for the Dawn Shard.
    A room lit by pre-dawn light from an unknown source.
    """
    hr(colour=Fore.YELLOW)
    print(c("  THE DAWN CHAMBER", Fore.YELLOW + Style.BRIGHT))
    hr(colour=Fore.YELLOW)
    print()
    wrap(
        "The room is lit by orange-pale light — the colour of the sky "
        "just before the sun appears. "
        "The light has no source. "
        "It comes from everywhere and casts no shadows. "
        "On a flat stone at the far end: a small fragment, "
        "pale orange, with its own warmth.",
        Fore.YELLOW)
    print()

    done = room.get("_dawn_done", set())

    while True:
        opts = []
        if "examine" not in done: opts.append("Examine the room")
        if "take" not in done and "obtained_dawn_shard" not in player.flags:
            opts.append("Take the Dawn Shard")
        if "sit" not in done:     opts.append("Sit in the light")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Examine the room":
            done.add("examine")
            wrap(
                "The walls are plain — no inscriptions, no carvings. "
                "Someone cleaned this room deliberately. "
                "In the corner, faint marks that might be old furniture's legs. "
                "Someone lived here, or worked here, "
                "and removed everything when they left.",
                Fore.YELLOW)
            wrap(
                "The light intensifies slightly when you stand near the stone. "
                "As though the shard is the source after all.",
                Fore.YELLOW)

        elif ch == "Take the Dawn Shard":
            done.add("take")
            success = try_give_unique(player, "Dawn Shard")
            if success:
                wrap(
                    "The shard is warm in a way that is not unpleasant. "
                    "When you pick it up, the light in the room dims slightly — "
                    "as though some of it was living in the shard "
                    "and has come with you.",
                    Fore.YELLOW)

        elif ch == "Sit in the light":
            done.add("sit")
            wrap(
                "You sit in the sourceless dawn light. "
                "It is not warm, exactly, but it is not cold. "
                "It is the temperature of a decision made a long time ago "
                "by someone who chose to be here rather than elsewhere. "
                "You remain for a while.",
                Fore.YELLOW)
            healed = random.randint(10, 20)
            player.hp = min(player.max_hp, player.hp + healed)
            if player.poisoned:
                player.poisoned = False
                print(c("  The light draws the poison out.", Fore.GREEN))
            if player.cursed:
                player.cursed = False
                print(c("  The light dissolves whatever was clouding you.", Fore.GREEN))
            print(c(f"  +{healed} HP. Poison and curses cleared.", Fore.GREEN))
            player.flags.add("sat_in_dawn_light")

        room["_dawn_done"] = done


def event_hollow_stone_room_fixed(player, room):
    """
    The Hollow Wall — fixed location for the Hollow Stone.
    (Replaces the old event_hollow_stone_room which had no guaranteed item.)
    """
    wrap(
        "A room with a sealed wall — perfectly flat, no seams, no mortar. "
        "In the centre of the wall: a circular indentation exactly the size of a hand. "
        "On the floor, resting against the wall: a smooth stone with a hole through it."
    )

    done = room.get("_hollow_done", set())

    while True:
        opts = []
        if "take_stone" not in done and "obtained_hollow_stone" not in player.flags:
            opts.append("Take the Hollow Stone")
        if "press" not in done:  opts.append("Press your hand into the indentation")
        if "place" not in done and player.has_item("Hollow Stone"):
            opts.append("Place the Hollow Stone in the indentation")
        if "look" not in done and player.has_item("Hollow Stone"):
            opts.append("Look through the Hollow Stone at the sealed wall")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Take the Hollow Stone":
            done.add("take_stone")
            try_give_unique(player, "Hollow Stone")
            wrap(
                "The hole through the stone is perfectly round. "
                "Impossibly so — no natural process makes a hole this clean. "
                "Looking through it, the wall beyond appears different: "
                "not sealed, but simply waiting.",
                Fore.YELLOW)

        elif ch == "Press your hand into the indentation":
            done.add("press")
            wrap(
                "Your hand fits. The stone is cold. Nothing happens, except: "
                "beyond the wall, faintly, something moves."
            )

        elif ch == "Place the Hollow Stone in the indentation":
            done.add("place")
            player.remove_item("Hollow Stone")
            wrap(
                "The stone fits perfectly — the hole aligns with something on the other side. "
                "A click. The wall section shifts inward.",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("hollow_stone_door")
            wrap(
                "Beyond: a small chamber. Shelves. On one shelf: "
                "a Rolled Parchment and a Fragment of the Seal. "
                "On the wall: 'Vaethar's gift was not a sacrifice. It was an investment. "
                "The Godshards remember what Vaethar chose to become.'",
                Fore.YELLOW)
            if pick_parchment_variant(player):
                pass
            player.pick_up(get_item("Fragment of the Seal"))
            player.flags.add("vaethar_inscription")

        elif ch == "Look through the Hollow Stone at the sealed wall":
            done.add("look")
            wrap(
                "Through the hole: the sealed wall is not sealed. "
                "Beyond it, clearly visible through the stone, "
                "a small room with shelves and something resting on them. "
                "The hole shows you what is there before you open it.",
                Fore.YELLOW + Style.BRIGHT)

        room["_hollow_done"] = done


def event_tolarion_room(player, room):
    """Talarion's Room — where the Chronicle was written. Has specific secrets."""
    hr(colour=Fore.CYAN)
    wrap("A scholar's room. Desk, shelves, the remnants of a life spent writing.", Fore.CYAN)
    hr(colour=Fore.CYAN)
    print()

    done = room.get("_talarion_done", set())

    while True:
        opts = []
        if "desk" not in done:    opts.append("Search the desk")
        if "shelves" not in done: opts.append("Search the shelves")
        if "mirror" not in done and player.has_item("Crystal Mirror"):
            opts.append("Hold up the Crystal Mirror")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Search the desk":
            done.add("desk")
            wrap(
                "Papers, mostly illegible with age. "
                "An ink-pot, dried to nothing. "
                "A small carved figure — a person, arms spread, falling. "
                "Arukiel, perhaps, or the artist's impression of something seen in a vision. "
                "Under the papers: a journal.",
                Fore.CYAN)
            if "obtained_talarion_chronicle" not in player.flags:
                try_give_unique(player, "Talarion's Chronicle")
            else:
                wrap("You already carry his chronicle.", Fore.LIGHTBLUE_EX + Style.BRIGHT)

        elif ch == "Search the shelves":
            done.add("shelves")
            wrap(
                "Books, mostly destroyed. One survives, spine intact: "
                "'A Complete Record of the Wars of the Shattered Crown, Vols I-VII.' "
                "You cannot carry all seven volumes. "
                "You open the last one to its final page.",
                Fore.CYAN)
            wrap(
                "'The wars ended not in a victor but in exhaustion. "
                "The three shards were returned to Eldros-Verath by common agreement — "
                "no single heir trusted to hold all three. "
                "They were placed in the Hall of the Shattered Crown, "
                "which was built for this purpose. "
                "The wars had killed more people than the Night of Collapse. "
                "The shards waited. They are still waiting.'",
                Fore.CYAN + Style.BRIGHT)
            player.flags.add("read_wars_record")

        elif ch == "Hold up the Crystal Mirror":
            done.add("mirror")
            if "mirror_scholar_vision" not in player.flags:
                wrap(
                    "In the mirror: the room as it was. A scholar at the desk. "
                    "They look up and see you.",
                    Fore.CYAN + Style.BRIGHT)
                player.flags.add("mirror_scholar_vision")
            else:
                wrap(
                    "The scholar is there again. This time they stand up, "
                    "walk to where you stand, and place something on the desk in front of you. "
                    "When you lower the mirror: nothing on the desk. "
                    "But the air where they stood is slightly warmer than the rest of the room.",
                    Fore.CYAN + Style.BRIGHT)
                player.flags.add("talarion_room_found")
                player.max_hp += 5; print(c("  Max HP +5.", Fore.GREEN))

        room["_talarion_done"] = done


# ─── MERCHANT ─────────────────────────────────────────────────────────────────
SHOP_STOCK = [
    {"name":"Health Potion",       "type":"consumable","rarity":"common",  "value":15,"price":10, "description":"Restores 15 HP."},
    {"name":"Strong Tonic",        "type":"consumable","rarity":"rare","value":25,"price":18, "description":"Restores 25 HP."},
    {"name":"Ember Flask",         "type":"consumable","rarity":"uncommon",  "value":20,"price":14, "description":"Restores 20 HP. Burns."},
    {"name":"Bloodmoss Tincture",  "type":"consumable","rarity":"common",  "value":10,"price":7,  "description":"Restores 10 HP."},
    {"name":"Antidote",            "type":"consumable","rarity":"uncommon",  "value":0, "price":8,  "description":"Cures poison."},
    {"name":"Clarity Draught",     "type":"consumable","rarity":"rare","value":0, "price":10, "description":"Removes curses."},
    {"name":"Void Salt",           "type":"consumable","rarity":"uncommon","value":0, "price":12, "description":"Wards vs drain for one fight."},
    {"name":"Vein-Sealer",         "type":"consumable","rarity":"unique",    "value":50,"price":40, "description":"Restores 50 HP. Hardens wounds against reopening."},

    {"name":"Iron Sword",          "type":"weapon",    "rarity":"common",  "value":6, "price":15, "description":"Reliable steel."},
    {"name":"Serrated Blade",      "type":"weapon",    "rarity":"common",  "value":7, "price":18, "description":"Notched for tearing."},
    {"name":"Bonespike",           "type":"weapon",    "rarity":"uncommon","value":9, "price":25, "description":"Carved from something large. Holds an edge badly."},
    {"name":"Needle of Vaethar",   "type":"weapon",    "rarity":"unique",  "value":18,"price":80, "description":"A thin blade. Something inside it hums when near the Void-well."},

    {"name":"Iron Shield",         "type":"armour",    "rarity":"common",  "value":5, "price":12, "description":"Heavy and dependable."},
    {"name":"Chain Vest",          "type":"armour",    "rarity":"uncommon",  "value":4, "price":10, "description":"Reliable rings."},
    {"name":"Voidhardened Vest",   "type":"armour",    "rarity":"rare",    "value":10,"price":38, "description":"Treated with something from deep below. Resists drain."},

    {"name":"Candle",              "type":"artefact",  "rarity":"common",  "value":0, "price":3,  "description":"Flickers in still air."},

    {"name":"Rolled Parchment",    "type":"lore",      "rarity":"uncommon",  "value":0, "price":8,  "description":"Sealed with black wax."},
]

# ── RARITY WEIGHTS & STOCK COUNTS ────────────────────────────────────────────

RARITY_WEIGHTS = {
    "common":   40,
    "uncommon": 28,
    "rare":     12,
    "unique":   5,
}

# How many items appear in each category's portion of the stock
STOCK_CONFIG = {
    "consumable": (1, 4),   # (min, max) slots
    "weapon":     (0, 3),
    "armour":     (0, 2),
    "artefact":   (0, 1),
    "lore":       (0, 1),
}


def _build_stock(player):
    """Build a randomised stock list for this visit. Unique items that the
    player has already purchased (tracked via player.flags) are excluded."""
    purchased_uniques = getattr(player, "purchased_uniques", set())
    stock = []

    by_type = {}
    for item in SHOP_STOCK:
        by_type.setdefault(item["type"], []).append(item)

    for itype, (mn, mx) in STOCK_CONFIG.items():
        pool = [
            it for it in by_type.get(itype, [])
            if not (it["rarity"] == "unique" and it["name"] in purchased_uniques)
        ]
        if not pool:
            continue

        # Weighted sampling without replacement
        weights = [RARITY_WEIGHTS[it["rarity"]] for it in pool]
        count = random.randint(mn, mx)
        count = min(count, len(pool))
        chosen = []
        pool_copy = list(zip(pool, weights))
        for _ in range(count):
            if not pool_copy:
                break
            names, ws = zip(*pool_copy)
            pick = random.choices(names, weights=ws, k=1)[0]
            chosen.append(pick)
            pool_copy = [(it, w) for it, w in pool_copy if it is not pick]

        stock.extend(chosen)

    return stock


def event_merchant(player, room):
    print(c("\n  'Take your time. I have been here longer than you know.'\n", Fore.YELLOW))

    shop_stock = _build_stock(player)

    while True:
        print(c(f"  Your gold: {player.gold}", Fore.YELLOW))

        def _item_label(it):
            rarity_tag = {"uncommon": " ~", "rare": " *", "unique": " **"}.get(it["rarity"], "")
            return f"{it['name']}{rarity_tag}  ({it['price']}g)"

        opts = (
                [_item_label(it) for it in shop_stock]
                + ["Sell something", "Ask him something", "Gamble (5g, coin flip)", "Leave"]
        )
        ch = prompt(opts)

        if ch == "Leave":
            print(c("  'Safe roads,' he says. 'If you find any.'", Fore.YELLOW))
            break

        elif ch == "Sell something":
            _merchant_sell(player)

        elif ch == "Gamble (5g, coin flip)":
            if player.gold < 5:
                print(c("  'Need at least 5 gold.'", Fore.YELLOW))
                continue
            player.gold -= 5
            call = prompt(["Heads", "Tails"])
            result = random.choice(["Heads", "Tails"])
            if call == result:
                won = random.randint(8, 15)
                player.gold += won
                print(c(f"  '{result}. You win.' He counts out {won} gold.", Fore.GREEN))
            else:
                print(c(f"  '{result}.' He pockets it without comment.", Fore.RED))

        elif ch == "Ask him something":
            wrap("What do you ask?", Fore.MAGENTA)
            spoken = secret_input(player)
            _merchant_response(player, spoken)

        elif ch == "Buy a rumour (15 gold)":
            if player.gold < 15:
                print(c("  'Rumours cost 15 gold.'", Fore.YELLOW))
            else:
                player.gold -= 15
                RUMOURS = [
                    "The Hall of the Shattered Crown is deeper than most go. "
                    "The third godshard is there — on a plinth. No one guarded it.",
                    "The Void-Touched know where the well is. "
                    "Follow one and they will lead you directly to it.",
                    "There is a room made from leftover space. "
                    "A Candle will show you the door. "
                    "It returns what the ruins have taken.",
                    "The black market is deeper than I go. "
                    "The stock is better. The merchant is not better.",
                    "The Crystal Mirror can be found in the Chamber of Reflections. "
                    "Face-down for a reason.",
                    "The prisoner will trade information for a potion. "
                    "They have been here longer than anyone should be.",
                    "The Hall of the Nine rewards patience. "
                    "Examine all nine. Start with Myrrakhel.",
                    "The Corrupted High Priest is the hardest fight in these ruins. "
                    "Prepare before seeking it out.",
                ]
                # Filter out rumours for things already discovered
                valid = [r for r in RUMOURS
                         if not any(word in r.lower() and flag in player.flags
                                    for word, flag in [
                                        ("shattered crown", "found_shattered_crown_hall"),
                                        ("void-touched", "fought_cultist"),
                                        ("leftover space", "found_recovery_room"),
                                        ("crystal mirror", "obtained_crystal_mirror"),
                                    ])]
                if not valid:
                    valid = RUMOURS  # fallback
                print(c(f"  '{random.choice(valid)}'", Fore.YELLOW))

        else:
            iname = ch.split("  (")[0].rstrip(" ~*")
            stock_item = next((it for it in shop_stock if it["name"] == iname), None)
            if stock_item is None:
                continue
            if player.gold < stock_item["price"]:
                print(c("  'You cannot afford that.'", Fore.RED))
            else:
                player.gold -= stock_item["price"]
                if stock_item["name"] == "Rolled Parchment":
                    player.pick_up(pick_parchment_variant(player))
                else:
                    player.pick_up({k: v for k, v in stock_item.items() if k not in ("price", "rarity")})
                if stock_item["rarity"] == "unique":
                    if not hasattr(player, "purchased_uniques"):
                        player.purchased_uniques = set()
                    player.purchased_uniques.add(stock_item["name"])
                shop_stock = [it for it in shop_stock if it is not stock_item]
                print(c(f"  He sets it on the counter without ceremony.", Fore.YELLOW))


# Items that can be recovered, and which offering flag to check.
# Format: {item_name: (offered_flag, description_of_how_lost)}
RECOVERABLE_ITEMS = {
    "Godshard Fragment": (
        "godshard_offered_shrine",
        "It was offered at the shrine. The ruins have not forgotten."),
    "Dawn Shard": (
        "dawn_shard_offered",
        "It was offered at the shrine. Something of it persists."),
    "Void Shard": (
        "shard_returned",
        "It was returned to the well. A fragment has been left behind."),
    "Vaethar's Tear": (
        "vaethar_tear_offered",
        "It was offered at the shrine or to Atheron."),
    "Dragon Scale": (
        "scale_returned_atheron",
        "It was returned to Atheron. A shed remains."),
    "Starlight Shard": (
        "arukiel_memory",
        "It was offered at the sanctuary pool."),
    "Hollow Stone": (
        "hollow_stone_door",
        "It was placed in the wall. The wall keeps a memory of it."),
    "Warden's Seal": (
        "warden_seal_inscription",
        "It was pressed into the inscription room ash."),
}

def event_recovery_room(player, room):
    """
    The Place Between — a hidden room that restores permanently lost/offered items.
    Only items the player has actually offered (tracked by flags) appear here.
    The room is accessed via a Candle secret in a specific atmospheric room.
    """
    hr("═", colour=Fore.MAGENTA)
    print(c("  THE PLACE BETWEEN", Fore.MAGENTA + Style.BRIGHT))
    hr("═", colour=Fore.MAGENTA)
    print()
    wrap(
        "A room that should not exist. "
        "The walls are the same stone as everywhere else in the ruins, "
        "but they are arranged differently — as though the room was made "
        "from the spaces left over after everything else was built. "
        "On a long shelf that runs the entire length of one wall: objects.",
        Fore.MAGENTA)
    print()
    wrap(
        "You recognise some of them. "
        "Or you would, if you had offered them elsewhere. "
        "The ruins receive. The ruins also, apparently, remember.",
        Fore.MAGENTA + Style.BRIGHT)
    print()
    player.flags.add("found_recovery_room")

    # Build the list of recoverable items this player has lost
    available = []
    for item_name, (flag, desc) in RECOVERABLE_ITEMS.items():
        if flag in player.flags and not player.has_item(item_name):
            # Check if still uniquely held
            unique_flag = UNIQUE_ITEMS.get(item_name)
            # Recovery room bypasses the unique flag — it's a special exception
            available.append((item_name, desc))

    # Also: always offer the three Godshards if missing and previously found
    # This is the critical safety net for the ritual
    for shard_name, obtained_flag in [
        ("Godshard Fragment", "obtained_godshard_1"),
        ("Second Godshard",   "obtained_godshard_2"),
        ("Third Godshard",    "obtained_godshard_3"),
    ]:
        if obtained_flag in player.flags and not player.has_item(shard_name):
            if (shard_name, "It was found and carried, then lost.") not in available:
                available.append((shard_name, "It was found and is no longer in your possession."))

    if not available:
        wrap(
            "The shelf is empty. "
            "You have not offered anything that the ruins can return. "
            "Or you still carry everything you have offered.",
            Fore.LIGHTBLUE_EX + Style.BRIGHT)
    else:
        print(c("  On the shelf:", Fore.MAGENTA))
        for item_name, desc in available:
            print(c(f"    {item_name}", Fore.YELLOW) +
                  c(f"  —  {desc}", Fore.LIGHTBLUE_EX + Style.BRIGHT))
        print()

        while True:
            recover_opts = [f"Take: {name}" for name, _ in available]
            recover_opts += ["Take everything", "Leave it all", "Leave"]
            ch = prompt(recover_opts)

            if ch == "Leave" or ch == "Leave it all":
                break

            elif ch == "Take everything":
                for item_name, _ in available:
                    item = get_item(item_name)
                    if item:
                        # Re-set the unique flag so they can hold it again
                        uf = UNIQUE_ITEMS.get(item_name)
                        if uf:
                            player.flags.add(uf)
                        player.inventory.append(item)
                        print(c(f"  Picked up: {item_name}", Fore.GREEN))
                available = []
                wrap("The shelf is empty.", Fore.MAGENTA)
                break

            else:
                item_name = ch.replace("Take: ", "")
                item = get_item(item_name)
                if item:
                    uf = UNIQUE_ITEMS.get(item_name)
                    if uf:
                        player.flags.add(uf)
                    player.inventory.append(item)
                    print(c(f"  Picked up: {item_name}", Fore.GREEN))
                    available = [(n, d) for n, d in available if n != item_name]
                if not available:
                    wrap("The shelf is empty.", Fore.MAGENTA)
                    break


def _trigger_recovery_room_check(player, room):
    """
    Called when the player holds the Candle in certain atmospheric rooms.
    If in the right room type, reveals a hidden door to the Recovery Room.
    Only fires once.
    """
    if "found_recovery_room" in player.flags:
        return False
    if "recovery_door_found" in player.flags:
        return False

    # The trigger: Candle + a warm room or a room with a drain (specific atmospherics)
    room_name = room.get("name", "")
    trigger_rooms = {"A Warm Room", "The Tilted Room", "The Counting Room"}
    if room_name not in trigger_rooms:
        return False

    wrap(
        "The candle's flame turns a deep, steady purple — "
        "a colour it has not shown before. "
        "It leans toward a section of wall you had not noticed. "
        "The wall, on close inspection, has a seam.",
        Fore.MAGENTA + Style.BRIGHT)
    print()
    ch = prompt(["Push on the seam", "Leave it"])
    if ch == "Push on the seam":
        player.flags.add("recovery_door_found")
        wrap(
            "The wall section turns on a central pivot. "
            "Beyond: a room that the ruins built from leftover space. "
            "On a shelf: things you recognise.",
            Fore.MAGENTA)
        # Create and enter the recovery room inline
        recovery_room = {
            "name":          "The Place Between",
            "description":   "A room made from the space left over after everything else was built.",
            "items":         [],
            "enemies":       [],
            "special_event": "recovery_room",
            "exits":         make_exits(None),
            "ambient":       None,
        }
        event_recovery_room(player, recovery_room)
        return True
    return False

BLACK_MARKET_STOCK = [
    {"name":"Voidforged Sword",     "type":"weapon",    "value":16, "price":55,
     "description":"Black metal. Heavier than it looks, lighter than it should be."},
    {"name":"Stonefather's Maul",   "type":"weapon",    "value":15, "price":50,
     "description":"Stone from elsewhere. Carries patience — and severity."},
    {"name":"Echoed Blade",         "type":"weapon",    "value":14, "price":45,
     "description":"The afterimage does damage too, slightly delayed."},
    {"name":"Null Plate",           "type":"armour",    "value":12, "price":55,
     "description":"Absorbs rather than deflects."},
    {"name":"Starweave Cloak",      "type":"armour",    "value":11, "price":48,
     "description":"Lighter than air. Warmer than stone."},
    {"name":"Ashbound Coat",        "type":"armour",    "value":10, "price":40,
     "description":"Resists curses. The treatment does not wash out."},
    {"name":"Shard of First Light", "type":"consumable","value":40, "price":60,
     "description":"Restores full HP. Cures all conditions. Single use."},
    {"name":"Draught of Echoes",    "type":"consumable","value":35, "price":45,
     "description":"Restores 35 HP. Removes all status effects."},
    {"name":"Void Tincture",        "type":"consumable","value":0,  "price":35,
     "description":"Drain immunity for three fights."},
    {"name":"Strong Tonic",         "type":"consumable","value":25, "price":18,
     "description":"Restores 25 HP."},
    {"name":"Vein-Sealer",          "type":"consumable","value":50, "price":40,
     "description":"Restores 50 HP."},
    # Unique — can only buy once
    {"name":"Void Shard",           "type":"artefact",  "value":0,  "price":80,
     "rarity":"unique",
     "description":"A sliver of absolute dark. It should not exist."},
    {"name":"Blood Key",            "type":"key",       "value":0,  "price":70,
     "rarity":"unique",
     "description":"Deep red. Warm. Not comforting."},
]

def event_black_market(player, room):
    """
    The Black Market — appears only at depth 15+.
    A different kind of merchant. No pleasantries.
    Also buys items at better rates than the regular merchant.
    """
    hr("═", colour=Fore.RED)
    print(c("  THE DEEP MARKET", Fore.RED + Style.BRIGHT))
    hr("═", colour=Fore.RED)
    print()
    wrap(
        "A figure sits behind a low table covered in cloth. "
        "No candles — the stock is lit by something the items themselves emit. "
        "The figure does not look up when you enter.",
        Fore.RED)
    print(c("  'Deep enough to find me. Spend or leave.'", Fore.RED))
    print()

    # Build stock — exclude uniques already purchased
    purchased_uniques = getattr(player, "purchased_uniques", set())
    current_stock = [
        it for it in BLACK_MARKET_STOCK
        if not (it.get("rarity") == "unique" and it["name"] in purchased_uniques)
    ]

    while True:
        print(c(f"  Your gold: {player.gold}", Fore.YELLOW))
        SELL_BONUS = 0.75  # black market pays better than regular merchant

        def _bm_label(it):
            tag = c(" **", Fore.RED) if it.get("rarity") == "unique" else ""
            return f"{it['name']}{tag}  ({it['price']}g)"

        opts = ([_bm_label(it) for it in current_stock]
                + ["Sell something (75% value)", "Leave"])
        ch = prompt(opts)

        if ch == "Leave":
            print(c("  The figure does not acknowledge your departure.", Fore.RED))
            break

        elif ch == "Sell something (75% value)":
            _black_market_sell(player, SELL_BONUS)

        else:
            iname = ch.split("  (")[0].rstrip(" *")
            item = next((it for it in current_stock if it["name"] == iname), None)
            if item is None:
                continue
            if player.gold < item["price"]:
                print(c("  'Not enough.'", Fore.RED))
            else:
                player.gold -= item["price"]
                purchased = {k: v for k, v in item.items()
                             if k not in ("price", "rarity")}
                uf = UNIQUE_ITEMS.get(item["name"])
                if uf:
                    player.flags.add(uf)
                player.pick_up(purchased)
                if item.get("rarity") == "unique":
                    if not hasattr(player, "purchased_uniques"):
                        player.purchased_uniques = set()
                    player.purchased_uniques.add(item["name"])
                    current_stock = [it for it in current_stock if it is not item]
                print(c("  They set it on the cloth without looking at you.", Fore.RED))


def _black_market_sell(player, rate: float):
    """Sell at a higher rate than the regular merchant."""
    sellable = [
        it for it in player.inventory
        if it.get("type") not in _UNSELLABLE_TYPES
           and it.get("name") not in _UNSELLABLE_NAMES
    ]
    if not sellable:
        print(c("  'Nothing I want.'", Fore.RED))
        return

    while True:
        def _bm_sell_value(item):
            base = _sell_value(item)
            return max(2, int(base * (rate / 0.55)))  # scale up from standard rate

        print(c(f"  Your gold: {player.gold}", Fore.YELLOW))
        opts = ([f"{it['name']}  ({_bm_sell_value(it)}g)" for it in sellable]
                + ["Done selling"])
        ch = prompt(opts)
        if ch == "Done selling":
            break
        iname = ch.split("  (")[0]
        item = next((it for it in sellable if it["name"] == iname), None)
        if item is None:
            continue
        if item is player.equipped.get("weapon") or item is player.equipped.get("armour"):
            slot = "weapon" if item is player.equipped.get("weapon") else "armour"
            confirm = prompt([f"Sell equipped {slot}?", "Keep it"])
            if confirm == "Keep it":
                continue
            player.equipped[slot] = None
        earned = _bm_sell_value(item)
        player.gold += earned
        player.inventory.remove(item)
        sellable = [it for it in sellable if it is not item]
        print(c(f"  They count out {earned} gold without comment.", Fore.RED))
        if not sellable:
            break

def event_cartographers_station(player, room):
    """
    The Cartographer's Station — a Remnant Scholar's abandoned workspace.
    The player can view their map, buy map improvements, and find lore.
    """
    hr(colour=Fore.CYAN)
    print(c("  THE CARTOGRAPHER'S STATION", Fore.CYAN + Style.BRIGHT))
    hr(colour=Fore.CYAN)
    print()
    wrap(
        "A scholar's workspace — tools for mapping, rulers, inks, "
        "a large flat table with partial maps pinned to it. "
        "The maps cover the upper ruins only. "
        "Below a certain depth, the cartographer apparently stopped.",
        Fore.CYAN)
    print()
    player.flags.add("found_cartographers_station")

    done = room.get("_cart_done", set())

    while True:
        opts = []
        if "view_maps" not in done: opts.append("Study the existing maps")
        #if "your_map" not in done:  opts.append("View your own map")
        opts.append("View your own map")  # always available after first visit
        if "buy_compass" not in done and player.gold >= 25:
            opts.append("Buy a compass (25 gold — shows room type hints)")
        if player.gold >= 15 and "buy_notes" not in done:
            opts.append("Buy the cartographer's notes (15 gold)")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Study the existing maps":
            done.add("view_maps")
            wrap(
                "The maps are incomplete but useful. "
                "They show the upper ruins in detail: "
                "the approach corridors, the first library, the shrine alcoves. "
                "A note in the margin: 'Void-Touched presence confirmed depth 8+. '",
                Fore.CYAN)
            wrap(
                "'Three factions confirmed: Remnant Scholars (non-hostile), "
                "Void-Touched (hostile, organised), Shard-Seekers (mercenary, variable). '",
                Fore.CYAN)
            wrap("'Do not engage the Void-Touched in groups.'", Fore.CYAN + Style.BRIGHT)
            player.flags.add("read_cartographer_maps")

        elif ch == "View your own map":
            if player.dungeon and player.map:
                player.dungeon.display_map(player.dungeon_pos, player)
            else:
                wrap("You have not yet been tracking your path.", Fore.LIGHTBLUE_EX + Style.BRIGHT)

        elif ch.startswith("Buy a compass"):
            done.add("buy_compass")
            player.gold -= 25
            player.flags.add("has_compass")
            wrap(
                "The compass is old but functional. "
                "It does not point north — it points toward the nearest unexplored exit. "
                "Or rather: it points toward the nearest room that is waiting.",
                Fore.GREEN)
            print(c("  -25 gold. Room hints now show more detail.", Fore.YELLOW))

        elif ch.startswith("Buy the cartographer's notes"):
            done.add("buy_notes")
            player.gold -= 15
            player.pick_up(get_item("Remnant Scholar's Notes"))
            print(c("  -15 gold.", Fore.YELLOW))

        room["_cart_done"] = done


def event_warden_bell(player, room):
    """
    The Warden's Bell. Ringing it is permanent and significant.
    """
    hr("═", colour=Fore.RED)
    print(c("  THE WARDEN'S BELL", Fore.RED + Style.BRIGHT))
    hr("═", colour=Fore.RED)
    print()
    wrap(
        "A bell, suspended from the ceiling by a chain that should have rusted "
        "through centuries ago. It is massive — the kind of bell that is not rung "
        "by a single person casually. A dedicated rope hangs from the striker. "
        "The bell is Eldrosian work, imperial period. "
        "Along its rim: AN IMPERIAL LOCKDOWN IS HEREBY DECLARED.",
        Fore.RED)
    print()

    if "warden_bell_rung" in player.flags:
        wrap(
            "The bell has already been rung. "
            "The ruins are already awake. "
            "The bell itself seems satisfied.",
            Fore.RED)
        return

    wrap(
        "The Eldrosian empire used these bells to signal lockdown — "
        "every gate sealed, every patrol activated, "
        "every creature in the ruins responding to a standing order "
        "that has apparently been waiting for someone to ring this bell "
        "for the past several centuries.",
        Fore.RED + Style.BRIGHT)
    print()
    wrap(
        "You do not have to ring it.",
        Fore.LIGHTBLUE_EX + Style.BRIGHT)
    print()

    ch = prompt([
        "Ring the bell",
        "Leave it silent",
        "Examine the bell more carefully",
    ])

    if ch == "Examine the bell more carefully":
        wrap(
            "The bell's interior has an inscription not visible from the outside: "
            "'TO WAKE THE RUINS IS TO EARN THEM.' "
            "Below this, a date — the last year of the empire — "
            "and a single name: SERETHAN. WARDEN-COMMANDER. "
            "He never rang it.",
            Fore.RED)
        player.flags.add("read_bell_inscription")
        print()
        ch = prompt(["Ring the bell", "Leave it silent"])

    if ch == "Ring the bell":
        if "warden_bell_rung" in player.flags:
            wrap("It has already been rung.", Fore.RED)
            return

        wrap(
            "You pull the rope.",
            Fore.RED + Style.BRIGHT)
        print()
        wrap(
            "The sound is not loud — not immediately. "
            "It starts as a resonance in the stone beneath your feet, "
            "then in the walls, then in the air, and by the time it reaches "
            "the pitch you recognise as a bell's strike it has already "
            "passed through the entire ruin.",
            Fore.RED + Style.BRIGHT)
        from colorama import Style as St
        import time
        for _ in range(3):
            print(c("  . . .", Fore.RED + St.BRIGHT))

        wrap(
            "Somewhere — everywhere — something responds. "
            "Not footsteps. Not movement. "
            "An alertness. The ruins are awake.",
            Fore.RED + Style.BRIGHT)
        print()
        wrap(
            "ALL ENEMIES NOW HAVE DOUBLED HEALTH AND ATTACK. "
            "SPAWN RATES HAVE INCREASED. "
            "THIS IS PERMANENT.",
            Fore.RED + Style.BRIGHT)
        print()
        player.flags.add("warden_bell_rung")


    else:
        wrap(
            "You leave the bell silent. "
            "Serethan left it silent too. "
            "Some things are better left for someone else to decide.",
            Fore.LIGHTBLUE_EX + Style.BRIGHT)


# ── SELL ──────────────────────────────────────────────────────────────────────

_UNSELLABLE_TYPES = {"key", "lore"}
_UNSELLABLE_NAMES = {
    "Godshard Fragment", "Second Godshard", "Third Godshard",
    "Vaethar's Tear", "Agreement Stone", "Void Shard",
    "Starlight Shard", "Starlight Key", "Ashen Key",
    "Warden's Key", "Blood Key", "Throne Key", "Hollow Stone",
    "Crystal Mirror", "Codex of the First Age",
}

# Sell rates by rarity (for shop items) or by type (for loot items)
_SELL_RATE_BY_RARITY = {
    "common":   0.55,
    "uncommon": 0.65,
    "rare":     0.75,
    "unique":   0.85,
}
_SELL_RATE_BY_TYPE = {
    "weapon":     0.55,
    "armour":     0.55,
    "consumable": 0.60,
    "artefact":   0.50,
}

# Build a lookup of shop prices by item name for use in _sell_value
_SHOP_PRICE_BY_NAME = {it["name"]: it["price"] for it in SHOP_STOCK}
def _sell_value(item):
    """
    Return gold the merchant will pay.
    Looks up the shop price first (by name), so loot items that also
    appear in the shop sell for a proper fraction of their buy price.
    Falls back to the item's value field for anything not sold in the shop.
    """
    name = item.get("name", "")

    if name in _SHOP_PRICE_BY_NAME:
        # Item exists in the shop — use its buy price and rarity rate
        shop_price = _SHOP_PRICE_BY_NAME[name]
        rarity = item.get("rarity") or next(
            (it["rarity"] for it in SHOP_STOCK if it["name"] == name), "common"
        )
        rate = _SELL_RATE_BY_RARITY.get(rarity, 0.55)
        return max(2, int(shop_price * rate))
    else:
        # Not in the shop — use value and type
        rate = _SELL_RATE_BY_TYPE.get(item.get("type", "weapon"), 0.55)
        base = item.get("value", 0)
        if base == 0:
            return 5
        return max(2, int(base * rate))


def _merchant_sell(player):
    """Let the player sell items from their inventory."""
    while True:
        sellable = [
            it for it in player.inventory
            if it.get("type") not in _UNSELLABLE_TYPES
               and it.get("name") not in _UNSELLABLE_NAMES
        ]
        if not sellable:
            print(c("  'Nothing I'd want from you.'", Fore.YELLOW))
            break

        print(c(f"\n  Your gold: {player.gold}", Fore.YELLOW))
        opts = (
                [f"{it['name']}  ({_sell_value(it)}g)" for it in sellable]
                + ["Done selling"]
        )
        ch = prompt(opts)

        if ch == "Done selling":
            break

        iname = ch.split("  (")[0]
        item = next((it for it in sellable if it["name"] == iname), None)
        if item is None:
            continue

        # Warn before selling equipped items
        if item is player.equipped.get("weapon") or item is player.equipped.get("armour"):
            slot = "weapon" if item is player.equipped.get("weapon") else "armour"
            confirm = prompt([f"Sell equipped {slot}?", "Keep it"])
            if confirm == "Keep it":
                continue
            player.equipped[slot] = None

        earned = _sell_value(item)
        player.gold += earned
        player.inventory.remove(item)
        print(c(f"  He turns it over once, sets down {earned} gold.", Fore.YELLOW))

def _merchant_response(player, spoken):
    # Gate checks — merchant won't answer what player hasn't earned context for
    if any(w in spoken for w in ("eldros","empire","ruins","capital")):
        wrap("'Eldros-Verath. The first empire. Grand, classical, loved ceremony. "
             "Gone in a single night.' He straightens a jar. "
             "'They called it divine punishment. I call it betrayal.'", Fore.YELLOW)

    elif any(w in spoken for w in ("vaelan","emperor")) and knows_vaelan(player):
        wrap("'Emperor Vaelan. The last emperor. Holder of the Godshards — the fragments of "
             "Vaethar, Atheron's chosen child, who gave their form to empower the imperial line.' "
             "He sets something down carefully. 'Vaelan died on his throne. "
             "The Godshards were there when it happened. Where they are now — ' "
             "He shrugs. 'Unknown.'", Fore.YELLOW)
        player.flags.add("merchant_godshards")

    elif any(w in spoken for w in ("vaelan","emperor")):
        wrap("'The emperor? You know enough to ask the question, but not enough yet for the answer. '", Fore.YELLOW)
        wrap("'Find out more about the fall first.'", Fore.YELLOW)

    elif any(w in spoken for w in ("godshard","godshards","vaethar")) and knows_godshards(player):
        wrap("'The Godshards.' He's quiet a moment. 'Fragments of Vaethar — Atheron's chosen child, "
             "who gave up their physical form so that the power could be divided across the imperial "
             "bloodline. The emperor who held the full set held something close to a god's authority.' "
             "A pause. 'Vaelan was the last to hold them all.'", Fore.YELLOW)
        player.flags.add("merchant_godshards")

    elif any(w in spoken for w in ("godshard","godshards","vaethar")):
        wrap("'You're asking about things that require more context than you currently have. '", Fore.YELLOW)
        wrap("'The ruins will tell you. Keep looking.'", Fore.YELLOW)

    elif any(w in spoken for w in ("morvath","veythari","near-mortal","near mortal")):
        wrap("'Near-mortals. Morvath love darkness. Veythari love starlight. "
             "Similar purpose, different faces. Both formed from wells. Most burned with Eldros.' "
             "He pauses. 'Not all.'", Fore.YELLOW)

    elif any(w in spoken for w in ("wells","void well","nine wells","the nine")) and knows_wells(player):
        wrap("'Nine wells beneath the world. The Void-well is the one below us — the oldest. '",Fore.YELLOW)
        wrap("'I know hints of others: a Bloodwell, an Astral-well, a Hollow-well, a Dawnwell. '",Fore.YELLOW)
        wrap("'Each produced something. Things, powers, artefacts. '",Fore.YELLOW)
        wrap("'At the centre of all of them — something older than the wells themselves.'",Fore.YELLOW)
        player.flags.add("merchant_told_wells")

    elif any(w in spoken for w in ("wells","void well","nine wells")):
        wrap("'I know about the wells. You don't yet know enough to understand my answer. '", Fore.YELLOW)
        wrap("'Keep exploring. You'll find the right questions first.'", Fore.YELLOW)

    elif any(w in spoken for w in ("thaun","hollow")) and knows_thaun(player):
        wrap("'Thaun the Hollow. Rose from the Void-well at the beginning of things. "
             "He is hollow because the void is still inside him.' "
             "He meets your eyes. 'The well is somewhere in these ruins.'", Fore.YELLOW)

    elif any(w in spoken for w in ("thaun","hollow")):
        wrap("'That name requires context I'm not sure you have yet.'", Fore.YELLOW)

    elif any(w in spoken for w in ("atheron","dragon","king of dragons")):
        wrap("'Atheron — King of Dragons. Walked the world when it was new. "
             "Some say he still sleeps in the deep places.' He glances at the floor. "
             "'Some say these are the deep places.'", Fore.YELLOW)

    elif any(w in spoken for w in ("arukiel","falling light")) and knows_arukiel(player):
        wrap("'Arukiel of the Falling Light — fell from the sky in choice, not accident. "
             "First Veythari. Ancestor of those who inhabit starlight.' "
             "'Her kin are mostly gone now.'", Fore.YELLOW)

    elif any(w in spoken for w in ("arukiel","falling light")):
        wrap("'That name is one I know. But you should find out about it yourself first.'", Fore.YELLOW)

    elif any(w in spoken for w in ("myrrakhel","deepest pulse")) and knows_gods(player):
        wrap("'Myrrakhel. The Deepest Pulse. First god — the one that made the others. "
             "Nine gods in total; Myrrakhel is the root. '", Fore.YELLOW + Style.BRIGHT)
        wrap("'The others have names: Kindrael, Loría, Thalás, Thar, Ishak, Ysena, Vastinö, Kelamaris — "
             "called the Thrys. The eight that Myrrakhel made.' He returns to his goods. "
             "'Myrrakhel has not spoken since the Night of Collapse.'", Fore.YELLOW + Style.BRIGHT)
        player.flags.add("merchant_myrrakhel")

    elif any(w in spoken for w in ("myrrakhel","deepest pulse")):
        wrap("'That name. You're not ready for what I'd have to say around it. '", Fore.YELLOW)
        wrap("'Find the context first.'", Fore.YELLOW)

    elif any(w in spoken for w in ("betrayal","betrayer","who did it","the fall")) and knows_betrayer_hint(player):
        wrap("'Names have been removed from every record here. Not forgotten — removed. '", Fore.YELLOW)
        wrap("'That is harder than forgetting and says more about whoever did it.' "
             "He returns to his goods. 'Stop asking before you find the answer.'", Fore.YELLOW)

    elif any(w in spoken for w in ("dravennis","blood of magi","drinks blood")) and knows_dravennis(player):
        wrap("He looks at you directly. 'Where did you hear that name?' A long pause. "
             "'Dravennis operates far from here. He who drinks the blood of magi. '", Fore.MAGENTA)
        wrap("'Do not say that name again in the deep rooms. Names carry differently down here.'", Fore.MAGENTA)
        player.flags.add("heard_dravennis")

    elif any(w in spoken for w in ("silver eyes","who are you","what are you")):
        wrap("He smiles. 'A merchant.' Holds your gaze. "
             "'The light down here makes eyes look strange.' Nothing else.", Fore.YELLOW)

    else:
        print(c(f"  {random.choice(['Answers cost more than gold.','Ask the walls. They were here first.','A good question. No intention of answering it.','Hmm.'])}", Fore.YELLOW))

# ─── ARCHIVIST ────────────────────────────────────────────────────────────────
def event_archivist(player, room):
    """
    The Archivist — a Remnant Scholar who has been here for years.
    Gives lore, sells maps, tracks faction information.
    """
    hr("═", colour=Fore.CYAN)
    print(c("  THE ARCHIVIST", Fore.CYAN + Style.BRIGHT))
    hr("═", colour=Fore.CYAN)
    print()

    if is_hostile(player, "scholars"):
        wrap(
            "The archivist looks up. Then away. "
            "'You've made enemies of my colleagues. "
            "I have nothing to say to you.'",
            Fore.CYAN)
        return

    if "met_archivist" not in player.flags:
        player.flags.add("met_archivist")
        adjust_reputation(player, "scholars", 1)
        wrap(
            "An elderly figure, seated on a folding stool, "
            "surrounded by papers and annotated maps. "
            "They look up at you with the calm of someone who has long since stopped "
            "being surprised by the ruins.",
            Fore.CYAN)
        print()
        wrap(
            "  'I've been here eleven years. I keep a record. "
            "My colleagues think I'm mad. They're probably right. "
            "Sit down, if you like — there's a crate.'",
            Fore.CYAN + Style.BRIGHT)
    else:
        wrap(
            "The Archivist nods at you. "
            "They are in the same place. The papers have changed.",
            Fore.CYAN)

    print()
    asked = room.get("_archivist_asked", set())

    while True:
        opts = []
        if "factions" not in asked:
            opts.append("Ask about the factions in the ruins")
        if "history" not in asked:
            opts.append("Ask what they have learned about Eldros")
        if "void_touched" not in asked and "fought_cultist" in player.flags:
            opts.append("Ask what they know about the Void-Touched")
        if "godshards" not in asked and "found_throne_room" in player.flags:
            opts.append("Ask what the Godshards mean — you have found them")
        if "atraxis" not in asked and "atraxis_named" in player.flags:
            opts.append("Share the name Atraxis")
        if player.gold >= 20 and "buy_map" not in asked:
            opts.append("Buy their partial map of the ruins (20 gold)")
        if player.gold >= 10 and "buy_notes" not in asked:
            opts.append("Buy the Field Guide to the Void-Touched (10 gold)")
        if is_allied(player, "scholars"):
            opts.append("Ask for their most secret discovery")
        opts.append("Leave")

        if len(opts) == 1:
            wrap("  'Ask me something.'", Fore.CYAN)
            break

        ch = prompt(opts)
        if ch == "Leave":
            wrap("  'Be methodical. The ruins reward patience.'", Fore.CYAN)
            break

        elif ch == "Ask about the factions in the ruins":
            asked.add("factions")
            wrap(
                "'Three groups, by my count. The Remnant Scholars — my colleagues — "
                "are here for knowledge. Non-violent. Mostly. '",
                Fore.CYAN)
            wrap(
                "'The Void-Touched are organised in a way that worries me. "
                "They have a hierarchy. Someone is giving instructions. '",
                Fore.CYAN)
            wrap(
                "'The Shard-Seekers are mercenaries. They work for someone outside — "
                "someone who wants the Godshards and has money. "
                "I have not been able to find out who.'",
                Fore.CYAN)
            player.flags.add("archivist_factions")

        elif ch == "Ask what they have learned about Eldros":
            asked.add("history")
            wrap(
                "'Eldros-Verath was the centre of the world for eleven hundred years. "
                "That is not metaphor — I mean literally. Every major road, trade route, "
                "and sea lane was measured from the capital. '",
                Fore.CYAN)
            wrap(
                "'It fell in a night. Not over a decade. Not over a year. One night. "
                "Whatever happened, it was decisive. Something wanted it done quickly.'",
                Fore.CYAN + Style.BRIGHT)
            player.flags.add("archivist_history")

        elif ch == "Ask what they know about the Void-Touched":
            asked.add("void_touched")
            wrap(
                "'They call themselves the Void-Touched because they believe "
                "contact with the Void improves them. They are wrong about the improvement. "
                "They are not entirely wrong about the contact. '",
                Fore.CYAN)
            wrap(
                "'Their leader — or what they treat as a leader — "
                "is somewhere in the deep ruins. '",
                Fore.CYAN)
            wrap(
                "'They know the name Atraxis. Some of them speak it during rituals. "
                "The ones who speak it most frequently are the ones who are furthest along.'",
                Fore.CYAN + Style.BRIGHT)
            if "atraxis_named" not in player.flags:
                wrap("'Furthest along what? I would rather not say.'", Fore.CYAN)
            player.flags.add("archivist_void_touched")

        elif ch == "Ask what the Godshards mean — you have found them":
            asked.add("godshards")
            wrap(
                "They set their pen down. Look at you properly for the first time.",
                Fore.CYAN)
            wrap(
                "'You found them. You actually found them. I've been theorising for "
                "eleven years — ' A pause. 'The Godshards are fragments of Vaethar, "
                "Atheron's chosen child. They were split across the imperial bloodline. '",
                Fore.CYAN)
            wrap(
                "'What I want to know — what I have wanted to know for eleven years — "
                "is whether the fragments respond to a specific invocation. '",
                Fore.CYAN)
            wrap(
                "'The Codex of the First Age would tell you. If you can read it. '",
                Fore.CYAN + Style.BRIGHT)
            player.flags.add("archivist_godshards")
            if "knows_ritual_phrase" in player.flags:
                wrap(
                    "You tell them what the Codex said. Their expression is difficult to read. "
                    "'Then it is possible. The ritual is possible.' "
                    "They begin writing very quickly.",
                    Fore.CYAN + Style.BRIGHT)
                adjust_reputation(player, "scholars", 1)

        elif ch == "Share the name Atraxis":
            asked.add("atraxis")
            wrap(
                "They react. Not dramatically — they simply go very still.",
                Fore.CYAN)
            wrap(
                "'Where did you hear that name?' "
                "You tell them. They write it down carefully. "
                "'The Void-Touched use it. We had suspected there was a proper name. '",
                Fore.CYAN)
            wrap(
                "'Atraxis. That is the Unmade's actual name. "
                "Not what the near-mortals call it — its name. "
                "The distinction matters. Names carry weight down here.'",
                Fore.CYAN + Style.BRIGHT)
            adjust_reputation(player, "scholars", 1)
            player.flags.add("archivist_atraxis")

        elif "Buy their partial map" in ch:
            asked.add("buy_map")
            player.gold -= 20
            player.pick_up({
                "name": "Archivist's Map", "type": "lore", "value": 0,
                "description": "A partial map of the ruins, annotated in a scholar's hand. "
                               "The upper two floors are detailed. The lower three are sketched "
                               "with the note: 'further investigation needed (see notes).'"
            })
            wrap("  'It's eleven years of work. Use it carefully.'", Fore.CYAN)
            print(c("  -20 gold.", Fore.YELLOW))

        elif "Buy the Field Guide" in ch:
            asked.add("buy_notes")
            player.gold -= 10
            player.pick_up(get_item("A Field Guide to the Void-Touched"))
            wrap("  'Read it. Then be careful.'", Fore.CYAN)
            print(c("  -10 gold.", Fore.YELLOW))

        elif "most secret discovery" in ch:
            wrap(
                "They hesitate for a long time.",
                Fore.CYAN)
            wrap(
                "'The Void-Touched have a ritual site. Deep. Floor four. '",
                Fore.CYAN)
            wrap(
                "'They have been performing a ritual there for months. "
                "I do not know what it does. "
                "I do know that the two scholars who went to observe did not come back. '",
                Fore.CYAN)
            wrap(
                "'The ritual site is near the Atraxis Scar. '",
                Fore.CYAN + Style.BRIGHT)
            player.flags.add("archivist_ritual_site")
            adjust_reputation(player, "scholars", 1)

        room["_archivist_asked"] = asked

# ─── BOUND ONE ────────────────────────────────────────────────────────────────
def event_bound_one(player, room):
    """
    The Bound One — a cultist who has partially accepted the Void
    and is struggling with it. Neither hostile nor trustworthy.
    """
    hr("═", colour=Fore.MAGENTA)
    print(c("  THE BOUND ONE", Fore.MAGENTA + Style.BRIGHT))
    hr("═", colour=Fore.MAGENTA)
    print()

    if is_hostile(player, "void_touched") and "met_bound_one" in player.flags:
        wrap(
            "They regard you with something dark. "
            "'You have made enemies of us. I have nothing to offer you.'",
            Fore.MAGENTA)
        _do_cultist_fight(player)
        return

    if "met_bound_one" not in player.flags:
        player.flags.add("met_bound_one")
        wrap(
            "A figure sits with their back against the wall, "
            "one hand pressing flat against the stone as if anchoring themselves. "
            "Half their face is in shadow. The half you can see looks exhausted.",
            Fore.MAGENTA)
        print()
        wrap(
            "  'I can hear it,' they say, without looking at you. "
            "'All the time. It is not a voice. It is a direction. '",
            Fore.MAGENTA + Style.BRIGHT)
        wrap(
            "  'I came here to find something. "
            "I found the Void-Touched instead. "
            "I thought they were going somewhere. "
            "They are. I am not sure I want to go there.'",
            Fore.MAGENTA + Style.BRIGHT)
    else:
        wrap("They are in the same position. Still anchoring themselves.", Fore.MAGENTA)

    print()
    asked = room.get("_bound_asked", set())

    while True:
        opts = []
        if "what" not in asked:
            opts.append("Ask what is happening to them")
        if "atraxis" not in asked:
            opts.append("Ask about Atraxis")
        if "ritual" not in asked and "archivist_ritual_site" in player.flags:
            opts.append("Ask about the ritual site")
        if "help" not in asked:
            opts.append("Offer to help them resist")
        if "name" not in asked and "atraxis_named" in player.flags:
            opts.append("Speak the name Atraxis aloud")
        if is_allied(player, "void_touched"):
            opts.append("Offer to guide them further into the process")
        opts.append("Leave them")

        ch = prompt(opts)
        if ch == "Leave them":
            wrap(
                "They do not watch you go. Their hand presses harder against the stone.",
                Fore.MAGENTA)
            break

        elif ch == "Ask what is happening to them":
            asked.add("what")
            wrap(
                "'The Void-Touched believe the contact with Atraxis improves you. "
                "They are right that it changes you. '",
                Fore.MAGENTA)
            wrap(
                "'What I feel: the direction is very clear. "
                "It tells me where Atraxis is — below, in the well — "
                "and it pulls. Not violently. Constantly. '",
                Fore.MAGENTA)
            wrap(
                "'The ones who are further along do not resist anymore. "
                "The ones who do not resist are the ones who lost their names.'",
                Fore.MAGENTA + Style.BRIGHT)
            player.flags.add("bound_one_explained")

        elif ch == "Ask about Atraxis":
            asked.add("atraxis")
            wrap(
                "'Atraxis is not what the Void-Touched say it is. '",
                Fore.MAGENTA)
            wrap(
                "'They say it is power. It is not power. "
                "It is — direction. Purpose without content. "
                "It points everything toward itself the way gravity points things down. '",
                Fore.MAGENTA)
            wrap(
                "'It does not want you. It is not capable of wanting. "
                "It is the shape of wanting, without the feeling of it.'",
                Fore.MAGENTA + Style.BRIGHT)
            player.flags.add("bound_one_atraxis")
            adjust_reputation(player, "void_touched", 1)  # knowing more makes them trust you

        elif ch == "Ask about the ritual site":
            asked.add("ritual")
            wrap(
                "'The Scar. They perform it at the Scar, where the Void came through. "
                "The ritual is an invitation — an open door. '",
                Fore.MAGENTA)
            wrap(
                "'They are trying to widen what Maelvyr opened. '",
                Fore.MAGENTA)
            wrap(
                "'I attended twice. The third time I — did not go. "
                "I came here instead. I pressed my hand against the stone.'",
                Fore.MAGENTA + Style.BRIGHT)
            player.flags.add("bound_one_ritual")

        elif ch == "Offer to help them resist":
            asked.add("help")
            if player.has_item("Dawn Shard"):
                wrap(
                    "On instinct, you hold out the Dawn Shard. "
                    "The light it holds brightens. "
                    "They recoil — then lean toward it, "
                    "the way something moving in the wrong direction "
                    "recognises that it has been moving in the wrong direction.",
                    Fore.YELLOW + Style.BRIGHT)
                wrap(
                    "The direction in their eyes dims. Very slightly. "
                    "'What is that?' "
                    "You let them hold it for a moment. "
                    "When they give it back, they are sitting up straighter.",
                    Fore.YELLOW)
                player.flags.add("bound_one_helped")
                adjust_reputation(player, "scholars", 1)
                adjust_reputation(player, "void_touched", -1)
                # They give something back
                wrap(
                    "'The deep route. The Void-Touched use a passage "
                    "behind the Naming Room. It goes directly to the fourth floor. '",
                    Fore.MAGENTA)
                player.flags.add("bound_one_passage")
            else:
                wrap(
                    "You offer. They look at your hands. "
                    "'You have nothing that counters it.' "
                    "Not unkindly. Factually.",
                    Fore.MAGENTA)

        elif ch == "Speak the name Atraxis aloud":
            asked.add("name")
            wrap(
                "When you speak the name, their eyes go wide. "
                "The half in shadow brightens — briefly, wrongly — "
                "and then they press their hand harder against the stone.",
                Fore.MAGENTA + Style.BRIGHT)
            wrap(
                "'Don't. That name — the direction gets stronger when you say it here. "
                "Someone told you the name. You know more than I thought.'",
                Fore.MAGENTA)
            adjust_reputation(player, "void_touched", 1)
            player.flags.add("bound_one_name_spoken")

        elif "guide them further" in ch:
            asked.add("guided")
            wrap(
                "You offer. They look at you for a long time. "
                "'You have allied yourself with them. I see that now.' "
                "A long pause. "
                "'Show me the way, then.'",
                Fore.RED)
            wrap(
                "They stand. The hand leaves the wall. "
                "Their eyes go to the direction. They go toward it. "
                "They do not look back.",
                Fore.RED + Style.BRIGHT)
            player.flags.add("bound_one_guided")
            adjust_reputation(player, "void_touched", 1)
            break

        room["_bound_asked"] = asked


# ─── PRISONER ─────────────────────────────────────────────────────────────────
def event_prisoner(player, room):
    wrap("They look up. Old — remarkably old — but their eyes are entirely clear. "
         "They do not seem afraid of you.")
    LINES = [
        "'The doors down here kept things in as often as out.'",
        "'Something large breathes in the deep halls. I've heard it for years.'",
        "'I came looking for the well. Found this cell. That was some time ago.'",
        "'What the empire buried, it buried carefully. That's worth remembering.'",
        "'There is a word on the lowest wall I found. I will not repeat it.'",
        "'The keys are scattered. The locks are patient.'",
    ]
    print(); print(c(f"  {random.choice(LINES)}", Fore.YELLOW)); print()
    asked = room.get("_prisoner_asked", set())

    while True:
        opts = []
        if "eldros" not in asked:
            opts.append("Ask about the ruins")
        if "well" not in asked and knows_eldros(player):
            opts.append("Ask about the well")
        if "gods" not in asked and knows_fall(player):
            opts.append("Ask about the gods")
        if "vaelan" not in asked and knows_fall(player):
            opts.append("Ask about the emperor")
        if "dravennis" not in asked and len(asked) >= 2:
            opts.append("Ask about anyone still connected to Eldros")
        opts += ["Offer a Health Potion", "Leave"]
        ch = prompt(opts)

        if ch == "Ask about the ruins":
            asked.add("eldros")
            wrap("'These are the ruins of Eldros-Verath — the capital, and the empire's name. "
                 "The first and greatest. Gone in a single night. '", Fore.YELLOW)
            wrap("'Something happened here. Records call it divine punishment.' "
                 "They look at their hands. 'I call it betrayal. The records won't say by whom.'", Fore.YELLOW)
            player.flags.add("prisoner_told_eldros")

        elif ch == "Ask about the well":
            asked.add("well")
            wrap("'There are nine wells beneath the world. This ruin sits above the Void-well — "
                 "the first, the deepest. I haven't reached it. Things formed from the wells. '", Fore.YELLOW)
            wrap("'Thaun from the Void-well. Others from others. '",Fore.YELLOW)
            wrap("'They are not gods. Not creatures. What was made before anything had a name for itself.'", Fore.YELLOW)
            player.flags.add("prisoner_told_well")

        elif ch == "Ask about the gods":
            asked.add("gods")
            wrap("'Nine gods. Made by the first of them — the oldest, the deepest. '", Fore.YELLOW)
            wrap("'They granted audience to Eldros. The records of those audiences are here somewhere. '",Fore.YELLOW)
            wrap("'They do not speak anymore. Something broke that relationship. '",Fore.YELLOW)
            wrap("'I've been down here long enough to suspect what.'", Fore.YELLOW)
            player.flags.add("prisoner_told_gods")

        elif ch == "Ask about the emperor":
            asked.add("vaelan")
            wrap("'Emperor Vaelan. The last emperor. He held the Godshards — '", Fore.YELLOW)
            wrap("'artefacts of tremendous power. One story says he died on his throne. '", Fore.YELLOW)
            wrap("'If that's true, and the throne is still in these ruins — ' "
                 "They stop. 'It would explain the condition of the throne room.'", Fore.YELLOW)
            player.flags.add("prisoner_told_vaelan")

        elif "still connected" in ch or "anyone" in ch:
            asked.add("dravennis")
            wrap("'There is a name I've heard. Someone far from here who seeks out those '", Fore.YELLOW)
            wrap("'with the gift of magik, and takes something from them. Blood, some say. '", Fore.YELLOW)
            wrap("'I don't know if the name is right. But I heard: Dravennis.'", Fore.YELLOW)
            player.flags.add("prisoner_dravennis")

        elif ch == "Offer a Health Potion":
            potion = next((it for it in player.inventory if it["name"] == "Health Potion"), None)
            if potion:
                player.inventory.remove(potion)
                if "obtained_ashen_key" not in player.flags:
                    wrap("They take it. Nod once. "
                         "'Kinder than the last one through here.' "
                         "They produce a small key — black, faintly warm. "
                         "'I found this. I can\\'t leave to use it.'", Fore.GREEN)
                    try_give_unique(player, "Ashen Key")
                    player.attack += 1
                    print(c("  Something about the act steadies you. ATK +1.", Fore.GREEN))
                else:
                    wrap("They take it. Nod once. "
                         "'You\\'ve already been kinder than most. I have nothing left to give.'",
                         Fore.YELLOW)
            else:
                print("  You have no potion to give.")

        elif ch == "Leave":
            print(c("  You leave them to their silence.", Fore.LIGHTBLUE_EX + Style.BRIGHT)); break

        room["_prisoner_asked"] = asked


# ─── SAEL ─────────────────────────────────────────────────────────────────────
def event_sael_chamber(player, room):
    wrap("The figure turns. Tall, with silver eyes illuminated from behind. "
         "She regards you for a long moment.", Fore.WHITE)
    print(); print(c("  'Another one,' she says, in a voice like cooled glass. 'Come in, then.'", Fore.WHITE)); print()
    asked = room.get("_sael_asked", set())

    while True:
        opts = []
        if "eldros" not in asked:
            opts.append("Ask about Eldros")
        if "race" not in asked:
            opts.append("Ask what she is")
        if "thaun" not in asked and knows_thaun(player):
            opts.append("Ask about Thaun the Hollow")
        if "arukiel" not in asked and knows_arukiel(player):
            opts.append("Ask about Arukiel")
        if "fall" not in asked and knows_fall(player):
            opts.append("Ask about the fall of the empire")
        if "wells" not in asked and knows_wells(player):
            opts.append("Ask about the wells")
        if "gods" not in asked and knows_gods(player):
            opts.append("Ask about the Great Gods")
        if "vaelan" not in asked and knows_vaelan(player):
            opts.append("Ask about Emperor Vaelan")
        if "vaethar" not in asked and knows_godshards(player):
            opts.append("Ask about Vaethar and the Godshards")
        if "betrayal" not in asked and knows_name_partial(player) and len(asked) >= 2:
            opts.append("Ask if she knows the betrayer's name")
        if "dravennis" not in asked and knows_dravennis(player):
            opts.append("Ask about Dravennis")
        opts.append("Leave")

        if len(opts) == 1:
            wrap("She watches you. 'You don't yet know the right questions to ask me.'", Fore.WHITE); break

        ch = prompt(opts)

        if ch == "Ask about Eldros":
            asked.add("eldros")
            wrap("'Eldros was the first empire. Grand, genuinely grand. They built their roads "
                 "to last ten thousand years. Most did. They worshipped the Great Gods properly, "
                 "not ceremonially. Audience was granted. Prayers were answered. '", Fore.WHITE)
            wrap("'It was, for a time, as close to correct as this world has managed.'", Fore.WHITE)

        elif ch == "Ask what she is":
            asked.add("race")
            wrap("'Veythari.' Without apology. 'Near-mortal. We inhabit starlight. '", Fore.WHITE)
            wrap("'The Morvath inhabit darkness. We both formed from wells. "
                 "We are what was made when the world first took shape. Not gods. Not human.'", Fore.WHITE)
            wrap("She looks at her own hand. 'Most of us are gone now.'", Fore.WHITE)
            player.flags.add("met_sael")

        elif ch == "Ask about Thaun the Hollow":
            asked.add("thaun")
            wrap("'Thaun is the first Morvath — rose from the Void-well at the dawn of things. '", Fore.WHITE)
            wrap("'He is hollow because he carries the void inside him still. '", Fore.WHITE)
            wrap("'He is not kind. Not cruel. He simply is.'", Fore.WHITE)

        elif ch == "Ask about Arukiel":
            asked.add("arukiel")
            wrap("'My ancestor. She fell from the sky on the brightest day the world has seen — '", Fore.WHITE)
            wrap("'a choice, not a fall. She saw the world forming and decided to be part of it. '", Fore.WHITE)
            wrap("'Of the Falling Light is a title of honour. She was the first Veythari.'", Fore.WHITE)
            wrap("'She would be appalled at what this world has become.'", Fore.WHITE)

        elif ch == "Ask about the fall of the empire":
            asked.add("fall")
            wrap("'I was there. Not in the capital — no one outside survived the night. '", Fore.WHITE)
            wrap("'Three hundred miles away, and I felt the moment it happened. '", Fore.WHITE)
            wrap("'A sound that was not a sound. A light going out at the centre of everything. '", Fore.WHITE)
            wrap("'The Great Gods withdrew after that. Whatever was done broke something between "
                 "this world and them.'", Fore.WHITE)

        elif ch == "Ask about the wells":
            asked.add("wells")
            wrap("'Nine wells beneath the world. The Void-well is the one below us. '", Fore.WHITE)
            wrap("'I know hints of others — a Bloodwell, an Astral-well, a Hollow-well, a Dawnwell. '", Fore.WHITE)
            wrap("'From the Dawnwell came the first human — Auridan. '", Fore.WHITE)
            wrap("'From the Bloodwell came the first Orkyn — Mograx. Each well produced something. '", Fore.WHITE)
            wrap("'At the centre of all of them: something older than the wells themselves.'", Fore.WHITE)
            player.flags.add("sael_told_wells")

        elif ch == "Ask about the Great Gods":
            asked.add("gods")
            wrap("'Nine gods. Made by the first — Myrrakhel, the Deepest Pulse. '", Fore.WHITE)
            wrap("'The others she created are called the Thrys: Kindrael the Flame at Dawn, '", Fore.WHITE)
            wrap("'Loría the Verdant Bloom, Thalás She of the Endless Tides, '", Fore.WHITE)
            wrap("'Thar the Stonefather, Ishak the Storm-Forge, '", Fore.WHITE)
            wrap("'Ysena Weaver of Shadows — who was spouse to Atheron — '", Fore.WHITE)
            wrap("'Vastinö the Frost-Child, and Kelamaris the Breath of the Heights.' "
                 "She pauses. 'They granted audience to Eldros. They do not speak anymore.'", Fore.WHITE)
            wrap("'Myrrakhel has not spoken since the Night of Collapse. '", Fore.WHITE)
            wrap("'I do not know if Myrrakhel is still what Myrrakhel was.'", Fore.WHITE)
            player.flags.add("sael_myrrakhel")

        elif ch == "Ask about Emperor Vaelan":
            asked.add("vaelan")
            wrap("'Emperor Vaelan. The last. He held the Godshards — the fragments of Vaethar, "
                 "Atheron's chosen child, who gave their form willingly to empower the imperial line. '", Fore.WHITE)
            wrap("'Vaelan held the full set. That was close to a god's authority in mortal hands. '", Fore.WHITE)
            wrap("'He died on his throne. Stormed. Killed. '", Fore.WHITE)
            wrap("'I will not say by whom until you already know.'", Fore.WHITE)
            player.flags.add("sael_told_vaelan")

        elif ch == "Ask about Vaethar and the Godshards":
            asked.add("vaethar")
            wrap("'Vaethar was Atheron's chosen child — not born, but made, or chosen, or both. '", Fore.WHITE)
            wrap("'They gave up their physical form so that the power could be divided '", Fore.WHITE)
            wrap("'and passed through the imperial bloodline. The fragments are the Godshards. '", Fore.WHITE)
            wrap("'Each emperor received one on their coronation. The full set, together, '", Fore.WHITE)
            wrap("'constituted something close to Vaethar. '", Fore.WHITE)
            wrap("'Vaelan was the first and last to hold all of them simultaneously.'", Fore.WHITE)
            player.flags.add("sael_vaethar")

        elif ch == "Ask if she knows the betrayer's name":
            asked.add("betrayal")
            wrap("Her silver eyes fix on you. Very still.", Fore.WHITE); print()
            wrap("'A priest. A high keeper of the old rites. Granted access to the Great Gods. '", Fore.WHITE)
            wrap("'He went in as a man.'", Fore.WHITE); print()
            if any(f in player.flags for f in ("found_blank_book","spoke_maelvyr_shrine",
                                               "inscription_variation","found_vault_door")):
                wrap("'You already know something. Then you know the word — DEMONGOD.' "
                     "She says it flatly. 'His name was removed from all records by unanimous decree. '", Fore.WHITE)
                wrap("'The witnesses wrote it once, because something must hold it. '", Fore.WHITE)
                wrap("'His name was Maelvyr. Do not write it down.'", Fore.MAGENTA + Style.BRIGHT)
                player.flags.add("sael_spoke_maelvyr")
            else:
                wrap("'I will not say it yet. You are not ready for what it costs to carry it. '", Fore.WHITE)
                wrap("'Find the name yourself. It is here somewhere.'", Fore.WHITE)

        elif ch == "Ask about Dravennis":
            asked.add("dravennis")
            wrap("She is still for a moment. 'Dravennis.' The name seems to cost her something. '", Fore.WHITE)
            wrap("'He who drinks the blood of magi. He operates far from these ruins — '", Fore.WHITE)
            wrap("'but if you have found anything about what happened at Eldros, '", Fore.WHITE)
            wrap("'you may have already guessed what Dravennis is. Or was.'", Fore.WHITE)
            if "sael_spoke_maelvyr" in player.flags:
                wrap("'The name Maelvyr. The man who became a Demongod. '", Fore.MAGENTA + Style.BRIGHT)
                wrap("'And Dravennis — who drinks the blood of those who work magik. '", Fore.MAGENTA + Style.BRIGHT)
                wrap("'I leave you to draw that line yourself.'", Fore.MAGENTA + Style.BRIGHT)
                player.flags.add("sael_dravennis_connection")
            else:
                wrap("'But you do not yet have what you need to understand the full answer.'", Fore.WHITE)

        elif ch == "Leave":
            print(c("  'Be careful,' she says. 'Of the deep.'", Fore.WHITE)); break

        room["_sael_asked"] = asked

    if (len(asked) >= 3 and not player.has_item("Starlight Shard")
            and "gave_shard" not in player.flags):
        player.flags.add("gave_shard")
        wrap("As you reach the door, she holds something out — a small glowing fragment. "
             "'It will open a door you may find. A gift for listening.'", Fore.WHITE)
        try_give_unique(player, "Starlight Shard")


# ─── ORRATH ───────────────────────────────────────────────────────────────────
def event_orrath_chamber(player, room):
    wrap("The figure in the corner turns. Its eyes are fully black — like the inside of "
         "something that does not reflect light.", Fore.LIGHTBLUE_EX + Style.BRIGHT)
    print(); print(c("  'You found this room,' it says. Low and even. 'Sit down.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)); print()
    asked = room.get("_orrath_asked", set())

    while True:
        opts = []
        if "morvath" not in asked:
            opts.append("Ask what it is")
        if "void" not in asked and knows_wells(player):
            opts.append("Ask about the Void-well")
        if "unmade" not in asked and any(f in player.flags for f in (
                "found_vault_door","inscription_unmade","found_blank_book","spoke_maelvyr_shrine")):
            opts.append("Ask about the Unmade")
        if "thaun" not in asked and knows_thaun(player):
            opts.append("Ask about Thaun")
        if "maelvyr" not in asked and knows_name_partial(player):
            opts.append("Ask about Maelvyr")
        if "vaelan" not in asked and knows_vaelan(player):
            opts.append("Ask about Emperor Vaelan")
        if "vaethar" not in asked and knows_godshards(player):
            opts.append("Ask about Vaethar")
        if "gods" not in asked and knows_gods(player):
            opts.append("Ask about Myrrakhel")
        if "dravennis" not in asked and knows_dravennis(player):
            opts.append("Ask about Dravennis")
        opts.append("Leave")

        if len(opts) == 1:
            wrap("'You don't know what to ask yet. Come back when you do.'", Fore.LIGHTBLUE_EX + Style.BRIGHT); break

        ch = prompt(opts)

        if ch == "Ask what it is":
            asked.add("morvath")
            wrap("'Morvath.' As though that explains everything. "
                 "'Near-mortal. Darkness. I inhabit what the Veythari cannot.' "
                 "A pause. 'We share a cause. Different faces.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            player.flags.add("met_orrath")

        elif ch == "Ask about the Void-well":
            asked.add("void")
            wrap("'The Void-well is below us.' Not looking at the floor — looking at you. "
                 "'Thaun came from it. I did not — I came from the Hollow-well, which is different.' "
                 "'What the Void-well holds at its bottom is older still.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)

        elif ch == "Ask about the Unmade":
            asked.add("unmade")
            wrap("'The Unmade existed before the wells.' "
                 "Said without inflection. 'Before Thaun. Before Arukiel. Before the dragon. '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'It was here when there was nothing, and when there was nothing it was already old.' "
                 "A long silence. 'At Eldros it found a door. A willing door.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)

        elif ch == "Ask about Thaun":
            asked.add("thaun")
            wrap("'He is my ancestor. The first Morvath.' Something shifts in the black eyes. "
                 "'He is not kind. Not cruel. Those distinctions require caring about the difference. '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'He does not.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)

        elif ch == "Ask about Maelvyr":
            asked.add("maelvyr")
            wrap("'A man who made an agreement he either didn't understand, or understood completely.' "
                 "'He became what the word Demongod was invented for. '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'He is not here. He has not been here since the night the empire fell.' "
                 "Its black eyes do not blink. 'He is elsewhere. Active.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            player.flags.add("orrath_maelvyr")

        elif ch == "Ask about Emperor Vaelan":
            asked.add("vaelan")
            wrap("'The emperor who held the Godshards.' A pause. 'Killed on his throne.' "
                 "Another pause. 'The one who killed him had already agreed to become something else. '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'The Godshards were there. What happened to them in that moment — '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'I don't know. I was not there. But I was nearby.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            player.flags.add("orrath_told_vaelan")

        elif ch == "Ask about Vaethar":
            asked.add("vaethar")
            wrap("'Atheron's chosen child. Gave their form so the power could be distributed. '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'The Godshards are what remains of Vaethar.' "
                 "It is still for a moment. 'I met Vaethar once. Before the fragmentation. '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'What they chose to do was not a sacrifice. It was a decision. There is a difference.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            player.flags.add("orrath_vaethar")

        elif ch == "Ask about Myrrakhel":
            asked.add("gods")
            wrap("'The Deepest Pulse. First god. Made the others.' "
                 "Said with something like respect. 'Myrrakhel has not spoken since the Night of Collapse.' "
                 "'I don't know if that is because Myrrakhel cannot. Or will not. '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'Or is no longer what Myrrakhel was.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            player.flags.add("orrath_myrrakhel")

        elif ch == "Ask about Dravennis":
            asked.add("dravennis")
            wrap("'Dravennis.' A very long pause. 'He who drinks the blood of magi. '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'I will not draw the line between him and what happened here. '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'But I will tell you: the man who was made into a Demongod at Eldros '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'did not stay in Eldros. He left. He has been building something, elsewhere, '", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            wrap("'for a very long time. And he is very hungry.'", Fore.LIGHTBLUE_EX + Style.BRIGHT)
            player.flags.add("orrath_dravennis")

        elif ch == "Leave":
            print(c("  It watches you go. It says nothing.", Fore.LIGHTBLUE_EX + Style.BRIGHT)); break

        room["_orrath_asked"] = asked

    if len(asked) >= 3 and "gave_orrath_gift" not in player.flags:
        player.flags.add("gave_orrath_gift")
        wrap("As you reach the door, something on the floor you didn't see before: "
             "a coin of dark red metal.", Fore.LIGHTBLUE_EX + Style.BRIGHT)
        player.gold += 15; print(c("  +15 gold.", Fore.YELLOW))

# ─── ECHO OF SERETHAN ─────────────────────────────────────────────────────────
def event_serethan_echo(player, room):
    """
    Serethan's Echo — a strong psychic impression near the bell or archive.
    Not a ghost. More like a standing memory.
    """
    hr("═", colour=Fore.YELLOW)
    print(c("  THE WARDEN'S ECHO", Fore.YELLOW + Style.BRIGHT))
    hr("═", colour=Fore.YELLOW)
    print()
    wrap(
        "The room is not empty. "
        "But the presence in it is not a person — "
        "it is the space a person occupied so completely "
        "that the stones remember them. "
        "A shape. Armoured. Standing at a window that no longer exists.",
        Fore.YELLOW)
    print()

    if "met_serethan" not in player.flags:
        player.flags.add("met_serethan")
        wrap(
            "The shape speaks. Not a voice — a resonance in the stone, "
            "as though the walls are remembering a voice.",
            Fore.YELLOW)
        print()

    # What the echo says depends on what the player knows
    done = room.get("_serethan_done", set())

    while True:
        opts = []
        if "bell" not in done:
            opts.append("Ask about the bell")
        if "collapse" not in done and "read_ashen_tablet" in player.flags:
            opts.append("Ask about the Night of Collapse")
        if "vaelan" not in done and "found_throne_room" in player.flags:
            opts.append("Ask about Emperor Vaelan")
        if "choice" not in done:
            opts.append("Ask why he did not ring the bell")
        if "maelvyr" not in done and "full_truth_known" in player.flags:
            opts.append("Tell him what happened — the full truth")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave":
            wrap(
                "The shape remains at the window. "
                "It always will. The stones will remember him for a very long time.",
                Fore.YELLOW)
            break

        elif ch == "Ask about the bell":
            done.add("bell")
            wrap(
                "The resonance deepens. "
                "'The bell signals lockdown. Every patrol activates. "
                "Every gate seals. Every creature in the ruins responds to standing orders "
                "that date from the founding of the city. '",
                Fore.YELLOW)
            wrap(
                "'I chose not to ring it. '",
                Fore.YELLOW)
            wrap(
                "'The ruins were already falling. Ringing the bell would have woken "
                "everything we had caged. The cost of the lockdown would have been "
                "the lives of everyone still alive to be saved. '",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("serethan_bell")

        elif ch == "Ask about the Night of Collapse":
            done.add("collapse")
            wrap(
                "'I was on the wall when it started. I felt the moment — '",
                Fore.YELLOW)
            wrap(
                "'Something opened. Not physically. Something in the nature of the city "
                "opened, and then closed again, and the closing was wrong. "
                "Like a door that has been jammed. '",
                Fore.YELLOW)
            wrap(
                "'We had eleven minutes before the first wave reached the outer districts. "
                "I know because I was counting.'",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("serethan_collapse")

        elif ch == "Ask about Emperor Vaelan":
            done.add("vaelan")
            wrap(
                "'Vaelan was not a great emperor. He was a competent one. "
                "The difference matters. '",
                Fore.YELLOW)
            wrap(
                "'He approved the High Keeper's final audience request against my advice. "
                "My objection is on record. I was overruled. '",
                Fore.YELLOW)
            wrap(
                "'He died fighting. That is more than most. '",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("serethan_vaelan")

        elif ch == "Ask why he did not ring the bell":
            done.add("choice")
            wrap(
                "A long silence in the stones.",
                Fore.YELLOW)
            wrap(
                "'Because I did not know what would happen if I did. '",
                Fore.YELLOW)
            wrap(
                "'I knew exactly what would happen if I did not. '",
                Fore.YELLOW)
            wrap(
                "'A Warden's first obligation is to his people. "
                "The bell serves the city. The city was gone. '",
                Fore.YELLOW + Style.BRIGHT)
            wrap(
                "'I left the decision to whoever came after.'",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("serethan_choice")
            if "warden_bell_rung" in player.flags:
                print()
                wrap(
                    "The resonance changes — briefly, something in it that might be relief. "
                    "'You rang it.' Not a question.",
                    Fore.YELLOW)
                wrap(
                    "'I hope it was the right time.' "
                    "The stone is warm under your hand.",
                    Fore.YELLOW)
                player.max_hp += 5
                print(c("  Max HP +5. The echo is grateful.", Fore.GREEN))

        elif ch == "Tell him what happened — the full truth":
            done.add("maelvyr")
            wrap(
                "You tell him. All of it. Maelvyr. The Agreement. The Unmade. "
                "The Godshards. What you found in the sanctum.",
                Fore.YELLOW)
            pause()
            wrap(
                "The stone is silent for a long time.",
                Fore.YELLOW)
            wrap(
                "'Maelvyr.' The resonance carries weight in that name. "
                "'I investigated him. I told the emperors. "
                "They told me I was seeing threats that weren't there. '",
                Fore.YELLOW)
            wrap(
                "'I was right. It did not help. '",
                Fore.YELLOW + Style.BRIGHT)
            wrap(
                "'Thank you for telling me. It is important to know. "
                "Even here. Even now.'",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("serethan_truth_told")
            player.max_hp += 8; player.attack += 1
            print(c("  Max HP +8, ATK +1. The truth has weight, and so does giving it.",
                    Fore.GREEN))

        room["_serethan_done"] = done

# ─── RANDOM CAPTAIN ───────────────────────────────────────────────────────────
def event_seeker_captain(player, room):
    """
    The Shard-Seeker Captain — has been here longer than the others,
    has lost crew, is considering leaving.
    """
    hr("═", colour=Fore.YELLOW)
    print(c("  THE SHARD-SEEKER CAPTAIN", Fore.YELLOW + Style.BRIGHT))
    hr("═", colour=Fore.YELLOW)
    print()

    if is_hostile(player, "seekers"):
        wrap(
            "They stand up. Hand on the weapon. "
            "'You've made enough trouble. We're done talking.'",
            Fore.RED)
        seeker = next((e for e in ENEMY_POOL if e["name"] == "Shard-Seeker"), None)
        if seeker:
            combat(player, spawn_enemy(seeker))
        return

    if "met_seeker_captain" not in player.flags:
        player.flags.add("met_seeker_captain")
        wrap(
            "A mercenary, but different from the others — "
            "better equipped, sitting rather than moving, "
            "reading from a small notebook. "
            "They look up without reaching for a weapon.",
            Fore.YELLOW)
        print()
        wrap(
            "  'You're not one of ours. You're not a Scholar. "
            "You're not — ' They look at you more carefully. "
            "'You've been deeper than us. I can tell. "
            "Sit down. I have questions.'",
            Fore.YELLOW + Style.BRIGHT)
    else:
        wrap(
            "The Captain is still here. Still reading. "
            "Still not leaving.",
            Fore.YELLOW)

    print()
    asked = room.get("_captain_asked", set())

    while True:
        opts = []
        if "employer" not in asked:
            opts.append("Ask who sent them")
        if "status" not in asked:
            opts.append("Ask why they are still here")
        if "trade" not in asked:
            opts.append("Trade information")
        if "ally" not in asked and is_allied(player, "seekers"):
            opts.append("Suggest they join you temporarily")
        if "godshards" not in asked and godshard_count(player) > 0:
            opts.append("Show them the Godshards")
        if "betray" not in asked and is_allied(player, "scholars"):
            opts.append("Tell the Scholars about their camp location")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave":
            wrap("  'Come back if you find anything worth trading.'", Fore.YELLOW)
            break

        elif ch == "Ask who sent them":
            asked.add("employer")
            wrap(
                "'Merchant house in the east. I don't give names — '",
                Fore.YELLOW)
            wrap(
                "'They want the Godshards. Not all three — they specified one. "
                "The one in Vaelan's throne room. They knew exactly where it was. '",
                Fore.YELLOW)
            wrap(
                "'That bothers me. People who know exactly where things are in a ruin "
                "they claim to have never visited — '",
                Fore.YELLOW + Style.BRIGHT)
            wrap(
                "'I've been doing this work for twenty years. "
                "That's not archaeology. That's retrieval.'",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("captain_employer")

        elif ch == "Ask why they are still here":
            asked.add("status")
            wrap(
                "'Lost six people to the cultists. "
                "The contract says retrieval, not survival. "
                "I have three crew left. '",
                Fore.YELLOW)
            wrap(
                "'I am — reconsidering. The money was good. "
                "The money was very good. '",
                Fore.YELLOW)
            wrap(
                "'But whoever is paying us knew what was down here. "
                "They knew about the Void-Touched. "
                "They sent us anyway. '",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("captain_status")

        elif ch == "Trade information":
            asked.add("trade")
            if "found_throne_room" in player.flags:
                wrap(
                    "You confirm the throne room location. "
                    "Their expression does not change, but they write something down.",
                    Fore.YELLOW)
                player.gold += 25
                player.pick_up({
                    "name": "Captain's Supply Cache Key",
                    "type": "key", "value": 0,
                    "description": "A small key stamped with the Shard-Seekers' mark. "
                                   "Opens a cache they've stashed somewhere in the upper ruins."
                })
                print(c("  +25 gold, Captain's Supply Cache Key.", Fore.YELLOW))
                adjust_reputation(player, "seekers", 1)
            else:
                wrap(
                    "'You haven't found it yet. Come back when you have.'",
                    Fore.YELLOW)

        elif ch == "Suggest they join you temporarily":
            asked.add("ally")
            wrap(
                "They consider this for a while.",
                Fore.YELLOW)
            wrap(
                "'Temporarily. For the next three rooms. "
                "I want to see what you are walking into.'",
                Fore.YELLOW + Style.BRIGHT)
            player.flags.add("captain_allied")
            adjust_reputation(player, "seekers", 1)
            wrap(
                "The Captain follows. In combat while this flag is set, "
                "they strike for 6 damage at the end of each round (free attack).",
                Fore.GREEN)
            # The flag is checked in combat — see captain_allied logic note

        elif ch == "Show them the Godshards":
            asked.add("godshards")
            count = godshard_count(player)
            wrap(
                f"You show them. They lean forward. "
                f"'{count} of them. You actually found them.' "
                "A very long pause.",
                Fore.YELLOW)
            wrap(
                "'My employer wants one. "
                "You have — depending on your plans — more than you need. '",
                Fore.YELLOW)
            wrap(
                "'I'll offer you sixty gold for one. "
                "No violence. No tricks. "
                "You can say no.'",
                Fore.YELLOW + Style.BRIGHT)
            ch2 = prompt(["Accept (60 gold, give one Godshard)", "Decline"])
            if "Accept" in ch2:
                # Which shard?
                shards_held = [it for it in player.inventory
                               if it["name"] in ("Godshard Fragment","Second Godshard","Third Godshard")]
                if shards_held:
                    sold = shards_held[-1]  # give the most recently acquired
                    player.inventory.remove(sold)
                    player.gold += 60
                    print(c(f"  Sold {sold['name']} for 60 gold.", Fore.YELLOW))
                    adjust_reputation(player, "seekers", 1)
                    player.flags.add("sold_godshard_captain")
            else:
                wrap("  'Fair enough.' They sit back down.", Fore.YELLOW)

        elif ch == "Tell the Scholars about their camp location":
            asked.add("betray")
            wrap(
                "You give the Archivist's faction the Captain's camp location. "
                "It is not a pleasant thing to do. It is effective.",
                Fore.CYAN)
            adjust_reputation(player, "scholars", 1)
            adjust_reputation(player, "seekers", -2)
            player.flags.add("betrayed_seekers")
            wrap(
                "The Captain looks up. They know immediately. "
                "'I see.' They stand. 'I would have expected that from someone else.'",
                Fore.RED)
            break

        room["_captain_asked"] = asked

# ─── DEEP SLEEPER ─────────────────────────────────────────────────────────────
def event_deep_sleeper(player, room):
    """
    The Deep Sleeper — something very old found at z=4.
    Not related to Atheron or the Architect.
    One question, one answer, then it sleeps.
    """
    hr("═", colour=Fore.WHITE)
    print(c("  THE DEEP SLEEPER", Fore.WHITE + Style.BRIGHT))
    hr("═", colour=Fore.WHITE)
    print()
    wrap(
        "In the deepest room, where the stone is a different colour "
        "from everything above it — older, perhaps, or simply more present — "
        "something is coiled around itself. "
        "Not a dragon. Not an animal. Something that existed before "
        "the categories had been invented.",
        Fore.WHITE)
    print()
    wrap(
        "It is vast. It is very still. "
        "The air in the room is the temperature of something that has been breathing "
        "very slowly for an extremely long time.",
        Fore.WHITE)
    print()
    player.flags.add("found_deep_sleeper")

    if "deep_sleeper_answered" in player.flags:
        wrap(
            "The Sleeper does not stir. "
            "It has answered one question. "
            "It will not answer another. "
            "It does not sleep more deeply than this — "
            "it simply does not respond to a second asking.",
            Fore.WHITE)
        return

    if "deep_sleeper_approached" not in player.flags:
        player.flags.add("deep_sleeper_approached")
        wrap(
            "Something shifts. Not a movement — an awareness. "
            "It knows you are here. It has been awake, in its way, "
            "since before you entered.",
            Fore.WHITE + Style.BRIGHT)
        print()
        wrap(
            "There is a quality to the air that is not a voice "
            "but functions like one. "
            "It is willing to hear one question.",
            Fore.WHITE)
        print()

    ch = prompt([
        "Ask about the Unmade / Atraxis",
        "Ask about the Void-well",
        "Ask about the Godshards",
        "Ask about Myrrakhel",
        "Ask about what it is",
        "Speak a question of your own",
        "Leave without asking",
    ])

    if ch == "Leave without asking":
        wrap(
            "The awareness does not pursue you. "
            "The air returns to ordinary.",
            Fore.WHITE)
        return

    player.flags.add("deep_sleeper_answered")
    print()
    hr(colour=Fore.WHITE)

    if ch == "Ask about the Unmade / Atraxis":
        wrap(
            "The answer is not in words. It is in an understanding that settles "
            "into the space behind your eyes, like something being placed carefully.",
            Fore.WHITE)
        wrap(
            "What you understand: "
            "the Unmade is not evil. It is not malevolent. "
            "It is the direction that everything that has no other direction "
            "falls toward. "
            "Its gathering of power is not conquest. "
            "It is the same force that makes water run downhill "
            "— applied to existence.",
            Fore.WHITE + Style.BRIGHT)
        wrap(
            "The understanding also contains: it can be redirected. "
            "Not stopped. Redirected.",
            Fore.WHITE + Style.BRIGHT)
        player.flags.add("sleeper_atraxis_answer")

    elif ch == "Ask about the Void-well":
        wrap(
            "A warmth passes through the room — brief, significant.",
            Fore.WHITE)
        wrap(
            "What you understand: "
            "the wells are not holes. They are points of origin. "
            "The Void-well is the first — older than the others — "
            "and what emerged from it carries the quality of origin. "
            "Thaun is not a creature of the dark. "
            "He is dark, the way a point of origin is its own thing.",
            Fore.WHITE + Style.BRIGHT)
        wrap(
            "The understanding also contains: "
            "the well does not need to be sealed. "
            "It needs to be witnessed correctly.",
            Fore.WHITE + Style.BRIGHT)
        player.flags.add("sleeper_well_answer")

    elif ch == "Ask about the Godshards":
        wrap(
            "The air becomes briefly very still.",
            Fore.WHITE)
        wrap(
            "What you understand: "
            "the Godshards do not merely hold power. "
            "They hold intention. "
            "Vaethar's intention at the moment of fragmentation "
            "is still in them — unchanged, intact, waiting. "
            "The ritual does not give you power. "
            "It gives you Vaethar's original intention.",
            Fore.WHITE + Style.BRIGHT)
        wrap(
            "You do not immediately understand what that means. "
            "You understand that it is significant.",
            Fore.WHITE)
        player.flags.add("sleeper_shards_answer")

    elif ch == "Ask about Myrrakhel":
        wrap(
            "A very long pause. The thing breathes once — slowly.",
            Fore.WHITE)
        wrap(
            "What you understand: "
            "Myrrakhel has not spoken since the Night of Collapse "
            "because Myrrakhel is listening. "
            "There is something Myrrakhel is waiting to hear. "
            "Not a name. Not a ritual. "
            "A quality of attention. "
            "Someone paying the right kind of attention to the right thing.",
            Fore.WHITE + Style.BRIGHT)
        wrap(
            "What the right thing is — "
            "the understanding does not include that.",
            Fore.WHITE)
        player.flags.add("sleeper_myrrakhel_answer")

    elif ch == "Ask about what it is":
        wrap(
            "The awareness that is not a voice becomes something closer "
            "to wry. Not quite amusement. The feeling of a long time "
            "and a question that has not been asked in a long time.",
            Fore.WHITE)
        wrap(
            "What you understand: "
            "it was here before the wells. "
            "It will be here after Atraxis is redirected. "
            "It has no investment in anything that happens above. "
            "It witnesses. "
            "That is all it has ever done.",
            Fore.WHITE + Style.BRIGHT)
        wrap(
            "What it is, in its own understanding: "
            "old enough to not be anything in particular anymore.",
            Fore.WHITE + Style.BRIGHT)
        player.flags.add("sleeper_self_answer")

    elif ch == "Speak a question of your own":
        wrap(
            "What is your question?",
            Fore.WHITE)
        spoken = secret_input(player)
        # Respond to key concepts
        if any(w in spoken for w in ("maelvyr", "demongod", "betrayer")):
            wrap(
                "What you understand: "
                "Maelvyr made the Agreement as a mortal making a mortal mistake. "
                "The Void did not trick him. "
                "He went to it with open eyes and chose. "
                "The choice was coherent. "
                "It was simply wrong.",
                Fore.WHITE + Style.BRIGHT)
        elif any(w in spoken for w in ("atheron", "dragon")):
            wrap(
                "What you understand: "
                "Atheron has been awake the entire time. "
                "The sleep is a choice. "
                "It is waiting for something specific.",
                Fore.WHITE + Style.BRIGHT)
            if "studied_atheron" in player.flags:
                wrap(
                    "The understanding also contains: "
                    "it is waiting for the Godshards to be reunited. "
                    "It has been waiting since Vaethar fragmented.",
                    Fore.YELLOW + Style.BRIGHT)
        elif any(w in spoken for w in ("me", "myself", "who am i", "vessel")):
            wrap(
                "What you understand: "
                "nothing about you specifically. "
                "You are a person who asked. "
                "That is, in the estimation of the Sleeper, "
                "neither small nor large. "
                "It is the correct thing to be.",
                Fore.WHITE + Style.BRIGHT)
        else:
            wrap(
                "The understanding does not come. "
                "Either the question has no answer the Sleeper carries, "
                "or the question was not one the Sleeper recognises.",
                Fore.WHITE)
        player.flags.add("sleeper_custom_answer")

    hr(colour=Fore.WHITE)
    print()
    wrap(
        "The awareness withdraws. The air returns to its slow temperature. "
        "The Sleeper has answered. It will not answer again.",
        Fore.WHITE)


def event_talarion_echo(player, room):
    """
    Called from event_crystal_mirror_room on second mirror use with right context.
    Talarion's echo — answers specific historical questions.
    """
    wrap(
        "In the Crystal Mirror: the room as it was. "
        "Talarion at the desk. He stands. "
        "He speaks. This time you can hear it — not through the air, "
        "through the glass.",
        Fore.CYAN + Style.BRIGHT)
    print()
    wrap(
        "  'You came back. Good. I don't have long in this form — "
        "stone remembers badly after a certain point. "
        "Ask what you need to ask.'",
        Fore.CYAN + Style.BRIGHT)
    print()
    player.flags.add("talarion_echo_active")

    asked = room.get("_echo_asked", set())
    for _ in range(3):  # three questions max
        opts = []
        if "maelvyr" not in asked:
            opts.append("Ask about Maelvyr")
        if "vaelan" not in asked:
            opts.append("Ask about Vaelan's final hours")
        if "tolos" not in asked:
            opts.append("Ask about Tolos")
        if "night" not in asked:
            opts.append("Ask what he saw on the Night of Collapse")
        if "shards" not in asked and "found_shattered_crown_hall" in player.flags:
            opts.append("Ask about the Wars of the Shattered Crown")
        opts.append("Ask nothing more")
        ch = prompt(opts)
        if ch == "Ask nothing more":
            break

        if ch == "Ask about Maelvyr":
            asked.add("maelvyr")
            wrap(
                "'Maelvyr was brilliant. I want to be clear about that. '",
                Fore.CYAN)
            wrap(
                "'He was the most brilliant person I had met up to that point. "
                "He was furious in a way that brilliant people sometimes are — "
                "furious that the world was not as it should be. '",
                Fore.CYAN)
            wrap(
                "'He was wrong about the method. "
                "He was not wrong about the problem. "
                "The gods were silent. That was real. '",
                Fore.CYAN + Style.BRIGHT)
            wrap(
                "'What I saw in the throne room: "
                "he wept over Tolos. Then he left. "
                "Injured — his chest — but he walked. '",
                Fore.CYAN + Style.BRIGHT)

        elif ch == "Ask about Vaelan's final hours":
            asked.add("vaelan")
            wrap(
                "'He knew. He had known for some time. '",
                Fore.CYAN)
            wrap(
                "'Not exactly — he did not know it was Maelvyr. "
                "He knew something was coming. "
                "He stayed on the throne because he was the emperor "
                "and emperors do not run. '",
                Fore.CYAN)
            wrap(
                "'He was holding the Godshards when it happened. "
                "He was trying to use them. They did not respond in time.'",
                Fore.CYAN + Style.BRIGHT)

        elif ch == "Ask about Tolos":
            asked.add("tolos")
            wrap(
                "'Tolos Merinain was Maelvyr's oldest friend. '",
                Fore.CYAN)
            wrap(
                "'He tried to stop him. He failed. "
                "He was — stripped of his titles, sent away. "
                "He came back anyway. '",
                Fore.CYAN)
            wrap(
                "'The leap he attempted — to reach Maelvyr "
                "before the killing blow — was not a soldier's move. "
                "It was a friend's move. '",
                Fore.CYAN + Style.BRIGHT)
            wrap(
                "'I put his name on the plinth. "
                "He tried. That is what the record should say.'",
                Fore.CYAN + Style.BRIGHT)

        elif ch == "Ask what he saw on the Night of Collapse":
            asked.add("night")
            wrap(
                "'I saw everything. That is my burden and my purpose. '",
                Fore.CYAN)
            wrap(
                "'The moment the Agreement was activated — "
                "I felt it in the stone. The whole city did, I think. '",
                Fore.CYAN)
            wrap(
                "'The Void came through. Not fully. "
                "Enough. Maelvyr became something else. "
                "The city did not survive the becoming.'",
                Fore.CYAN + Style.BRIGHT)
            wrap(
                "'I wrote it down. I built the Hall of the Shattered Crown "
                "to hold the shards when the wars ended. "
                "I placed Tolos's name on the plinth. '",
                Fore.CYAN + Style.BRIGHT)
            wrap(
                "'And then I stayed to make sure someone read it.'",
                Fore.CYAN + Style.BRIGHT)
            player.flags.add("talarion_full_account")

        elif ch == "Ask about the Wars of the Shattered Crown":
            asked.add("shards")
            wrap(
                "'Three generations. '",
                Fore.CYAN)
            wrap(
                "'I watched all of them. The echoes of a name — "
                "children fighting over what their parent held, "
                "not understanding what it was. '",
                Fore.CYAN)
            wrap(
                "'In the end they were tired. "
                "I told them to give the shards back. "
                "They listened. That was something.'",
                Fore.CYAN + Style.BRIGHT)

        room["_echo_asked"] = asked

    wrap(
        "The mirror fogs. The room in it dims. "
        "In the last moment before it goes ordinary: "
        "Talarion raises a hand. Not waving. "
        "The gesture of someone finishing a sentence.",
        Fore.CYAN)
    player.flags.add("talarion_echo_spoken")


# ─── TRAP VAULT ───────────────────────────────────────────────────────────────
def event_trap_vault(player, room):
    wrap("Gold, gems, an item on a shelf. Seven pressure plates between you and it.")
    ch = prompt(["Step carefully across","Grab quickly and run","Back away"])
    if ch == "Step carefully across":
        if random.random() < 0.60:
            loot = random_item(); gold = random.randint(10,22)
            player.gold += gold; player.pick_up(loot)
            print(c(f"  You make it. {loot['name']} and {gold} gold.", Fore.GREEN))
            if random.random() < 0.3: try_give_unique(player, "Iron Key")
        else:
            dmg = random.randint(8,16); player.hp -= dmg
            print(c(f"  A blade from the wall. -{dmg} HP. ({player.hp}/{player.max_hp})", Fore.RED))
    elif ch == "Grab quickly and run":
        loot = random_item(); player.pick_up(loot)
        if random.random() < 0.80:
            dmg = random.randint(12,20); player.hp -= dmg
            print(c(f"  The room erupts. -{dmg} HP. ({player.hp}/{player.max_hp})", Fore.RED))
        else:
            print(c("  Somehow nothing triggers.", Fore.GREEN))
    else:
        print("  Wisdom over greed.")

# ─── LIBRARY ──────────────────────────────────────────────────────────────────
LIBRARY_BOOKS = [
    # (title, condition_fn, text, flag)
    ("Consolidated Histories of Eldros, Vol. IV",
     lambda p: True,
     "'...the Consolidation period marked the first unified census of the empire. "
     "At its height, Eldros-Verath housed two hundred thousand souls and the outer provinces "
     "a further eight hundred thousand. The emperor's authority extended to the coast in all "
     "directions. The final entry in this volume is dated three years before the Night of Collapse. "
     "The author notes that the High Keeper's office has been sealed by imperial edict.'",
     "found_histories"),

    ("On the Nature of the Nine Wells (cover only)",
     lambda p: True,
     "The book is destroyed beyond the cover. The cover reads: "
     "'Being an Account of the Wells Beneath the World, Their Origins, Their Products, "
     "and the Things That Emerged From Them Before the Age of Records.' "
     "The author is listed as: 'A Veythari, name withheld.' The date given is older than the empire.",
     "found_wells_book"),

    ("The Thrys: A Theological Survey",
     lambda p: knows_gods(p),
     "'The nine gods of Eldros, collectively called the Thrys by the people, "
     "were understood as distinct in purpose but unified in origin. '  "
     "'Myrrakhel, the Deepest Pulse, was acknowledged as the first and as the source of the others. '  "
     "'The eight that Myrrakhel created — Kindrael, Loría, Thalás, Thar, Ishak, Ysena, Vastinö, "
     "and Kelamaris — each took a domain and maintained it. '  "
     "'The relationship between the Gods and the empire was one of mutual acknowledgement. '  "
     "'This relationship ended with the Night of Collapse. No theological explanation has been satisfactory.'",
     "found_thrys_survey"),

    ("Accounts of the Near-Mortal Races",
     lambda p: any(f in p.flags for f in ("met_sael","met_orrath","prisoner_told_well")),
     "'The Morvath and the Veythari are distinct races with common function. '  "
     "'Both are what scholarship has termed near-mortal: neither fully divine nor fully mortal. '  "
     "'They formed from the wells at the beginning of things. '  "
     "'The Morvath inhabit and draw strength from darkness; the Veythari from starlight. '  "
     "'Their numbers were never great. Their involvement in the affairs of Eldros was advisory. '  "
     "'After the Night of Collapse, sightings became rare, then ceased.'",
     "found_near_mortal_book"),

    ("Vaethar and the Dragon-line",
     lambda p: knows_godshards(p),
     "'Vaethar, the Chosen Child of Atheron the King of Dragons, chose to fragment their physical '  "
     "'form into the pieces now known as the Godshards, that the power might serve the imperial line '  "
     "'across generations. Each emperor received one shard on coronation. '  "
     "'Emperor Vaelan was the first emperor to inherit all remaining shards simultaneously, '  "
     "'as the bloodline had narrowed over generations to a single heir. '  "
     "'The theological implications of a mortal holding the full form of Vaethar's power '  "
     "'were being debated when the Night of Collapse rendered the debate moot.'",
     "found_vaethar_book"),

    ("The Audience Protocols",
     lambda p: knows_fall(p),
     "'The granting of formal audience with the Great Gods was a closely regulated affair. '  "
     "'The High Keeper's office maintained the protocols. Access was restricted. '  "
     "'The final audience, in the last year of the Consolidated Age, was unusual in that it was '  "
     "'requested by the High Keeper himself rather than arranged by the throne. '  "
     "'Emperor Vaelan is recorded as having approved the request with noted reluctance. '  "
     "'The High Keeper's name does not appear in this record. The space is blank.'",
     "found_audience_protocols"),

    ("A Brief Etymological Study of the Word DEMONGOD",
     lambda p: any(f in p.flags for f in ("spoke_maelvyr_shrine","found_blank_book","found_sealed_sanctum")),
     "'The compound term appears in no text preceding the Night of Collapse. '  "
     "'It was coined in the immediate aftermath by survivors of the outer provinces '  "
     "'attempting to describe something for which no existing vocabulary was adequate. '  "
     "'The two components — Demon, meaning a being that has crossed from one nature into another '  "
     "'by choice or corruption, and God, meaning a being of power beyond mortality — '  "
     "'were combined because neither alone was sufficient. '  "
     "'The scholars who coined it noted in their margin: this word is still not enough.'",
     "found_demongod_etymology"),

    ("A Sealed Book (no title)",
     lambda p: True,
     None,  # special — triggers blank book event
     "_blank_book"),

    ("The Codex of the First Age",
     lambda p: any(f in p.flags for f in ("found_vaethar_book","sael_vaethar","orrath_vaethar")),
     None,   # special — handled separately
     "_codex"),
]

def event_library(player, room):
    wrap("The open book on the lectern contains a single legible page. You read it aloud before you decide to.")
    if not player.has_item("Codex of the First Age") and "codex_placed" not in room:
        room["codex_placed"] = True
        room["items"] = room.get("items", []) + [get_item("Codex of the First Age")]
        wrap("On the lectern beside the open book: a heavy volume you haven\\'t seen before.",
             Fore.YELLOW)
    outcome = random.choice(["buff_attack","buff_defence","buff_hp","curse","curse_hp","lore_entry"])
    if outcome == "buff_attack":
        player.attack += 2; wrap("Battle-rites. ATK +2.", Fore.GREEN)
    elif outcome == "buff_defence":
        player.defence += 2; wrap("Warding glyphs. DEF +2.", Fore.GREEN)
    elif outcome == "buff_hp":
        player.max_hp += 8; player.hp = min(player.hp+8, player.max_hp)
        wrap("Vitality runes. Max HP +8.", Fore.GREEN)
    elif outcome == "curse":
        player.cursed = True; wrap("A weakening hex. [CURSED]", Fore.RED)
    elif outcome == "curse_hp":
        player.max_hp = max(10, player.max_hp-6); player.hp = min(player.hp, player.max_hp)
        wrap("A draining curse. Max HP -6.", Fore.RED)
    elif outcome == "lore_entry":
        wrap("The page describes the Night of Collapse in careful prose: "
             "'One person. The records are very careful not to say by whom.'", Fore.CYAN)
        player.flags.add("found_library_collapse")

    print()
    # Now let player browse other books (can do multiple)
    browsed = room.get("_books_opened", set())
    while True:
        ch = prompt(["Browse the other shelves", "Leave the library"])
        if ch == "Leave the library": break

        available = [(title, cond, text, flag) for title, cond, text, flag in LIBRARY_BOOKS
                     if flag not in browsed]
        if not available:
            wrap("You have opened everything readable on these shelves."); break

        # Show accessible titles (even locked ones shown, just greyed out)
        def book_label(t, cond, fl):
            if cond(player): return t
            return t + c(" (you lack the context to understand this yet)", Fore.LIGHTBLUE_EX + Style.BRIGHT)

        book_opts = [book_label(t,c2,fl) for t,c2,tx,fl in available] + ["Stop browsing"]
        bch = prompt(book_opts)
        if bch == "Stop browsing": break

        # Find which book was chosen
        chosen = None
        for entry in available:
            t, cond, text, flag = entry
            if t in bch or (t + c(" (you lack", Fore.LIGHTBLUE_EX+Style.BRIGHT)) in bch:
                chosen = entry; break
        if not chosen:
            chosen = available[0]  # fallback
        t, cond, text, flag = chosen
        browsed.add(flag)

        if not cond(player):
            wrap("You open it. You can read the words, but without the right context "
                 "they do not connect to anything. You close it.", Fore.LIGHTBLUE_EX+Style.BRIGHT)
        elif flag == "_blank_book":
            # Special blank book
            wrap("The thread snaps. One page: "
                 "'He came to us as a priest. We granted him audience with the Gods. "
                 "He did not return a man. What he returned as, we have no word for.' "
                 "The word DEMONGOD is added later, in the margin. "
                 "Beneath it: a name, scratched through many times. M___VYR.", Fore.MAGENTA)
            player.flags.add("found_blank_book")
            if "spoke_maelvyr_shrine" in player.flags:
                print(c("  The name fits the gap you already carry.", Fore.MAGENTA + Style.BRIGHT))
        elif flag == "_codex":
            if not player.has_item("Crystal Mirror"):
                wrap("You open the Codex of the First Age. The text is scrambled — letters "
                     "in the right script but in the wrong order. You cannot read it. "
                     "Something about it resists direct reading.", Fore.LIGHTBLUE_EX + Style.BRIGHT)
                wrap("You feel that viewing it differently might help.", Fore.LIGHTBLUE_EX + Style.BRIGHT)
                try_give_unique(player, "Codex of the First Age")
            else:
                wrap("You open the Codex. You cannot read it directly. "
                     "On instinct, you hold up the Crystal Mirror.", Fore.CYAN)
                wrap("In the mirror's reflection, the scrambled text resolves. "
                     "You read it in the glass — backwards, correct:", Fore.CYAN + Style.BRIGHT)
                print()
                hr(colour=Fore.YELLOW)
                wrap("'The vessel is not made. The vessel chooses. "
                     "The shards remember what they were — call them home by name. '",
                     Fore.YELLOW + Style.BRIGHT)
                wrap("'Speak the name of the child. Speak the name of the father who witnessed. '",
                     Fore.YELLOW + Style.BRIGHT)
                wrap("'Say: I am the vessel. The shards will hear it.'",
                     Fore.YELLOW + Style.BRIGHT)
                hr(colour=Fore.YELLOW)
                print()
                wrap("The mirror fogs. The text in the book is scrambled again. "
                     "But you have read it.", Fore.CYAN)
                player.flags.add("decoded_codex")
                player.flags.add("knows_ritual_phrase")
        else:
            hr(colour=Fore.CYAN)
            wrap(text, Fore.CYAN)
            hr(colour=Fore.CYAN)
            player.flags.add(flag)

        room["_books_opened"] = browsed


# ─── MURAL HALL ───────────────────────────────────────────────────────────────
def event_mural_hall(player, room):
    hr(colour=Fore.CYAN)
    wrap("You move along the mural slowly. It tells a story.", Fore.CYAN); print()

    sections_seen = room.get("_mural_sections", set())
    while True:
        opts = []
        if "left" not in sections_seen:  opts.append("Examine the left panel")
        if "right" not in sections_seen: opts.append("Examine the right panel")
        if "centre" not in sections_seen:opts.append("Examine the central panel")
        if "fourth" not in sections_seen:opts.append("Examine the far edge")
        if "crack" not in sections_seen: opts.append("Examine the crack in the wall")
        if (player.has_item("Candle") and "fourth" in sections_seen
                and "candle_used" not in sections_seen):
            opts.append("Hold the Candle to the chiselled section")
        if (player.has_item("Crystal Mirror") and "centre" in sections_seen
                and "mirror_mural" not in sections_seen):
            opts.append("Hold up the Crystal Mirror to the central panel")
        opts.append("Leave the mural hall")
        ch = prompt(opts)
        if ch == "Leave the mural hall": break

        if ch == "Examine the left panel":
            sections_seen.add("left")
            wrap("A dark pool in stone that predates any architecture. From it rises a tall figure "
                 "wrapped in shadow or absence — featureless face, ancient posture. "
                 "Around it, the world is in the process of being made. "
                 "Beneath: THAUN. THE HOLLOW. FIRST OF THE VOID-WELL.", Fore.CYAN)

        elif ch == "Examine the right panel":
            sections_seen.add("right")
            wrap("A figure falling from an impossibly bright sky — in choice, not accident. "
                 "Arms spread, face upturned. The sun blazes in gold so thick it has cracked. "
                 "The figure lands as a ring of silver light. "
                 "Beneath: ARUKIEL. OF THE FALLING LIGHT.", Fore.CYAN)

        elif ch == "Examine the central panel":
            sections_seen.add("centre")
            wrap("A dragon — massively, overwhelmingly large. Its wingspan spans the full width. "
                 "Scales painted black, shifting toward gold at certain angles. "
                 "Coiled around what appears to be the world itself — protectively. "
                 "Its eyes are open. Looking at you.", Fore.CYAN)
            wrap("Beside the dragon, much smaller, a figure in robes with her hand resting "
                 "on the dragon's flank. She looks outward also, not at the dragon. "
                 "Beneath the pair: ATH___N. KING OF ___GONS. AND YSENA. WEAVER OF SHADOWS. "
                 "SPOUSE.", Fore.CYAN)
            player.flags.add("found_ysena")
            if "found_mural" not in player.flags:
                player.flags.add("found_mural")

        elif ch == "Examine the far edge":
            sections_seen.add("fourth")
            wrap("At the mural's far edge — nearly hidden — a fourth figure. Smaller. Human-shaped. "
                 "Standing before something deliberately painted over in thick, frantic strokes: "
                 "a swirling mass of black shadow, layered, larger than the dragon. "
                 "The human figure's face is turned toward it, not away. "
                 "The inscription beneath this section has been chiselled off entirely.", Fore.MAGENTA)
            player.flags.add("found_mural")

        elif ch == "Examine the crack in the wall":
            sections_seen.add("crack")
            wrap("The crack goes deep. Something warm breathes through it — slow, enormous, patient. "
                 "Not threatening. Something at rest.", Fore.YELLOW)

        elif ch == "Hold the Candle to the chiselled section":
            sections_seen.add("candle_used")
            wrap("The candle's flame turns deep, steady blue. In the blue light the chiselled "
                 "stone becomes briefly transparent — beneath the damage, the ghost of letters. "
                 "Three legible: M, L, R. The candle returns to ordinary light.", Fore.MAGENTA + Style.BRIGHT)
            player.flags.add("candle_mural_secret")

        elif ch == "Hold up the Crystal Mirror to the central panel":
            sections_seen.add("mirror_mural")
            wrap("In the mirror's surface, the mural is slightly different. Atheron is the same. "
                 "Ysena is the same. But in the reflection, the shadow at the far edge — "
                 "the one painted over — is not painted over. "
                 "You can see it clearly in the mirror, though not directly. "
                 "It is a shape: vast, formless, and its attention, even in reflection, "
                 "is turned toward the human figure beside it.", Fore.MAGENTA + Style.BRIGHT)
            player.flags.add("mirror_mural_secret")

        room["_mural_sections"] = sections_seen


# ─── INSCRIPTION ROOM ─────────────────────────────────────────────────────────
def event_inscription_room(player, room):
    wrap("The sentence loops every surface without pause: "
         "'what the wells made the wells may remember' — endlessly.")
    done = room.get("_inscription_done", set())

    while True:
        opts = []
        if "speak" not in done:    opts.append("Speak a name into the ash")
        if "read" not in done:     opts.append("Read the full inscription")
        if "candle" not in done and player.has_item("Candle"):
            opts.append("Hold the Candle to the walls")
        if "mirror" not in done and player.has_item("Crystal Mirror"):
            opts.append("Hold up the Crystal Mirror")
        if "parchment" not in done and player.has_item("Warden's Seal"):
            opts.append("Press the Warden's Seal into the ash")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Speak a name into the ash":
            done.add("speak")
            wrap("What do you say?", Fore.MAGENTA)
            spoken = secret_input(player)
            if "void" in spoken:
                wrap("The ash rises and forms the shape of a figure emerging from water. "
                     "A crack appears in the floor, pointing toward the nearest doorway.", Fore.CYAN + Style.BRIGHT)
                player.flags.add("void_pointed")
            elif any(w in spoken for w in ("star","light","arukiel","veythari")):
                wrap("Each particle briefly catches light — a constellation in a dish. "
                     "One drifts to your palm and marks a glyph. It fades in seconds.", Fore.WHITE + Style.BRIGHT)
                player.defence += 1; print(c("  DEF +1.", Fore.GREEN))
            elif any(w in spoken for w in ("atheron","dragon")):
                wrap("The walls vibrate — once — with something shifting its weight far below.", Fore.YELLOW)
            elif any(w in spoken for w in ("maelvyr","betrayer","demongod")):
                wrap("The ash scatters violently. The inscription goes dark. "
                     "On the far wall, one word pulses as if lit from behind the stone: UNMADE.",
                     Fore.RED + Style.BRIGHT)
                player.flags.add("inscription_unmade")
            elif any(w in spoken for w in ("myrrakhel","deepest pulse")):
                wrap("The ash rises, reforms, and spells BEFORE before collapsing. "
                     "The inscription on the walls accelerates — loops faster. Then stills.",
                     Fore.YELLOW + Style.BRIGHT)
                player.flags.add("inscription_myrrakhel")
            elif any(w in spoken for w in ("vaelan","emperor")):
                wrap("The ash does not scatter. It arranges itself into the shape of a crown, "
                     "briefly, then collapses.", Fore.CYAN)
                player.flags.add("inscription_vaelan")
            elif any(w in spoken for w in ("vaethar","chosen child")):
                wrap("The ash rises in a spiral — upward — and holds for a moment "
                     "before gently descending. The dish is empty. No: on the floor beside it, "
                     "a single warm fragment.", Fore.YELLOW + Style.BRIGHT)
                player.flags.add("inscription_vaethar")
                if not player.has_item("Godshard Fragment"):
                    try_give_unique(player, "Godshard Fragment")
            elif any(w in spoken for w in ("atraxis",)):
                wrap("The ash rises in a shape that has no name — "
                     "a shape that is not a shape. "
                     "KNOWN is pressed into the dish.", Fore.RED + Style.BRIGHT)
                player.flags.add("inscription_atraxis")
                player.flags.add("atraxis_named")
            elif any(w in spoken for w in ("thalas", "tides", "endless tides")):
                wrap("The ash forms a wave. Rises. Breaks. Settles.", Fore.CYAN)
                player.flags.add("inscription_thalas")
            elif any(w in spoken for w in ("kindrael", "flame at dawn", "first flame")):
                wrap("The ash ignites briefly — gold — then falls as fresh ash.", Fore.YELLOW)
                player.flags.add("inscription_kindrael")
            else:
                wrap("The ash is still. The inscription continues.")

        elif ch == "Read the full inscription":
            done.add("read")
            wrap("Three full circuits before finding a variation: "
                 "'what the wells made the wells may remember what was taken from the wells cannot return' — "
                 "then the repetition resumes. "
                 "Beneath the altered passage, in tiny script: 'M___VYR UNMADE THE AGREEMENT.'", Fore.CYAN)
            player.flags.add("inscription_variation")

        elif ch == "Hold the Candle to the walls":
            done.add("candle")
            wrap("The candle's flame turns blue-white. In that light, beneath the visible inscription, "
                 "another layer of script appears — older, in a language even older than Eldrosian. "
                 "You cannot read it. But one symbol repeats, and you recognise it: "
                 "it is the same as the symbol on the Ashen Key, if you have seen one. "
                 "The candle returns to yellow.", Fore.MAGENTA + Style.BRIGHT)
            player.flags.add("candle_inscription_secret")

        elif ch == "Hold up the Crystal Mirror":
            done.add("mirror")
            wrap("In the mirror, the inscription runs in the opposite direction — "
                 "and is different. Not reversed: different. Different words. "
                 "You can read one phrase in the mirror-version: "
                 "'the name that was removed will be found by whoever is patient enough to look.'",
                 Fore.MAGENTA + Style.BRIGHT)
            player.flags.add("mirror_inscription_secret")

        elif ch == "Press the Warden's Seal into the ash":
            done.add("parchment")
            wrap("The Warden's Seal sinks into the ash as if it belongs there. "
                 "The inscription on the walls briefly stops — every loop halts simultaneously — "
                 "and then resumes, faster. "
                 "In the dish, beneath the ash where the seal now rests: a Warden's Key.", Fore.YELLOW + Style.BRIGHT)
            player.flags.add("warden_seal_inscription")
            player.remove_item("Warden's Seal")
            try_give_unique(player, "Warden's Key")

        room["_inscription_done"] = done


# ─── DRAGON HALL ──────────────────────────────────────────────────────────────
def event_dragon_hall(player, room):
    wrap("A vast scaled hide — black as deep water but with an inner quality that suggests gold. "
         "Legs like columns. Slow breathing. One eye, closed.", Fore.YELLOW)
    done = room.get("_dragon_done", set())

    while True:
        opts = []
        if "study" not in done:   opts.append("Study the dragon from the doorway")
        if "approach" not in done:opts.append("Approach very carefully")
        if "name" not in done:    opts.append("Speak the dragon's name")
        if "scale" not in done and "study" in done:
            opts.append("Take the shed scale near the doorway")
        if (player.has_item("Dragon Scale") and "scale_offered" not in done
                and "atheron_named" in player.flags):
            opts.append("Offer the Dragon Scale to Atheron")
        if (player.has_item("Vaethar's Tear") and "tear_offered" not in done
                and "atheron_named" in player.flags):
            opts.append("Offer Vaethar's Tear to Atheron")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Study the dragon from the doorway":
            done.add("study")
            wrap("Scales the size of shields. Black at rest, gold at angles. "
                 "The lintel above: ATH — the rest buried. The rubble has formed around it, "
                 "not fallen on it.", Fore.YELLOW)
            wrap("Near the doorway: a single shed scale, lying there for decades.")
            player.flags.add("studied_atheron")
            if "found_ysena" in player.flags:
                wrap("On the dragon's flank, barely visible, a marking — "
                     "not a wound, but a deliberate mark, pressed into the scale "
                     "by something that loved it. A handprint, small.", Fore.CYAN)
                player.flags.add("ysena_handprint")

        elif ch == "Take the shed scale near the doorway":
            done.add("scale")
            player.pick_up(get_item("Dragon Scale"))

        elif ch == "Approach very carefully":
            done.add("approach")
            if random.random() < 0.5:
                wrap("Your foot disturbs a stone. The eye opens — gold, burning, focusing on you "
                     "with intelligence that makes the space between your thoughts feel small.", Fore.RED)
                print(); print(c("  ATHERON — KING OF DRAGONS", Fore.RED + Style.BRIGHT)); print()
                sub = prompt(["Stand still","Run","Speak"])
                if sub == "Stand still":
                    wrap("You do not move. The gold eye considers you at length. Then closes. "
                         "You are allowed to leave.", Fore.YELLOW)
                    player.flags.add("atheron_woke_and_spared")
                    player.max_hp += 10; print(c("  Max HP +10.", Fore.GREEN))
                elif sub == "Run":
                    dmg = random.randint(20,35); player.hp -= dmg
                    print(c(f"  The dragon exhales. Not fire — force. -{dmg} HP.", Fore.RED))
                elif sub == "Speak":
                    spoken = secret_input(player)
                    if any(w in spoken for w in ("atheron","king","eldest")):
                        wrap("The eye opens wider. A sound closer to agreement than roar. Closes again. "
                             "The room grows warm rather than dangerous.", Fore.YELLOW)
                        player.flags.add("atheron_named")
                        player.attack += 2; print(c("  ATK +2.", Fore.GREEN))
                    elif any(w in spoken for w in ("ysena","weaver","spouse")):
                        wrap("Both eyes open. The sound that comes from the dragon is not words — "
                             "but it is clear. Then both eyes close again. "
                             "The warmth in the room increases, and does not return to what it was.", Fore.CYAN)
                        player.flags.add("atheron_ysena_named")
                        player.max_hp += 8; player.hp = min(player.hp+8, player.max_hp)
                        print(c("  Max HP +8.", Fore.GREEN))
                    elif any(w in spoken for w in ("vaethar","chosen child","godshard")):
                        wrap("A very long pause. Then the eye closes. "
                             "The floor vibrates — once — with something that might be grief.", Fore.YELLOW)
                        player.flags.add("atheron_vaethar_named")
                    else:
                        wrap("Hot air from its nose moves your hair. The eye closes. You are dismissed.",
                             Fore.YELLOW)
            else:
                wrap("You reach the rubble without waking it. In a crack where its foreleg rests: a small chest.",
                     Fore.GREEN)
                gold = random.randint(25,40); player.gold += gold
                loot = get_item("Eldrosian Spear") or random_item(); player.pick_up(loot)
                print(c(f"  {gold} gold and {loot['name']}.", Fore.GREEN))

        elif ch == "Speak the dragon's name":
            done.add("name")
            wrap("What do you say?", Fore.MAGENTA)
            spoken = secret_input(player)
            if any(w in spoken for w in ("atheron","king of dragons","eldest")):
                if "atheron_named" not in player.flags:
                    player.flags.add("atheron_named")
                    wrap("Both eyes open. Gold and the colour of first light and the colour of endings. "
                         "Long patience. Then they close. Something has been acknowledged.", Fore.YELLOW + Style.BRIGHT)
                    player.attack += 2; player.max_hp += 5
                    print(c("  ATK +2, Max HP +5.", Fore.GREEN))
                else:
                    wrap("Both eyes open. They close again. You have already been seen.", Fore.YELLOW)
            elif any(w in spoken for w in ("ysena","weaver of shadows")):
                if "atheron_ysena_named" not in player.flags:
                    player.flags.add("atheron_ysena_named")
                    wrap("Both eyes open at once. The sound that comes from the dragon reverberates "
                         "through the rubble. Not anger — memory. Then quiet.", Fore.CYAN)
                    player.max_hp += 8; player.hp = min(player.hp+8, player.max_hp)
                    print(c("  Max HP +8.", Fore.GREEN))
                else:
                    wrap("The eye opens. Closes. It has heard you say this before.", Fore.CYAN)
            else:
                wrap("The dragon breathes. It has heard you. It does not react.", Fore.YELLOW)

        elif ch == "Offer the Dragon Scale to Atheron":
            done.add("scale_offered")
            player.remove_item("Dragon Scale")
            wrap("You hold the scale toward the sleeping dragon. "
                 "One eye opens. It regards the scale for a long moment. "
                 "Then it exhales — very gently — and the scale dissolves in the warm breath, "
                 "returning to where it came from. The eye closes. "
                 "On the floor where you stood: a Godshard Fragment.", Fore.YELLOW + Style.BRIGHT)
            try_give_unique(player, "Godshard Fragment")
            player.flags.add("scale_returned_atheron")

        elif ch == "Offer Vaethar's Tear to Atheron":
            done.add("tear_offered")
            player.remove_item("Vaethar's Tear")
            wrap("You hold the Tear toward the sleeping dragon. "
                 "Both eyes open. The warmth in the room increases sharply. "
                 "The Tear glows — gold — and then the dragon's breath takes it. "
                 "Both eyes close. The room is very warm now, and stays that way.", Fore.YELLOW + Style.BRIGHT)
            player.attack += 3; player.max_hp += 12; player.hp = player.max_hp
            print(c("  ATK +3, Max HP +12, fully healed. Atheron has acknowledged the return.",Fore.GREEN))
            player.flags.add("vaethar_tear_atheron")

        room["_dragon_done"] = done


# ─── VAULT DOOR ───────────────────────────────────────────────────────────────
def event_vault_door(player, room):
    wrap("A chamber that exists only to contain a door. Lock the size of your fist. "
         "Above the frame: 'What the empire buried, the empire kept.'")
    if "vault_opened" in room:
        wrap("The vault stands open. You have already been inside.", Fore.LIGHTBLUE_EX+Style.BRIGHT); return
    if player.has_item("Iron Key"):
        if prompt(["Use the Iron Key","Leave it locked"]) == "Use the Iron Key":
            player.remove_item("Iron Key"); room["vault_opened"] = True
            hr(colour=Fore.YELLOW)
            gold = random.randint(15,30); player.gold += gold
            try_give_unique(player, "Ashen Tablet")
            try_give_unique(player, "Imperial Edict")
            print(c(f"  Found {gold} gold.", Fore.YELLOW))
            wrap("Inscription on the back wall: "
                 "'Do not look for who is responsible in the records — they were removed. "
                 "Look instead for what was agreed with in the dark. "
                 "The name is secondary.' Beneath, in different handwriting: UNMADE.", Fore.CYAN)
            player.flags.add("found_vault_door")
        else:
            print("  The door waits.")
    else:
        wrap("The lock requires a key you do not have.")


# ─── SEALED SANCTUM ───────────────────────────────────────────────────────────
def event_sealed_sanctum(player, room):
    wrap("Runes on the frame pulse like a heartbeat. No handle. No force will open this.")
    if "sanctum_opened" in room:
        wrap("The sanctum stands open. You have already been inside.", Fore.LIGHTBLUE_EX+Style.BRIGHT); return
    if player.has_item("Ashen Key"):
        sub = prompt(["Use the Ashen Key","Study the runes first","Leave"])
        if sub == "Study the runes first":
            wrap("Pre-imperial Eldrosian: 'This sanctum holds what the empire could not destroy. "
                 "What is here was witnessed. The witness survives. "
                 "The thing witnessed has not been undone.'", Fore.CYAN)
            sub = prompt(["Use the Ashen Key","Leave"])
        if sub == "Use the Ashen Key":
            player.remove_item("Ashen Key"); room["sanctum_opened"] = True
            hr("═", colour=Fore.MAGENTA)
            wrap("The key dissolves in the lock — does not turn, simply becomes ash.", Fore.MAGENTA)
            hr("═", colour=Fore.MAGENTA); pause()
            wrap("The account on the walls reads: "
                 "'In the final year, the High Keeper of the Rites was granted the last "
                 "formal audience with the Great Gods. He claimed to carry a question of "
                 "imperial importance. The witnesses reported he did not ask a question. '", Fore.MAGENTA)
            pause()
            wrap("'He made an agreement — with something that was not the Great Gods. "
                 "Something present in every prior audience, undetected — depicted in every mural "
                 "as a swirling shadow at the image's edge. The witnesses called it the Unmade. '", Fore.MAGENTA)
            pause()
            wrap("'The High Keeper's agreement: in exchange for his mortal nature — "
                 "his death, his limitation, his ending — he would be remade. '", Fore.MAGENTA)
            wrap("'The Unmade agreed. The empire died the same night. '", Fore.MAGENTA)
            wrap("'He stormed the capital. He killed Emperor Vaelan on his throne. '", Fore.MAGENTA)
            wrap("'The Godshards were present. What happened to them in that moment '", Fore.MAGENTA)
            wrap("'the witnesses could not determine. '", Fore.MAGENTA)
            wrap("'The High Keeper's name was removed from all records by unanimous decree. '", Fore.MAGENTA)
            wrap("'The witnesses wrote it here once, because something must hold it: '", Fore.MAGENTA)
            wrap("'MAELVYR. The word DEMONGOD was coined afterward. It does not capture it.'",
                 Fore.MAGENTA + Style.BRIGHT)
            hr("═", colour=Fore.MAGENTA)
            player.flags.add("found_sealed_sanctum"); player.flags.add("full_truth_known")
            player.flags.add("sanctum_vaelan_detail")
            try_give_unique(player, "Starlight Key"); try_give_unique(player, "Void Shard"); try_give_unique(player, "Third Godshard")
            wrap("The sealed book's final page: "
                 "'The Veythari call it the Unmade. The Morvath: the thing before the wells. '", Fore.CYAN)
            wrap("'Both agree: it existed before Thaun. Before Arukiel. Before the dragons. '", Fore.CYAN)
            wrap("'It has always been here. It has always been patient.'", Fore.CYAN)
    else:
        wrap("The keyhole does not accept anything you carry.")


# ─── VEYTHARI DOOR ────────────────────────────────────────────────────────────
def event_veythari_door(player, room):
    wrap("The door glows from itself. It has been waiting.")
    if "veythari_opened" in room:
        wrap("The archive stands open. You have already been inside.", Fore.LIGHTBLUE_EX+Style.BRIGHT); return
    has_key = player.has_item("Starlight Key") or player.has_item("Starlight Shard")
    if has_key:
        kn = "Starlight Key" if player.has_item("Starlight Key") else "Starlight Shard"
        if prompt([f"Use the {kn}","Leave"]) == f"Use the {kn}":
            player.remove_item(kn); room["veythari_opened"] = True
            hr("═",colour=Fore.WHITE)
            wrap("A chord. The door opens. Light from the walls themselves.", Fore.WHITE); pause()
            wrap("A Veythari archive. The final entry, left open: "
                 "'The Morvath confirm what we suspected. The Unmade predates all of us. '", Fore.WHITE)
            wrap("'It was here before the wells formed. At Eldros, it finally succeeded — '", Fore.WHITE)
            wrap("'briefly, through one man who opened the door. '", Fore.WHITE)
            wrap("'We do not know if it has withdrawn. We do not know if it can. '", Fore.WHITE)
            wrap("'We write this because we are the last who remember. '", Fore.WHITE)
            wrap("'If you read this, you were meant to.'", Fore.WHITE)
            player.flags.add("found_veythari_archive")
            if not player.has_item("Scale Armour"):
                wrap("At the base of the first shelf: armour, scale-worked from something large and dark.",Fore.WHITE)
                player.pick_up(get_item("Scale Armour"))
    else:
        wrap("The keyhole is shaped like a shard. You have nothing that fits.")


# ─── VOID WELL ────────────────────────────────────────────────────────────────
def event_void_well(player, room):
    hr("═", colour=Fore.LIGHTBLUE_EX+Style.BRIGHT)
    wrap("A well of darkness so complete it seems solid. The stones around the rim bear "
         "symbols older than any script. The stone hums.", Fore.LIGHTBLUE_EX+Style.BRIGHT)
    hr("═", colour=Fore.LIGHTBLUE_EX+Style.BRIGHT); print()
    done = room.get("_well_done", set())

    while True:
        opts = []
        if "look" not in done:    opts.append("Look into the well")
        if "speak" not in done:   opts.append("Speak into the well")
        if "offer" not in done:   opts.append("Leave an offering")
        if "hollow" not in done and player.has_item("Hollow Stone"):
            opts.append("Look through the Hollow Stone into the well")

        # New option: trigger confrontation
        if (confrontation_unlocked(player) and
                "confrontation_done" not in player.flags and
                "trigger_confrontation" not in done):
            opts.append("Something is rising from the well")

        # New option: attempt the sealing
        if ("refused_the_offer" in player.flags and
                "spoke_myrrakhel_shrine" in player.flags and
                "full_truth_known" in player.flags and
                "sealing_done" not in done):
            opts.append("Speak Myrrakhel\\'s name into the well as a question")

        opts.append("Turn back")
        ch = prompt(opts)
        if ch == "Turn back": break

        if ch == "Look into the well":
            done.add("look")
            wrap("The darkness looks back. Something shifts, orients, focuses. "
                 "Very far below: the outline of something vast. Not Atheron. Something that predates names. "
                 "You pull back.", Fore.LIGHTBLUE_EX+Style.BRIGHT)
            if "full_truth_known" in player.flags:
                wrap("You understand what you are looking at. The Unmade. Still here. "
                     "The agreement with Maelvyr was not a door that could close again. "
                     "It was a crack.", Fore.RED+Style.BRIGHT)
            player.flags.add("looked_void_well")

        elif ch == "Speak into the well":
            done.add("speak")
            wrap("The well is listening.", Fore.MAGENTA)
            spoken = secret_input(player)
            if any(w in spoken for w in ("maelvyr","demongod")):
                wrap("The darkness convulses — once — then is still. Cold to the edge of pain. "
                     "A word pressed into the rim from below: WITNESSED.", Fore.RED+Style.BRIGHT)
                if "void_well_witnessed" not in player.flags:
                    player.flags.add("void_well_witnessed")
                    player.max_hp += 15; player.attack += 3
                    print(c("  Max HP +15, ATK +3.", Fore.GREEN))
            elif any(w in spoken for w in ("thaun","thaun the hollow")):
                wrap("The darkness rises slightly toward your voice. Curious. Then settles.", Fore.CYAN)
            elif any(w in spoken for w in ("atheron","dragon")):
                wrap("The floor vibrates. Three times. Rhythmic. Something above has heard you.", Fore.YELLOW)
            elif "unmade" in spoken:
                wrap("All light goes out. In the dark the well is everywhere. "
                     "Then light returns. The well is in its place.", Fore.RED+Style.BRIGHT)
                player.flags.add("spoke_unmade")
            elif any(w in spoken for w in ("atraxis",)):
                if "atraxis_well" not in player.flags:
                    player.flags.add("atraxis_well")
                    player.flags.add("atraxis_named")
                    wrap("The well responds differently to this name. "
                         "Not the convulsion of 'unmade' — something slower. "
                         "The darkness rises to the rim and rests there. "
                         "Looking. Recognising that you know what to call it.",
                         Fore.RED + Style.BRIGHT)
                    wrap("A word is pressed into the rim — not WITNESSED this time. "
                         "One word: KNOWN.", Fore.RED + Style.BRIGHT)
                    player.max_hp += 8; player.attack += 2
                    print(c("  Max HP +8, ATK +2. The oldest name has power.", Fore.GREEN))
                else:
                    wrap("The well rises to the rim again. It knows you know. "
                         "It is patient with the knowledge.", Fore.RED)
            elif any(w in spoken for w in ("myrrakhel","deepest pulse")):
                wrap("A single pulse of warmth rises from the dark — not cold, not threatening. "
                     "Acknowledgement. It fades. The cold returns.", Fore.YELLOW+Style.BRIGHT)
                player.flags.add("void_well_myrrakhel")
            elif any(w in spoken for w in ("vaelan","emperor")):
                wrap("The darkness is still for a long time. Then, from very deep, "
                     "a sound like something heavy settling — slowly, finally, to rest.", Fore.CYAN)
                player.flags.add("void_well_vaelan")
            elif any(w in spoken for w in ("vaethar","chosen child","godshard")):
                wrap("The darkness rises all the way to the rim and holds — gold, briefly, "
                     "at the very surface — then drops away. The coldness that remains "
                     "is a different kind of cold. Older.", Fore.YELLOW+Style.BRIGHT)
                player.flags.add("void_well_vaethar")
            elif any(w in spoken for w in ("thalas", "tides")):
                wrap("A sound from the well — not a voice, but the frequency of moving water. "
                     "The well has heard this name before.", Fore.CYAN)
                player.flags.add("void_well_thalas")
            elif any(w in spoken for w in ("kindrael", "flame")):
                wrap("The darkness briefly turns gold at the very bottom. "
                     "Then ordinary black.", Fore.YELLOW)
                player.flags.add("void_well_kindrael")
            elif any(w in spoken for w in ("serethan", "warden")):
                wrap("A warmth from the well — rising, not falling. "
                     "As though the well is passing on a message.", Fore.YELLOW)
                player.flags.add("void_well_serethan")
                if "met_serethan" in player.flags:
                    wrap("You understand: Serethan's echo reaches even here.", Fore.YELLOW + Style.BRIGHT)
            else:
                wrap("Your voice falls in. It does not echo.", Fore.LIGHTBLUE_EX+Style.BRIGHT)

        elif ch == "Leave an offering":
            done.add("offer")
            offerable = [it for it in player.inventory
                         if it["name"] in ("Void Shard","Relic Coin","Godshard Fragment",
                                           "Dawn Shard","Blood Amber","Vaethar's Tear")]
            if not offerable:
                wrap("You have nothing that feels right. The well waits anyway."); continue
            opts2 = [it["name"] for it in offerable] + ["Nothing"]
            name = prompt(opts2)
            if name == "Nothing": continue
            player.remove_item(name)
            if name == "Void Shard":
                wrap("It falls — down and down — until gone. One low note, felt. "
                     "Something has been returned.", Fore.LIGHTBLUE_EX+Style.BRIGHT)
                player.max_hp += 10; player.defence += 2
                print(c("  Max HP +10, DEF +2.", Fore.GREEN)); player.flags.add("shard_returned")
            elif name == "Relic Coin":
                wrap("The coin vanishes. Six coins appear on the rim, placed with care.", Fore.YELLOW)
                player.gold += 30; print(c("  +30 gold.", Fore.YELLOW))
            elif name == "Godshard Fragment":
                wrap("The shard falls. The well is silent for a long moment. "
                     "Then a pulse — gold — from far below — rises and warms the chamber "
                     "before fading. Something was recognised.", Fore.YELLOW+Style.BRIGHT)
                player.max_hp += 12; player.attack += 2; player.hp = player.max_hp
                print(c("  Max HP +12, ATK +2, fully healed.", Fore.GREEN))
                player.flags.add("godshard_offered_well")
            elif name == "Dawn Shard":
                wrap("The shard glows brighter as it falls — orange, then gold, then white — "
                     "until it is gone. The well is briefly warm. Then cold again.", Fore.YELLOW)
                player.max_hp += 8; player.hp = player.max_hp
                print(c("  Max HP +8, fully healed.", Fore.GREEN))
                player.flags.add("dawn_shard_offered_well")
            elif name == "Blood Amber":
                wrap("The amber hits the edge of the well and cracks. "
                     "Something dark pours from it into the dark below. "
                     "The well receives it without comment.", Fore.RED)
                player.gold += 15; player.max_hp += 5
                print(c("  +15 gold, Max HP +5.", Fore.YELLOW))
            elif name == "Vaethar's Tear":
                wrap("The Tear falls and the well goes gold — entirely, instantaneously — "
                     "for one second, before returning to darkness. "
                     "In that second the room is warmer than it has ever been.", Fore.YELLOW+Style.BRIGHT)
                player.max_hp += 20; player.attack += 3; player.hp = player.max_hp
                player.flags.add("vaethar_tear_well")
                print(c("  Max HP +20, ATK +3, fully healed. The well remembers Vaethar.", Fore.GREEN))

        elif ch == "Look through the Hollow Stone into the well":
            done.add("hollow")
            wrap("You hold the Hollow Stone over the well and look through its hole. "
                 "Through the hole, the well looks different — not dark, but full. "
                 "Full of something like light, but not light. Something that predates light. "
                 "And at the very bottom, a shape — not formless. A shape. "
                 "Looking back at you through the stone. "
                 "When you lower the stone, the well is dark again.", Fore.MAGENTA+Style.BRIGHT)
            player.flags.add("hollow_stone_well")
            player.max_hp += 5; print(c("  Max HP +5. You have seen something few have.",Fore.GREEN))

        elif ch == "Something is rising from the well":
            done.add("trigger_confrontation")
            _confrontation(player)

        elif ch == "Speak Myrrakhel\\'s name into the well as a question":
            done.add("sealing_done")
            _ending_sealing(player)

        room["_well_done"] = done


# ─── BLOOD DOOR ───────────────────────────────────────────────────────────────
def event_blood_door(player, room):
    wrap("The door is warm. The keyhole is shaped like a wound.")
    if "blood_opened" in room:
        wrap("The door stands open.", Fore.LIGHTBLUE_EX+Style.BRIGHT); return
    if player.has_item("Blood Key"):
        if prompt(["Use the Blood Key","Leave"]) == "Use the Blood Key":
            player.remove_item("Blood Key"); room["blood_opened"] = True
            hr("═",colour=Fore.RED)
            wrap("The door opens like an exhale. Vials on the walls. A stone table. "
                 "An inscription: 'The Bloodwell produces what the others cannot. "
                 "Not a creature — a hunger. A need that outlasts the body that carries it. '", Fore.RED)
            wrap("'We sealed this room because the research was unfinished. '", Fore.RED)
            wrap("'If someone is still looking — a being who seeks the blood of those who work magik — '", Fore.RED)
            wrap("'that is not our responsibility. We stopped.' Beneath, added later: "
                 "'We should have stopped sooner. Mograx, first of the Orkyn, warned us.'", Fore.RED)
            player.flags.add("found_blood_door")
            if any(f in player.flags for f in ("prisoner_dravennis","heard_dravennis")):
                wrap("The name Dravennis slots against this. The research. The hunger.", Fore.MAGENTA)
            player.pick_up(get_item("Blood Amber"))
            gold = random.randint(10,20); player.gold += gold
            print(c(f"  Blood Amber and {gold} gold.", Fore.YELLOW))
    else:
        wrap("The keyhole does not accept what you carry.")


# ─── WARDEN'S ARCHIVE ─────────────────────────────────────────────────────────
def event_wardens_archive(player, room):
    wrap("A door bearing the eye-and-scales emblem of the Warden's office. "
         "Beneath the emblem, a keyhole.")
    if "archive_opened" in room:
        wrap("The archive stands open.", Fore.LIGHTBLUE_EX+Style.BRIGHT); return
    if player.has_item("Warden's Key"):
        if prompt(["Use the Warden's Key","Leave"]) == "Use the Warden's Key":
            player.remove_item("Warden's Key"); room["archive_opened"] = True
            hr(colour=Fore.YELLOW)
            wrap("A records room. Rows of ledgers, sealed case files, indexed by year. "
                 "Most are damaged. Three sections are legible:", Fore.YELLOW)
            wrap("'YEAR 1190: The High Keeper's office formally established under Imperial Charter. '", Fore.YELLOW)
            wrap("'YEAR 1203: First formal audience with the Great Gods conducted under new protocols. '", Fore.YELLOW)
            wrap("'YEAR 1243 (FINAL ENTRY): The High Keeper has requested personal audience. '", Fore.YELLOW)
            wrap("'Emperor Vaelan has approved with noted reluctance. The Warden's office has lodged '", Fore.YELLOW)
            wrap("'a formal objection. This objection was overruled. This file is hereby sealed.'", Fore.YELLOW)
            hr(colour=Fore.YELLOW)
            player.flags.add("found_wardens_archive")
            player.pick_up(random_lore())
            gold = random.randint(12,22); player.gold += gold
            print(c(f"  A lore document and {gold} gold.", Fore.YELLOW))
    elif player.has_item("Warden's Seal"):
        wrap("The emblem on your Warden's Seal matches the one on the door. "
             "But the seal alone isn't a key — you need the actual Warden's Key.")
    else:
        wrap("The emblem-lock requires a Warden's Key.")


# ─── THRONE ROOM (EMPEROR VAELAN'S) ──────────────────────────────────────────
def event_throne_room(player, room):
    hr("═",colour=Fore.RED)
    print(c("  THE THRONE OF ELDROS-VERATH", Fore.RED+Style.BRIGHT))
    hr("═",colour=Fore.RED); print()
    wrap("This room is different. Not in ruin — in stillness. "
         "The destruction here was not the slow work of centuries. "
         "It was one event, and that event left everything exactly where it fell. "
         "Overturned furniture. Shattered windows. "
         "And the throne — intact, black stone — with someone still sitting in it.", Fore.RED); pause()
    wrap("The figure is armoured. Has been for a very long time. "
         "The armour is Eldrosian, ceremonial, undamaged. "
         "The person inside it is not. They died here. They died in their throne. "
         "On the throne's arm, still held by the figure's gauntleted hand: "
         "something that vibrates at a frequency you feel in your chest.", Fore.RED); pause()
    wrap("The Godshard. One fragment — the largest, by the look of it — "
         "still clutched in the hand of Emperor Vaelan.", Fore.RED+Style.BRIGHT); print()
    player.flags.add("found_throne_room")

    done = room.get("_throne_done", set())
    while True:
        opts = []
        if "read" not in done:   opts.append("Read the inscriptions in the room")
        if "vaelan" not in done: opts.append("Approach Emperor Vaelan")
        if "take" not in done and "vaelan" in done:
            opts.append("Take the Godshard from his hand")
        if "crown" not in done and player.has_item("Old Crown") and "vaelan" in done:
            opts.append("Place the Old Crown on the throne")
        if "mirror" not in done and player.has_item("Crystal Mirror"):
            opts.append("Hold up the Crystal Mirror in this room")
        if "hollow" not in done and player.has_item("Hollow Stone") and "vaelan" in done:
            opts.append("Look through the Hollow Stone at Vaelan")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Read the inscriptions in the room":
            done.add("read")
            wrap("The walls of the throne room are covered in records — the acts and edicts of "
                 "every Eldrosian emperor, in order, going back to the founding. "
                 "The series ends abruptly mid-sentence in the account of Vaelan's reign. "
                 "Someone was mid-inscription when the Night of Collapse happened. "
                 "The chisel marks in the stone are still fresh, by comparison.", Fore.CYAN)
            wrap("Above the throne, carved largest of all: "
                 "VAELAN. EMPEROR. HOLDER OF THE GODSHARDS. CHOSEN OF THE DRAGON-LINE. "
                 "LAST OF THE CONSOLIDATED AGE.", Fore.CYAN)
            # Tolos plinth
            wrap("To the left of the throne, a secondary plinth — smaller, "
                 "not imperial, added after the fact. "
                 "Carved on its face: TOLOS. "
                 "Below the name: a date, and beneath the date, "
                 "two words in a hand you recognise from the Chronicle if you have read it: "
                 "HE TRIED.",
                 Fore.CYAN + Style.BRIGHT)
            player.flags.add("found_tolos_plinth")
            if "read_talarion_chronicle" in player.flags:
                wrap("Talarion placed this here. He said he would tell the story. "
                     "He also, apparently, came back to carve a name.", Fore.CYAN)

        elif ch == "Approach Emperor Vaelan":
            done.add("vaelan")
            wrap("Up close: the armour is immaculate. The figure is not. "
                 "Centuries have done what they do. But the armour has held everything in place, "
                 "as though unwilling to let the emperor be less than he was.", Fore.RED)
            wrap("The Godshard in his hand pulses very faintly. It has been pulsing for centuries. "
                 "It is the only thing in this room that is still doing anything.", Fore.RED+Style.BRIGHT)
            if "full_truth_known" in player.flags:
                wrap("You know who killed him. You know what that person became. "
                     "You know what the Godshards are — fragments of Vaethar, Atheron's chosen child. "
                     "You know that Maelvyr took something that was not his to take.", Fore.MAGENTA+Style.BRIGHT)
                player.flags.add("throne_full_context")

        elif ch == "Take the Godshard from his hand":
            done.add("take")
            wrap("You reach for the Godshard. The hand's grip does not resist.", Fore.RED)
            success = try_give_unique(player, "Godshard Fragment")
            if success:
                player.flags.add("took_godshard_from_vaelan")
                wrap("The armoured figure settles — as though something has been released.", Fore.RED)
            else:
                wrap("You already carry it. Vaelan's hand holds empty air now.", Fore.RED)

        elif ch == "Place the Old Crown on the throne":
            done.add("crown")
            player.remove_item("Old Crown")
            wrap("You set the crown on the arm of the throne, beside where Vaelan sits. "
                 "The inscription at the shrine said: worn by those who came before Vaelan. "
                 "You are returning it. "
                 "The Godshard pulses once — brighter — and then settles.", Fore.YELLOW+Style.BRIGHT)
            player.flags.add("crown_returned_throne")
            player.max_hp += 10; player.attack += 2
            print(c("  Max HP +10, ATK +2. The act was correct.", Fore.GREEN))

        elif ch == "Hold up the Crystal Mirror in this room":
            done.add("mirror")
            wrap("In the mirror, the throne room is as it was — alive, full, before the event. "
                 "Vaelan sits in the throne: armoured, upright, present. "
                 "A figure stands before him — smaller, robed — and there is something "
                 "behind that figure that the mirror shows clearly. "
                 "Something dark, something vast, something that has been there for the entire "
                 "duration of the Eldrosian empire, always at the edge of every image, "
                 "always overlooked. Until it was not.", Fore.MAGENTA+Style.BRIGHT)
            player.flags.add("mirror_throne_room")
            if "full_truth_known" in player.flags:
                wrap("The robed figure is Maelvyr. The thing behind him is the Unmade. "
                     "The Unmade's shadow falls over the entire throne room in the mirror. "
                     "In the real room: nothing. The shadow is gone from here. "
                     "It has moved elsewhere.", Fore.MAGENTA+Style.BRIGHT)

        elif ch == "Look through the Hollow Stone at Vaelan":
            done.add("hollow")
            wrap("Through the Hollow Stone, Vaelan is not a figure in armour. "
                 "He is a light — dim, but present — still sitting in the throne. "
                 "Not quite gone. Something of him remains in the room, "
                 "held there by the Godshard he held for so long. "
                 "When you lower the stone, the room is just a room again.", Fore.CYAN+Style.BRIGHT)
            player.flags.add("hollow_stone_vaelan")
            if "took_godshard_from_vaelan" in player.flags:
                wrap("The light, through the stone, is slightly less than it was. "
                     "You took the thing that was holding it. It will fade now.", Fore.CYAN)

        room["_throne_done"] = done


# ─── OSSUARY ──────────────────────────────────────────────────────────────────
def event_ossuary(player, room):
    wrap("Bones stacked with deliberate care along every wall. "
         "Each skull has something placed in its eye sockets. All the same.")
    done = room.get("_ossuary_done", set())
    while True:
        opts = []
        if "examine" not in done: opts.append("Examine the objects in the eye sockets")
        if "name" not in done:    opts.append("Look for a named alcove")
        if "candle" not in done and player.has_item("Candle"):
            opts.append("Hold the Candle to the back wall")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Examine the objects in the eye sockets":
            done.add("examine")
            obj = random.choice(["small round stones, each with a hole through the centre",
                                 "copper coins bearing an erased face",
                                 "fragments of dark material that is neither stone nor metal",
                                 "seeds — long dead but intact"])
            wrap(f"The objects are {obj} — all the same, in every skull. "
                 "Someone visited each alcove and placed these deliberately.")
            if random.random() < 0.3:
                item = random.choice([get_item("Relic Coin"),get_item("Iron Key"),get_item("Candle")])
                if item:
                    wrap(f"In one skull, different from the others: {item['name']}.")
                    if prompt(["Take it","Leave it"]) == "Take it":
                        player.pick_up(item)

        elif ch == "Look for a named alcove":
            done.add("name")
            wrap("One alcove, at the far end, has a name chiselled above it — "
                 "the only name in the room, chiselled through many times. "
                 "Still legible: M — something — L. Then a gap. Then R.", Fore.CYAN)
            player.flags.add("ossuary_name")

        elif ch == "Hold the Candle to the back wall":
            done.add("candle")
            wrap("The candle turns blue. Behind the back wall's surface, in the blue light: "
                 "a passage. Not bricked up — simply disguised by plaster. "
                 "There is a handhold, and when you pull it, the wall section moves.", Fore.MAGENTA+Style.BRIGHT)
            player.flags.add("ossuary_secret_passage")
            wrap("The passage leads to a small hidden chamber. On a shelf: "
                 "a sealed Rolled Parchment and a modest amount of gold.")
            player.pick_up(pick_parchment_variant(player))
            gold = random.randint(10,18); player.gold += gold
            print(c(f"  +{gold} gold.", Fore.YELLOW))

        room["_ossuary_done"] = done


# ─── GAMBLING DEN ─────────────────────────────────────────────────────────────
def event_gambling_den(player, room):
    wrap("Three figures around a low table. They look up without surprise. "
         "'Room for one more.'")
    LINES = [
        (None, "'Know what's funny? They thought they'd last forever. They all do.'"),
        (None, "'The lights down here never go out. Ask yourself who keeps them burning.'"),
        ("prisoner_told_well", "'Been to the bottom yet? There is a bottom. I didn't go far enough.'"),
        ("found_mural", "'Mural room, was it? Fourth figure gets everyone. Painted over for a reason.'"),
        ("spoke_maelvyr_shrine", "'Careful with names down here. They're heavier than above ground.'"),
        (None, "'Nine of everything in this place. I stop counting after a while.'"),
        ("found_throne_room", "'Sat on the throne? I didn't. Some things you just know not to do.'"),
        ("sael_spoke_maelvyr", "'You've got the look of someone who found out something they wish they hadn't.'"),
    ]
    while True:
        print(c(f"  Your gold: {player.gold}", Fore.YELLOW))
        ch = prompt(["Play a hand (10g)","Double or nothing on a die (5g)","Ask a gambler something","Leave"])
        if ch == "Leave": print("  None of them watch you go."); break

        elif ch == "Play a hand (10g)":
            if player.gold < 10: print(c("  'Need 10 gold.'", Fore.YELLOW)); continue
            player.gold -= 10
            pr = random.randint(1,6)+random.randint(1,6)
            hr2 = random.randint(1,6)+random.randint(1,6)
            print(c(f"  You roll: {pr}.  House rolls: {hr2}.", Fore.YELLOW))
            if pr > hr2:
                won = random.randint(14,22); player.gold += won; print(c(f"  You win {won} gold.", Fore.GREEN))
            elif pr == hr2:
                player.gold += 10; print(c("  Tie. Stake returned.", Fore.YELLOW))
            else:
                print(c("  House wins.", Fore.RED))

        elif ch == "Double or nothing on a die (5g)":
            if player.gold < 5: print(c("  'Need 5 gold.'", Fore.YELLOW)); continue
            player.gold -= 5
            if random.random() < 0.5:
                player.gold += 10; print(c("  High roll. You win 10 gold.", Fore.GREEN))
            else:
                print(c("  Low roll. The house takes it.", Fore.RED))

        elif ch == "High stakes (50g, double or triple)":
            if player.gold < 50:
                print(c("  'Need 50 gold for the high table.'", Fore.YELLOW))
                continue
            player.gold -= 50
            roll_p = random.randint(1,6)+random.randint(1,6)+random.randint(1,6)
            roll_h = random.randint(1,6)+random.randint(1,6)+random.randint(1,6)
            print(c(f"  You roll: {roll_p}.  House rolls: {roll_h}.", Fore.YELLOW))
            if roll_p > roll_h + 2:
                player.gold += 150
                print(c("  Triple. You win 150 gold.", Fore.GREEN))
            elif roll_p > roll_h:
                player.gold += 100
                print(c("  Double. You win 100 gold.", Fore.GREEN))
            elif roll_p == roll_h:
                player.gold += 50
                print(c("  Tie. Stake returned.", Fore.YELLOW))
            else:
                print(c("  House wins.", Fore.RED))

        elif ch == "Ask a gambler something":
            valid = [(req,line) for req,line in LINES
                     if req is None or req in player.flags]
            _, line = random.choice(valid)
            print(c(f"  {line}", Fore.YELLOW))


# ─── BROKEN ALTAR ─────────────────────────────────────────────────────────────
def event_broken_altar(player, room):
    wrap("An altar split clean in two by force. The halves have slid apart. "
         "Between them: a sealed cavity in the stone base.")
    done = room.get("_altar_done", set())
    while True:
        opts = []
        if "open" not in done:   opts.append("Open the cavity")
        if "seal" not in done and player.has_item("Broken Seal"):
            opts.append("Press the Broken Seal halves together on the altar")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Open the cavity":
            done.add("open")
            outcome = random.choice(["item","gold","lore","curse"])
            if outcome == "item":
                loot = random_item(); wrap(f"Inside: {loot['name']}, placed on folded cloth.", Fore.YELLOW)
                player.pick_up(loot)
            elif outcome == "gold":
                g = random.randint(15,28); player.gold += g
                wrap(f"Inside: {g} gold coins. Old, heavy, cold.", Fore.YELLOW)
            elif outcome == "lore":
                wrap("A small tablet: 'The gods were nine. Myrrakhel was the root. "
                     "Made the others in the first age. The audience was granted once. "
                     "Withdrawn once. Those two events are connected.' The rest is illegible.", Fore.CYAN)
                player.flags.add("altar_myrrakhel_hint")
            elif outcome == "curse":
                player.cursed = True
                wrap("Nothing inside. But when you reach in, a cold presses into your palm "
                     "that does not leave. [CURSED]", Fore.RED)

        elif ch == "Press the Broken Seal halves together on the altar":
            done.add("seal")
            player.remove_item("Broken Seal")
            wrap("The two halves of the seal click together on the altar surface. "
                 "The serpent-eating-the-sun emblem is complete. "
                 "A low vibration through the stone. The cavity, if not yet opened, opens itself. "
                 "On the altar surface: a key that was not there before.", Fore.YELLOW+Style.BRIGHT)
            player.flags.add("seal_restored")
            try_give_unique(player, "Warden's Key")
            if "open" not in done:
                # Also give cavity loot
                loot = random_item(); player.pick_up(loot)

        room["_altar_done"] = done


# ─── MIRROR CHAMBER ───────────────────────────────────────────────────────────
def event_mirror_chamber(player, room):
    wrap("Two surviving mirrors face each other. In the reflections: you, receding — "
         "but the thing at the far end of the reflection is the same size in every iteration. "
         "It is not you.")
    done = room.get("_mirror_done", set())
    while True:
        opts = []
        if "look" not in done:   opts.append("Look directly at what is at the end of the reflections")
        if "touch" not in done:  opts.append("Touch the mirror surface")
        if "crystal" not in done and player.has_item("Crystal Mirror"):
            opts.append("Hold up the Crystal Mirror between the two large mirrors")
        if "dawn" not in done and player.has_item("Dawn Shard"):
            opts.append("Hold the Dawn Shard up in this room")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Look directly at what is at the end of the reflections":
            done.add("look")
            wrap("Roughly humanoid. At a distance that should be hundreds of feet but is also "
                 "directly behind the glass. Looking back. After a moment it raises one hand — "
                 "then the reflection is just you again.", Fore.MAGENTA)
            player.flags.add("mirror_figure")
            if "full_truth_known" in player.flags:
                wrap("You know what that shape is. The Unmade has many reflections.", Fore.MAGENTA+Style.BRIGHT)

        elif ch == "Touch the mirror surface":
            done.add("touch")
            if random.random() < 0.5:
                wrap("Your hand passes through the cold. When you pull back, "
                     "your arm is numb to the elbow. It fades within minutes.", Fore.MAGENTA)
                player.hp -= 4; print(c(f"  -4 HP. ({player.hp}/{player.max_hp})", Fore.RED))
            else:
                wrap("Cold, solid, ordinary. The reflection mismatches your movement "
                     "for a half-second, then catches up.")

        elif ch == "Hold up the Crystal Mirror between the two large mirrors":
            done.add("crystal")
            wrap("Between three mirrors: you, then you, then the thing at the end of the "
                 "reflections — and in the Crystal Mirror's surface, the thing turns away. "
                 "It does not want to be seen in the Crystal Mirror. "
                 "When it turns, you see its back. No detail. "
                 "Just shadow, and the shape of something.", Fore.MAGENTA+Style.BRIGHT)
            player.flags.add("mirror_crystal_secret")

        elif ch == "Hold the Dawn Shard up in this room":
            done.add("dawn")
            wrap("The Dawn Shard glows — warm, orange-gold — and in the mirrors, "
                 "the thing at the far end of the reflections recoils. "
                 "Not frightened. Averse. The way some things are averse to certain lights. "
                 "It does not reappear while the shard is held.", Fore.YELLOW+Style.BRIGHT)
            player.flags.add("dawn_shard_mirror")

        room["_mirror_done"] = done


# ─── ASTRAL WELL HINT ─────────────────────────────────────────────────────────
def event_astral_well_hint(player, room):
    wrap("Stars on the ceiling — not the right stars. A different sky. "
         "The silver water in the depression does not reflect the ceiling above. "
         "It reflects stars from somewhere else entirely.")
    done = room.get("_astral_done", set())
    while True:
        opts = []
        if "touch" not in done:  opts.append("Touch the water")
        if "look" not in done:   opts.append("Look at the stars directly")
        if "hollow" not in done and player.has_item("Hollow Stone"):
            opts.append("Look through the Hollow Stone at the ceiling")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Touch the water":
            done.add("touch")
            wrap("Cool and still. Your reflection appears in stars you don't know. "
                 "Something deep below pulses once, like a heartbeat.", Fore.CYAN)
            if random.random() < 0.4:
                player.max_hp += 5; player.hp = min(player.hp+5, player.max_hp)
                print(c("  Something from depth. Max HP +5.", Fore.CYAN))
            player.flags.add("touched_astral_water")

        elif ch == "Look at the stars directly":
            done.add("look")
            wrap("They are moving — but not the way stars move. "
                 "They are moving toward a point directly above where you are standing. "
                 "Then a cloud — below ground — passes, and the stars are gone. "
                 "Ordinary stone above you.", Fore.CYAN)
            player.flags.add("studied_astral_room")
            if "read_parchment_wells" in player.flags:
                wrap("The parchment's diagram. The Astral-well label. "
                     "You are standing above something the parchment depicted as a circle.", Fore.CYAN+Style.BRIGHT)

        elif ch == "Look through the Hollow Stone at the ceiling":
            done.add("hollow")
            wrap("Through the Hollow Stone: the stars are still there — but more of them. "
                 "And they are not moving toward a point. "
                 "They are arranged around a point. "
                 "Something is at the centre of all those stars. "
                 "Something that is not a star. Something that, when you lower the stone, "
                 "is gone.", Fore.MAGENTA+Style.BRIGHT)
            player.flags.add("hollow_stone_astral")

        room["_astral_done"] = done

def event_near_mortal_ossuary(player, room):
    """The Ossuary of the Near-Mortals — Morvath and Veythari remains."""
    hr(colour=Fore.WHITE)
    print(c("  THE OSSUARY OF THE NEAR-MORTALS", Fore.WHITE + Style.BRIGHT))
    hr(colour=Fore.WHITE)
    print()
    wrap(
        "This ossuary is different from the others. "
        "The bones here are not human — longer, differently jointed, "
        "with a quality of stillness that is not just death. "
        "Some of them are wrapped in cloth that still holds faint light. "
        "Some are wrapped in cloth that holds faint dark.",
        Fore.WHITE)
    print()
    player.flags.add("found_near_mortal_ossuary")

    done = room.get("_nm_oss_done", set())
    while True:
        opts = []
        if "light" not in done: opts.append("Examine the silver-wrapped remains")
        if "dark" not in done:  opts.append("Examine the shadow-wrapped remains")
        if "relic_v" not in done and "light" in done:
            opts.append("Search carefully near the silver remains")
        if "relic_m" not in done and "dark" in done:
            opts.append("Search carefully near the shadow remains")
        if "sael" not in done and "met_sael" in player.flags and "light" in done:
            opts.append("Think about what Sael would make of this")
        if "orrath" not in done and "met_orrath" in player.flags and "dark" in done:
            opts.append("Think about what Orrath would make of this")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Examine the silver-wrapped remains":
            done.add("light")
            wrap(
                "Veythari. The proportions — the height, the way the hands were folded — "
                "are not quite human. The silver cloth holds its own faint glow "
                "even now. Someone wrapped them carefully, "
                "with more ceremony than they gave the human dead.",
                Fore.WHITE)
            player.flags.add("found_veythari_remains")

        elif ch == "Examine the shadow-wrapped remains":
            done.add("dark")
            wrap(
                "Morvath. The bones are darker than human bone — "
                "not stained, just dark, the way things are dark "
                "that have always inhabited darkness. "
                "The wrapping holds its shadow even in direct light. "
                "It does not reflect.",
                Fore.LIGHTBLUE_EX + Style.BRIGHT)
            player.flags.add("found_morvath_remains")

        elif ch == "Search carefully near the silver remains":
            done.add("relic_v")
            wrap(
                "Between two of the Veythari alcoves, "
                "set into the wall with deliberate care: "
                "a single silver-white feather. "
                "It holds light from a source that isn't present.",
                Fore.WHITE + Style.BRIGHT)
            if "obtained_veythari_feather" not in player.flags:
                ch2 = prompt(["Take the Veythari Feather", "Leave it"])
                if "Take" in ch2:
                    player.flags.add("obtained_veythari_feather")
                    player.pick_up(get_item("Veythari Feather"))

        elif ch == "Search carefully near the shadow remains":
            done.add("relic_m")
            wrap(
                "In a small hollow behind the largest Morvath alcove: "
                "something sealed in dark resin. "
                "When you open it, you find a preserved eye. "
                "Fully black. Fully Morvath.",
                Fore.LIGHTBLUE_EX + Style.BRIGHT)
            if "obtained_morvath_eye" not in player.flags:
                ch2 = prompt(["Take the Morvath Eye", "Leave it"])
                if "Take" in ch2:
                    player.flags.add("obtained_morvath_eye")
                    player.pick_up(get_item("Morvath Eye"))

        elif ch == "Think about what Sael would make of this":
            done.add("sael")
            wrap(
                "Sael is Veythari. Most of her kind are gone. "
                "These are some of the ones who went. "
                "They were placed carefully, by someone who knew what they were. "
                "Perhaps Sael herself. Perhaps Orrath.",
                Fore.WHITE + Style.BRIGHT)
            player.flags.add("near_mortal_ossuary_sael")

        elif ch == "Think about what Orrath would make of this":
            done.add("orrath")
            wrap(
                "Orrath said: 'Most of us are gone now.' "
                "These are some of the most. "
                "The shadow wrapping is Morvath craft — Orrath would know the technique. "
                "The care with which the Veythari are interred "
                "suggests the same hand placed both.",
                Fore.LIGHTBLUE_EX + Style.BRIGHT)
            player.flags.add("near_mortal_ossuary_orrath")

        room["_nm_oss_done"] = done


def event_war_room(player, room):
    """The War Room — Eldrosian military planning room."""
    hr(colour=Fore.RED)
    print(c("  THE WAR ROOM", Fore.RED + Style.BRIGHT))
    hr(colour=Fore.RED)
    print()
    wrap(
        "A large table, covered in a map of the city as it was — "
        "intact, radiating from a central keep. "
        "Markers on the map. Routes drawn in different inks. "
        "Someone was planning something. "
        "The plans were never implemented.",
        Fore.RED)
    print()
    player.flags.add("found_war_room")

    done = room.get("_war_done", set())
    while True:
        opts = []
        if "map" not in done:     opts.append("Study the city map")
        if "plans" not in done:   opts.append("Read the tactical notes")
        if "blood_door" not in done and "found_blood_door" not in player.flags:
            opts.append("Check the marked location on the east wall")
        if "supply" not in done:  opts.append("Search the supply cabinet")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Study the city map":
            done.add("map")
            wrap(
                "The map shows Eldros-Verath at its height. "
                "Nine districts radiating from the central keep. "
                "Several buildings are marked in red — "
                "the Void-well's location is one of them. "
                "Someone knew.",
                Fore.RED)
            wrap(
                "The High Keeper's quarters are marked in black. "
                "On the map, in the High Keeper's district, "
                "written in a different hand: 'WATCH THIS ONE.'",
                Fore.RED + Style.BRIGHT)
            player.flags.add("war_room_map")

        elif ch == "Read the tactical notes":
            done.add("plans")
            wrap(
                "The notes are in military shorthand. "
                "Two plans: one for external attack (never the primary concern), "
                "one for internal threat. "
                "The internal threat plan has a name at the top: "
                "CONTINGENCY MAELVYR. "
                "It was prepared. It was never activated.",
                Fore.RED + Style.BRIGHT)
            player.flags.add("war_room_contingency")
            wrap(
                "The activation order was to have been signed by the Warden-Commander. "
                "Serethan. His signature is absent.",
                Fore.RED)

        elif ch == "Check the marked location on the east wall":
            done.add("blood_door")
            wrap(
                "A marker on the map corresponds to a location in the current ruins. "
                "Red. Labelled: BLOODWELL RESEARCH — SEALED BY ORDER. "
                "The note beneath it: 'Access via blood key only. Key held by Herald.'",
                Fore.RED + Style.BRIGHT)
            player.flags.add("war_room_blood_door_hint")
            wrap(
                "You know where the Blood Door is now, and how it opens.",
                Fore.RED)

        elif ch == "Search the supply cabinet":
            done.add("supply")
            if random.random() < 0.5:
                item = random.choice([
                    get_item("Void Salt"),
                    get_item("Antidote"),
                    {"name": "Bone Shard", "type": "thrown", "value": 8,
                     "description": "A sharpened fragment of something's femur. Throws for 8 damage and bleeds. Single use.",
                     "throw_damage": 8, "throw_effect": "bleed"},
                ])
                wrap(f"  A locked cabinet, unlockable by force. Inside: {item['name']}.", Fore.GREEN)
                player.pick_up(item)
            else:
                wrap("  The cabinet is empty. Someone was here before you.", Fore.LIGHTBLUE_EX + Style.BRIGHT)

        room["_war_done"] = done


def event_chapel_of_thrys(player, room):
    """The Chapel of the Thrys — nine prayer niches, specific effects."""
    hr("═", colour=Fore.YELLOW)
    print(c("  THE CHAPEL OF THE THRYS", Fore.YELLOW + Style.BRIGHT))
    hr("═", colour=Fore.YELLOW)
    print()
    wrap(
        "A small chapel. Nine niches, each carved with a different symbol — "
        "the same symbols as the Hall of the Nine, but here they are prayer niches, "
        "not monuments. Small offerings remain in some of them. "
        "The candles in the niches are still lit. "
        "None of them have wax.",
        Fore.YELLOW)
    print()
    player.flags.add("found_chapel_thrys")

    prayed = room.get("_chapel_prayed", set())

    NICHES = {
        "Myrrakhel": ("warmth from the stone, briefly",
                      lambda p: (setattr(p, "max_hp", p.max_hp + 3),
                                 setattr(p, "hp", min(p.hp + 3, p.max_hp + 3)),
                                 p.flags.add("chapel_myrrakhel")),
                      Fore.YELLOW, "Max HP +3."),

        "Kindrael":  ("the candle in this niche burns gold",
                      lambda p: (setattr(p, "attack", p.attack + 1),
                                 p.flags.add("chapel_kindrael")),
                      Fore.YELLOW, "ATK +1."),

        "Loria":     ("the stone grows something — brief, impossible, gone",
                      lambda p: (setattr(p, "hp", min(p.max_hp, p.hp + 5)),
                                 p.flags.add("chapel_loria")),
                      Fore.GREEN, "+5 HP."),

        "Thalas":    ("a cold rush, like water",
                      lambda p: (setattr(p, "poisoned", False),
                                 p.flags.add("chapel_thalas")),
                      Fore.CYAN, "Poison cleared."),

        "Thar":      ("the stone is very heavy beneath you",
                      lambda p: (setattr(p, "defence", p.defence + 1),
                                 p.flags.add("chapel_thar")),
                      Fore.WHITE, "DEF +1."),

        "Ishak":     ("lightning nearby, briefly",
                      lambda p: (p.flags.add("chapel_ishak"),),
                      Fore.YELLOW, "Nothing. Ishak does not answer mortals easily."),

        "Ysena":     ("the shadows lean toward you",
                      lambda p: (setattr(p, "cursed", False),
                                 p.flags.add("chapel_ysena")),
                      Fore.MAGENTA, "Curse lifted."),

        "Vastino":   ("a mirror-image of yourself in the niche stone",
                      lambda p: (p.flags.add("chapel_vastino"),),
                      Fore.WHITE, "You see yourself. That is all."),

        "Kelamaris": ("the air moves",
                      lambda p: (setattr(p, "hp", max(1, p.hp - 3)),
                                 p.flags.add("chapel_kelamaris")),
                      Fore.RED, "-3 HP. Kelamaris is unpredictable."),
    }

    while True:
        unprayed = [(n, v) for n, v in NICHES.items() if n not in prayed]
        opts = [f"Pray at the niche of {name}" for name, _ in unprayed]
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        for name, (desc, effect, col, result) in NICHES.items():
            if f"Pray at the niche of {name}" == ch:
                prayed.add(name)
                wrap(f"You kneel at the niche of {name}. {desc.capitalize()}.", col)
                effect(player)
                print(c(f"  {result}", col))
                break

        room["_chapel_prayed"] = prayed


def event_observatory(player, room):
    """The Observatory — open to the sky somehow. Stars not from this world."""
    hr(colour=Fore.WHITE)
    print(c("  THE OBSERVATORY", Fore.WHITE + Style.BRIGHT))
    hr(colour=Fore.WHITE)
    print()
    wrap(
        "The ceiling is open to the sky. "
        "This should be impossible — you are underground. "
        "The sky visible through the opening is not the sky above the ruins. "
        "The stars are wrong. The constellations are not any you know. "
        "Something large is in the centre of the visible sky, "
        "and it is not the moon.",
        Fore.WHITE)
    print()
    player.flags.add("found_observatory")

    done = room.get("_obs_done", set())
    while True:
        opts = []
        if "stars" not in done:    opts.append("Study the stars")
        if "telescope" not in done:opts.append("Use the telescope")
        if "centre" not in done:   opts.append("Look at what is in the centre of the sky")
        if "hollow" not in done and player.has_item("Hollow Stone"):
            opts.append("Look through the Hollow Stone at the sky")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Study the stars":
            done.add("stars")
            wrap(
                "The constellations are different from any you know — "
                "but they are stable. They do not move. "
                "Whatever sky this is, it is a fixed sky. "
                "A sky that is not changing.",
                Fore.WHITE)
            wrap(
                "At the edge of the visible circle: "
                "a constellation that looks like a frost-covered cathedral. "
                "Vastinö's Work, reflected in a sky that should not be here.",
                Fore.WHITE + Style.BRIGHT)
            player.flags.add("observatory_stars")

        elif ch == "Use the telescope":
            done.add("telescope")
            wrap(
                "The telescope is Eldrosian-made, beautifully maintained. "
                "Through it, the stars are closer. "
                "They are not light sources. "
                "They are points of absence — "
                "places where the fabric of something is pinned.",
                Fore.WHITE + Style.BRIGHT)
            player.flags.add("observatory_telescope")

        elif ch == "Look at what is in the centre of the sky":
            done.add("centre")
            wrap(
                "You look directly at it. "
                "It is not a star. It is not a planet. "
                "It is a shape — vast, cold, patient. "
                "Looking at it, you understand that it is not in the sky. "
                "It is on the other side of the sky. "
                "The sky is a membrane.",
                Fore.WHITE + Style.BRIGHT)
            wrap(
                "You look away. "
                "The shape was not looking back. "
                "That is the only good thing about this.",
                Fore.WHITE)
            player.flags.add("observatory_centre")
            player.max_hp += 4
            print(c("  Max HP +4. You looked at something you should not have "
                    "and survived the looking.", Fore.GREEN))

        elif ch == "Look through the Hollow Stone at the sky":
            done.add("hollow")
            wrap(
                "Through the Hollow Stone, the sky shows what it actually is: "
                "a window into the space between wells. "
                "The stars are anchor points. "
                "The thing in the centre is on the other side of everything. "
                "It is not Atraxis. It is something that Atraxis fears.",
                Fore.WHITE + Style.BRIGHT)
            player.flags.add("observatory_hollow_truth")

        room["_obs_done"] = done


def event_naming_room(player, room):
    """The Naming Room — walls covered in names of the dead."""
    hr(colour=Fore.CYAN)
    print(c("  THE NAMING ROOM", Fore.CYAN + Style.BRIGHT))
    hr(colour=Fore.CYAN)
    print()
    wrap(
        "Every surface is covered in names. "
        "Not carved — grown, as though the stone was persuaded to hold them. "
        "New names appear as you watch: "
        "a name forms at the edge of your vision, settles, becomes permanent. "
        "The room is cataloguing the dead. "
        "It has been doing this since the Night of Collapse.",
        Fore.CYAN)
    print()
    player.flags.add("found_naming_room")

    done = room.get("_naming_done", set())
    while True:
        opts = []
        if "read" not in done:    opts.append("Try to read the names")
        if "add" not in done:     opts.append("Speak a name")
        if "find" not in done:    opts.append("Look for a specific name")
        if "tolos" not in done and "found_tolos_memorial" in player.flags:
            opts.append("Look for Tolos's name")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Try to read the names":
            done.add("read")
            wrap(
                "There are thousands. Hundreds of thousands. "
                "Every person who died in Eldros-Verath. "
                "Every soldier. Every citizen. "
                "The names continue past what you can read — "
                "the Wars of the Shattered Crown are here, "
                "and the names stop somewhere in the past two centuries.",
                Fore.CYAN)
            wrap(
                "The most recent names are from people who came to these ruins "
                "and did not leave. "
                "You see a name you recognise: "
                "one of the Shard-Seekers the Captain mentioned.",
                Fore.CYAN + Style.BRIGHT)
            player.flags.add("naming_room_read")

        elif ch == "Speak a name":
            done.add("add")
            wrap("Whose name do you speak?", Fore.MAGENTA)
            spoken = secret_input(player)
            if any(w in spoken for w in ("tolos", "merinain")):
                wrap(
                    "The stone considers this. "
                    "Tolos's name is not here — he is already on the plinth. "
                    "The room knows. It does not add it. "
                    "It nods, in the way stone nods.",
                    Fore.CYAN + Style.BRIGHT)
            elif any(w in spoken for w in ("maelvyr", "sathorin vale")):
                wrap(
                    "The name does not form on the wall. "
                    "The room will not catalogue him — "
                    "he is not dead. "
                    "The stone knows.",
                    Fore.RED)
            elif any(w in spoken for w in ("vaelan", "emperor")):
                wrap(
                    "Vaelan is already here. "
                    "The room shows you where: "
                    "near the top, in letters twice the size of the others. "
                    "Last of the Consolidated Age. Holder of the Godshards.",
                    Fore.CYAN + Style.BRIGHT)
            else:
                wrap(
                    "The name forms. Settles. Becomes permanent. "
                    "The room has catalogued whoever you named.",
                    Fore.CYAN)
                wrap(
                    "You are not sure what this means for them. "
                    "It feels significant.",
                    Fore.CYAN)
            player.flags.add("naming_room_spoke")

        elif ch == "Look for a specific name":
            done.add("find")
            wrap("Whose name do you search for?", Fore.MAGENTA)
            spoken = secret_input(player)
            if any(w in spoken for w in ("serethan", "warden")):
                wrap(
                    "Serethan is here. "
                    "He is also not here — the room notes him as present, "
                    "not dead. "
                    "The echo you met in the ruins registers as alive.",
                    Fore.YELLOW + Style.BRIGHT)
                player.flags.add("naming_serethan_found")
            elif any(w in spoken for w in ("talarion",)):
                wrap(
                    "Talarion is here. "
                    "His name is large — he was the last chronicler. "
                    "Beneath his name, added later, in a different texture of stone: "
                    "'He told it.'",
                    Fore.CYAN + Style.BRIGHT)
            else:
                wrap(
                    "You search. The name may be here — the room is very large. "
                    "You cannot find it in the time you have.",
                    Fore.CYAN)

        elif ch == "Look for Tolos's name":
            done.add("tolos")
            wrap(
                "You search for Tolos Merinain. "
                "His name is here. Smaller than Vaelan's. "
                "No title — his titles were stripped. Just the name.",
                Fore.CYAN + Style.BRIGHT)
            wrap(
                "Beneath it, in the smallest script the stone can manage: "
                "'He loved his friend. That is what the room remembers.'",
                Fore.CYAN + Style.BRIGHT)
            player.flags.add("naming_tolos_found")

        room["_naming_done"] = done


def event_archive_of_agreements(player, room):
    """The Archive of Agreements — all formal agreements of Eldros, including the final one."""
    hr("═", colour=Fore.MAGENTA)
    print(c("  THE ARCHIVE OF AGREEMENTS", Fore.MAGENTA + Style.BRIGHT))
    hr("═", colour=Fore.MAGENTA)
    print()
    wrap(
        "Shelves of bound volumes, each recording a formal agreement "
        "made in the name of the Empire of Eldros. "
        "Trade deals. Military pacts. Diplomatic arrangements. "
        "A thousand years of empire in paper and ink.",
        Fore.MAGENTA)
    print()
    player.flags.add("found_archive_agreements")

    done = room.get("_archive_done", set())
    while True:
        opts = []
        if "browse" not in done:   opts.append("Browse the archive")
        if "final" not in done:    opts.append("Find the final entry")
        if "terms" not in done and "final" in done:
            opts.append("Read the terms of the Agreement")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Browse the archive":
            done.add("browse")
            wrap(
                "The archive is meticulously organised. "
                "Trade agreements with seven different peoples. "
                "Military alliances that lasted decades. "
                "One interesting entry: an agreement with 'the near-mortal peoples' — "
                "Morvath and Veythari — that grants them certain protections "
                "within Eldros-Verath. "
                "Signed by Emperor Vaelan. "
                "One of his last acts.",
                Fore.MAGENTA)
            player.flags.add("archive_vaelan_agreement")

        elif ch == "Find the final entry":
            done.add("final")
            wrap(
                "The final entry is at the end of the last volume. "
                "It is not formatted like the others. "
                "The others are formal, legalistic, in precise Eldrosian. "
                "This one is in a personal hand.",
                Fore.MAGENTA + Style.BRIGHT)
            wrap(
                "It reads: 'I, Maelvyr, called High Keeper of the Rites, "
                "do enter into the following Agreement — '",
                Fore.MAGENTA + Style.BRIGHT)

        elif ch == "Read the terms of the Agreement":
            done.add("terms")
            pause()
            wrap(
                "The terms are written in a hand that is half-Maelvyr, half-something else. "
                "The handwriting changes midway through the document.",
                Fore.MAGENTA)
            wrap(
                "First party: Maelvyr, High Keeper of the Rites, subject of the Empire of Eldros.",
                Fore.MAGENTA + Style.BRIGHT)
            wrap(
                "Second party: unnamed. Described only as 'that which has always been present.'",
                Fore.MAGENTA + Style.BRIGHT)
            wrap(
                "Terms, as recorded: "
                "'In exchange for his mortal limitation — "
                "his death, his ending, his smallness — "
                "the first party will be remade. '",
                Fore.MAGENTA + Style.BRIGHT)
            wrap(
                "'The second party will provide: transformation. "
                "The first party will provide: presence. '",
                Fore.MAGENTA + Style.BRIGHT)
            wrap(
                "'This Agreement is binding and irrevocable. '",
                Fore.MAGENTA + Style.BRIGHT)
            wrap(
                "The final line is in the second handwriting entirely: "
                "'WITNESSED AND AGREED.'",
                Fore.RED + Style.BRIGHT)
            player.flags.add("read_agreement_terms")
            if "full_truth_known" in player.flags:
                wrap(
                    "You know exactly what this is. "
                    "The formal record of the thing that ended the empire. "
                    "Filed in its own archive. "
                    "Maelvyr filed it. Whatever he was becoming made him file it.",
                    Fore.MAGENTA + Style.BRIGHT)

        room["_archive_done"] = done


def event_atraxis_scar(player, room):
    """The Atraxis Scar — where the Void physically breached the stone."""
    hr("═", colour=Fore.RED)
    print(c("  THE ATRAXIS SCAR", Fore.RED + Style.BRIGHT))
    hr("═", colour=Fore.RED)
    print()
    wrap(
        "The floor here is wrong. "
        "Not cracked — wrong. "
        "The stone is a different colour than it should be: "
        "a deep red-black at the centre of the room that bleeds outward "
        "in a pattern that is not any natural fracture. "
        "It is a scar. Something came through here.",
        Fore.RED + Style.BRIGHT)
    print()
    pause()
    wrap(
        "The air is different. Not colder. Not warmer. "
        "Present in a way that air is not usually present. "
        "As though the space itself is aware.",
        Fore.RED)
    print()
    player.flags.add("found_atraxis_scar")

    done = room.get("_scar_done", set())
    while True:
        opts = []
        if "examine" not in done:  opts.append("Examine the Scar")
        if "stand" not in done:    opts.append("Stand at the centre of the Scar")
        if "speak" not in done:    opts.append("Speak into the Scar")
        if "candle" not in done and player.has_item("Candle"):
            opts.append("Hold the Candle over the Scar")
        if "hollow" not in done and player.has_item("Hollow Stone"):
            opts.append("Look through the Hollow Stone at the Scar")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Examine the Scar":
            done.add("examine")
            wrap(
                "The red-black colouration is not superficial — "
                "it goes into the stone as far as you can see. "
                "The pattern is not random. "
                "It radiates from a single central point "
                "in perfect circles, "
                "like a stone dropped into water.",
                Fore.RED)
            wrap(
                "At the exact centre: a point of absolute black. "
                "Not darkness. "
                "The absence of material. "
                "A hole the size of a finger. "
                "Something very small came through here first, "
                "and then something much larger.",
                Fore.RED + Style.BRIGHT)

        elif ch == "Stand at the centre of the Scar":
            done.add("stand")
            wrap(
                "You stand at the centre. "
                "The presence in the air is stronger here. "
                "It does not press against you — "
                "it simply is, the way a significant thing is, "
                "the way a place where something terrible happened "
                "holds the terrible thing in its structure.",
                Fore.RED)
            if "full_truth_known" in player.flags:
                wrap(
                    "You know what happened here. "
                    "This is where the Void came through. "
                    "This is where Maelvyr's Agreement became physical. "
                    "The stone around you is the scar of that moment.",
                    Fore.RED + Style.BRIGHT)
                player.flags.add("scar_understood")
                player.max_hp += 5
                print(c("  Max HP +5. Understanding costs something. "
                        "It also gives something.", Fore.GREEN))
            else:
                wrap(
                    "You feel the weight of something that happened here. "
                    "You do not know its name.",
                    Fore.RED)

        elif ch == "Speak into the Scar":
            done.add("speak")
            wrap("The Scar is listening.", Fore.RED)
            spoken = secret_input(player)
            if any(w in spoken for w in ("atraxis",)):
                wrap(
                    "The hole at the centre widens by a fraction. "
                    "Then closes. "
                    "The name has partial power here — "
                    "more power than anywhere else in the ruins. "
                    "Something beneath the stone recognises it.",
                    Fore.RED + Style.BRIGHT)
                player.flags.add("scar_atraxis_spoken")
            elif any(w in spoken for w in ("maelvyr",)):
                wrap(
                    "The scar radiates — briefly — "
                    "with the same pattern, brighter. "
                    "As if remembering who opened it.",
                    Fore.RED + Style.BRIGHT)
                player.flags.add("scar_maelvyr_spoken")
            elif any(w in spoken for w in ("myrrakhel", "deepest pulse")):
                wrap(
                    "The presence in the air shifts — "
                    "not retreating. Orienting. "
                    "The name draws attention from somewhere else.",
                    Fore.YELLOW + Style.BRIGHT)
                player.flags.add("scar_myrrakhel_spoken")
            else:
                wrap(
                    "Your voice falls into the Scar. "
                    "The Scar holds it for a moment. "
                    "Then releases it.",
                    Fore.RED)

        elif ch == "Hold the Candle over the Scar":
            done.add("candle")
            wrap(
                "The candle does not change colour — "
                "it simply goes out. "
                "In the darkness: the Scar is visible without light. "
                "It generates its own not-light. "
                "The pattern is clearer in the dark.",
                Fore.RED + Style.BRIGHT)
            player.flags.add("scar_candle")
            # Relight the candle
            wrap("The candle relights when you move away. It would not stay lit here.", Fore.YELLOW)

        elif ch == "Look through the Hollow Stone at the Scar":
            done.add("hollow")
            wrap(
                "Through the Hollow Stone, the Scar is a window. "
                "Not into the Void — into the moment of the Agreement. "
                "You see it happening: a figure, robed, in a circle. "
                "Something vast pressing through from the other side. "
                "The stone accepting the pressure. "
                "The figure accepting everything else.",
                Fore.RED + Style.BRIGHT)
            player.flags.add("scar_hollow_truth")

        room["_scar_done"] = done


def event_poison_garden(player, room):
    """The Poison Garden — plants that shouldn't be underground."""
    hr(colour=Fore.GREEN)
    wrap("The air smells wrong in a way that is almost pleasant.", Fore.GREEN)
    print()
    wrap(
        "Plants. Underground. "
        "Not the kind that grow from water seeping through cracks — "
        "these were planted deliberately, in rows, tended. "
        "They glow faintly. They should not glow. "
        "Several of them are clearly toxic.",
        Fore.GREEN)
    print()
    player.flags.add("found_poison_garden")

    done = room.get("_garden_done", set())
    while True:
        opts = []
        if "examine" not in done:  opts.append("Examine the plants")
        if "harvest" not in done:  opts.append("Carefully harvest something")
        if "move" not in done:     opts.append("Move through carefully")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Examine the plants":
            done.add("examine")
            PLANTS = [
                "Void-Root: black, grows toward the well. Highly toxic. Used in cultist rituals.",
                "Goldcap Mushroom: orange-gold, warm. Non-toxic. Used in healing by the Remnant Scholars.",
                "Shadow Moss: grey-black, cold. Mildly toxic. Absorbs light rather than reflecting it.",
                "Ember Flower: red, hot to the touch. Not toxic but causes burns. Used in the Ember Flask.",
                "Pale Bell: white, bell-shaped. Purifies poison when prepared correctly.",
            ]
            for p in PLANTS:
                wrap(f"  — {p}", Fore.GREEN)
            player.flags.add("garden_examined")

        elif ch == "Carefully harvest something":
            done.add("harvest")
            if "garden_examined" in player.flags:
                ch2 = prompt([
                    "Harvest Goldcap Mushroom (healing)",
                    "Harvest Pale Bell (antidote)",
                    "Harvest Ember Flower (combat material)",
                    "Leave"
                ])
                if "Goldcap" in ch2:
                    player.pick_up(get_item("Dried Cave Mushroom") or
                                   {"name":"Dried Cave Mushroom","type":"food","value":3,
                                    "description":"Bitter but safe. Restores 3 HP.",
                                    "food_effect":{"hp":3}})
                elif "Pale Bell" in ch2:
                    player.pick_up(get_item("Antidote"))
                elif "Ember Flower" in ch2:
                    player.pick_up(get_item("Ember Flask") or get_item("Ember Vial") or
                                   {"name":"Ember Vial","type":"thrown","value":18,
                                    "description":"A sealed vial of captured flame. 18 fire damage. Single use.",
                                    "throw_damage":18,"throw_effect":None})
            else:
                wrap("You grab something without knowing what it is.", Fore.RED)
                if random.random() < 0.6:
                    player.poisoned = True
                    wrap("POISONED.", Fore.RED)
                else:
                    player.pick_up(get_item("Antidote"))
                    wrap("Lucky. It was the pale bell.", Fore.GREEN)

        elif ch == "Move through carefully":
            done.add("move")
            if random.random() < 0.3:
                player.poisoned = True
                wrap(
                    "Despite your care, something brushes your hand. "
                    "The poison is fast. [POISONED]",
                    Fore.RED)
            else:
                wrap(
                    "You move carefully and emerge on the other side unharmed.",
                    Fore.GREEN)

        room["_garden_done"] = done



# ─── HOLLOW STONE ROOM (special room for Hollow Stone use) ────────────────────
def event_hollow_stone_room(player, room):
    wrap("A room with a sealed wall — perfectly flat, no seams, no mortar. "
         "In the centre of the wall: a circular indentation exactly the size of a hand.")
    done = room.get("_hollow_done", set())
    while True:
        opts = []
        if "press" not in done:  opts.append("Press your hand into the indentation")
        if "stone" not in done and player.has_item("Hollow Stone"):
            opts.append("Place the Hollow Stone in the indentation")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Press your hand into the indentation":
            done.add("press")
            wrap("Your hand fits. The stone is cold. Nothing happens, except: "
                 "beyond the wall, faintly, you hear something move.")

        elif ch == "Place the Hollow Stone in the indentation":
            done.add("stone")
            wrap("The stone fits perfectly — the hole aligns with something on the other side. "
                 "A click. The wall section shifts inward.", Fore.YELLOW+Style.BRIGHT)
            player.remove_item("Hollow Stone")  # consumed
            player.flags.add("hollow_stone_door")
            wrap("Beyond: a small chamber. Shelves. On one shelf: "
                 "a Rolled Parchment and a Godshard Fragment. "
                 "On the wall, carved: 'Vaethar's gift was not a sacrifice. It was an investment. '",
                 Fore.YELLOW)
            wrap("'The Godshards do not diminish the one who holds them. '", Fore.YELLOW)
            wrap("'They remember what Vaethar chose to become.'", Fore.YELLOW)
            player.pick_up(pick_parchment_variant(player))
            try_give_unique(player, "Godshard Fragment")
            player.flags.add("vaethar_inscription")

        room["_hollow_done"] = done


# ─── DEEPER STAIRCASE (only on 2nd+ descent) ─────────────────────────────────
def event_deeper_staircase(player, room):
    hr("═",colour=Fore.MAGENTA)
    wrap("A staircase. Not the one you came in on — different stone, different direction, "
         "and descending at a much steeper angle than anything you have navigated before. "
         "The air coming up from it is colder than the rest of the ruins.", Fore.MAGENTA)
    hr("═",colour=Fore.MAGENTA)
    ch = prompt(["Descend the staircase","Leave it"])
    if ch == "Descend the staircase":
        wrap("You descend. For a long time. Much longer than you expected. "
             "The staircase goes deeper than the ruins logically should. "
             "When it ends, you are somewhere much further down.", Fore.MAGENTA)
        player.depth = max(player.depth, 18)  # jump to deep content
        player.flags.add("took_deeper_staircase")
        print(c("  You are now in the deep ruins. Depth advanced significantly.", Fore.MAGENTA+Style.BRIGHT))
    else:
        wrap("You leave it alone. It continues downward regardless.")


# ─── ATMOSPHERIC EVENTS ───────────────────────────────────────────────────────
def event_flooded_room(player, room):
    wrap("The water is cold enough to ache. An object glints on the true floor.")
    if "flooded_searched" in room:
        wrap("You have already searched the water.", Fore.LIGHTBLUE_EX+Style.BRIGHT); return
    room["flooded_searched"] = True
    if prompt(["Wade in and retrieve it","Leave it"]) == "Wade in and retrieve it":
        if random.random() < 0.65:
            loot = random_item()
            print(c(f"  Numbingly cold. You retrieve: {loot['name']}.", Fore.GREEN))
            player.pick_up(loot)
        else:
            dmg = random.randint(4,10); player.hp -= dmg
            loot = random_item(); player.pick_up(loot)
            print(c(f"  Something cuts you. {loot['name']} retrieved. -{dmg} HP.", Fore.RED))

def event_listening_room(player, room):
    wrap("The walls record voices. One fragment resolves if you stand still long enough:")
    FRAGS = [
        "'...the agreement was not theirs to make...'",
        "'...nine and one and none...'",
        "'...the gods did not leave. They were pushed...'",
        "'...do not speak the name near the well...'",
        "'...it was always here. even before the wells...'",
        "'...Eldros-Verath stood for a thousand years and fell in one night...'",
        "'...Vaelan held all the shards. that was not supposed to happen...'",
        "'...Vaethar gave the choice. Vaelan did not choose to give it back...'",
    ]
    print(c(f"  {random.choice(FRAGS)}", Fore.CYAN))
    player.flags.add("heard_listening_room")

def event_sealed_window(player, room):
    wrap("You press your eye to the crack. On the other side: a corridor, perfectly intact, "
         "lit by a blue-white light. Empty. At the far end: a door with a shape you recognise — "
         "one of the nine circles from the parchment, if you have found it. "
         "Then the light dims.")
    player.flags.add("saw_sealed_window")

def event_empty_throne(player, room):
    """
    The lesser throne room. Contains the Old Crown.
    (The real throne room — Vaelan's — is event_throne_room.)
    """
    wrap(
        "A throne room, grand in ruin. The throne is intact — black stone, high-backed, "
        "serpents eating each other's tails carved on the arms. "
        "On the throne's headrest: a crown, sitting as though someone placed it there "
        "and meant to return for it. "
        "Something about the throne itself resists you. "
        "A great closed door stands sealed behind the throne."
    )
    done = room.get("_throne_small_done", set())

    while True:
        opts = []
        if "crown" not in done and "obtained_old_crown" not in player.flags:
            opts.append("Take the crown from the throne")
        elif "crown_examined" not in done:
            opts.append("Examine the crown on the throne")
        if "sit" not in done:   opts.append("Sit on the throne")
        if "door" not in done:  opts.append("Examine the sealed door")
        if "carve" not in done: opts.append("Read the serpent carvings on the throne arms")
        if (player.has_item("Old Crown") and "crown_placed_back" not in done
                and "vaelan" not in done):
            opts.append("Replace the crown and leave")
        opts.append("Leave")
        ch = prompt(opts)
        if ch == "Leave": break

        if ch == "Take the crown from the throne":
            done.add("crown")
            try_give_unique(player, "Old Crown")
            wrap(
                "The crown is heavier than it looks. "
                "The metal is unlike anything you know — not iron, not gold, "
                "not any alloy you can name. "
                "It is warm to the touch, and when you lift it from the throne "
                "the room is very slightly darker than it was.",
                Fore.YELLOW)
            wrap(
                "This crown predates Vaelan. Predates, perhaps, the empire itself. "
                "Whatever it was made for, it was made for something larger than you.",
                Fore.YELLOW)

        elif ch == "Examine the crown on the throne":
            done.add("crown_examined")
            wrap(
                "The crown rests where it was placed. "
                "It is already yours — you carry it. "
                "This throne held one like it, once.",
                Fore.LIGHTBLUE_EX + Style.BRIGHT)

        elif ch == "Sit on the throne":
            done.add("sit")
            out = random.choice(["vision", "curse", "nothing", "buff"])
            if out == "vision":
                wrap(
                    "The room changes — alive, full, before. "
                    "Someone occupied this throne. The crown was on their head, not on the headrest. "
                    "They were larger than you. They were afraid of something. "
                    "Then ruin again.",
                    Fore.CYAN)
                player.flags.add("throne_vision")
            elif out == "curse":
                player.cursed = True
                wrap("The cold of the stone comes through your clothing. [CURSED]", Fore.RED)
            elif out == "nothing":
                wrap(
                    "You sit in a lesser throne of the first empire. "
                    "Nothing happens. The standing-up feels like the important part.",
                )
            elif out == "buff":
                player.max_hp += 5; player.hp = min(player.hp + 5, player.max_hp)
                wrap(
                    "Something about sitting here, knowing what you know, settles you. "
                    "Max HP +5.",
                    Fore.GREEN)

        elif ch == "Examine the sealed door":
            done.add("door")
            wrap(
                "Barred from this side. You lift the bars. "
                "Beyond: a corridor, collapsed at the far end. "
                "On the floor of the corridor, just within reach: a Rolled Parchment.",
            )
            pick_parchment_variant(player)

        elif ch == "Read the serpent carvings on the throne arms":
            done.add("carve")
            wrap(
                "The serpents are eating each other's tails — not their own. "
                "A circle of two, not one. "
                "Whatever the distinction means, it was important enough to carve into the throne. "
                "At the Shrine of Eon, the serpent eats its own tail. "
                "Here: two serpents, completing each other.",
                Fore.CYAN)
            player.flags.add("throne_carvings")
            if "found_mural" in player.flags:
                wrap(
                    "The mural showed a dragon coiled around the world — protectively. "
                    "The shrine shows a single loop. "
                    "This throne shows two serpents completing each other. "
                    "Someone was thinking very carefully about what kind of circle to carve.",
                    Fore.CYAN + Style.BRIGHT)

        elif ch == "Replace the crown and leave":
            done.add("crown_placed_back")
            wrap(
                "You set the crown back on the headrest. "
                "The room is very slightly brighter than it was when you took it. "
                "You carry a copy of the knowledge that it belongs here — "
                "and that it belongs equally in the throne room below.",
                Fore.YELLOW)

        room["_throne_small_done"] = done
