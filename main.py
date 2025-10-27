import random, math, os, json, pygame, sys, time
from graphics import Visualizer  # import the external graphics file

# FUNCTION TO CLEAR SCREEN
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# BASE MONSTERS, ELEMENTS, AND STATS
monsters = ["cat", "dog", "rat"]
elements = ["fire", "water", "grass"]

base_stats = {
    "cat": {"atk": 50, "def": 40, "spd": 60},
    "dog": {"atk": 60, "def": 50, "spd": 55},
    "rat": {"atk": 45, "def": 35, "spd": 70}
}

# ELEMENT AND FUSION TABLES
element_results = {
    frozenset(["fire", "water"]): "vapor",
    frozenset(["fire", "grass"]): "blaze",
    frozenset(["water", "grass"]): "mud",
    frozenset(["fire"]): "inferno",
    frozenset(["water"]): "torrent",
    frozenset(["grass"]): "thorn"
}

fusion_species = {
    frozenset(["cat", "cat"]): "tigron",
    frozenset(["dog", "dog"]): "cerberus",
    frozenset(["rat", "rat"]): "gnawlord",
    frozenset(["cat", "dog"]): "felhound",
    frozenset(["cat", "rat"]): "scavlynx",
    frozenset(["dog", "rat"]): "burrowfang"
}

# MONSTER ENCYCLOPEDIA
encyclopedia = {}
SAVE_FILE = "encyclopedia.json"

def load_encyclopedia():
    global encyclopedia
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            encyclopedia.update(json.load(f))
    # Add base monsters to encyclopedia by default
    for element in elements:
        for monster in monsters:
            base_name = f"{element}_{monster}"
            if base_name not in encyclopedia:
                base_monster = {
                    "name": base_name,
                    "elements": [element],
                    "species": monster,
                    "atk": base_stats[monster]["atk"],
                    "def": base_stats[monster]["def"],
                    "spd": base_stats[monster]["spd"],
                    "skills": [],
                    "mutations": []
                }
                encyclopedia[base_name] = base_monster
    save_encyclopedia()

def save_encyclopedia():
    with open(SAVE_FILE, "w") as f:
        json.dump(encyclopedia, f, indent=2)

def clear_encyclopedia():
    global encyclopedia
    encyclopedia.clear()
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    # Reload base monsters after clear
    load_encyclopedia()

# IMAGE HANDLING
IMAGE_FOLDER = "monster_images"

def get_monster_image(name):
    filename = f"{name.lower()}.png"
    path = os.path.join(IMAGE_FOLDER, filename)
    return path if os.path.exists(path) else os.path.join(IMAGE_FOLDER, "default.png")

# PARSE ELEMENT + MONSTER HELPER
def parse_element_monster(text):
    if "_" not in text:
        return None, None, "Invalid format! Use element_monster (e.g., fire_cat)."
    element, monster = text.split("_", 1)
    if element not in elements:
        return None, None, f"'{element}' is not a valid element."
    if monster not in monsters:
        return None, None, f"'{monster}' is not a valid monster."
    return element, monster, None

# FUSION LOGIC
def fuse_monsters(e1, m1, e2, m2):
    fusion_elem_key = frozenset([e1, e2])
    new_elem = element_results.get(fusion_elem_key, f"{e1}_{e2}")
    fusion_species_key = frozenset([m1, m2])
    new_species = fusion_species.get(fusion_species_key, f"{m1}_{m2}")

    def calculate_stat(stat_name):
        base_avg = (base_stats[m1][stat_name] + base_stats[m2][stat_name]) / 2
        multiplier = random.uniform(0.75, 2.5)
        return int(base_avg * multiplier)

    # Generate unique name for duplicate fusions
    base_name = f"{new_elem}_{new_species}"
    fusion_count = 1
    final_name = base_name

    # Count how many times this fusion already exists
    for existing_name in encyclopedia:
        if existing_name.startswith(base_name):
            if existing_name == base_name:
                fusion_count = 2
            elif existing_name.startswith(base_name + "_"):
                try:
                    count = int(existing_name.split("_")[-1])
                    fusion_count = max(fusion_count, count + 1)
                except ValueError:
                    fusion_count += 1

    if fusion_count > 1:
        final_name = f"{base_name}_{fusion_count}"

    fused_monster = {
        "name": final_name,
        "elements": [e1, e2],
        "species": new_species,
        "atk": calculate_stat("atk"),
        "def": calculate_stat("def"),
        "spd": calculate_stat("spd"),
        "skills": [],
        "mutations": []
    }
    return fused_monster, None

# BATTLE SIMULATION
def simulate_battle(mon1_name, mon2_name):
    m1 = encyclopedia.get(mon1_name)
    m2 = encyclopedia.get(mon2_name)
    if not m1 or not m2:
        return "One or both monsters not found in encyclopedia."

    hp1 = (m1["atk"] + m1["def"]) // 2
    hp2 = (m2["atk"] + m2["def"]) // 2
    log = [f"=== BATTLE START ===", f"{mon1_name} vs {mon2_name}\n"]

    round_num = 1
    while hp1 > 0 and hp2 > 0 and round_num <= 10:
        dmg1 = random.randint(10, 30)
        dmg2 = random.randint(10, 30)

        log.append(f"--- Round {round_num} ---")

        # Monster 1 attacks first
        hp2 -= dmg1
        log.append(f"{mon1_name} attacks {mon2_name} for {dmg1} damage! ({max(hp2, 0)} HP left)")

        # Check if monster 2 is defeated after first attack
        if hp2 <= 0:
            log.append(f"{mon2_name} has been defeated!")
            break

        # Monster 2 attacks back
        hp1 -= dmg2
        log.append(f"{mon2_name} attacks {mon1_name} for {dmg2} damage! ({max(hp1, 0)} HP left)")

        # Check if monster 1 is defeated after counter attack
        if hp1 <= 0:
            log.append(f"{mon1_name} has been defeated!")
            break
        round_num += 1
        
    # Determine winner based on remaining HP
    if hp1 > hp2:
        winner = mon1_name
    elif hp2 > hp1:
        winner = mon2_name
    else:
        # If both have same HP (including both at 0), it's a tie - choose randomly
        winner = random.choice([mon1_name, mon2_name])
        log.append(f"Draw! {winner} wins by decision!")
    log.append(f"\nWinner: {winner}")
    return "\n".join(log), winner

# VISUALIZER INTEGRATION
visualizer = Visualizer()  # create one visualizer for the session

# SAFE EXECUTION
def safe_execute(command, context):
    try:
        commands = [cmd.strip() for cmd in command.split(';') if cmd.strip()]
        result = ""

        for cmd in commands:
            tokens = cmd.lower().split()
            if not tokens:
                continue

            # help
            if tokens[0] == "help":
                result += """Available commands:
fuse [element_monster] + [element_monster]
battle [monster1] [monster2]
summon [monster_name]
view en / clear en / exit
"""
                continue

            # view encyclopedia
            if tokens[0] == "view" and len(tokens) > 1 and tokens[1] == "en":
                if not encyclopedia:
                    result += "Encyclopedia is empty.\n"
                else:
                    # Separate base monsters from fused monsters
                    base_monsters = []
                    fused_monsters = []

                    for name, data in encyclopedia.items():
                        hp = (data['atk'] + data['def']) // 2
                        entry = f"{name} | HP {hp} ATK {data['atk']} DEF {data['def']} SPD {data['spd']}"

                        # Check if it's a base monster (element_base format)
                        parts = name.split('_')
                        if len(parts) == 2 and parts[0] in elements and parts[1] in monsters:
                            base_monsters.append(entry)
                        else:
                            fused_monsters.append(entry)

                    if base_monsters:
                        result += "=== BASE MONSTERS ===\n"
                        result += "\n".join(base_monsters) + "\n"

                    if fused_monsters:
                        result += "=== FUSED MONSTERS ===\n"
                        result += "\n".join(fused_monsters) + "\n"

                # Show visual Pokedex
                visualizer.show_pokedex(encyclopedia)
                continue

            # clear encyclopedia
            if tokens[0] == "clear" and len(tokens) > 1 and tokens[1] == "en":
                clear_encyclopedia()
                result += "Encyclopedia cleared.\n"
                continue

            # fuse
            if tokens[0] == "fuse" and "+" in tokens:
                idx = tokens.index("+")
                e1, m1, err1 = parse_element_monster(tokens[1])
                e2, m2, err2 = parse_element_monster(tokens[idx + 1])
                if err1 or err2:
                    result += (err1 or err2) + "\n"
                    continue
                fused, _ = fuse_monsters(e1, m1, e2, m2)
                encyclopedia[fused['name']] = fused
                save_encyclopedia()

                # visualize automatically
                visualizer.show_fusion(m1, m2, fused)

                result += f"Fusion successful: {fused['name']}\n"
                context = fused
                continue

            # battle
            if tokens[0] == "battle" and len(tokens) >= 3:
                mon1, mon2 = tokens[1], tokens[2]
                if mon1 not in encyclopedia or mon2 not in encyclopedia:
                    result += "One or both monsters not in encyclopedia.\n"
                    continue
                battle_log, winner = simulate_battle(mon1, mon2)
                visualizer.show_battle(mon1, mon2, winner)
                result += battle_log + "\n"
                continue

            # summon
            if tokens[0] == "summon" and len(tokens) >= 2:
                name = tokens[1]
                mon = encyclopedia.get(name)
                if not mon:
                    result += f"Monster '{name}' not found in encyclopedia.\n"
                else:
                    visualizer.show_summon(mon)
                    result += f"{name} has been summoned.\n"
                continue

            result += "Unknown command.\n"

        return context, result.strip()

    except Exception as e:
        return context, f"Error: {e}"

# MAIN LOOP
def run():
    load_encyclopedia()
    clear()
    print("=== DIGITAL MONSTER FUSION INTERPRETER ===")
    print("Type 'help' to view available commands. Type 'exit' to quit.\n")
    context = None

    while True:
        cmd = input("\nEnter command: ").strip()
        if not cmd:
            continue
        if cmd.lower() == "exit":
            save_encyclopedia()
            print("Exiting...")
            break
        context, response = safe_execute(cmd, context)
        print(response)

if __name__ == "__main__":
    run()
