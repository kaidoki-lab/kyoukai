# genome_defs.py — ゲノム定義（コア・器官・シェル・変異・伝説ゲノム・体型）
# 外部依存なし。

CORES = {
    "C1": {"name": "Seed Core",  "branch": "kind"},
    "C2": {"name": "Egg Core",   "branch": "kind"},
    "C3": {"name": "Eye Core",   "branch": "attention"},
    "C4": {"name": "Maw Core",   "branch": "aggression"},
    "C5": {"name": "Void Core",  "branch": "chaos"},
}

ORGANS = {
    "O1":  "Antlers",
    "O2":  "Multi Eyes",
    "O3":  "Mouth Ring",
    "O4":  "Tentacles",
    "O5":  "Wings",
    "O6":  "Bone Spikes",
    "O7":  "Signal Antenna",
    "O8":  "Bloom Organ",
    "O9":  "Meteor Carapace",
    "O10": "Cryo Crystal Limbs",
    "O11": "Predator Spines",
    "O12": "Abyssal Asymmetry",
    "O13": "Halo Crown",
    "O14": "Bone Crown",
    "O15": "Eye Cathedral Cluster",
    "O16": "Choir Throat",
}

SHELLS = {
    "S1": "Halo Ring",
    "S2": "Coral Shell",
    "S3": "Temple Body",
    "S4": "Leviathan Body",
    "S5": "Fracture Body",
}

MUTATIONS = {
    "M0": "None",
    "M1": "Malice",
    "M2": "Instability",
    "M3": "Complex",
}

LEGEND_GENOMES = {
    82: {"name": "Seed Oracle",       "genome": {"core": "C1", "organs": ["O1", "O8"],          "shell": "S1", "mutation": "M0"}, "rarity": "Legend", "branch": "kind"},
    83: {"name": "Coral Shepherd",    "genome": {"core": "C1", "organs": ["O1", "O4"],          "shell": "S2", "mutation": "M0"}, "rarity": "Legend", "branch": "kind"},
    84: {"name": "Moon Antler",       "genome": {"core": "C1", "organs": ["O1", "O5"],          "shell": "S1", "mutation": "M3"}, "rarity": "Legend", "branch": "kind"},
    85: {"name": "Bone Tyrant",       "genome": {"core": "C4", "organs": ["O6", "O3"],          "shell": "S3", "mutation": "M1"}, "rarity": "Legend", "branch": "aggression"},
    86: {"name": "Crimson Maw",       "genome": {"core": "C4", "organs": ["O3", "O6"],          "shell": "S5", "mutation": "M1"}, "rarity": "Legend", "branch": "aggression"},
    87: {"name": "Rift Hunter",       "genome": {"core": "C5", "organs": ["O4", "O6"],          "shell": "S4", "mutation": "M2"}, "rarity": "Legend", "branch": "aggression"},
    88: {"name": "Eye Cathedral",     "genome": {"core": "C3", "organs": ["O2", "O2"],          "shell": "S3", "mutation": "M3"}, "rarity": "Legend", "branch": "attention"},
    89: {"name": "Signal Watcher",    "genome": {"core": "C3", "organs": ["O7", "O2"],          "shell": "S1", "mutation": "M0"}, "rarity": "Legend", "branch": "attention"},
    90: {"name": "Abyss Observer",    "genome": {"core": "C3", "organs": ["O2", "O4"],          "shell": "S4", "mutation": "M2"}, "rarity": "Legend", "branch": "attention"},
    91: {"name": "Choir Organism",    "genome": {"core": "C1", "organs": ["O3", "O3"],          "shell": "S1", "mutation": "M3"}, "rarity": "Legend", "branch": "talk"},
    92: {"name": "Whisper Archive",   "genome": {"core": "C3", "organs": ["O3", "O7"],          "shell": "S3", "mutation": "M3"}, "rarity": "Legend", "branch": "talk"},
    93: {"name": "Tongue Saint",      "genome": {"core": "C1", "organs": ["O3", "O5"],          "shell": "S1", "mutation": "M1"}, "rarity": "Legend", "branch": "talk"},
    94: {"name": "Fracture Bloom",    "genome": {"core": "C5", "organs": ["O8", "O4"],          "shell": "S5", "mutation": "M2"}, "rarity": "Legend", "branch": "chaos"},
    95: {"name": "Void Leviathan",    "genome": {"core": "C5", "organs": ["O4", "O6"],          "shell": "S4", "mutation": "M2"}, "rarity": "Legend", "branch": "chaos"},
    96: {"name": "Weeping Sun",       "genome": {"core": "C5", "organs": ["O2", "O5"],          "shell": "S1", "mutation": "M3"}, "rarity": "Myth",   "branch": "myth"},
    97: {"name": "Cathedral of Teeth","genome": {"core": "C4", "organs": ["O6", "O6"],          "shell": "S3", "mutation": "M1"}, "rarity": "Myth",   "branch": "myth"},
    98: {"name": "Dream Parasite",    "genome": {"core": "C5", "organs": ["O4", "O4"],          "shell": "S5", "mutation": "M2"}, "rarity": "Myth",   "branch": "myth"},
    99: {"name": "Black Halo Child",  "genome": {"core": "C2", "organs": ["O2", "O3"],          "shell": "S1", "mutation": "M3"}, "rarity": "Myth",   "branch": "myth"},
    100:{"name": "Genesis Return",    "genome": {"core": "C2", "organs": ["O1","O2","O3","O4","O5","O6","O7","O8"], "shell": "S1", "mutation": "M3"}, "rarity": "Apex", "branch": "apex"},
}

BODY_PLANS = {
    "egg":               "Stage0 only. Ovoid base.",
    "larva_soft":        "Soft larval body, no egg silhouette.",
    "jaw_larva":         "Forward jaw larva.",
    "optic_pod":         "Orbital pod with long eye structure.",
    "choir_larva":       "Vocal larva with mouth organ.",
    "amorphous":         "Unstable amorphous life.",
    "quadruped_seed":    "Four-legged seed beast.",
    "raptor":            "Forward predator body.",
    "orb_walker":        "Stilt eye walker.",
    "chorus_beast":      "Wide-mouth chorus beast.",
    "tentacled":         "Radial tentacled life.",
    "antler_beast":      "Antlered beast silhouette.",
    "spiked_predator":   "Spiked predator silhouette.",
    "many_eyed":         "Many-eyed watcher silhouette.",
    "cathedral_throat":  "Cathedral-mouth body.",
    "rift_serpent":      "Serpentine chaos body.",
    "halo_titan":        "Mythic halo titan.",
    "bone_tyrant":       "Bone tyrant.",
    "eye_cathedral":     "Eye cathedral.",
    "choir_organism":    "Choir organism.",
    "void_leviathan":    "Void leviathan.",
}
