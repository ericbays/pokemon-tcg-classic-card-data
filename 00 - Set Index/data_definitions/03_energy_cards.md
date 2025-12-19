# Energy Card Schema Documentation

This document covers both Basic and Special Energy card schemas, including Go type definitions and implementation examples.

## Overview

Energy cards power Pokemon attacks. There are two categories:

| Type | Description | Examples |
|------|-------------|----------|
| **Basic Energy** | Single type, no special effects | Fire Energy, Water Energy |
| **Special Energy** | Provides energy with additional effects | Double Colorless, Rainbow Energy |

## Energy Types

The original Pokemon TCG features these energy types:

| Type | Color | Strong Against | Weak Against |
|------|-------|----------------|--------------|
| Fire | Red | Grass, Metal | Water |
| Water | Blue | Fire, Fighting | Lightning, Grass |
| Lightning | Yellow | Water, Colorless | Fighting |
| Grass | Green | Water, Fighting | Fire |
| Fighting | Brown | Lightning, Colorless | Psychic |
| Psychic | Purple | Fighting, Psychic | Psychic |
| Colorless | White/Gray | (None) | Fighting |

**Note:** Darkness, Metal, Dragon, and Fairy types were introduced in later sets.

## Go Type Definitions

```go
package energy

// EnergyCard represents an energy card
type EnergyCard struct {
    // Identity
    ID        string   `json:"id"`
    Name      string   `json:"name"`
    Number    int      `json:"number"`
    Set       SetInfo  `json:"set"`
    CardType  string   `json:"cardType"`  // "energy"
    Supertype string   `json:"supertype"` // "Energy"
    Subtypes  []string `json:"subtypes"`  // ["Basic"] or ["Special"]
    Rarity    string   `json:"rarity"`

    // Energy Properties
    EnergyType string          `json:"energyType"` // Primary type classification
    Provides   []EnergyProvide `json:"provides"`   // What energy it provides

    // Effect (Special Energy only)
    Effect *EnergyEffect `json:"effect,omitempty"`

    // Metadata
    Illustrator string       `json:"illustrator,omitempty"`
    ImageURL    string       `json:"imageUrl"`
    Legality    Legality     `json:"legality"`
    Gameplay    *EnergyGameplay `json:"gameplay,omitempty"`
}

// EnergyProvide describes what energy the card provides
type EnergyProvide struct {
    Type   string `json:"type"`   // Energy type (Fire, Water, Any, etc.)
    Amount int    `json:"amount"` // Amount provided (usually 1, can be 2)
}

// EnergyEffect describes special energy effects
type EnergyEffect struct {
    Text             string            `json:"text"`             // Printed text
    EffectType       string            `json:"effectType"`       // Categorized effect
    ProvidesEnergy   string            `json:"providesEnergy,omitempty"`   // "all_types", etc.
    EnergyAmount     int               `json:"energyAmount,omitempty"`
    AttachmentEffect *AttachmentEffect `json:"attachmentEffect,omitempty"`
    InPlayBehavior   string            `json:"inPlayBehavior,omitempty"`
    NotInPlayBehavior string           `json:"notInPlayBehavior,omitempty"`
    Conditions       []EnergyCondition `json:"conditions,omitempty"`
    Restrictions     []EnergyRestriction `json:"restrictions,omitempty"`
    SpecialRules     *EnergySpecialRules `json:"specialRules,omitempty"`
}

// AttachmentEffect describes effects when energy is attached
type AttachmentEffect struct {
    Action          string `json:"action"`          // damage, heal, etc.
    Amount          int    `json:"amount"`
    Target          string `json:"target"`          // attached_pokemon
    ApplyWeakness   bool   `json:"applyWeakness"`
    ApplyResistance bool   `json:"applyResistance"`
}

// EnergyCondition describes conditions for energy effects
type EnergyCondition struct {
    Type  string      `json:"type"`  // pokemon_type, evolution_stage, etc.
    Value interface{} `json:"value"`
}

// EnergyRestriction describes attachment restrictions
type EnergyRestriction struct {
    Type  string      `json:"type"`  // attach_to_type, once_per_turn, etc.
    Value interface{} `json:"value"`
}

// EnergySpecialRules contains special game rules
type EnergySpecialRules struct {
    CountsAsBasic    bool `json:"countsAsBasic"`
    DiscardAfterUse  bool `json:"discardAfterUse"`
    DamageOnAttach   int  `json:"damageOnAttach"`
    CanBeSearched    bool `json:"canBeSearched"`    // With Energy Search
    CanBeRetrieved   bool `json:"canBeRetrieved"`   // With Energy Retrieval
}

// EnergyGameplay contains strategic information
type EnergyGameplay struct {
    PrimaryUse string   `json:"primaryUse"`
    DeckTypes  []string `json:"deckTypes"`
    Notes      string   `json:"notes,omitempty"`
}
```

### Energy Effect Types

| Effect Type | Description | Example |
|-------------|-------------|---------|
| `none` | No special effect | Basic Energy |
| `multi_energy` | Provides multiple energy | Double Colorless |
| `conditional_energy` | Energy depends on conditions | (Future sets) |
| `damage_boost` | Increases attack damage | (Future sets) |
| `damage_reduction` | Reduces incoming damage | (Future sets) |
| `healing` | Heals when attached/used | Potion Energy |
| `status_immunity` | Prevents status conditions | Full Heal Energy |
| `retreat_modifier` | Affects retreat cost | (Future sets) |

## Loading Energy Cards

```go
package energy

import (
    "encoding/json"
    "fmt"
    "os"
)

// LoadEnergyCard loads an energy card from JSON
func LoadEnergyCard(filePath string) (*EnergyCard, error) {
    data, err := os.ReadFile(filePath)
    if err != nil {
        return nil, fmt.Errorf("reading file: %w", err)
    }

    var card EnergyCard
    if err := json.Unmarshal(data, &card); err != nil {
        return nil, fmt.Errorf("parsing JSON: %w", err)
    }

    if card.CardType != "energy" {
        return nil, fmt.Errorf("not an energy card: %s", card.CardType)
    }

    return &card, nil
}

// IsBasicEnergy checks if energy is basic type
func (e *EnergyCard) IsBasicEnergy() bool {
    for _, subtype := range e.Subtypes {
        if subtype == "Basic" {
            return true
        }
    }
    return false
}

// IsSpecialEnergy checks if energy is special type
func (e *EnergyCard) IsSpecialEnergy() bool {
    for _, subtype := range e.Subtypes {
        if subtype == "Special" {
            return true
        }
    }
    return false
}

// GetProvidedTypes returns all energy types this card can provide
func (e *EnergyCard) GetProvidedTypes() []string {
    var types []string
    for _, provide := range e.Provides {
        if provide.Type == "Any" {
            // Rainbow Energy - can provide any type
            types = append(types,
                "Fire", "Water", "Lightning", "Grass",
                "Fighting", "Psychic", "Colorless",
            )
        } else {
            types = append(types, provide.Type)
        }
    }
    return types
}

// GetTotalEnergy returns total energy amount provided
func (e *EnergyCard) GetTotalEnergy() int {
    total := 0
    for _, provide := range e.Provides {
        total += provide.Amount
    }
    return total
}
```

## Basic Energy Cards

Basic Energy cards are straightforward - they provide one energy of a single type.

### Basic Energy Data Structure

```go
// Example: Fire Energy
fireEnergy := &EnergyCard{
    ID:        "base1-098",
    Name:      "Fire Energy",
    Number:    98,
    CardType:  "energy",
    Supertype: "Energy",
    Subtypes:  []string{"Basic"},
    Rarity:    "Common",
    EnergyType: "Fire",
    Provides: []EnergyProvide{
        {Type: "Fire", Amount: 1},
    },
    Effect:    nil, // Basic energy has no special effect
    ImageURL:  "098_fire-energy.jpg",
}
```

### Basic Energy Types in Database

| Card Name | Energy Type | Set(s) Present |
|-----------|-------------|----------------|
| Fire Energy | Fire | Base Set, Base Set 2 |
| Water Energy | Water | Base Set, Base Set 2 |
| Lightning Energy | Lightning | Base Set, Base Set 2 |
| Grass Energy | Grass | Base Set, Base Set 2 |
| Fighting Energy | Fighting | Base Set, Base Set 2 |
| Psychic Energy | Psychic | Base Set, Base Set 2 |

## Special Energy Cards

Special Energy cards provide unique effects beyond basic energy provision.

### Double Colorless Energy

**The most important Special Energy in Base Set era.**

```go
// Double Colorless Energy
dce := &EnergyCard{
    ID:        "base1-096",
    Name:      "Double Colorless Energy",
    Number:    96,
    CardType:  "energy",
    Supertype: "Energy",
    Subtypes:  []string{"Special"},
    Rarity:    "Uncommon",
    EnergyType: "Special",
    Provides: []EnergyProvide{
        {Type: "Colorless", Amount: 2},
    },
    Effect: &EnergyEffect{
        Text:       "Provides 2 Colorless energy. Doesn't count as a basic Energy card.",
        EffectType: "multi_energy",
        SpecialRules: &EnergySpecialRules{
            CountsAsBasic:  false,
            CanBeSearched:  false,  // Energy Search finds Basic only
            CanBeRetrieved: false,  // Energy Retrieval retrieves Basic only
        },
    },
}
```

**Key Programming Considerations:**
- Provides 2 Colorless energy with a single attachment
- Does NOT count as Basic Energy (cannot be searched/retrieved with Basic Energy cards)
- Can fulfill Colorless requirements in attack costs
- Cannot fulfill specific type requirements (Fire, Water, etc.)

### Rainbow Energy (Team Rocket)

**Universal energy that comes with a drawback.**

```go
// Rainbow Energy
rainbowEnergy := &EnergyCard{
    ID:        "rocket-080",
    Name:      "Rainbow Energy",
    Number:    80,
    CardType:  "energy",
    Supertype: "Energy",
    Subtypes:  []string{"Special"},
    Rarity:    "Rare",
    EnergyType: "Special",
    Provides: []EnergyProvide{
        {Type: "Any", Amount: 1},
    },
    Effect: &EnergyEffect{
        Text: "Attach Rainbow Energy to 1 of your Pokemon. While in play, Rainbow Energy counts as every type of basic Energy but only provides 1 Energy at a time. (Doesn't count as a basic Energy card when not in play.) When you attach this card from your hand to 1 of your Pokemon, it does 10 damage to that Pokemon.",
        EffectType:     "multi_energy",
        ProvidesEnergy: "all_types",
        EnergyAmount:   1,
        AttachmentEffect: &AttachmentEffect{
            Action:          "damage",
            Amount:          10,
            Target:          "attached_pokemon",
            ApplyWeakness:   false,
            ApplyResistance: false,
        },
        InPlayBehavior:    "Counts as every type of basic Energy",
        NotInPlayBehavior: "Does not count as basic Energy",
    },
}
```

**Key Programming Considerations:**
- Counts as ALL energy types while in play
- Only provides 1 energy total (not 1 of each type)
- Deals 10 damage when attached from hand
- Does NOT deal damage when moved by effects (like Energy Trans)
- Does NOT count as Basic when in hand/deck/discard

### Full Heal Energy (Team Rocket)

```go
// Full Heal Energy
fullHealEnergy := &EnergyCard{
    ID:        "rocket-081",
    Name:      "Full Heal Energy",
    Number:    81,
    CardType:  "energy",
    Supertype: "Energy",
    Subtypes:  []string{"Special"},
    Rarity:    "Uncommon",
    EnergyType: "Special",
    Provides: []EnergyProvide{
        {Type: "Colorless", Amount: 1},
    },
    Effect: &EnergyEffect{
        Text:       "Full Heal Energy provides 1 Colorless energy. When you attach this card from your hand to 1 of your Pokemon, the Pokemon is no longer affected by a Special Condition.",
        EffectType: "status_immunity",
        AttachmentEffect: &AttachmentEffect{
            Action: "remove_status",
            Target: "attached_pokemon",
        },
    },
}
```

### Potion Energy (Team Rocket)

```go
// Potion Energy
potionEnergy := &EnergyCard{
    ID:        "rocket-082",
    Name:      "Potion Energy",
    Number:    82,
    CardType:  "energy",
    Supertype: "Energy",
    Subtypes:  []string{"Special"},
    Rarity:    "Uncommon",
    EnergyType: "Special",
    Provides: []EnergyProvide{
        {Type: "Colorless", Amount: 1},
    },
    Effect: &EnergyEffect{
        Text:       "Potion Energy provides 1 Colorless energy. When you attach this card from your hand to 1 of your Pokemon, remove 1 damage counter from that Pokemon.",
        EffectType: "healing",
        AttachmentEffect: &AttachmentEffect{
            Action: "heal",
            Amount: 10, // 1 damage counter = 10 damage
            Target: "attached_pokemon",
        },
    },
}
```

## Energy Management System

### In-Game Energy Representation

```go
package game

// AttachedEnergy represents energy attached to a Pokemon
type AttachedEnergy struct {
    Card         *energy.EnergyCard
    CardID       string

    // What the energy provides (can change based on abilities)
    ProvidedType string   // Current type being provided
    ProvidedAmount int    // Amount of energy (usually 1, 2 for DCE)

    // Special state
    ConvertedType string  // If converted by ability (Energy Burn)
    IsRainbow     bool    // Tracks Rainbow Energy for type flexibility
}

// NewAttachedEnergy creates a new attached energy from a card
func NewAttachedEnergy(card *energy.EnergyCard) *AttachedEnergy {
    ae := &AttachedEnergy{
        Card:           card,
        CardID:         card.ID,
        ProvidedAmount: card.GetTotalEnergy(),
    }

    // Set provided type
    if len(card.Provides) > 0 {
        ae.ProvidedType = card.Provides[0].Type
    }

    // Check for Rainbow Energy
    for _, provide := range card.Provides {
        if provide.Type == "Any" {
            ae.IsRainbow = true
            break
        }
    }

    return ae
}

// CanProvideType checks if this energy can fulfill a type requirement
func (ae *AttachedEnergy) CanProvideType(requiredType string) bool {
    // If converted by an ability
    if ae.ConvertedType != "" {
        return ae.ConvertedType == requiredType
    }

    // Rainbow Energy can provide any type
    if ae.IsRainbow {
        return true
    }

    // Colorless can only fulfill Colorless requirements
    if requiredType == "Colorless" {
        return true // Any type can fulfill Colorless
    }

    return ae.ProvidedType == requiredType
}
```

### Energy Attachment Logic

```go
// AttachEnergy handles attaching energy to a Pokemon
func (game *GameState) AttachEnergy(
    player *Player,
    energyCard *energy.EnergyCard,
    targetPokemon *GamePokemon,
) error {
    // Check once-per-turn normal attachment
    if !player.HasAttachedEnergyThisTurn {
        // This is the normal energy attachment
        player.HasAttachedEnergyThisTurn = true
    } else if !isFromAbility {
        // Already attached this turn (without ability bypass)
        return fmt.Errorf("already attached energy this turn")
    }

    // Create attached energy
    attachedEnergy := NewAttachedEnergy(energyCard)

    // Handle attachment effects for special energy
    if energyCard.Effect != nil && energyCard.Effect.AttachmentEffect != nil {
        effect := energyCard.Effect.AttachmentEffect

        switch effect.Action {
        case "damage":
            // Rainbow Energy does 10 damage when attached
            targetPokemon.TakeDamage(effect.Amount)

        case "heal":
            // Potion Energy heals 10 damage
            targetPokemon.Heal(effect.Amount)

        case "remove_status":
            // Full Heal Energy removes status conditions
            targetPokemon.ClearStatusConditions()
        }
    }

    // Attach the energy
    targetPokemon.AttachedEnergy = append(targetPokemon.AttachedEnergy, attachedEnergy)

    // Remove from player's hand
    game.RemoveCardFromHand(player, energyCard)

    return nil
}
```

### Energy Requirement Checking

```go
// CheckEnergyRequirement verifies attack cost can be paid
func CheckEnergyRequirement(
    pokemon *GamePokemon,
    attackCost []string,
) bool {
    // Count available energy by type
    energyPool := make(map[string]int)
    colorlessPool := 0
    rainbowEnergy := []*AttachedEnergy{}

    for _, ae := range pokemon.AttachedEnergy {
        if ae.IsRainbow {
            rainbowEnergy = append(rainbowEnergy, ae)
        } else if ae.ProvidedType == "Colorless" || ae.ConvertedType == "Colorless" {
            colorlessPool += ae.ProvidedAmount
        } else {
            t := ae.ProvidedType
            if ae.ConvertedType != "" {
                t = ae.ConvertedType
            }
            energyPool[t] += ae.ProvidedAmount
        }
    }

    // Count requirements
    specificNeeded := make(map[string]int)
    colorlessNeeded := 0

    for _, req := range attackCost {
        if req == "Colorless" {
            colorlessNeeded++
        } else {
            specificNeeded[req]++
        }
    }

    // Try to fulfill specific requirements first
    for energyType, needed := range specificNeeded {
        available := energyPool[energyType]

        if available >= needed {
            energyPool[energyType] -= needed
        } else {
            // Not enough specific energy, try Rainbow
            shortfall := needed - available
            if len(rainbowEnergy) >= shortfall {
                rainbowEnergy = rainbowEnergy[shortfall:]
                energyPool[energyType] = 0
            } else {
                return false // Cannot fulfill
            }
        }
    }

    // Now fulfill Colorless with any remaining energy
    totalRemaining := colorlessPool
    for _, count := range energyPool {
        totalRemaining += count
    }
    totalRemaining += len(rainbowEnergy)

    return totalRemaining >= colorlessNeeded
}
```

### Energy Retrieval and Search

```go
// CanBeFoundByEnergySearch checks if Energy Search can find this card
func (e *EnergyCard) CanBeFoundByEnergySearch() bool {
    // Energy Search finds Basic Energy only
    if e.IsBasicEnergy() {
        return true
    }

    // Check special rules for special energy
    if e.Effect != nil && e.Effect.SpecialRules != nil {
        return e.Effect.SpecialRules.CanBeSearched
    }

    return false
}

// CanBeRetrievedByEnergyRetrieval checks if Energy Retrieval can get this card
func (e *EnergyCard) CanBeRetrievedByEnergyRetrieval() bool {
    // Energy Retrieval retrieves Basic Energy only
    if e.IsBasicEnergy() {
        return true
    }

    // Check special rules for special energy
    if e.Effect != nil && e.Effect.SpecialRules != nil {
        return e.Effect.SpecialRules.CanBeRetrieved
    }

    return false
}

// FindBasicEnergyInDiscard finds retrievable energy in discard pile
func FindBasicEnergyInDiscard(player *Player) []*energy.EnergyCard {
    var basicEnergy []*energy.EnergyCard

    for _, card := range player.DiscardPile {
        if energyCard, ok := card.(*energy.EnergyCard); ok {
            if energyCard.CanBeRetrievedByEnergyRetrieval() {
                basicEnergy = append(basicEnergy, energyCard)
            }
        }
    }

    return basicEnergy
}
```

## Energy Interactions with Abilities

### Charizard's Energy Burn

```go
// ApplyEnergyBurn converts all attached energy to Fire type
func ApplyEnergyBurn(charizard *GamePokemon) {
    for i := range charizard.AttachedEnergy {
        // Store original type for end of turn reset
        if charizard.AttachedEnergy[i].ConvertedType == "" {
            charizard.AttachedEnergy[i].OriginalType = charizard.AttachedEnergy[i].ProvidedType
        }
        charizard.AttachedEnergy[i].ConvertedType = "Fire"
    }
}

// ResetEnergyConversion resets energy types at end of turn
func ResetEnergyConversion(pokemon *GamePokemon) {
    for i := range pokemon.AttachedEnergy {
        if pokemon.AttachedEnergy[i].OriginalType != "" {
            pokemon.AttachedEnergy[i].ProvidedType = pokemon.AttachedEnergy[i].OriginalType
            pokemon.AttachedEnergy[i].ConvertedType = ""
            pokemon.AttachedEnergy[i].OriginalType = ""
        }
    }
}
```

### Ditto's Transform - Energy as Any Type

```go
// DittoEnergyAny makes Ditto's attached energy count as any type
func (ditto *GamePokemon) CanProvideEnergyForCopiedAttack(
    attackCost []string,
) bool {
    // When Ditto uses Transform, its energy counts as any type
    if ditto.IsTransformed {
        totalEnergy := 0
        for _, ae := range ditto.AttachedEnergy {
            totalEnergy += ae.ProvidedAmount
        }

        totalRequired := len(attackCost)
        return totalEnergy >= totalRequired
    }

    // Not transformed, use normal energy checking
    return CheckEnergyRequirement(ditto, attackCost)
}
```

## Energy Cards Reference Table

### Base Set Energy

| # | Name | Type | Provides | Special Effect |
|---|------|------|----------|----------------|
| 96 | Double Colorless Energy | Special | 2 Colorless | None (not Basic) |
| 97 | Fighting Energy | Basic | 1 Fighting | None |
| 98 | Fire Energy | Basic | 1 Fire | None |
| 99 | Grass Energy | Basic | 1 Grass | None |
| 100 | Lightning Energy | Basic | 1 Lightning | None |
| 101 | Psychic Energy | Basic | 1 Psychic | None |
| 102 | Water Energy | Basic | 1 Water | None |

### Team Rocket Energy

| # | Name | Type | Provides | Special Effect |
|---|------|------|----------|----------------|
| 17/80 | Rainbow Energy | Special | 1 Any | 10 damage on attach |
| 81 | Full Heal Energy | Special | 1 Colorless | Remove status on attach |
| 82 | Potion Energy | Special | 1 Colorless | Heal 10 on attach |
