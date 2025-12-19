# Pokemon Card Schema Documentation

This document provides comprehensive documentation for the Pokemon card data structure, including Go type definitions and implementation examples.

## Schema Overview

Pokemon cards are the core of the game, representing creatures that battle on the field. Each Pokemon card contains:
- **Identity**: ID, name, set information
- **Battle Stats**: HP, types, weakness, resistance, retreat cost
- **Evolution**: Stage, evolution chain
- **Abilities**: Pokemon Powers (passive or activated abilities)
- **Attacks**: Damaging moves with energy costs
- **Metadata**: Pokedex info, artwork, legality

## Go Type Definitions

### Core Pokemon Card Structure

```go
package pokemon

// PokemonCard represents a complete Pokemon card
type PokemonCard struct {
    // Identity
    ID        string   `json:"id"`        // Format: "{setCode}-{paddedNumber}"
    Name      string   `json:"name"`      // Pokemon name as printed
    Number    int      `json:"number"`    // Card number in set
    Set       SetInfo  `json:"set"`       // Set information
    CardType  string   `json:"cardType"`  // Always "pokemon"
    Supertype string   `json:"supertype"` // Always "Pokemon"
    Subtypes  []string `json:"subtypes"`  // ["Basic"], ["Stage 1"], ["Stage 2"]
    Rarity    string   `json:"rarity"`    // Common, Uncommon, Rare, Rare Holo

    // Battle Stats
    HP                   int           `json:"hp"`                   // Hit Points (10-400, multiples of 10)
    Types                []string      `json:"types"`                // Pokemon types (Fire, Water, etc.)
    Stage                string        `json:"stage"`                // Basic, Stage 1, Stage 2
    Weakness             *TypeModifier `json:"weakness"`             // Weakness type and value
    Resistance           *TypeModifier `json:"resistance"`           // Resistance type and value
    RetreatCost          []string      `json:"retreatCost"`          // Energy types required to retreat
    ConvertedRetreatCost int           `json:"convertedRetreatCost"` // Total retreat cost

    // Evolution
    EvolvesFrom string   `json:"evolvesFrom"` // Name of previous evolution (null if Basic)
    EvolvesTo   []string `json:"evolvesTo"`   // Names of possible evolutions

    // Abilities and Attacks
    Abilities []Ability `json:"abilities"` // Pokemon Powers
    Attacks   []Attack  `json:"attacks"`   // Attack moves

    // Metadata
    Pokedex     *PokedexInfo `json:"pokedex,omitempty"`
    FlavorText  string       `json:"flavorText,omitempty"`
    Illustrator string       `json:"illustrator"`
    ImageURL    string       `json:"imageUrl"`
    Rules       []string     `json:"rules,omitempty"`

    // Gameplay Analysis
    Legality Legality     `json:"legality"`
    Gameplay *GameplayInfo `json:"gameplay,omitempty"`

    // Historical
    CompetitiveHistory string   `json:"competitiveHistory,omitempty"`
    Rulings            []Ruling `json:"rulings,omitempty"`
}

// SetInfo contains information about the card set
type SetInfo struct {
    ID          string `json:"id"`          // Set code (base1, jungle, etc.)
    Name        string `json:"name"`        // Full set name
    Series      string `json:"series"`      // Series name (Original, Neo, etc.)
    ReleaseDate string `json:"releaseDate"` // ISO date format
    TotalCards  int    `json:"totalCards"`  // Number of cards in set
}

// TypeModifier represents weakness or resistance
type TypeModifier struct {
    Type  string `json:"type"`  // Energy type
    Value string `json:"value"` // "x2", "+30", "-30"
}

// PokedexInfo contains flavor information
type PokedexInfo struct {
    NationalNumber int    `json:"nationalNumber"`
    Category       string `json:"category"`
    Height         string `json:"height"`
    Weight         string `json:"weight"`
    Level          int    `json:"level,omitempty"`
}

// Legality indicates format legality
type Legality struct {
    Standard  bool `json:"standard"`
    Expanded  bool `json:"expanded"`
    Unlimited bool `json:"unlimited"`
}

// GameplayInfo provides strategic analysis
type GameplayInfo struct {
    Role       string   `json:"role"`       // Attacker, Support, Tank, etc.
    Strengths  []string `json:"strengths"`
    Weaknesses []string `json:"weaknesses"`
    Synergies  []string `json:"synergies"`
    Counters   []string `json:"counters"`
}

// Ruling represents an official game ruling
type Ruling struct {
    Date   string `json:"date,omitempty"`
    Ruling string `json:"ruling"`
    Source string `json:"source,omitempty"`
}
```

### Ability Structure

```go
// Ability represents a Pokemon Power, Poke-Power, Poke-Body, or Ability
type Ability struct {
    Name   string        `json:"name"`   // Ability name
    Type   string        `json:"type"`   // "Pokemon Power", "Poke-Power", etc.
    Text   string        `json:"text"`   // Full text as printed
    Effect *AbilityEffect `json:"effect,omitempty"`
}

// AbilityEffect contains structured effect data for game logic
type AbilityEffect struct {
    EffectType   string                 `json:"effectType"`   // Effect category
    Trigger      string                 `json:"trigger"`      // When ability can be used
    Timing       string                 `json:"timing"`       // Turn timing
    Target       string                 `json:"target"`       // What it affects
    Restrictions []string               `json:"restrictions"` // Usage restrictions
    Parameters   map[string]interface{} `json:"parameters"`   // Effect-specific data
}
```

#### Ability Effect Types

| Effect Type | Description | Example |
|-------------|-------------|---------|
| `damage_transfer` | Move damage counters between Pokemon | Alakazam's Damage Swap |
| `energy_conversion` | Convert energy types | Charizard's Energy Burn |
| `energy_acceleration` | Attach extra energy | Blastoise's Rain Dance |
| `healing` | Remove damage counters | Various healing powers |
| `damage_prevention` | Block damage above threshold | Mr. Mime's Invisible Wall |
| `damage_boost` | Increase damage output | Various attack boosters |
| `status_immunity` | Prevent status conditions | Various immunities |
| `special` | Unique mechanics | Ditto's Transform |

#### Ability Triggers

| Trigger | Description |
|---------|-------------|
| `once_per_turn` | Can use once per turn |
| `unlimited_per_turn` | Can use multiple times per turn |
| `passive` | Always active |
| `on_damage` | Triggers when Pokemon is damaged |
| `on_attack` | Triggers when attacking |
| `while_active` | Only works while Active Pokemon |

### Attack Structure

```go
// Attack represents an attack a Pokemon can use
type Attack struct {
    Name                string        `json:"name"`
    Cost                []string      `json:"cost"`                // Energy types required
    ConvertedEnergyCost int           `json:"convertedEnergyCost"` // Total energy cost
    Damage              string        `json:"damage"`              // "30", "100", "30+", "10x"
    BaseDamage          int           `json:"baseDamage"`          // Numeric base damage
    Text                string        `json:"text"`                // Effect description
    Effect              *AttackEffect `json:"effect,omitempty"`
}

// AttackEffect contains structured attack effect data
type AttackEffect struct {
    EffectType     string            `json:"effectType"`
    CoinFlip       *CoinFlipEffect   `json:"coinFlip,omitempty"`
    Conditions     []AttackCondition `json:"conditions,omitempty"`
    StatusCondition string           `json:"statusCondition,omitempty"`
    SelfDamage     interface{}       `json:"selfDamage,omitempty"`     // int or object
    EnergyDiscard  *EnergyDiscard    `json:"energyDiscard,omitempty"`
    BenchDamage    interface{}       `json:"benchDamage,omitempty"`    // int or object
    Parameters     map[string]interface{} `json:"parameters,omitempty"`
}

// CoinFlipEffect defines coin flip mechanics
type CoinFlipEffect struct {
    Count   int              `json:"count"`   // Number of coins
    OnHeads *CoinFlipResult  `json:"onHeads"` // Result on heads
    OnTails *CoinFlipResult  `json:"onTails"` // Result on tails
}

// CoinFlipResult defines what happens on a coin flip result
type CoinFlipResult struct {
    Damage          int    `json:"damage,omitempty"`
    DamagePerHead   int    `json:"damagePerHead,omitempty"`
    Effect          string `json:"effect,omitempty"`
    StatusCondition string `json:"statusCondition,omitempty"`
    SelfDamage      int    `json:"selfDamage,omitempty"`
    Fail            bool   `json:"fail,omitempty"`
    PreventDamage   bool   `json:"preventDamage,omitempty"`
}

// EnergyDiscard defines energy discard requirements
type EnergyDiscard struct {
    Count        interface{} `json:"count"` // int or "all" or "heads_flipped"
    Type         string      `json:"type"`  // "any", "specific", or energy type
    SpecificType string      `json:"specificType,omitempty"`
}

// AttackCondition defines conditions that modify attacks
type AttackCondition struct {
    Type      string      `json:"type"`      // Condition type
    Scaling   interface{} `json:"scaling"`   // How it scales
    OnSuccess interface{} `json:"onSuccess"` // Effect when met
    OnFailure interface{} `json:"onFailure"` // Effect when not met
}
```

#### Attack Effect Types

| Effect Type | Description | Example |
|-------------|-------------|---------|
| `none` | No special effect | Basic damage attacks |
| `status_condition` | Inflicts status | Paralyze, Poison, etc. |
| `self_damage` | Damages self | Thunder Jolt |
| `energy_discard` | Discards energy as cost | Fire Spin |
| `coin_flip_damage` | Damage based on flips | Continuous Fireball |
| `bench_damage` | Damages bench Pokemon | Spark |
| `scaling_damage` | Damage scales with condition | Hydro Pump |
| `healing` | Heals damage | Drain, Absorb |

## Loading and Parsing Pokemon Cards

```go
package pokemon

import (
    "encoding/json"
    "fmt"
    "os"
    "path/filepath"
    "strings"
)

// CardLoader handles loading Pokemon cards from JSON files
type CardLoader struct {
    BaseDir string
}

// NewCardLoader creates a new card loader
func NewCardLoader(baseDir string) *CardLoader {
    return &CardLoader{BaseDir: baseDir}
}

// LoadPokemonCard loads a single Pokemon card from a JSON file
func (cl *CardLoader) LoadPokemonCard(filePath string) (*PokemonCard, error) {
    data, err := os.ReadFile(filePath)
    if err != nil {
        return nil, fmt.Errorf("reading file: %w", err)
    }

    var card PokemonCard
    if err := json.Unmarshal(data, &card); err != nil {
        return nil, fmt.Errorf("parsing JSON: %w", err)
    }

    // Validate it's a Pokemon card
    if card.CardType != "pokemon" {
        return nil, fmt.Errorf("not a Pokemon card: %s", card.CardType)
    }

    return &card, nil
}

// LoadAllPokemon loads all Pokemon cards from all sets
func (cl *CardLoader) LoadAllPokemon() ([]*PokemonCard, error) {
    var cards []*PokemonCard

    setDirs := []string{
        "01 - Base Set 1 (BS)",
        "02 - Jungle (JU)",
        "03 - Fossil (FO)",
        "04 - Base Set 2 (B2)",
        "05 - Team Rocket (RO)",
    }

    for _, setDir := range setDirs {
        cardPath := filepath.Join(cl.BaseDir, setDir, "card_details")
        files, err := os.ReadDir(cardPath)
        if err != nil {
            continue
        }

        for _, file := range files {
            if !strings.HasSuffix(file.Name(), ".json") {
                continue
            }

            card, err := cl.LoadPokemonCard(filepath.Join(cardPath, file.Name()))
            if err != nil {
                continue // Skip non-Pokemon cards
            }

            cards = append(cards, card)
        }
    }

    return cards, nil
}

// FindByName finds a Pokemon by name
func (cl *CardLoader) FindByName(cards []*PokemonCard, name string) []*PokemonCard {
    var results []*PokemonCard
    for _, card := range cards {
        if strings.EqualFold(card.Name, name) {
            results = append(results, card)
        }
    }
    return results
}

// FindByType finds Pokemon by type
func (cl *CardLoader) FindByType(cards []*PokemonCard, typeName string) []*PokemonCard {
    var results []*PokemonCard
    for _, card := range cards {
        for _, t := range card.Types {
            if strings.EqualFold(t, typeName) {
                results = append(results, card)
                break
            }
        }
    }
    return results
}

// FindByStage finds Pokemon by evolution stage
func (cl *CardLoader) FindByStage(cards []*PokemonCard, stage string) []*PokemonCard {
    var results []*PokemonCard
    for _, card := range cards {
        if strings.EqualFold(card.Stage, stage) {
            results = append(results, card)
        }
    }
    return results
}
```

## In-Game Pokemon Representation

When using cards in an actual game, you need additional state:

```go
package game

import "pokemon"

// GamePokemon represents a Pokemon in play during a game
type GamePokemon struct {
    Card           *pokemon.PokemonCard

    // Current state
    CurrentHP      int           // Remaining HP
    DamageCounters int           // Number of damage counters (damage / 10)
    AttachedEnergy []AttachedEnergy

    // Status
    StatusConditions []StatusCondition

    // Turn tracking
    TurnPlayed     int  // Turn number when played
    EvolvedThisTurn bool
    UsedPowerThisTurn map[string]bool // Track once-per-turn powers

    // Position
    IsActive       bool
}

// AttachedEnergy represents energy attached to a Pokemon
type AttachedEnergy struct {
    CardID     string   // ID of the energy card
    EnergyType string   // Type of energy it provides
    Amount     int      // Amount provided (usually 1, 2 for DCE)
    IsSpecial  bool     // Whether it's a Special Energy
    Card       interface{} // The actual energy card data
}

// StatusCondition represents a status effect
type StatusCondition struct {
    Condition     string // Asleep, Confused, Paralyzed, Poisoned, Burned
    TurnsRemaining int   // For conditions that expire
}

// NewGamePokemon creates a new in-game Pokemon from a card
func NewGamePokemon(card *pokemon.PokemonCard, turnNumber int) *GamePokemon {
    return &GamePokemon{
        Card:              card,
        CurrentHP:         card.HP,
        DamageCounters:    0,
        AttachedEnergy:    make([]AttachedEnergy, 0),
        StatusConditions:  make([]StatusCondition, 0),
        TurnPlayed:        turnNumber,
        EvolvedThisTurn:   false,
        UsedPowerThisTurn: make(map[string]bool),
        IsActive:          false,
    }
}

// TakeDamage applies damage to the Pokemon
func (gp *GamePokemon) TakeDamage(amount int) {
    // Damage is in multiples of 10
    counters := amount / 10
    gp.DamageCounters += counters
    gp.CurrentHP = gp.Card.HP - (gp.DamageCounters * 10)
}

// IsKnockedOut checks if the Pokemon is knocked out
func (gp *GamePokemon) IsKnockedOut() bool {
    return gp.CurrentHP <= 0
}

// CanAttack checks if the Pokemon can attack
func (gp *GamePokemon) CanAttack() bool {
    // Cannot attack if affected by certain status conditions
    for _, status := range gp.StatusConditions {
        switch status.Condition {
        case "Asleep", "Paralyzed":
            return false
        }
    }
    return true
}

// CanRetreat checks if the Pokemon can retreat
func (gp *GamePokemon) CanRetreat() bool {
    // Cannot retreat if paralyzed or asleep
    for _, status := range gp.StatusConditions {
        switch status.Condition {
        case "Asleep", "Paralyzed":
            return false
        }
    }
    return true
}

// HasEnoughEnergyForAttack checks if enough energy is attached for an attack
func (gp *GamePokemon) HasEnoughEnergyForAttack(attack *pokemon.Attack) bool {
    // Count attached energy by type
    energyCounts := make(map[string]int)
    colorlessCount := 0

    for _, energy := range gp.AttachedEnergy {
        if energy.EnergyType == "Colorless" || energy.EnergyType == "Any" {
            colorlessCount += energy.Amount
        } else {
            energyCounts[energy.EnergyType] += energy.Amount
        }
    }

    // Check each required energy type
    colorlessNeeded := 0
    for _, required := range attack.Cost {
        if required == "Colorless" {
            colorlessNeeded++
            continue
        }

        if energyCounts[required] > 0 {
            energyCounts[required]--
        } else if colorlessCount > 0 {
            // Cannot use colorless for specific type requirements
            return false
        } else {
            return false
        }
    }

    // Check if we have enough for colorless requirements
    // Any type can fulfill colorless
    totalRemaining := colorlessCount
    for _, count := range energyCounts {
        totalRemaining += count
    }

    return totalRemaining >= colorlessNeeded
}

// CanUsePower checks if a Pokemon Power can be used
func (gp *GamePokemon) CanUsePower(ability *pokemon.Ability) bool {
    // Check if already used (for once-per-turn powers)
    if ability.Effect != nil && ability.Effect.Trigger == "once_per_turn" {
        if gp.UsedPowerThisTurn[ability.Name] {
            return false
        }
    }

    // Check restrictions
    if ability.Effect != nil {
        for _, restriction := range ability.Effect.Restrictions {
            switch restriction {
            case "not_asleep":
                if gp.HasStatus("Asleep") {
                    return false
                }
            case "not_confused":
                if gp.HasStatus("Confused") {
                    return false
                }
            case "not_paralyzed":
                if gp.HasStatus("Paralyzed") {
                    return false
                }
            }
        }
    }

    return true
}

// HasStatus checks if Pokemon has a specific status condition
func (gp *GamePokemon) HasStatus(condition string) bool {
    for _, status := range gp.StatusConditions {
        if status.Condition == condition {
            return true
        }
    }
    return false
}
```

## Example: Working with Specific Pokemon

### Charizard - Energy Burn + Fire Spin

```go
package examples

import (
    "pokemon"
    "game"
)

// HandleEnergyBurn processes Charizard's Energy Burn ability
func HandleEnergyBurn(charizard *game.GamePokemon) error {
    // Verify this is Charizard with Energy Burn
    if charizard.Card.Name != "Charizard" {
        return fmt.Errorf("not a Charizard")
    }

    // Find the Energy Burn ability
    var energyBurn *pokemon.Ability
    for i := range charizard.Card.Abilities {
        if charizard.Card.Abilities[i].Name == "Energy Burn" {
            energyBurn = &charizard.Card.Abilities[i]
            break
        }
    }

    if energyBurn == nil {
        return fmt.Errorf("Charizard doesn't have Energy Burn")
    }

    // Check if can use power
    if !charizard.CanUsePower(energyBurn) {
        return fmt.Errorf("cannot use Energy Burn (status condition)")
    }

    // Convert all attached energy to Fire type for this turn
    for i := range charizard.AttachedEnergy {
        charizard.AttachedEnergy[i].OriginalType = charizard.AttachedEnergy[i].EnergyType
        charizard.AttachedEnergy[i].EnergyType = "Fire"
    }

    return nil
}

// HandleFireSpin processes Charizard's Fire Spin attack
func HandleFireSpin(charizard *game.GamePokemon, defender *game.GamePokemon) (int, error) {
    // Verify has enough energy (4 Fire after Energy Burn)
    fireCount := 0
    for _, energy := range charizard.AttachedEnergy {
        if energy.EnergyType == "Fire" {
            fireCount += energy.Amount
        }
    }

    if fireCount < 4 {
        return 0, fmt.Errorf("not enough Fire energy: have %d, need 4", fireCount)
    }

    // Discard 2 energy cards (required cost)
    discarded := 0
    for i := len(charizard.AttachedEnergy) - 1; i >= 0 && discarded < 2; i-- {
        charizard.AttachedEnergy = append(
            charizard.AttachedEnergy[:i],
            charizard.AttachedEnergy[i+1:]...,
        )
        discarded++
    }

    // Calculate damage
    baseDamage := 100

    // Apply weakness
    finalDamage := baseDamage
    if defender.Card.Weakness != nil && defender.Card.Weakness.Type == "Fire" {
        if defender.Card.Weakness.Value == "x2" {
            finalDamage *= 2
        }
    }

    // Apply resistance
    if defender.Card.Resistance != nil && defender.Card.Resistance.Type == "Fire" {
        // Parse resistance value like "-30"
        finalDamage -= 30
    }

    // Minimum 0 damage
    if finalDamage < 0 {
        finalDamage = 0
    }

    return finalDamage, nil
}
```

### Blastoise - Rain Dance

```go
// HandleRainDance processes Blastoise's Rain Dance ability
func HandleRainDance(
    blastoise *game.GamePokemon,
    waterEnergy *game.EnergyCard,
    targetPokemon *game.GamePokemon,
) error {
    // Verify Blastoise has Rain Dance
    var rainDance *pokemon.Ability
    for i := range blastoise.Card.Abilities {
        if blastoise.Card.Abilities[i].Name == "Rain Dance" {
            rainDance = &blastoise.Card.Abilities[i]
            break
        }
    }

    if rainDance == nil {
        return fmt.Errorf("Blastoise doesn't have Rain Dance")
    }

    // Check if can use power
    if !blastoise.CanUsePower(rainDance) {
        return fmt.Errorf("cannot use Rain Dance (status condition)")
    }

    // Verify energy is Water type
    if waterEnergy.EnergyType != "Water" {
        return fmt.Errorf("Rain Dance can only attach Water Energy")
    }

    // Verify target is a Water-type Pokemon
    isWaterType := false
    for _, t := range targetPokemon.Card.Types {
        if t == "Water" {
            isWaterType = true
            break
        }
    }

    if !isWaterType {
        return fmt.Errorf("Rain Dance can only attach to Water Pokemon")
    }

    // Attach the energy (this is in ADDITION to normal attachment)
    targetPokemon.AttachedEnergy = append(targetPokemon.AttachedEnergy, game.AttachedEnergy{
        CardID:     waterEnergy.ID,
        EnergyType: "Water",
        Amount:     1,
        IsSpecial:  false,
    })

    // Rain Dance can be used unlimited times per turn
    // (no need to mark as used)

    return nil
}
```

## Evolution Chain Lookup

```go
// EvolutionChain represents a complete evolution line
type EvolutionChain struct {
    Basic   []*pokemon.PokemonCard
    Stage1  []*pokemon.PokemonCard
    Stage2  []*pokemon.PokemonCard
}

// BuildEvolutionChain builds the evolution chain for a Pokemon
func BuildEvolutionChain(allCards []*pokemon.PokemonCard, pokemonName string) *EvolutionChain {
    chain := &EvolutionChain{}

    // Find all cards with this name
    var targetCards []*pokemon.PokemonCard
    for _, card := range allCards {
        if card.Name == pokemonName {
            targetCards = append(targetCards, card)
        }
    }

    if len(targetCards) == 0 {
        return nil
    }

    // Use first card to trace lineage
    target := targetCards[0]

    // Trace back to Basic
    current := target
    for current.EvolvesFrom != "" {
        // Find the previous evolution
        for _, card := range allCards {
            if card.Name == current.EvolvesFrom {
                current = card
                break
            }
        }
    }

    // Now build forward from Basic
    // Find all Basic cards of this line
    for _, card := range allCards {
        if card.Name == current.Name {
            chain.Basic = append(chain.Basic, card)
        }
    }

    // Find Stage 1 evolutions
    for _, card := range allCards {
        if card.EvolvesFrom == current.Name {
            chain.Stage1 = append(chain.Stage1, card)
        }
    }

    // Find Stage 2 evolutions
    if len(chain.Stage1) > 0 {
        for _, stage1 := range chain.Stage1 {
            for _, card := range allCards {
                if card.EvolvesFrom == stage1.Name {
                    chain.Stage2 = append(chain.Stage2, card)
                }
            }
        }
    }

    return chain
}
```

## Example Output

When you load Charizard from Base Set:

```json
{
  "id": "base1-004",
  "name": "Charizard",
  "number": 4,
  "cardType": "pokemon",
  "hp": 120,
  "types": ["Fire"],
  "stage": "Stage 2",
  "evolvesFrom": "Charmeleon",
  "abilities": [
    {
      "name": "Energy Burn",
      "type": "Pokemon Power",
      "text": "As often as you like during your turn (before your attack), you may turn all Energy attached to Charizard into Fire Energy for the rest of the turn...",
      "effect": {
        "type": "energy_conversion",
        "convertsTo": "Fire",
        "frequency": "unlimited_per_turn",
        "duration": "rest_of_turn"
      }
    }
  ],
  "attacks": [
    {
      "name": "Fire Spin",
      "cost": ["Fire", "Fire", "Fire", "Fire"],
      "damage": "100",
      "baseDamage": 100,
      "text": "Discard 2 Energy cards attached to Charizard in order to use this attack.",
      "effect": {
        "type": "energy_discard",
        "discardCount": 2,
        "discardType": "any_energy",
        "timing": "cost"
      }
    }
  ],
  "weakness": {"type": "Water", "value": "x2"},
  "resistance": {"type": "Fighting", "value": "-30"},
  "retreatCost": ["Colorless", "Colorless", "Colorless"]
}
```
