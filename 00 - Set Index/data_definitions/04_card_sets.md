# Card Set Documentation

This document provides detailed information about each card set in the database, including release information, notable cards, set-specific mechanics, and programming considerations.

## Set Overview

| # | Code | Set Name | Release | Cards | Unique Features |
|---|------|----------|---------|-------|-----------------|
| 01 | base1 | Base Set | 1999-01-09 | 102 | Foundation set, Pokemon Powers |
| 02 | jungle | Jungle | 1999-06-16 | 64 | First expansion, no Trainers (mostly) |
| 03 | fossil | Fossil | 1999-10-10 | 62 | Fossil Pokemon, Ditto |
| 04 | base2 | Base Set 2 | 2000-02-24 | 130 | Reprint compilation |
| 05 | rocket | Team Rocket | 2000-04-24 | 83 | Dark Pokemon, Special Energy |

---

## Base Set (01)

**Set Code:** `base1`
**Release Date:** January 9, 1999
**Total Cards:** 102
**Series:** Original

### Set Information Object

```go
baseSetInfo := SetInfo{
    ID:          "base1",
    Name:        "Base Set",
    Series:      "Original",
    ReleaseDate: "1999-01-09",
    TotalCards:  102,
}
```

### Card Distribution

| Rarity | Count | Notable Cards |
|--------|-------|---------------|
| Rare Holo | 16 | Charizard, Blastoise, Venusaur, Alakazam |
| Rare | 16 | Electabuzz, Hitmonchan, Scyther |
| Uncommon | 32 | Charmeleon, Ivysaur, Wartortle |
| Common | 31 | Pikachu, Charmander, Squirtle, Bulbasaur |
| Energy | 7 | Basic + Double Colorless |

### Key Pokemon Powers

Base Set introduced Pokemon Powers - abilities that provide effects outside of attacks:

| Pokemon | Power | Type | Effect |
|---------|-------|------|--------|
| Alakazam | Damage Swap | damage_transfer | Move damage counters between your Pokemon |
| Blastoise | Rain Dance | energy_acceleration | Attach extra Water Energy to Water Pokemon |
| Charizard | Energy Burn | energy_conversion | Convert all energy to Fire type |
| Venusaur | Energy Trans | energy_manipulation | Move Grass Energy between your Pokemon |
| Ninetales | Fire Immunity | damage_prevention | Prevent Fire damage |

### Iconic Trainer Cards

| Card | Effect | Power Level |
|------|--------|-------------|
| Professor Oak | Discard hand, draw 7 | Format-Defining |
| Bill | Draw 2 cards | Staple |
| Computer Search | Discard 2, search any card | High |
| Item Finder | Discard 2, retrieve Trainer | High |
| Super Energy Removal | Discard 1, remove 2 opponent's | High |
| Energy Removal | Remove 1 opponent's energy | Staple |
| Gust of Wind | Force opponent switch | Staple |

### Programming Notes

1. **Pokemon Powers** are the original ability system - treated differently from later Poke-Powers/Bodies/Abilities in rules
2. **Energy Burn** (Charizard) creates temporary energy type conversion that lasts only until end of turn
3. **Rain Dance** (Blastoise) bypasses the once-per-turn energy attachment rule
4. **Damage Swap** (Alakazam) cannot knock out your own Pokemon
5. **Clefairy Doll** is a Trainer that plays as a Pokemon with special rules

---

## Jungle (02)

**Set Code:** `jungle`
**Release Date:** June 16, 1999
**Total Cards:** 64
**Series:** Original

### Set Information Object

```go
jungleSetInfo := SetInfo{
    ID:          "jungle",
    Name:        "Jungle",
    Series:      "Original",
    ReleaseDate: "1999-06-16",
    TotalCards:  64,
}
```

### Card Distribution

| Rarity | Count | Notable Cards |
|--------|-------|---------------|
| Rare Holo | 16 | Mr. Mime, Scyther, Wigglytuff, Snorlax |
| Rare | 16 | Jolteon, Flareon, Vaporeon |
| Uncommon | 16 | Butterfree, Victreebel, Vileplume |
| Common | 16 | Pikachu, Eevee, Jigglypuff |

### Unique Pokemon Abilities

| Pokemon | Power/Ability | Implementation |
|---------|---------------|----------------|
| Mr. Mime | Invisible Wall | Block all attacks dealing 30+ damage |
| Snorlax | Thick Skinned | Take 30 less damage while Asleep |
| Wigglytuff | Do the Wave | 10 damage per benched Pokemon |
| Electrode | Buzzap | Self-KO to become any type of energy |
| Clefable | Metronome | Copy any of opponent's active's attacks |

### Key Programming Challenges

#### Mr. Mime's Invisible Wall

```go
// CheckInvisibleWall determines if damage is blocked
func CheckInvisibleWall(mrMime *GamePokemon, incomingDamage int) int {
    // Check if Mr. Mime has status conditions that disable powers
    if mrMime.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
        return incomingDamage // Power disabled
    }

    // Invisible Wall blocks damage of 30 or more
    // IMPORTANT: This is AFTER weakness/resistance calculation
    if incomingDamage >= 30 {
        return 0 // Blocked completely
    }

    return incomingDamage
}
```

#### Electrode's Buzzap

```go
// ExecuteBuzzap implements Electrode's self-sacrifice energy ability
func ExecuteBuzzap(electrode *GamePokemon, player *Player, energyType string) error {
    // Buzzap knocks out Electrode
    electrode.CurrentHP = 0

    // Electrode becomes a special energy card
    buzzapEnergy := &SpecialEnergyFromPokemon{
        OriginalPokemon: electrode,
        ProvidesType:    energyType,
        ProvidesAmount:  2, // Provides 2 of chosen type
    }

    // Opponent takes a prize for Electrode's KO
    opponent.TakePrize()

    // The "energy" can now be attached to a Pokemon
    // Note: If this energy is removed, it goes to discard as Electrode
    return nil
}
```

#### Clefable's Metronome

```go
// ExecuteMetronome copies an attack from the defending Pokemon
func ExecuteMetronome(clefable *GamePokemon, defender *GamePokemon) error {
    // Get available attacks from defender
    availableAttacks := defender.Card.Attacks

    // Player selects which attack to copy
    selectedAttack, err := game.UI.PromptAttackSelection(availableAttacks)
    if err != nil {
        return err
    }

    // Execute the attack as if Clefable had it
    // IMPORTANT: Uses Clefable's attached energy to pay cost
    // Energy type matching uses Colorless equivalence
    return executeAttackAsCopy(clefable, defender, selectedAttack)
}
```

### Jungle Pikachu vs Base Set Pikachu

Jungle introduced a different Pikachu with unique attacks:

| Version | HP | Attack 1 | Attack 2 |
|---------|-----|----------|----------|
| Base Set (#58) | 40 | Gnaw (10) | Thunder Jolt (30, self-damage) |
| Jungle (#60) | 50 | Spark (20 + bench damage) | - |

```go
// JunglePikachuSpark handles the bench sniping attack
func JunglePikachuSpark(pikachu *GamePokemon, defender *GamePokemon, opponent *Player) {
    // Deal 20 damage to defender
    defender.TakeDamage(20)

    // If opponent has benched Pokemon, deal 10 to one of choice
    if len(opponent.Bench) > 0 {
        target := selectBenchTarget(opponent.Bench)
        // Bench damage does NOT apply weakness/resistance
        target.TakeDamage(10)
    }
}
```

---

## Fossil (03)

**Set Code:** `fossil`
**Release Date:** October 10, 1999
**Total Cards:** 62
**Series:** Original

### Set Information Object

```go
fossilSetInfo := SetInfo{
    ID:          "fossil",
    Name:        "Fossil",
    Series:      "Original",
    ReleaseDate: "1999-10-10",
    TotalCards:  62,
}
```

### Card Distribution

| Rarity | Count | Notable Cards |
|--------|-------|---------------|
| Rare Holo | 15 | Ditto, Gengar, Dragonite, Articuno |
| Rare | 15 | Lapras, Muk, Hypno, Kabutops |
| Uncommon | 16 | Haunter, Slowbro, Omastar |
| Common | 14 | Gastly, Shellder, Omanyte, Kabuto |
| Trainer | 2 | Mysterious Fossil, Mr. Fuji |

### Fossil Pokemon Mechanic

Fossil introduced "Fossil Pokemon" that evolve from the Mysterious Fossil trainer card:

```go
// MysteriousFossil is a Trainer that plays as a Basic Pokemon
type MysteriousFossil struct {
    TrainerCard
    HP          int    // 10 HP
    CanAttack   bool   // false
    CanRetreat  bool   // false
    GivesNoPrize bool  // true
    EvolvesTo   []string // ["Kabuto", "Omanyte", "Aerodactyl"]
}

// CanEvolveFossil checks if a Pokemon can evolve from Mysterious Fossil
func CanEvolveFossil(pokemon string) bool {
    fossilEvolutions := map[string]bool{
        "Kabuto":     true,
        "Omanyte":    true,
        "Aerodactyl": true,
    }
    return fossilEvolutions[pokemon]
}
```

### Ditto - The Most Complex Card

Ditto has one of the most complex abilities in the original sets:

```go
// DittoTransform implements Ditto's Transform Pokemon Power
type DittoTransform struct {
    IsActive         bool
    CopiedPokemon    *PokemonCard // The defending Pokemon being copied
}

// ApplyTransform applies Ditto's transformation
func (ditto *GamePokemon) ApplyTransform(defender *GamePokemon) {
    if !ditto.IsActive {
        return // Transform only works while Active
    }

    if ditto.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
        return // Transform disabled by status
    }

    ditto.Transform = &DittoTransform{
        IsActive:      true,
        CopiedPokemon: defender.Card,
    }

    // When transformed, Ditto copies:
    // - HP (max HP, not current damage)
    // - Type
    // - Weakness
    // - Resistance
    // - Attacks
    // - Retreat Cost

    // Ditto does NOT copy:
    // - Pokemon Powers/Abilities (keeps Transform)
    // - Evolution capability (cannot evolve)

    // Special: Ditto's attached energy counts as ANY type
}

// GetEffectiveStats returns Ditto's current stats (transformed or not)
func (ditto *GamePokemon) GetEffectiveStats() *EffectiveStats {
    if ditto.Transform == nil || !ditto.Transform.IsActive {
        // Return base Ditto stats
        return &EffectiveStats{
            HP:         50,
            Types:      []string{"Colorless"},
            Weakness:   TypeModifier{Type: "Fighting", Value: "x2"},
            Resistance: TypeModifier{Type: "Psychic", Value: "-30"},
            Attacks:    []Attack{}, // Ditto has no attacks of its own
        }
    }

    // Return copied stats
    copied := ditto.Transform.CopiedPokemon
    return &EffectiveStats{
        HP:         copied.HP,
        Types:      copied.Types,
        Weakness:   copied.Weakness,
        Resistance: copied.Resistance,
        Attacks:    copied.Attacks,
        // Retreat cost is also copied
        RetreatCost: copied.RetreatCost,
    }
}
```

### Legendary Birds

Fossil introduced the Legendary Bird trio with unique attacks:

| Pokemon | HP | Signature Attack | Effect |
|---------|-----|------------------|--------|
| Articuno | 70 | Blizzard (50) | Flip coin: heads = 10 to all opponent bench |
| Moltres | 70 | Wildfire | Discard fire energy to discard opponent's deck |
| Zapdos | 80 | Thunderstorm (70) | Damages all benched Pokemon (both players) |

```go
// ZapdosThunderstorm deals splash damage to ALL benched Pokemon
func ZapdosThunderstorm(zapdos *GamePokemon, defender *GamePokemon,
    myBench []*GamePokemon, oppBench []*GamePokemon) {

    // Main attack damage
    defender.TakeDamage(70)

    // Splash damage to all benched Pokemon
    // (Bench damage doesn't apply weakness/resistance)
    for _, poke := range myBench {
        poke.TakeDamage(10)
    }
    for _, poke := range oppBench {
        poke.TakeDamage(10)
    }
}
```

### Gengar's Curse

```go
// GengarCurse moves damage counters to opponent's Pokemon
func GengarCurse(opponent *Player) error {
    // Select opponent Pokemon with damage
    var damagedPokemon []*GamePokemon
    for _, poke := range opponent.GetAllPokemon() {
        if poke.DamageCounters > 0 {
            damagedPokemon = append(damagedPokemon, poke)
        }
    }

    if len(damagedPokemon) == 0 {
        return fmt.Errorf("no damaged Pokemon to curse")
    }

    // Select source (Pokemon to take damage FROM)
    source := selectPokemon(damagedPokemon, "Select Pokemon to take damage counter from")

    // Select destination (Pokemon to move damage TO)
    allOpponentPokemon := opponent.GetAllPokemon()
    // Can move to any opponent Pokemon, even undamaged
    dest := selectPokemon(allOpponentPokemon, "Select Pokemon to receive damage counter")

    // Move one damage counter
    source.DamageCounters--
    dest.DamageCounters++
    source.CurrentHP += 10
    dest.CurrentHP -= 10

    return nil
}
```

---

## Base Set 2 (04)

**Set Code:** `base2`
**Release Date:** February 24, 2000
**Total Cards:** 130
**Series:** Original

### Set Information Object

```go
baseSet2Info := SetInfo{
    ID:          "base2",
    Name:        "Base Set 2",
    Series:      "Original",
    ReleaseDate: "2000-02-24",
    TotalCards:  130,
}
```

### Set Composition

Base Set 2 is a compilation set containing reprints from Base Set and Jungle:

| Source | Cards | Examples |
|--------|-------|----------|
| Base Set | ~80 | Charizard, Blastoise, Bill, Professor Oak |
| Jungle | ~50 | Scyther, Wigglytuff, Snorlax, Mr. Mime |

### Programming Notes

1. **Identical Cards**: Cards in Base Set 2 are functionally identical to their Base Set/Jungle counterparts
2. **Different IDs**: Use `base2-XXX` format for set identification
3. **Deck Building**: In formats allowing Base Set 2, you can run up to 4 copies total of a card (e.g., 2 Base Set Charizard + 2 Base Set 2 Charizard = 4 total)

```go
// CheckSameCard determines if two cards are the same for deck building
func CheckSameCard(card1, card2 *Card) bool {
    // Compare by name (not by ID)
    // Charizard from Base Set = Charizard from Base Set 2
    return card1.Name == card2.Name
}

// CountCardCopies counts total copies of a card in deck
func CountCardCopies(deck []Card, cardName string) int {
    count := 0
    for _, card := range deck {
        if card.Name == cardName {
            count++
        }
    }
    return count
}
```

---

## Team Rocket (05)

**Set Code:** `rocket`
**Release Date:** April 24, 2000
**Total Cards:** 83
**Series:** Original

### Set Information Object

```go
teamRocketInfo := SetInfo{
    ID:          "rocket",
    Name:        "Team Rocket",
    Series:      "Original",
    ReleaseDate: "2000-04-24",
    TotalCards:  83,
}
```

### Card Distribution

| Rarity | Count | Notable Cards |
|--------|-------|---------------|
| Rare Holo | 17 | Dark Charizard, Dark Blastoise, Dark Dragonite |
| Rare | 17 | Dark Alakazam, Dark Slowbro, Rainbow Energy |
| Uncommon | 25 | Dark Charmeleon, Dark Wartortle |
| Common | 24 | Dark Raticate, Rocket's Sneak Attack |

### Dark Pokemon Mechanic

"Dark" Pokemon are alternate versions of existing Pokemon with different stats and attacks:

```go
// Dark Pokemon have these characteristics:
// - Lower HP than regular counterparts
// - Often more aggressive/disruptive attacks
// - Different evolution chains (Dark Charmeleon -> Dark Charizard)

type DarkPokemonCard struct {
    PokemonCard
    IsDark bool // True for Dark Pokemon
}

// Example: Comparing Charizard versions
// Base Set Charizard: 120 HP, Energy Burn + Fire Spin
// Dark Charizard: 80 HP, Nail Flick + Continuous Fireball
```

### Dark Charizard's Continuous Fireball

One of the most unique attack mechanics:

```go
// ContinuousFireball is a variable coin flip damage attack
func ContinuousFireball(charizard *GamePokemon) (damage int, discardedEnergy int) {
    // Count Fire Energy cards attached
    fireEnergyCount := 0
    var fireEnergyCards []*AttachedEnergy

    for _, energy := range charizard.AttachedEnergy {
        if energy.Card.EnergyType == "Fire" {
            fireEnergyCount++
            fireEnergyCards = append(fireEnergyCards, energy)
        }
    }

    // Flip coins equal to Fire Energy count
    headsCount := 0
    for i := 0; i < fireEnergyCount; i++ {
        if flipCoin() {
            headsCount++
        }
    }

    // Damage = 50 per heads
    damage = headsCount * 50

    // Must discard Fire Energy equal to heads flipped
    for i := 0; i < headsCount && i < len(fireEnergyCards); i++ {
        removeEnergy(charizard, fireEnergyCards[i])
        discardedEnergy++
    }

    return damage, discardedEnergy
}
```

### Special Energy Cards

Team Rocket introduced Special Energy beyond Double Colorless:

#### Rainbow Energy

```go
// RainbowEnergy implementation
type RainbowEnergy struct {
    EnergyCard
    // Counts as all types while in play
    // Deals 10 damage when attached
}

func AttachRainbowEnergy(pokemon *GamePokemon, rainbow *RainbowEnergy) {
    // Deal 10 damage to Pokemon when attached
    pokemon.TakeDamage(10)

    // Attach as "Any" type energy
    pokemon.AttachedEnergy = append(pokemon.AttachedEnergy, &AttachedEnergy{
        Card:       rainbow,
        IsRainbow:  true,
        ProvidedAmount: 1,
    })
}
```

#### Full Heal Energy & Potion Energy

```go
// Full Heal Energy removes status conditions when attached
func AttachFullHealEnergy(pokemon *GamePokemon) {
    pokemon.ClearAllStatusConditions()
    // Then provides 1 Colorless energy
}

// Potion Energy heals when attached
func AttachPotionEnergy(pokemon *GamePokemon) {
    pokemon.Heal(10) // 1 damage counter
    // Then provides 1 Colorless energy
}
```

### Team Rocket Trainer Cards

| Card | Effect | Type |
|------|--------|------|
| Here Comes Team Rocket! | Flip all prizes face-up | Information |
| Rocket's Sneak Attack | Look at opponent's hand, discard 1 Trainer | Disruption |
| Imposter Oak's Revenge | Shuffle hand, opponent draws 4 | Disruption |
| The Boss's Way | Search deck for evolution of Dark Pokemon | Search |
| Nightly Garbage Run | Return 3 basic Energy or Pokemon from discard | Recovery |
| Goop Gas Attack | Disable all Pokemon Powers until end of turn | Power Shutdown |

### Goop Gas Attack

One of the most impactful trainers for abilities:

```go
// ApplyGoopGasAttack disables ALL Pokemon Powers until end of next turn
func ApplyGoopGasAttack(gameState *GameState) {
    gameState.GoopGasActive = true
    gameState.GoopGasExpiresAfterTurn = gameState.CurrentTurn + 1
}

// CheckPokemonPowerUsable considers Goop Gas
func CheckPokemonPowerUsable(gameState *GameState, pokemon *GamePokemon) bool {
    // Goop Gas disables ALL powers
    if gameState.GoopGasActive {
        return false
    }

    // Normal status checks
    return pokemon.CanUsePower()
}
```

### Dark Vileplume's Hay Fever

Permanent Pokemon Power shutdown:

```go
// HayFever prevents all Trainers from being played
func CheckTrainerPlayable(gameState *GameState) bool {
    // Check if Dark Vileplume with Hay Fever is in play
    for _, player := range gameState.Players {
        for _, pokemon := range player.GetAllPokemon() {
            if pokemon.Card.Name == "Dark Vileplume" {
                // Check if Hay Fever is active (not status-disabled)
                if !pokemon.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
                    return false // No trainers can be played!
                }
            }
        }
    }
    return true
}
```

---

## Cross-Set Compatibility

### Deck Building Rules

```go
// ValidateDeck checks deck legality
func ValidateDeck(deck []Card) error {
    // 60 cards exactly
    if len(deck) != 60 {
        return fmt.Errorf("deck must have exactly 60 cards")
    }

    // Count copies of each card (by name)
    cardCounts := make(map[string]int)
    basicPokemon := 0

    for _, card := range deck {
        cardCounts[card.Name]++

        // Check for Basic Pokemon
        if pokemon, ok := card.(*PokemonCard); ok {
            if pokemon.Stage == "Basic" {
                basicPokemon++
            }
        }
    }

    // Max 4 copies of any card (except Basic Energy)
    for name, count := range cardCounts {
        if count > 4 && !isBasicEnergy(name) {
            return fmt.Errorf("too many copies of %s: %d", name, count)
        }
    }

    // Must have at least 1 Basic Pokemon
    if basicPokemon == 0 {
        return fmt.Errorf("deck must contain at least 1 Basic Pokemon")
    }

    return nil
}
```
