# Trainer Card Schema Documentation

This document covers both Trainer Item and Trainer Supporter card schemas, including Go type definitions and implementation examples.

## Overview

In the original Base Set era (1999-2000), all Trainer cards could be played without restriction. Modern rules later reclassified some powerful trainers as "Supporters" (limited to one per turn). This data supports both historical accuracy and modern rule interpretations.

### Card Subtypes

| Subtype | Description | Play Limit |
|---------|-------------|------------|
| **Item** | Standard trainer cards | Unlimited per turn |
| **Supporter** | Powerful effect trainers | One per turn (modern rules) |

## Go Type Definitions

### Trainer Item Cards

```go
package trainer

// TrainerItemCard represents a Trainer Item card
type TrainerItemCard struct {
    // Identity
    ID        string   `json:"id"`
    Name      string   `json:"name"`
    Number    int      `json:"number"`
    Set       SetInfo  `json:"set"`
    CardType  string   `json:"cardType"`  // "trainer" or "trainer-item"
    Supertype string   `json:"supertype"` // "Trainer"
    Subtypes  []string `json:"subtypes"`  // ["Item"]
    Rarity    string   `json:"rarity"`

    // Effect
    Effect TrainerEffect `json:"effect"`

    // Special Rules (for cards like Clefairy Doll)
    SpecialRules *SpecialTrainerRules `json:"specialRules,omitempty"`

    // Metadata
    Illustrator string   `json:"illustrator"`
    ImageURL    string   `json:"imageUrl"`
    Legality    Legality `json:"legality"`

    // Gameplay
    Gameplay *TrainerGameplay `json:"gameplay,omitempty"`
    Rulings  []Ruling         `json:"rulings,omitempty"`
}

// TrainerEffect describes the trainer's effect
type TrainerEffect struct {
    Text         string             `json:"text"`         // Full printed text
    EffectType   string             `json:"effectType"`   // Categorized effect
    Actions      []TrainerAction    `json:"actions"`      // Ordered actions
    Cost         *TrainerCost       `json:"cost,omitempty"`
    Requirements []TrainerRequirement `json:"requirements,omitempty"`
    CoinFlip     *CoinFlipMechanic  `json:"coinFlip,omitempty"`
    Targeting    *TargetingRules    `json:"targeting,omitempty"`
}

// TrainerAction represents a single action performed by the trainer
type TrainerAction struct {
    Action     string                 `json:"action"`     // Action type
    Amount     int                    `json:"amount,omitempty"`
    Target     string                 `json:"target,omitempty"`
    Condition  *ActionCondition       `json:"condition,omitempty"`
    Parameters map[string]interface{} `json:"parameters,omitempty"`
}

// TrainerCost defines the cost to play the trainer
type TrainerCost struct {
    Type        string `json:"type"`        // discard_cards, discard_energy, etc.
    Amount      int    `json:"amount"`
    Target      string `json:"target"`      // hand, energy_from_pokemon, etc.
    Description string `json:"description"`
}

// TrainerRequirement defines requirements to play the trainer
type TrainerRequirement struct {
    Type        string `json:"type"`        // cards_in_hand, pokemon_in_play, etc.
    Minimum     int    `json:"minimum,omitempty"`
    Description string `json:"description,omitempty"`
}

// SpecialTrainerRules for unusual trainers like Clefairy Doll
type SpecialTrainerRules struct {
    PlaysAsPokemon     bool               `json:"playsAsPokemon,omitempty"`
    AttachesToPokemon  bool               `json:"attachesToPokemon,omitempty"`
    AttachmentDuration string             `json:"attachmentDuration,omitempty"`
    PokemonStats       *TrainerPokemonStats `json:"pokemonStats,omitempty"`
}

// TrainerPokemonStats for trainers that play as Pokemon
type TrainerPokemonStats struct {
    HP             int  `json:"hp"`
    CanAttack      bool `json:"canAttack"`
    CanRetreat     bool `json:"canRetreat"`
    ImmuneToStatus bool `json:"immuneToStatus"`
    GivesNoPrize   bool `json:"givesNoPrize"`
}
```

### Trainer Action Types

| Action | Description | Example Card |
|--------|-------------|--------------|
| `draw_cards` | Draw cards from deck | Bill |
| `search_deck` | Search deck for cards | Computer Search |
| `heal_damage` | Remove damage counters | Potion |
| `remove_energy` | Remove energy from Pokemon | Energy Removal |
| `attach_energy` | Attach energy to Pokemon | (Special trainers) |
| `discard_hand` | Discard your hand | Professor Oak |
| `shuffle_deck` | Shuffle deck | (Many cards) |
| `switch_pokemon` | Switch active Pokemon | Switch |
| `return_pokemon` | Return Pokemon to hand | Scoop Up |
| `revive_pokemon` | Revive from discard | Revive |
| `boost_damage` | Increase attack damage | PlusPower |
| `reduce_damage` | Decrease incoming damage | Defender |
| `remove_status` | Remove status conditions | Full Heal |
| `force_switch` | Force opponent to switch | Gust of Wind |
| `view_cards` | Look at hidden cards | Pokedex |
| `rearrange_cards` | Reorder cards | Pokedex |
| `play_as_pokemon` | Play trainer as Pokemon | Clefairy Doll |
| `attach_to_pokemon` | Attach trainer to Pokemon | PlusPower, Defender |
| `recover_from_discard` | Return cards from discard | Energy Retrieval |
| `disable_pokemon_powers` | Disable Pokemon Powers | Goop Gas Attack |

### Trainer Supporter Cards

```go
// TrainerSupporterCard represents a Trainer Supporter card
type TrainerSupporterCard struct {
    // Identity
    ID        string   `json:"id"`
    Name      string   `json:"name"`
    Number    int      `json:"number"`
    Set       SetInfo  `json:"set"`
    CardType  string   `json:"cardType"`  // "trainer"
    Supertype string   `json:"supertype"` // "Trainer"
    Subtypes  []string `json:"subtypes"`  // ["Supporter"]
    Rarity    string   `json:"rarity"`

    // Historical Classification
    HistoricalClassification *HistoricalClass `json:"historicalClassification,omitempty"`

    // Effect
    Effect SupporterEffect `json:"effect"`

    // Usage Restrictions
    UsageRestriction *UsageRestriction `json:"usageRestriction,omitempty"`

    // Metadata
    Illustrator        string           `json:"illustrator"`
    ImageURL           string           `json:"imageUrl"`
    Legality           Legality         `json:"legality"`
    CompetitiveHistory string           `json:"competitiveHistory,omitempty"`
    Gameplay           *SupporterGameplay `json:"gameplay,omitempty"`
    Rulings            []Ruling         `json:"rulings,omitempty"`
}

// HistoricalClass tracks reclassification of cards
type HistoricalClass struct {
    OriginalSubtype      string `json:"originalSubtype"`
    ReclassifiedAs       string `json:"reclassifiedAs"`
    ReclassificationDate string `json:"reclassificationDate,omitempty"`
    Note                 string `json:"note,omitempty"`
}

// SupporterEffect describes the supporter's effect
type SupporterEffect struct {
    Text           string              `json:"text"`
    EffectType     string              `json:"effectType"`
    Actions        []SupporterAction   `json:"actions"`
    AffectsOpponent bool               `json:"affectsOpponent,omitempty"`
    TargetPlayer   string              `json:"targetPlayer,omitempty"` // self, opponent, both
    Cost           *TrainerCost        `json:"cost,omitempty"`
    Requirements   []TrainerRequirement `json:"requirements,omitempty"`
}

// SupporterAction represents an action performed by the supporter
type SupporterAction struct {
    Action     string                 `json:"action"`
    Amount     int                    `json:"amount,omitempty"`
    Target     string                 `json:"target,omitempty"`
    Condition  *ActionCondition       `json:"condition,omitempty"`
    Parameters map[string]interface{} `json:"parameters,omitempty"`
}

// UsageRestriction defines play restrictions
type UsageRestriction struct {
    OncePerTurn    bool                  `json:"oncePerTurn"`
    NotOnFirstTurn bool                  `json:"notOnFirstTurn,omitempty"`
    FormatSpecific *FormatRestrictions   `json:"formatSpecific,omitempty"`
}

// SupporterGameplay contains strategic analysis
type SupporterGameplay struct {
    Category       string   `json:"category"`       // Draw, Refresh, Search, etc.
    PowerLevel     string   `json:"powerLevel"`     // Low, Medium, High, Staple
    Timing         string   `json:"timing"`
    DeckInclusion  string   `json:"deckInclusion"`
    Synergies      []string `json:"synergies"`
    AntiSynergies  []string `json:"antiSynergies,omitempty"`
    Counters       []string `json:"counters,omitempty"`
    Tips           []string `json:"tips,omitempty"`
}
```

### Supporter Effect Types

| Effect Type | Description | Example |
|-------------|-------------|---------|
| `draw` | Draw cards | (Generic draw) |
| `hand_refresh` | Discard hand, draw new | Professor Oak |
| `search` | Search deck for cards | Pokemon Trader |
| `hand_disruption` | Disrupt opponent's hand | Lass, Impostor Oak |
| `deck_disruption` | Disrupt opponent's deck | (Various) |
| `recovery` | Recover cards from discard | (Various) |
| `multi_effect` | Multiple effects combined | (Various) |

## Loading Trainer Cards

```go
package trainer

import (
    "encoding/json"
    "fmt"
    "os"
)

// CardType constants
const (
    CardTypeTrainer     = "trainer"
    CardTypeTrainerItem = "trainer-item"
)

// LoadTrainerCard loads a trainer card and determines its subtype
func LoadTrainerCard(filePath string) (interface{}, error) {
    data, err := os.ReadFile(filePath)
    if err != nil {
        return nil, fmt.Errorf("reading file: %w", err)
    }

    // First, unmarshal to determine card type
    var baseCard struct {
        CardType string   `json:"cardType"`
        Subtypes []string `json:"subtypes"`
    }

    if err := json.Unmarshal(data, &baseCard); err != nil {
        return nil, fmt.Errorf("parsing base card: %w", err)
    }

    // Check if it's a trainer
    if baseCard.CardType != "trainer" && baseCard.CardType != "trainer-item" {
        return nil, fmt.Errorf("not a trainer card: %s", baseCard.CardType)
    }

    // Determine subtype
    for _, subtype := range baseCard.Subtypes {
        switch subtype {
        case "Supporter":
            var card TrainerSupporterCard
            if err := json.Unmarshal(data, &card); err != nil {
                return nil, fmt.Errorf("parsing supporter: %w", err)
            }
            return &card, nil
        case "Item":
            var card TrainerItemCard
            if err := json.Unmarshal(data, &card); err != nil {
                return nil, fmt.Errorf("parsing item: %w", err)
            }
            return &card, nil
        }
    }

    // Default to item card
    var card TrainerItemCard
    if err := json.Unmarshal(data, &card); err != nil {
        return nil, fmt.Errorf("parsing trainer: %w", err)
    }
    return &card, nil
}
```

## Implementing Trainer Effects

### Generic Trainer Executor

```go
package game

import (
    "fmt"
    "trainer"
)

// TrainerExecutor handles playing trainer cards
type TrainerExecutor struct {
    game *GameState
}

// ExecuteTrainerItem plays a trainer item card
func (te *TrainerExecutor) ExecuteTrainerItem(
    player *Player,
    card *trainer.TrainerItemCard,
) error {
    // Check requirements
    if err := te.checkRequirements(player, card.Effect.Requirements); err != nil {
        return fmt.Errorf("requirements not met: %w", err)
    }

    // Pay cost
    if card.Effect.Cost != nil {
        if err := te.payCost(player, card.Effect.Cost); err != nil {
            return fmt.Errorf("cannot pay cost: %w", err)
        }
    }

    // Execute actions in order
    for _, action := range card.Effect.Actions {
        if err := te.executeAction(player, &action); err != nil {
            return fmt.Errorf("action %s failed: %w", action.Action, err)
        }
    }

    // Move card to discard pile (unless special rules apply)
    if card.SpecialRules == nil || !card.SpecialRules.PlaysAsPokemon {
        player.DiscardPile = append(player.DiscardPile, card)
    }

    return nil
}

// executeAction handles individual trainer actions
func (te *TrainerExecutor) executeAction(player *Player, action *trainer.TrainerAction) error {
    switch action.Action {
    case "draw_cards":
        return te.actionDrawCards(player, action.Amount)
    case "search_deck":
        return te.actionSearchDeck(player, action)
    case "heal_damage":
        return te.actionHealDamage(player, action)
    case "switch_pokemon":
        return te.actionSwitch(player)
    case "boost_damage":
        return te.actionBoostDamage(player, action)
    case "discard_hand":
        return te.actionDiscardHand(player)
    // ... more actions
    default:
        return fmt.Errorf("unknown action: %s", action.Action)
    }
}

func (te *TrainerExecutor) actionDrawCards(player *Player, amount int) error {
    for i := 0; i < amount; i++ {
        if len(player.Deck) == 0 {
            // Out of cards - game loss condition (handled elsewhere)
            return nil
        }
        card := player.Deck[0]
        player.Deck = player.Deck[1:]
        player.Hand = append(player.Hand, card)
    }
    return nil
}

func (te *TrainerExecutor) actionSearchDeck(player *Player, action *trainer.TrainerAction) error {
    target := action.Target
    params := action.Parameters

    // Present deck to player for selection
    // (In a real implementation, this would involve UI interaction)

    selectedCard, err := te.game.UI.PromptCardSelection(
        player,
        player.Deck,
        target,
        params,
    )
    if err != nil {
        return err
    }

    // Remove from deck and add to destination
    destination := "hand"
    if d, ok := params["destination"].(string); ok {
        destination = d
    }

    te.removeCardFromDeck(player, selectedCard)

    switch destination {
    case "hand":
        player.Hand = append(player.Hand, selectedCard)
    case "bench":
        // For Pokemon search cards
        if err := te.game.PlayPokemonToBench(player, selectedCard); err != nil {
            return err
        }
    }

    // Shuffle deck afterward
    te.shuffleDeck(player)

    return nil
}

func (te *TrainerExecutor) actionHealDamage(player *Player, action *trainer.TrainerAction) error {
    amount := action.Amount // Damage to remove

    // Select target Pokemon
    target, err := te.game.UI.PromptPokemonSelection(player, "your_pokemon")
    if err != nil {
        return err
    }

    // Remove damage counters
    countersToRemove := amount / 10
    target.DamageCounters -= countersToRemove
    if target.DamageCounters < 0 {
        target.DamageCounters = 0
    }
    target.CurrentHP = target.Card.HP - (target.DamageCounters * 10)

    return nil
}
```

### Example: Computer Search

```go
// ExecuteComputerSearch implements Computer Search's effect
func (te *TrainerExecutor) ExecuteComputerSearch(player *Player) error {
    // Requirement: Must have at least 2 other cards in hand
    if len(player.Hand) < 3 { // Computer Search + 2 others
        return fmt.Errorf("need at least 2 other cards in hand to discard")
    }

    // Select 2 cards to discard
    cardsToDiscard, err := te.game.UI.PromptMultiCardSelection(
        player,
        player.Hand,
        2,
        "Select 2 cards to discard",
    )
    if err != nil {
        return err
    }

    // Discard the selected cards
    for _, card := range cardsToDiscard {
        te.removeCardFromHand(player, card)
        player.DiscardPile = append(player.DiscardPile, card)
    }

    // Search deck for any card
    selectedCard, err := te.game.UI.PromptCardSelection(
        player,
        player.Deck,
        "any_card",
        nil,
    )
    if err != nil {
        return err
    }

    // Add to hand
    te.removeCardFromDeck(player, selectedCard)
    player.Hand = append(player.Hand, selectedCard)

    // Shuffle deck
    te.shuffleDeck(player)

    return nil
}
```

### Example: Clefairy Doll (Plays as Pokemon)

```go
// ExecuteClefairyDoll handles Clefairy Doll's unique mechanic
func (te *TrainerExecutor) ExecuteClefairyDoll(player *Player, card *trainer.TrainerItemCard) error {
    // Check if bench has space
    if len(player.Bench) >= 5 {
        return fmt.Errorf("bench is full")
    }

    // Create a special "Pokemon" from the trainer
    dollPokemon := &GamePokemon{
        Card: &PokemonCard{
            ID:       card.ID,
            Name:     "Clefairy Doll",
            HP:       10,
            CardType: "trainer-as-pokemon",
        },
        CurrentHP:      10,
        DamageCounters: 0,
        IsTrainerCard:  true,
        OriginalCard:   card,

        // Special rules
        CanAttack:      false,
        CanRetreat:     false,
        ImmuneToStatus: true,
        GivesNoPrize:   true,
        CanSelfDiscard: true,
    }

    // Add to bench
    player.Bench = append(player.Bench, dollPokemon)

    return nil
}

// HandleClefairyDollKnockout processes when Clefairy Doll is knocked out
func HandleClefairyDollKnockout(doll *GamePokemon, opponent *Player) {
    // Clefairy Doll doesn't give a prize when knocked out
    // Just discard it
    // (Prize logic is skipped for this card)
}

// PlayerCanDiscardClefairyDoll allows player to voluntarily discard
func (te *TrainerExecutor) PlayerCanDiscardClefairyDoll(
    player *Player,
    doll *GamePokemon,
) error {
    if !doll.IsTrainerCard || !doll.CanSelfDiscard {
        return fmt.Errorf("cannot self-discard this Pokemon")
    }

    // Remove from play
    te.removePokemonFromPlay(player, doll)

    // Add original trainer card to discard
    player.DiscardPile = append(player.DiscardPile, doll.OriginalCard)

    return nil
}
```

### Example: Professor Oak (Supporter)

```go
// ExecuteProfessorOak implements Professor Oak's effect
func (te *TrainerExecutor) ExecuteProfessorOak(player *Player) error {
    // Cost: Discard entire hand
    for _, card := range player.Hand {
        player.DiscardPile = append(player.DiscardPile, card)
    }
    player.Hand = []interface{}{} // Empty hand

    // Requirement check: Must have at least 7 cards in deck
    if len(player.Deck) < 7 {
        return fmt.Errorf("not enough cards in deck (need 7, have %d)", len(player.Deck))
    }

    // Draw 7 cards
    for i := 0; i < 7; i++ {
        card := player.Deck[0]
        player.Deck = player.Deck[1:]
        player.Hand = append(player.Hand, card)
    }

    return nil
}
```

### Example: Gust of Wind (Force Switch)

```go
// ExecuteGustOfWind forces opponent to switch active Pokemon
func (te *TrainerExecutor) ExecuteGustOfWind(player *Player, opponent *Player) error {
    // Requirement: Opponent must have benched Pokemon
    if len(opponent.Bench) == 0 {
        return fmt.Errorf("opponent has no benched Pokemon")
    }

    // Player selects which of opponent's benched Pokemon to bring up
    selectedPokemon, err := te.game.UI.PromptOpponentPokemonSelection(
        player,
        opponent.Bench,
        "Select opponent's benched Pokemon to switch to Active",
    )
    if err != nil {
        return err
    }

    // Switch opponent's active with selected bench Pokemon
    oldActive := opponent.Active
    oldActive.IsActive = false
    opponent.Bench = append(opponent.Bench, oldActive)

    // Remove selected from bench
    te.removePokemonFromBench(opponent, selectedPokemon)
    selectedPokemon.IsActive = true
    opponent.Active = selectedPokemon

    return nil
}
```

### Example: Energy Removal

```go
// ExecuteEnergyRemoval removes energy from opponent's Pokemon
func (te *TrainerExecutor) ExecuteEnergyRemoval(player *Player, opponent *Player) error {
    // Select one of opponent's Pokemon with energy attached
    var validTargets []*GamePokemon
    allOpponentPokemon := append([]*GamePokemon{opponent.Active}, opponent.Bench...)

    for _, poke := range allOpponentPokemon {
        if len(poke.AttachedEnergy) > 0 {
            validTargets = append(validTargets, poke)
        }
    }

    if len(validTargets) == 0 {
        return fmt.Errorf("no opponent Pokemon have energy attached")
    }

    // Select target Pokemon
    targetPokemon, err := te.game.UI.PromptPokemonSelection(
        player,
        validTargets,
        "Select Pokemon to remove energy from",
    )
    if err != nil {
        return err
    }

    // Select which energy to remove
    energyToRemove, err := te.game.UI.PromptEnergySelection(
        player,
        targetPokemon.AttachedEnergy,
        "Select energy to discard",
    )
    if err != nil {
        return err
    }

    // Remove the energy
    te.removeEnergyFromPokemon(targetPokemon, energyToRemove)
    opponent.DiscardPile = append(opponent.DiscardPile, energyToRemove.Card)

    return nil
}
```

## Attachment Trainers (PlusPower, Defender)

Some trainers attach to Pokemon and provide effects until end of turn:

```go
// AttachmentTrainer represents a trainer attached to a Pokemon
type AttachmentTrainer struct {
    Card              *trainer.TrainerItemCard
    AttachedTo        *GamePokemon
    ExpiresEndOfTurn  bool
    Effect            TrainerAttachmentEffect
}

// TrainerAttachmentEffect defines attached trainer effects
type TrainerAttachmentEffect struct {
    DamageBoost     int  // +10, +20, etc.
    DamageReduction int  // -10, -20, etc.
    // Add more as needed
}

// AttachPlusPower attaches PlusPower to a Pokemon
func (te *TrainerExecutor) AttachPlusPower(
    player *Player,
    plusPowerCard *trainer.TrainerItemCard,
) error {
    // Select one of your Pokemon
    target, err := te.game.UI.PromptPokemonSelection(
        player,
        player.GetAllPokemon(),
        "Select Pokemon to attach PlusPower to",
    )
    if err != nil {
        return err
    }

    // Create attachment
    attachment := &AttachmentTrainer{
        Card:             plusPowerCard,
        AttachedTo:       target,
        ExpiresEndOfTurn: true,
        Effect: TrainerAttachmentEffect{
            DamageBoost: 10,
        },
    }

    // Add to player's active attachments
    player.AttachedTrainers = append(player.AttachedTrainers, attachment)

    return nil
}

// CleanupEndOfTurn removes expired trainer attachments
func (te *TrainerExecutor) CleanupEndOfTurn(player *Player) {
    var remaining []*AttachmentTrainer

    for _, attachment := range player.AttachedTrainers {
        if !attachment.ExpiresEndOfTurn {
            remaining = append(remaining, attachment)
        } else {
            // Discard the trainer card
            player.DiscardPile = append(player.DiscardPile, attachment.Card)
        }
    }

    player.AttachedTrainers = remaining
}

// CalculateDamageWithAttachments includes trainer bonuses
func (te *TrainerExecutor) CalculateDamageWithAttachments(
    attacker *GamePokemon,
    attackerPlayer *Player,
    baseDamage int,
) int {
    totalDamage := baseDamage

    // Add PlusPower bonuses
    for _, attachment := range attackerPlayer.AttachedTrainers {
        if attachment.AttachedTo == attacker {
            totalDamage += attachment.Effect.DamageBoost
        }
    }

    return totalDamage
}
```

## Key Trainer Cards Reference

### Draw/Search
| Card | Effect | Notes |
|------|--------|-------|
| Bill | Draw 2 cards | Simple, no cost |
| Professor Oak | Discard hand, draw 7 | Powerful hand refresh |
| Computer Search | Discard 2, search for any 1 | Flexible but costly |
| Pokemon Trader | Trade 1 Pokemon for 1 from deck | Pokemon-specific search |
| Pokedex | Look at top 5, rearrange | Information + deck manipulation |

### Healing/Protection
| Card | Effect | Notes |
|------|--------|-------|
| Potion | Heal 20 damage | Basic healing |
| Super Potion | Discard energy, heal 40 | Better ratio with cost |
| Pokemon Center | Heal all your Pokemon, discard all energy | Massive heal, massive cost |
| Defender | Reduce damage by 20 this turn | Attaches to Pokemon |
| Full Heal | Remove all status conditions | Status removal |

### Disruption
| Card | Effect | Notes |
|------|--------|-------|
| Energy Removal | Remove 1 energy from opponent | Powerful disruption |
| Super Energy Removal | Discard 1 of yours, remove 2 of theirs | Even stronger |
| Gust of Wind | Force opponent to switch active | Punish setup |
| Lass | Both shuffle trainers back | Aggressive play |

### Utility
| Card | Effect | Notes |
|------|--------|-------|
| Switch | Switch your active Pokemon | Free retreat |
| Scoop Up | Return Pokemon and cards to hand | Save damaged Pokemon |
| PlusPower | +10 damage this turn | Reach KO thresholds |
| Item Finder | Discard 2, retrieve trainer | Recursion engine |
| Revive | Put basic from discard to bench | Pokemon recovery |
