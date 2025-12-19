# Shared Cards Across Sets

This document identifies cards that appear in multiple sets, detailing their mechanical similarities and differences, as well as aesthetic variations.

## Overview

Several cards were reprinted across the five sets in this database. Understanding these relationships is important for:
- Deck building (4-copy limit applies by name)
- Card identification
- Historical context
- Game logic implementation

## Reprint Categories

### 1. Identical Reprints (Same Mechanics)
Cards that are functionally identical across sets.

### 2. Different Versions (Same Pokemon, Different Cards)
Same Pokemon name but with different attacks, abilities, or stats.

### 3. Dark Variants (Team Rocket)
"Dark" versions of existing Pokemon with completely different mechanics.

---

## Base Set 2 Reprints

Base Set 2 is entirely composed of reprints from Base Set and Jungle. All cards are **functionally identical** to their originals.

### From Base Set

| Pokemon | Base Set # | Base Set 2 # | Notes |
|---------|------------|--------------|-------|
| Alakazam | 1 | 1 | Identical Damage Swap |
| Blastoise | 2 | 2 | Identical Rain Dance |
| Chansey | 3 | 3 | Identical |
| Charizard | 4 | 4 | Identical Energy Burn + Fire Spin |
| Clefairy | 5 | 5 | Identical |
| Gyarados | 6 | 6 | Identical |
| Hitmonchan | 7 | 7 | Identical |
| Machamp | 8 | 8 | Identical |
| Magneton | 9 | 9 | Identical |
| Mewtwo | 10 | 10 | Identical |
| Nidoking | 11 | 11 | Identical |
| Ninetales | 12 | 12 | Identical |
| Poliwrath | 13 | 13 | Identical |
| Raichu | 14 | 14 | Identical |
| Venusaur | 15 | 15 | Identical Energy Trans |
| Zapdos | 16 | 16 | Identical |

### Trainer Reprints (Base Set -> Base Set 2)

| Trainer | Base Set # | Base Set 2 # |
|---------|------------|--------------|
| Professor Oak | 88 | 116 |
| Bill | 91 | 118 |
| Computer Search | 71 | 101 |
| Item Finder | 74 | 103 |
| Pokemon Trader | 77 | 106 |
| Switch | 95 | 123 |
| Energy Removal | 92 | 119 |
| Gust of Wind | 93 | 120 |
| Potion | 94 | 122 |
| Super Potion | 90 | 117 |

### From Jungle

| Pokemon | Jungle # | Base Set 2 # | Notes |
|---------|----------|--------------|-------|
| Mr. Mime | 6/22 | 27 | Identical Invisible Wall |
| Scyther | 10/26 | 82 | Identical Swords Dance + Slash |
| Wigglytuff | 16/32 | 71 | Identical Do the Wave |
| Snorlax | 11/27 | 64 | Identical Thick Skinned |

---

## Same Pokemon, Different Cards

### Pikachu (3 Distinct Versions)

```go
// Base Set Pikachu (base1-058)
baseSetPikachu := &PokemonCard{
    Name: "Pikachu",
    HP:   40,
    Attacks: []Attack{
        {Name: "Gnaw", Cost: []string{"Colorless"}, Damage: "10"},
        {Name: "Thunder Jolt", Cost: []string{"Lightning", "Colorless"}, Damage: "30",
         Effect: &AttackEffect{
             EffectType: "coin_flip_recoil",
             CoinFlip: &CoinFlipEffect{
                 OnTails: &CoinFlipResult{SelfDamage: 10},
             },
         }},
    },
}

// Jungle Pikachu (jungle-060)
junglePikachu := &PokemonCard{
    Name: "Pikachu",
    HP:   50, // Higher HP!
    Attacks: []Attack{
        {Name: "Spark", Cost: []string{"Lightning", "Lightning"}, Damage: "20",
         Effect: &AttackEffect{
             EffectType: "bench_damage",
             BenchDamage: &BenchDamageEffect{
                 Target: "opponent_benched_choice",
                 Damage: 10,
             },
         }},
    },
}

// Key Differences:
// - Jungle Pikachu has 50 HP vs Base Set's 40 HP
// - Base Set has 2 attacks; Jungle has 1 attack
// - Thunder Jolt (Base) does more damage but has self-damage risk
// - Spark (Jungle) damages bench Pokemon
```

### Comparison Table

| Attribute | Base Set (#58) | Jungle (#60) |
|-----------|---------------|--------------|
| HP | 40 | 50 |
| Attack 1 | Gnaw (C) - 10 | Spark (LL) - 20 + bench |
| Attack 2 | Thunder Jolt (LC) - 30, self-damage | - |
| Weakness | Fighting x2 | Fighting x2 |
| Retreat | 1 | 1 |

**Deck Building Note:** You can run 4 copies total of "Pikachu" (any combination of versions).

---

### Raichu (2 Distinct Versions)

```go
// Base Set Raichu (base1-014)
baseSetRaichu := &PokemonCard{
    Name:       "Raichu",
    HP:         80,
    Stage:      "Stage 1",
    EvolvesFrom: "Pikachu",
    Attacks: []Attack{
        {Name: "Agility", Cost: []string{"Lightning", "Colorless", "Colorless"}, Damage: "20",
         Effect: &AttackEffect{
             EffectType:     "coin_flip_effect",
             CoinFlip: &CoinFlipEffect{
                 OnHeads: &CoinFlipResult{Effect: "prevent_damage_and_effects_next_turn"},
             },
         }},
        {Name: "Thunder", Cost: []string{"Lightning", "Lightning", "Lightning", "Colorless"}, Damage: "60",
         Effect: &AttackEffect{
             EffectType: "coin_flip_recoil",
             CoinFlip: &CoinFlipEffect{
                 OnTails: &CoinFlipResult{SelfDamage: 30},
             },
         }},
    },
}

// Fossil Raichu (fossil-014/029)
fossilRaichu := &PokemonCard{
    Name:       "Raichu",
    HP:         90, // Higher HP!
    Stage:      "Stage 1",
    EvolvesFrom: "Pikachu",
    Attacks: []Attack{
        {Name: "Gigashock", Cost: []string{"Lightning", "Lightning", "Lightning", "Lightning"}, Damage: "30",
         Effect: &AttackEffect{
             EffectType: "multi_effect",
             BenchDamage: &BenchDamageEffect{
                 Target: "opponent_bench",
                 Damage: 10,
                 Count: "up_to_3",
             },
         }},
    },
}
```

| Attribute | Base Set (#14) | Fossil (#14/29) |
|-----------|---------------|-----------------|
| HP | 80 | 90 |
| Attack 1 | Agility (LCC) - 20, evade | Gigashock (LLLL) - 30, bench spread |
| Attack 2 | Thunder (LLLC) - 60, recoil | - |
| Strategy | High damage, risk/reward | Spread damage |

---

### Zapdos (2 Distinct Versions)

```go
// Base Set Zapdos (base1-016)
baseSetZapdos := &PokemonCard{
    Name: "Zapdos",
    HP:   90,
    Stage: "Basic",
    Attacks: []Attack{
        {Name: "Thunder", Cost: []string{"Lightning", "Lightning", "Lightning", "Colorless"}, Damage: "60",
         Effect: &AttackEffect{
             EffectType: "coin_flip_recoil",
             CoinFlip: &CoinFlipEffect{
                 OnTails: &CoinFlipResult{SelfDamage: 30},
             },
         }},
        {Name: "Thunderbolt", Cost: []string{"Lightning", "Lightning", "Lightning", "Lightning"}, Damage: "100",
         Effect: &AttackEffect{
             EffectType: "energy_discard",
             EnergyDiscard: &EnergyDiscardCost{Count: -1, Type: "all"}, // Discard all energy
         }},
    },
}

// Fossil Zapdos (fossil-015/030)
fossilZapdos := &PokemonCard{
    Name: "Zapdos",
    HP:   80,
    Stage: "Basic",
    Attacks: []Attack{
        {Name: "Thunderstorm", Cost: []string{"Lightning", "Lightning", "Lightning", "Lightning"}, Damage: "70",
         Effect: &AttackEffect{
             EffectType: "bench_damage",
             BenchDamage: &BenchDamageEffect{
                 Target: "all_bench", // Both players!
                 Damage: 10,
             },
         }},
    },
}
```

| Attribute | Base Set (#16) | Fossil (#15/30) |
|-----------|---------------|-----------------|
| HP | 90 | 80 |
| Attack 1 | Thunder (LLLC) - 60, recoil | Thunderstorm (LLLL) - 70, ALL bench |
| Attack 2 | Thunderbolt (LLLL) - 100, discard all | - |

---

### Magneton (2 Distinct Versions)

| Attribute | Base Set (#9) | Fossil (#11/26) |
|-----------|--------------|------------------|
| HP | 60 | 80 |
| Attacks | Thunder Wave, Selfdestruct | Sonicboom, Selfdestruct |
| Self-destruct Damage | 80 to opponent, 20 to all bench | 100 to opponent, 20 to all bench |

---

### Haunter (2 Distinct Versions)

| Attribute | Base Set (#29) | Fossil (#6/21) |
|-----------|---------------|-----------------|
| HP | 50 | 60 |
| Key Attack | Dream Eater (Psychic) | Nightmare (no damage, flip for sleep) |
| Strategy | Conditional damage | Status control |

---

## Dark Pokemon (Team Rocket)

Team Rocket introduced "Dark" variants that are **completely different cards** from their normal counterparts.

### Dark Charizard vs Charizard

```go
// These are treated as DIFFERENT Pokemon for deck building
// You can run 4 Charizard AND 4 Dark Charizard

baseSetCharizard := &PokemonCard{
    Name: "Charizard",     // Card name for deck building
    HP:   120,
    // Energy Burn + Fire Spin
}

darkCharizard := &PokemonCard{
    Name: "Dark Charizard", // Different name!
    HP:   80,               // Much lower HP
    // Nail Flick + Continuous Fireball
}
```

| Attribute | Charizard (Base) | Dark Charizard (Rocket) |
|-----------|-----------------|-------------------------|
| HP | 120 | 80 |
| Ability | Energy Burn | None |
| Attack 1 | Fire Spin (100, discard 2) | Nail Flick (10) |
| Attack 2 | - | Continuous Fireball (50x coin flips) |
| Evolution | Charmeleon | Dark Charmeleon |

**Key Point:** Dark Charizard evolves from Dark Charmeleon, NOT regular Charmeleon.

### Dark Pokemon Evolution Lines

| Normal Line | Dark Line |
|-------------|-----------|
| Charmander -> Charmeleon -> Charizard | Charmander -> Dark Charmeleon -> Dark Charizard |
| Squirtle -> Wartortle -> Blastoise | Squirtle -> Dark Wartortle -> Dark Blastoise |
| Abra -> Kadabra -> Alakazam | Abra -> Dark Kadabra -> Dark Alakazam |
| Magikarp -> Gyarados | Magikarp -> Dark Gyarados |

```go
// Evolution validation for Dark Pokemon
func CanEvolveTo(basePokemon, evolutionPokemon *PokemonCard) bool {
    // Dark Pokemon can only evolve from matching basics
    // and regular evolution cards

    // Charmander can evolve into Charmeleon OR Dark Charmeleon
    // But Dark Charmeleon can ONLY evolve into Dark Charizard

    if strings.HasPrefix(evolutionPokemon.Name, "Dark ") {
        // Dark Stage 2 must come from Dark Stage 1
        if evolutionPokemon.Stage == "Stage 2" {
            expectedPre := evolutionPokemon.EvolvesFrom
            return basePokemon.Name == expectedPre
        }

        // Dark Stage 1 can come from normal Basic
        if evolutionPokemon.Stage == "Stage 1" {
            expectedBasic := strings.TrimPrefix(
                evolutionPokemon.EvolvesFrom,
                "Dark ", // Remove "Dark " if present
            )
            // Dark Charmeleon evolves from Charmander
            return basePokemon.Name == evolutionPokemon.EvolvesFrom
        }
    }

    return basePokemon.Name == evolutionPokemon.EvolvesFrom
}
```

### All Dark Pokemon in Team Rocket

| Dark Pokemon | HP | Normal Counterpart HP | Notable Difference |
|--------------|-----|----------------------|-------------------|
| Dark Alakazam | 60 | 80 | Different attack, no Damage Swap |
| Dark Arbok | 60 | - | New Pokemon (Arbok not in Base) |
| Dark Blastoise | 70 | 100 | Different attack, no Rain Dance |
| Dark Charizard | 80 | 120 | No Energy Burn, coin flip attack |
| Dark Dragonite | 70 | 100 | Different abilities |
| Dark Dugtrio | 50 | 70 | More aggressive attacks |
| Dark Golbat | 50 | - | New evolution line |
| Dark Gyarados | 70 | 100 | Self-damage mechanic |
| Dark Hypno | 60 | 90 | Disruption focused |
| Dark Machamp | 70 | 100 | Different fighting style |
| Dark Magneton | 60 | 60/80 | Similar HP to Base |
| Dark Slowbro | 60 | - | Different from Fossil Slowbro |
| Dark Vileplume | 60 | - | Hay Fever (Trainer lock!) |
| Dark Weezing | 60 | - | Self-sacrifice attack |
| Dark Raichu | 70 | 80 | Secret rare, sneak attack |

---

## Identical Cards for Game Logic

When implementing game logic, cards from different sets with the same name should be treated identically for:

### Deck Building

```go
func CountCardsByName(deck []Card, name string) int {
    count := 0
    for _, card := range deck {
        if card.GetName() == name {
            count++
        }
    }
    return count
}

func ValidateFourCopyRule(deck []Card) error {
    nameCounts := make(map[string]int)

    for _, card := range deck {
        name := card.GetName()

        // Basic Energy is unlimited
        if isBasicEnergy(card) {
            continue
        }

        nameCounts[name]++
        if nameCounts[name] > 4 {
            return fmt.Errorf("too many copies of %s: %d (max 4)", name, nameCounts[name])
        }
    }

    return nil
}
```

### Evolution Matching

```go
// Any Pikachu can evolve into any Raichu (from any set)
func CanEvolve(base *PokemonCard, evolution *PokemonCard) bool {
    // Match by name, not by ID
    return base.Name == evolution.EvolvesFrom
}

// Example:
// Base Set Pikachu (base1-058) can evolve into:
//   - Base Set Raichu (base1-014)
//   - Fossil Raichu (fossil-014)
//   - Base Set 2 Raichu (base2-014)
```

### Display Differentiation

While game logic treats same-named cards identically, display should differentiate:

```go
type CardDisplay struct {
    Name       string
    SetName    string
    SetCode    string
    CardNumber int
    ImageURL   string
}

func GetCardDisplay(card *Card) CardDisplay {
    return CardDisplay{
        Name:       card.Name,
        SetName:    card.Set.Name,
        SetCode:    card.Set.ID,
        CardNumber: card.Number,
        ImageURL:   card.ImageURL,
    }
}

// Display: "Pikachu (Base Set #58)" vs "Pikachu (Jungle #60)"
```

---

## Reference: All Shared Pokemon Names

| Pokemon Name | Sets Present | Functionally Different? |
|--------------|--------------|------------------------|
| Pikachu | Base Set, Jungle, Base Set 2 | Yes (Base/Jungle different) |
| Raichu | Base Set, Fossil, Base Set 2 | Yes (Base/Fossil different) |
| Zapdos | Base Set, Fossil, Base Set 2 | Yes (Base/Fossil different) |
| Magneton | Base Set, Fossil, Base Set 2 | Yes (Base/Fossil different) |
| Haunter | Base Set, Fossil | Yes |
| Gastly | Base Set, Fossil | Yes |
| Charizard | Base Set, Base Set 2, (Dark: Rocket) | No (Base/BS2 same) |
| Blastoise | Base Set, Base Set 2, (Dark: Rocket) | No (Base/BS2 same) |
| Alakazam | Base Set, Base Set 2, (Dark: Rocket) | No (Base/BS2 same) |
| Muk | Fossil, (Dark: Rocket) | Yes (Dark is different) |
| Vileplume | Jungle, (Dark: Rocket) | Yes (Dark is different) |

---

## Holo vs Non-Holo Variants

Several Rare Holo cards have non-holo counterparts in the same set:

### Jungle Dual Prints

| Pokemon | Holo # | Non-Holo # | Mechanically Identical |
|---------|--------|------------|----------------------|
| Clefable | 1 | 17 | Yes |
| Electrode | 2 | 18 | Yes |
| Flareon | 3 | 19 | Yes |
| Jolteon | 4 | 20 | Yes |
| Kangaskhan | 5 | 21 | Yes |
| Mr. Mime | 6 | 22 | Yes |
| Nidoqueen | 7 | 23 | Yes |
| Pidgeot | 8 | 24 | Yes |
| Pinsir | 9 | 25 | Yes |
| Scyther | 10 | 26 | Yes |
| Snorlax | 11 | 27 | Yes |
| Vaporeon | 12 | 28 | Yes |
| Venomoth | 13 | 29 | Yes |
| Victreebel | 14 | 30 | Yes |
| Vileplume | 15 | 31 | Yes |
| Wigglytuff | 16 | 32 | Yes |

### Fossil Dual Prints

| Pokemon | Holo # | Non-Holo # |
|---------|--------|------------|
| Aerodactyl | 1 | 16 |
| Articuno | 2 | 17 |
| Ditto | 3 | 18 |
| Dragonite | 4 | 19 |
| Gengar | 5 | 20 |
| Haunter | 6 | 21 |
| Hitmonlee | 7 | 22 |
| Hypno | 8 | 23 |
| Kabutops | 9 | 24 |
| Lapras | 10 | 25 |
| Magneton | 11 | 26 |
| Moltres | 12 | 27 |
| Muk | 13 | 28 |
| Raichu | 14 | 29 |
| Zapdos | 15 | 30 |

**Programming Note:** Holo and non-holo versions of the same card are **mechanically identical** and count toward the same 4-copy limit.
