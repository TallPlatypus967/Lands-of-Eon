
# ─── LORE JOURNAL ─────────────────────────────────────────────────────────────
ALL_FLAGS = [
    "found_mural","found_ysena","read_ashen_tablet","read_charred_ledger","read_parchment_wells",
    "read_imperial_edict","read_priests_journal","found_library_collapse","found_blank_book",
    "found_histories","found_wells_book","found_thrys_survey","found_near_mortal_book",
    "found_vaethar_book","found_audience_protocols","found_demongod_etymology",
    "spoke_maelvyr_shrine","spoke_atheron_shrine","spoke_myrrakhel_shrine","spoke_vaelan_shrine",
    "spoke_vaethar_shrine","spoke_ysena_shrine","met_sael","sael_spoke_maelvyr","sael_myrrakhel",
    "sael_told_wells","sael_told_vaelan","sael_vaethar","sael_dravennis_connection",
    "met_orrath","orrath_maelvyr","orrath_myrrakhel","orrath_told_vaelan","orrath_vaethar","orrath_dravennis",
    "found_vault_door","found_sealed_sanctum","sanctum_vaelan_detail","full_truth_known",
    "found_veythari_archive","looked_void_well","void_well_witnessed","void_well_myrrakhel",
    "void_well_vaelan","void_well_vaethar","shard_returned","spoke_unmade","godshard_offered_well",
    "vaethar_tear_well","dawn_shard_offered_well","hollow_stone_well",
    "studied_atheron","atheron_woke_and_spared","atheron_named","atheron_ysena_named","atheron_vaethar_named",
    "scale_returned_atheron","vaethar_tear_atheron","ysena_handprint",
    "candle_mural_secret","inscription_variation","inscription_unmade","inscription_myrrakhel",
    "inscription_vaelan","inscription_vaethar","candle_inscription_secret","mirror_inscription_secret",
    "warden_seal_inscription","mirror_mural_secret",
    "found_blood_door","heard_dravennis","prisoner_dravennis","orrath_dravennis",
    "found_wardens_archive","found_throne_room","throne_full_context","took_godshard_from_vaelan",
    "crown_returned_throne","mirror_throne_room","hollow_stone_vaelan",
    "seal_restored","vaethar_inscription","hollow_stone_door","hollow_stone_astral",
    "dawn_shard_mirror","mirror_crystal_secret","mirror_figure",
    "ossuary_name","ossuary_secret_passage","altar_myrrakhel_hint",
    "heard_listening_room","saw_sealed_window","touched_astral_water","studied_astral_room",
    "prisoner_told_eldros","prisoner_told_well","prisoner_told_gods","prisoner_told_vaelan","prisoner_dravennis",
    "merchant_told_wells","merchant_myrrakhel","merchant_godshards",
    "dawn_shard_offered","godshard_offered_shrine","vaethar_tear_offered","old_crown_shrine","scale_shrine_blessed",
    "spoke_maelvyr_shrine","void_pointed","throne_vision","throne_carvings",
    "took_deeper_staircase","found_chamber_of_agreement", "stood_in_circle", "agreement_stone_circle", "agreement_chamber_inscription",
    "candle_agreement_chamber", "knows_ritual_phrase", "decoded_codex", "ritual_summmoned_confrontation",
    "refused_the_offer", "confrontation_done", "unmade_spoke_its_nature", "unmade_spoke_maelvyr", "knows_agreement_stone_use",
    "ritual_failed_once", "found_hall_of_nine", "nine_completed", "kindrael_alcove", "loria_alcove",
    "thalas_alcove", "thar_alcove", "ishak_alcove", "ysena_alcove", "vastino_alcove",
    "kelamaris_alcove", "myrrakhel_alcove", "candle_hall_of_nine", "dawn_shard_nine",
    "found_shattered_crown_hall", "read_shattered_crown_mural", "found_tolos_memorial",
    "candle_crown_hall", "found_third_godshard",
    "found_veythari_sanctuary", "sanctuary_pool_vision", "sanctuary_sael_tree",
    "arukiel_memory", "sanctuary_mirror_figure",
    "mirror_room_vision", "studied_reflection_walls", "mirror_scholar_vision",
    "sat_in_dawn_light", "talarion_room_found", "found_tolos_plinth",
    "read_talarion_chronicle", "read_scholar_notes", "read_shard_map", "read_wars_record",
    "atraxis_named", "atraxis_well", "heard_dissonance",
    "scholar_gave_info", "scholar_told_locations", "seeker_exchanged",
    "fought_cultist", "hollow_stone_door","found_recovery_room", "recovery_door_found",
    "found_cartographers_station", "read_cartographer_maps", "has_compass",
    "atraxis_well", "heard_dissonance","read_serethan_note", "read_wars_summary", "read_myrrakhel_fragment",
    "read_thaun_account", "read_eldros_founding", "read_atraxis_description", "read_tolos_account", "read_nine_gods_list",
    "read_maelvyr_survival", "found_forge", "forge_dust_found","met_named","met_shepherd", "met_witness",
    "killed_flesh_architect", "killed_void_priest","equipped_morvath_eye","equipped_veythari_feather",

    # NPC encounter flags
    "met_archivist", "met_bound_one", "met_serethan", "met_seeker_captain",
    "found_deep_sleeper", "deep_sleeper_answered", "deep_sleeper_approached",
    "talarion_echo_active", "talarion_echo_spoken", "talarion_full_account",
    # Archivist progress
    "archivist_factions", "archivist_history", "archivist_void_touched",
    "archivist_godshards", "archivist_atraxis", "archivist_ritual_site",
    # Bound One progress
    "bound_one_explained", "bound_one_atraxis", "bound_one_ritual",
    "bound_one_helped", "bound_one_passage", "bound_one_guided",
    "bound_one_name_spoken",
    # Serethan
    "serethan_bell", "serethan_collapse", "serethan_vaelan",
    "serethan_choice", "serethan_truth_told",
    # Captain
    "captain_employer", "captain_status", "captain_allied",
    "sold_godshard_captain", "betrayed_seekers",
    # Deep Sleeper answers
    "sleeper_atraxis_answer", "sleeper_well_answer", "sleeper_shards_answer",
    "sleeper_myrrakhel_answer", "sleeper_self_answer", "sleeper_custom_answer",
    # New room discoveries
    "found_near_mortal_ossuary", "found_veythari_remains", "found_morvath_remains",
    "found_war_room", "war_room_map", "war_room_contingency", "war_room_blood_door_hint",
    "found_chapel_thrys", "found_observatory", "observatory_stars",
    "observatory_telescope", "observatory_centre", "observatory_hollow_truth",
    "found_naming_room", "naming_room_read", "naming_room_spoke",
    "naming_serethan_found", "naming_tolos_found",
    "found_archive_agreements", "archive_vaelan_agreement", "read_agreement_terms",
    "found_atraxis_scar", "scar_understood", "scar_atraxis_spoken",
    "scar_maelvyr_spoken", "scar_myrrakhel_spoken", "scar_candle", "scar_hollow_truth",
    "found_poison_garden", "garden_examined",
    # Book lore flags
    "read_warden_log", "read_void_touched_guide", "read_vaelan_journal", "read_named_grimoire",
    # Spoken word expansion
    "inscription_atraxis", "inscription_thalas", "inscription_kindrael",
    "void_well_thalas", "void_well_kindrael", "void_well_serethan",
    # Reputation actions
    "obtained_veythari_feather", "obtained_morvath_eye",
    "near_mortal_ossuary_sael", "near_mortal_ossuary_orrath",
    "chapel_myrrakhel", "chapel_kindrael", "chapel_loria", "chapel_thalas",
    "chapel_thar", "chapel_ishak", "chapel_ysena", "chapel_vastino", "chapel_kelamaris",
]

DISCOVERY_TEXT = {
    "found_mural":             "You found the Hall of the Mural: Thaun rising from the Void-well, Arukiel falling, Atheron coiled around the world — and a fourth figure facing something painted over.",
    "found_ysena":             "The mural's central panel showed Ysena, Weaver of Shadows — one of the nine gods — standing beside Atheron. She was his spouse.",
    "read_ashen_tablet":       "An Ashen Tablet described the Night of Collapse — a priest who visited the Gods and did not return the same.",
    "read_charred_ledger":     "A Charred Ledger: hundreds of crossed-out names. Final line: 'The agreement was not with the Gods. It was with what stands behind them.'",
    "read_parchment_wells":    "A Rolled Parchment showed a diagram of nine circles — the nine wells — four labelled: BLOOD, ASTRAL, HOLLOW, DAWN. A tenth, larger, filled black at the centre.",
    "read_imperial_edict":     "An Imperial Edict, signed by Emperor Vaelan, sealed the High Keeper's records three days before the Night of Collapse.",
    "read_priests_journal":    "A Priest's Journal: careful scholarship, then a second darker ink mid-entry. Final line: 'If they knew what I was going to — ' The entry ends.",
    "found_library_collapse":  "A library book described the Night of Collapse — one person, unnamed, responsible.",
    "found_blank_book":        "A sealed blank book held one page: a firsthand account of the betrayer — M___VYR — who came back from the Gods as something else.",
    "spoke_maelvyr_shrine":    "At a shrine you spoke a name. The candles died. DEMONGOD appeared in the ash.",
    "spoke_atheron_shrine":    "You named Atheron at the shrine. The flame turned gold. Something acknowledged you.",
    "spoke_myrrakhel_shrine":  "You named Myrrakhel at the shrine. Every candle burned brighter and colder simultaneously.",
    "spoke_vaelan_shrine":     "You named Vaelan at the shrine. The flame turned crimson. A sound like a distant echo of something that happened here.",
    "spoke_vaethar_shrine":    "You named Vaethar at the shrine. Gold warmth — sustaining rather than sudden. The ash formed wings briefly.",
    "spoke_ysena_shrine":      "You named Ysena at the shrine. The candles went blue-grey. A warmth in the shadows, briefly, then gone.",
    "met_sael":                "You met Sael — a Veythari, near-mortal of the starlight.",
    "sael_spoke_maelvyr":      "Sael named the betrayer: Maelvyr, a High Keeper who made an agreement with the Unmade. The empire fell the same night. DEMONGOD.",
    "sael_myrrakhel":          "Sael named all nine gods: Myrrakhel and the Thrys. She said Myrrakhel may not be what Myrrakhel was.",
    "sael_told_wells":         "Sael described the wells and their products: from the Dawnwell came Auridan, first human; from the Bloodwell came Mograx, first Orkyn.",
    "sael_told_vaelan":        "Sael confirmed Emperor Vaelan held all the Godshards — fragments of Vaethar — and died on his throne, stormed.",
    "sael_vaethar":            "Sael described Vaethar: Atheron's chosen child, who fragmented their form into the Godshards to empower the imperial line.",
    "sael_dravennis_connection":"Sael drew the line: Maelvyr, the Demongod, is also Dravennis — he who drinks the blood of magi.",
    "met_orrath":              "You met Orrath — a Morvath, near-mortal of the darkness, from the Hollow-well.",
    "orrath_maelvyr":          "Orrath confirmed Maelvyr is active, elsewhere, building something. He is very hungry.",
    "orrath_told_vaelan":      "Orrath was nearby on the Night of Collapse. The one who killed Vaelan had already agreed to become something else.",
    "orrath_vaethar":          "Orrath met Vaethar before the fragmentation. 'What they chose was not a sacrifice. It was a decision.'",
    "orrath_dravennis":        "Orrath named Dravennis: the man made into a Demongod at Eldros, who left, and has been building something, elsewhere, for a very long time.",
    "found_vault_door":        "An Iron Key opened a vault: 'Look for what was agreed with in the dark. The name is secondary.' Beneath: UNMADE.",
    "found_sealed_sanctum":    "The sealed sanctum held the full account: Maelvyr, High Keeper, made an agreement with the Unmade. He stormed the capital. He killed Emperor Vaelan on his throne. He became a Demongod.",
    "found_veythari_archive":  "A Veythari archive: the Unmade predates the wells. At Eldros it succeeded — briefly — through one man who opened the door.",
    "looked_void_well":        "You looked into the Void-well. Something looked back. Vast, old, not Atheron.",
    "void_well_witnessed":     "You spoke Maelvyr's name into the Void-well. WITNESSED was pressed into the rim from below.",
    "void_well_vaelan":        "You named Vaelan at the well. A sound from deep below — like something heavy settling, finally, to rest.",
    "studied_atheron":         "You studied the sleeping dragon: ATH___N, the King of Dragons.",
    "atheron_woke_and_spared": "Atheron woke. You stood still. It let you leave.",
    "atheron_named":           "You named Atheron to his face. He acknowledged it.",
    "atheron_ysena_named":     "You named Ysena to Atheron. Both his eyes opened. The sound was not a roar. Memory.",
    "found_throne_room":       "You found the Throne of Eldros-Verath — not ruined, but arrested. Emperor Vaelan still sits in his throne, still holding a Godshard.",
    "throne_full_context":     "You stood in the throne room knowing everything: who killed Vaelan, what Maelvyr became, what the Godshards are.",
    "took_godshard_from_vaelan":"You took the Godshard from Vaelan's hand. His armour settled. Something that had been holding it upright was released.",
    "crown_returned_throne":   "You returned the Old Crown to the throne room. The Godshard pulsed once in acknowledgement. ATK +2, Max HP +10.",
    "found_blood_door":        "The Blood Door contained research on the Bloodwell — a hunger that outlasts the body that carries it. 'We should have stopped sooner.'",
    "sael_dravennis_connection":"Sael drew the line between Maelvyr and Dravennis explicitly.",
    "orrath_dravennis":        "Orrath described Dravennis as Maelvyr, building something, elsewhere, for a very long time. Very hungry.",
    "heard_dravennis":         "The merchant warned you: the name Dravennis carries differently in the deep rooms.",
    "prisoner_told_vaelan":    "The prisoner told you about Vaelan — he held the Godshards and died on his throne.",
    "ossuary_name":            "In the ossuary, one alcove had a name chiselled through above it: M — something — L. Then a gap. Then R.",
    "inscription_variation":   "One iteration of the inscription room's loop changed: 'M___VYR UNMADE THE AGREEMENT.'",
    "found_wardens_archive":   "The Warden's Archive recorded the final entry: the Warden's office lodged a formal objection to the High Keeper's audience request. It was overruled.",
    "vaethar_inscription":     "Hidden behind a Hollow Stone wall: 'Vaethar's gift was not a sacrifice. It was an investment. The Godshards remember what Vaethar chose to become.'",
    "mirror_throne_room":      "In the Crystal Mirror in the throne room: Vaelan on his throne, a robed figure before him — and behind that figure, the Unmade's shadow falling over everything.",
    "ysena_handprint":         "On Atheron's flank: a handprint, small, pressed deliberately. Ysena's. Even here, her mark remains.",
    "found_thrys_survey":      "A theological survey named all nine gods: Myrrakhel and the eight Thrys — Kindrael, Loría, Thalás, Thar, Ishak, Ysena, Vastinö, Kelamaris.",
    "found_vaethar_book":      "A book on Vaethar confirmed: Vaelan was the first and last emperor to hold all godshards simultaneously. The theological implications were being debated when the Night of Collapse rendered them moot.",
    "found_audience_protocols":"The Audience Protocols recorded the final audience as unusual — requested by the High Keeper himself, approved by Vaelan with noted reluctance. The High Keeper's name is blank.",
    "found_demongod_etymology": "An etymological study of DEMONGOD: coined after the Night of Collapse by survivors. 'The scholars noted: this word is still not enough.'",
    "found_chamber_of_agreement":
        "You found the Chamber of the Agreement — the room where Maelvyr met the Unmade. "
        "Two sets of footprints are pressed into the stone. One human. One not.",
    "stood_in_circle":
        "You stood in the circle where the Agreement was made. "
        "For a moment you understood what it felt like to say yes.",
    "agreement_chamber_inscription":
        "The Chamber of the Agreement's walls read: 'The Unmade requires a willing door. "
        "It cannot force entry. It can only wait.'",
    "decoded_codex":
        "Using the Crystal Mirror, you decoded the Codex of the First Age. "
        "The ritual phrase: name Vaethar, name Atheron as witness, "
        "and claim: I am the vessel.",
    "refused_the_offer":
        "The Unmade — speaking through the shadow of Maelvyr — offered you what it offered him. "
        "You said no. The shadow called this interesting.",
    "unmade_spoke_its_nature":
        "The Unmade described itself: not the absence of something, but a presence. "
        "Here before the wells. Before the gods. Before everything. Patient.",
    "unmade_spoke_maelvyr":
        "The Unmade described Maelvyr's fate: he killed Vaelan, walked away from the ruins, "
        "and has been building something elsewhere ever since. He grows. He is a door, "
        "learning to open wider.",
    "knows_agreement_stone_use":
        "You learned that the Agreement Stone is a record — a receipt — "
        "of what happened in the Chamber of the Agreement. It can invoke that event.",
    "found_hall_of_nine":
        "You found the Hall of the Nine — nine alcoves, each bearing the symbol of one of the Sera. "
        "The golden centre of the floor mosaic has been pried out.",
    "nine_completed":
        "You stood before all nine alcoves. Something settled — "
        "the sense of a set finally seen whole.",
    "found_shattered_crown_hall":
        "You found the Hall of the Shattered Crown — built after the fall, "
        "by someone who came back. It depicts the Wars of the Shattered Crown: "
        "three generations of heirs, each holding one Godshard, each believing the full set "
        "would restore the empire.",
    "found_tolos_memorial":
        "The walls of the Shattered Crown Hall list the war dead. "
        "Three names are largest: Calyren. Vaelan. Tolos. "
        "Beneath Tolos: 'He tried.'",
    "found_third_godshard":
        "You took the Third Godshard from the Hall of the Shattered Crown. "
        "The three shards pulsed together — once — and then settled into a shared frequency.",
    "found_veythari_sanctuary":
        "You found the Veythari Sanctuary — silver-lit, still, with a pale leafless tree "
        "and a pool that shows things that are not the room.",
    "arukiel_memory":
        "You offered the Starlight Shard to the sanctuary pool and witnessed a memory of Arukiel — "
        "the Falling Light, choosing to be part of the world. "
        "The memory is now yours.",
    "found_tolos_plinth":
        "In the throne room: a secondary plinth, added after the fact. "
        "TOLOS. A date. HE TRIED. "
        "Talarion placed it there.",
    "read_talarion_chronicle":
        "Talarion's Chronicle: he was there when it ended. He saw Maelvyr weep over Tolos. "
        "He saw Maelvyr leave — injured, diminished, but alive. "
        "'I tell the story because someone must.'",
    "read_wars_record":
        "The Wars of the Shattered Crown lasted three generations. "
        "The Godshards were returned to Eldros-Verath by common agreement — "
        "no heir trusted to hold all three. They were placed in the Hall. They waited.",
    "atraxis_named":
        "You learned the name Atraxis — the deeper name for the Unmade. "
        "The Void-Touched cultists use it. It is older than the name Unmade.",
    "atraxis_well":
        "You spoke Atraxis into the Void-well. The darkness rose to the rim and rested there. "
        "The word pressed into stone: KNOWN.",
    "heard_dissonance":
        "In the Chamber of the Agreement, you heard Dissonance — "
        "a resonance between a voice and music that your mind cannot interpret as either.",
    "candle_crown_hall":
        "The Candle revealed a covered section of the Shattered Crown mural: "
        "a fourth figure watching the wars from a distance, and a covered caption: "
        "'AND HE WATCHED FROM AFAR, AND WAS GLAD.'",
    "mirror_scholar_vision":
        "In the Crystal Mirror, in Talarion's room, you saw Talarion himself — "
        "writing at his desk. He looked up and saw you.",
    "scholar_gave_info":
        "A Remnant Scholar in the ruins told you: "
        "'The thing in the well is older than the wells. The Remnant Scholars call it Atraxis.'",
    "found_recovery_room":
        "You found the Place Between — a room made from leftover space. "
        "The ruins receive offerings and remember them.",
    "found_cartographers_station":
        "You found the Cartographer's Station — a scholar's abandoned workspace "
        "with partial maps of the upper ruins and notes on the three factions.",
    "read_cartographer_maps":
        "The cartographer's maps confirmed: Void-Touched presence from depth 8+. "
        "Three factions in the ruins — scholars, cultists, mercenaries.",
    "read_serethan_note":
        "A Rolled Parchment was a note from Serethan, Warden-Commander: "
        "he chose not to ring the bell. He left the decision to whoever came after.",
    "read_wars_summary":
        "A Rolled Parchment described the Wars of the Shattered Crown — "
        "three generations of heirs, each holding one Godshard. "
        "The wars ended in exhaustion. The shards were returned to Eldros-Verath.",
    "read_myrrakhel_fragment":
        "A Rolled Parchment described something before Myrrakhel — the Architect. "
        "The Architect was destroyed. Its mind did not die with its form. "
        "Where it went: the question the Remnant Scholars cannot answer.",
    "read_thaun_account":
        "A Rolled Parchment was written by Thaun himself: "
        "'I am what happens when the void decides to have opinions. "
        "What is beneath the well is older than I am.'",
    "read_eldros_founding":
        "A Rolled Parchment described the founding of Eldros-Verath: "
        "the city was built here because of the Void-well. "
        "'The near-mortals said the well was a source of power. They were not wrong. They were incomplete.'",
    "read_atraxis_description":
        "A Rolled Parchment described Atraxis: not wanting, but gravity — "
        "pulling everything toward void. The margin note read: 'Yes.' "
        "Atraxis is aware of what it is.",
    "read_tolos_account":
        "A Rolled Parchment was a letter from Tolos to Maelvyr, never sent: "
        "'You wanted the gods to listen. So did I. "
        "The difference is I accepted that they might not.'",
    "read_nine_gods_list":
        "A Rolled Parchment listed all nine Sera by their near-mortal names. "
        "The final line: 'Myrrakhel made the others. Who made Myrrakhel is not recorded here.'",
    "read_maelvyr_survival":
        "A Rolled Parchment was a field report compiled by Talarion: "
        "Maelvyr was seen leaving Eldros-Verath on the night of the collapse. Injured. Alive. "
        "Recommendation: assume he survived. Assume he is dangerous.",
    "found_forge":
        "You found the Forge — still burning after centuries. "
        "Above it: 'This work is a poor shadow of the Forge Above.' "
        "The mortals who built it knew exactly what they were imitating.",
    "met_named":
        "You encountered The Named — a cultist in incomplete transformation. "
        "One half of their face was becoming something else. "
        "They spoke Atraxis's name once. The name has partial power.",
    "met_shepherd":
        "You encountered the Unmade Shepherd — a void-creature that commands others. "
        "When it fell, everything it was herding scattered.",
    "met_witness":
        "You encountered the Agreement's Witness — a being that was present "
        "when Maelvyr made the Agreement and has not left since. "
        "It did not die of anything you did. It was finally permitted to.",
    "killed_void_priest":
        "You killed a Void Priest — a cultist who invoked Atraxis by name during combat. "
        "The name had partial effect. The drain felt intentional.",
    "met_archivist":
        "You met the Archivist — a Remnant Scholar who has been in the ruins for eleven years. "
        "They know the factions, the layout, and that something is being organised in the deep.",
    "met_bound_one":
        "You met the Bound One — a cultist partially resisting the Void's pull. "
        "They are becoming a direction. They know this.",
    "met_serethan":
        "You encountered Serethan's Echo — the Warden-Commander's strong memory, "
        "still standing at a window that no longer exists.",
    "serethan_truth_told":
        "You told Serethan's Echo the full truth about Maelvyr and the Agreement. "
        "'Thank you for telling me. It is important to know. Even here. Even now.'",
    "serethan_choice":
        "Serethan did not ring the bell because he knew the lockdown "
        "would wake everything they had caged. He left the decision to whoever came after.",
    "found_deep_sleeper":
        "You found the Deep Sleeper — something vast and old in the deepest room, "
        "coiled around itself. Not a dragon. Something that existed before the categories.",
    "sleeper_shards_answer":
        "The Deep Sleeper's answer about the Godshards: "
        "they hold intention — Vaethar's original intention at the moment of fragmentation. "
        "The ritual gives you Vaethar's intention, not merely power.",
    "sleeper_myrrakhel_answer":
        "The Deep Sleeper's answer about Myrrakhel: "
        "Myrrakhel has been listening since the Night of Collapse. "
        "Waiting for a quality of attention. Not a name. Not a ritual. A quality.",
    "talarion_full_account":
        "Talarion's Echo, through the Crystal Mirror, gave the full account: "
        "Vaelan stayed because emperors do not run. "
        "Tolos jumped because friends do not calculate. "
        "Talarion built the Hall because someone had to.",
    "found_near_mortal_ossuary":
        "You found the Ossuary of the Near-Mortals — "
        "Morvath and Veythari remains, placed with ceremony. "
        "The same hand placed both.",
    "found_archive_agreements":
        "You found the Archive of Agreements — every formal agreement Eldros ever made. "
        "The final entry is Maelvyr's Agreement with the Void.",
    "read_agreement_terms":
        "You read the terms of the Agreement in the Archive: "
        "'In exchange for his mortal limitation, the first party will be remade.' "
        "WITNESSED AND AGREED. Filed. Catalogued. An empire in its own archive.",
    "found_atraxis_scar":
        "You found the Atraxis Scar — where the Void physically breached the stone "
        "at the moment of Maelvyr's Agreement. The stone has not recovered.",
    "scar_understood":
        "Standing at the centre of the Atraxis Scar, knowing the full truth, "
        "you understood: this is where it happened. "
        "This is the physical mark of the moment that ended the empire.",
    "war_room_contingency":
        "The War Room held a file labelled CONTINGENCY MAELVYR. "
        "The plan was prepared. The activation order was never signed.",
    "captain_employer":
        "The Shard-Seeker Captain's employer knew exactly where the Godshards were. "
        "People who know what's in ruins they've never visited are not archaeologists. "
        "They are retrieval agents.",
    "bound_one_helped":
        "You helped the Bound One resist using the Dawn Shard. "
        "In return, they told you about a passage the Void-Touched use "
        "behind the Naming Room.",
    "observatory_hollow_truth":
        "Through the Hollow Stone, the Observatory's sky revealed itself: "
        "a window into the space between wells. "
        "The thing in the centre is on the other side of everything. "
        "It is not Atraxis. It is something Atraxis fears.",
    "naming_tolos_found":
        "In the Naming Room, you found Tolos Merinain's name. "
        "No titles — they were stripped. Just the name. "
        "And beneath it, in the smallest script the stone could manage: "
        "'He loved his friend. That is what the room remembers.'",
    "read_warden_log":
        "The Last Warden's Log: Serethan stood at the bell on the night of the collapse. "
        "He could not ring it. The lockdown would have woken everything they caged.",
    "read_vaelan_journal":
        "Vaelan's journal: he approved Maelvyr's audience request because he was running out of options. "
        "'I made a mistake. I do not know how large a mistake yet.'",
    "read_named_grimoire":
        "The Named's Grimoire: 'I have learned the name. The name is changing me. "
        "I wanted power. This is not power. This is direction. I am becoming a direction.'",
}

def show_lore_journal(player):
    title_bar("DISCOVERIES")
    found = [(f, DISCOVERY_TEXT[f]) for f in ALL_FLAGS
             if f in player.flags and f in DISCOVERY_TEXT]
    if not found:
        print(c("  Nothing recorded yet.", Fore.LIGHTBLUE_EX+Style.BRIGHT)); return
    for _, text in found:
        print(c("  ·", Fore.CYAN))
        wrap(f"  {text}", Fore.WHITE)
    print()
    discoverable = len(DISCOVERY_TEXT)
    print(c(f"  {len(found)} of {discoverable} notable discoveries made.", Fore.CYAN))
