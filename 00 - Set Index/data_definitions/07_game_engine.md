# Pokemon TCG Game Engine Implementation Guide

This document provides a comprehensive guide for implementing a digital version of the Pokemon Trading Card Game using the card data in this repository.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       Game Engine                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Card Loader  │  │ Rule Engine  │  │ Effect System│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                  │                  │
│         ▼                 ▼                  ▼                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                   Game State                          │      │
│  │  ┌─────────────────┐  ┌─────────────────────────┐    │      │
│  │  │    Player 1     │  │       Player 2          │    │      │
│  │  │ - Deck          │  │ - Deck                  │    │      │
│  │  │ - Hand          │  │ - Hand                  │    │      │
│  │  │ - Active        │  │ - Active                │    │      │
│  │  │ - Bench         │  │ - Bench                 │    │      │
│  │  │ - Prizes        │  │ - Prizes                │    │      │
│  │  │ - Discard       │  │ - Discard               │    │      │
│  │  └─────────────────┘  └─────────────────────────┘    │      │
│  └──────────────────────────────────────────────────────┘      │
│         │                                                       │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              Turn Manager / Action Queue              │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Core Data Structures

### Game State

```go
package game

// GameState represents the complete state of a game
type GameState struct {
    // Players
    Player1       *Player
    Player2       *Player
    CurrentPlayer *Player

    // Turn tracking
    TurnNumber    int
    Phase         TurnPhase
    ActionsTaken  []Action

    // Global effects
    GoopGasActive         bool
    GoopGasExpiresEndOf   int
    AttachedTrainers      []*AttachmentTrainer

    // Game status
    GameOver      bool
    Winner        *Player
    WinCondition  WinCondition

    // Random number generator (for coin flips)
    RNG           *rand.Rand
}

type TurnPhase int

const (
    PhaseSetup TurnPhase = iota
    PhaseDraw
    PhaseMain
    PhaseAttack
    PhaseEnd
    PhaseBetweenTurns
)

type WinCondition int

const (
    WinByPrizes WinCondition = iota
    WinByDeckOut
    WinByNoBasicPokemon
    WinByConcede
)
```

### Player State

```go
// Player represents one player's game state
type Player struct {
    ID               string
    Name             string

    // Card zones
    Deck             []Card
    Hand             []Card
    Active           *GamePokemon
    Bench            []*GamePokemon  // Max 5
    DiscardPile      []Card
    Prizes           []Card          // 6 at start

    // Turn state
    HasAttachedEnergyThisTurn bool
    HasPlayedSupporterThisTurn bool
    HasRetreatedThisTurn       bool // Some formats restrict
    EvolvedPokemonThisTurn     []*GamePokemon

    // Attached trainers (PlusPower, Defender)
    ActiveAttachments []*TrainerAttachment
}

// GamePokemon represents a Pokemon in play
type GamePokemon struct {
    Card               *PokemonCard

    // State
    CurrentHP          int
    DamageCounters     int
    AttachedEnergy     []*AttachedEnergy
    StatusConditions   []StatusCondition

    // Position
    IsActive           bool

    // Turn tracking
    TurnPlayed         int
    EvolvedThisTurn    bool
    UsedPowerThisTurn  map[string]bool

    // Special states
    TransformState     *TransformState  // For Ditto
    EnergyBurnActive   bool             // For Charizard
    IsTrainerCard      bool             // For Clefairy Doll
    OriginalTrainer    *TrainerCard     // If IsTrainerCard
}
```

### Action System

```go
// Action represents a player action
type Action interface {
    Validate(gameState *GameState) error
    Execute(gameState *GameState) error
    GetType() ActionType
}

type ActionType int

const (
    ActionPlayBasicPokemon ActionType = iota
    ActionAttachEnergy
    ActionEvolve
    ActionPlayTrainer
    ActionUsePokemonPower
    ActionRetreat
    ActionAttack
    ActionPass
)

// Example action implementations
type PlayBasicPokemonAction struct {
    PlayerID string
    CardID   string
}

func (a *PlayBasicPokemonAction) Validate(gs *GameState) error {
    player := gs.GetPlayer(a.PlayerID)

    // Check card is in hand
    card := player.FindCardInHand(a.CardID)
    if card == nil {
        return fmt.Errorf("card not in hand")
    }

    // Check it's a Basic Pokemon
    pokemon, ok := card.(*PokemonCard)
    if !ok || pokemon.Stage != "Basic" {
        return fmt.Errorf("not a Basic Pokemon")
    }

    // Check bench space (or no active Pokemon)
    if player.Active != nil && len(player.Bench) >= 5 {
        return fmt.Errorf("bench is full")
    }

    return nil
}

func (a *PlayBasicPokemonAction) Execute(gs *GameState) error {
    player := gs.GetPlayer(a.PlayerID)
    card := player.RemoveCardFromHand(a.CardID).(*PokemonCard)

    newPokemon := NewGamePokemon(card, gs.TurnNumber)

    if player.Active == nil {
        newPokemon.IsActive = true
        player.Active = newPokemon
    } else {
        player.Bench = append(player.Bench, newPokemon)
    }

    return nil
}
```

## Game Setup

```go
// SetupGame initializes a new game
func SetupGame(deck1, deck2 []Card, seed int64) (*GameState, error) {
    gs := &GameState{
        Player1:    NewPlayer("player1", deck1),
        Player2:    NewPlayer("player2", deck2),
        TurnNumber: 0,
        Phase:      PhaseSetup,
        RNG:        rand.New(rand.NewSource(seed)),
    }

    // Validate decks
    if err := ValidateDeck(deck1); err != nil {
        return nil, fmt.Errorf("player 1 deck invalid: %w", err)
    }
    if err := ValidateDeck(deck2); err != nil {
        return nil, fmt.Errorf("player 2 deck invalid: %w", err)
    }

    // Shuffle decks
    gs.ShuffleDeck(gs.Player1)
    gs.ShuffleDeck(gs.Player2)

    // Draw initial hands (7 cards)
    for i := 0; i < 7; i++ {
        gs.DrawCard(gs.Player1)
        gs.DrawCard(gs.Player2)
    }

    // Mulligan handling
    for !gs.HasBasicPokemon(gs.Player1) {
        gs.HandleMulligan(gs.Player1, gs.Player2)
    }
    for !gs.HasBasicPokemon(gs.Player2) {
        gs.HandleMulligan(gs.Player2, gs.Player1)
    }

    // Place Prize cards (6)
    gs.SetupPrizes(gs.Player1)
    gs.SetupPrizes(gs.Player2)

    // Players select starting Pokemon
    // (This would involve player input in a real implementation)

    // Determine who goes first (coin flip)
    if gs.FlipCoin() {
        gs.CurrentPlayer = gs.Player1
    } else {
        gs.CurrentPlayer = gs.Player2
    }

    gs.Phase = PhaseDraw
    gs.TurnNumber = 1

    return gs, nil
}

func (gs *GameState) HandleMulligan(mulliganPlayer, otherPlayer *Player) {
    // Reveal hand (in real implementation)

    // Shuffle hand into deck
    mulliganPlayer.Deck = append(mulliganPlayer.Deck, mulliganPlayer.Hand...)
    mulliganPlayer.Hand = []Card{}
    gs.ShuffleDeck(mulliganPlayer)

    // Draw new hand
    for i := 0; i < 7; i++ {
        gs.DrawCard(mulliganPlayer)
    }

    // Opponent may draw 1 card
    // (Optional - opponent chooses)
    gs.DrawCard(otherPlayer)
}

func (gs *GameState) SetupPrizes(player *Player) {
    for i := 0; i < 6; i++ {
        card := player.Deck[0]
        player.Deck = player.Deck[1:]
        player.Prizes = append(player.Prizes, card)
    }
}
```

## Turn Structure

```go
// ExecuteTurn runs a complete turn
func (gs *GameState) ExecuteTurn() error {
    player := gs.CurrentPlayer

    // Reset turn state
    player.HasAttachedEnergyThisTurn = false
    player.HasPlayedSupporterThisTurn = false
    player.EvolvedPokemonThisTurn = []*GamePokemon{}

    // Reset Pokemon states
    for _, pokemon := range player.GetAllPokemon() {
        pokemon.EvolvedThisTurn = false
        pokemon.UsedPowerThisTurn = make(map[string]bool)
    }

    // Phase 1: Draw
    gs.Phase = PhaseDraw
    if err := gs.DrawPhase(); err != nil {
        return err
    }

    // Phase 2: Main Phase
    gs.Phase = PhaseMain
    if err := gs.MainPhase(); err != nil {
        return err
    }

    // Phase 3: Attack Phase
    gs.Phase = PhaseAttack
    if err := gs.AttackPhase(); err != nil {
        return err
    }

    // Phase 4: End Phase
    gs.Phase = PhaseEnd
    if err := gs.EndPhase(); err != nil {
        return err
    }

    // Between turns
    gs.Phase = PhaseBetweenTurns
    if err := gs.BetweenTurnsPhase(); err != nil {
        return err
    }

    // Switch current player
    if gs.CurrentPlayer == gs.Player1 {
        gs.CurrentPlayer = gs.Player2
    } else {
        gs.CurrentPlayer = gs.Player1
    }

    gs.TurnNumber++

    return nil
}

func (gs *GameState) DrawPhase() error {
    player := gs.CurrentPlayer

    // Draw one card
    if len(player.Deck) == 0 {
        // Deck out - opponent wins
        gs.GameOver = true
        gs.Winner = gs.GetOpponent(player)
        gs.WinCondition = WinByDeckOut
        return nil
    }

    gs.DrawCard(player)
    return nil
}

func (gs *GameState) MainPhase() error {
    // Main phase allows:
    // - Play Basic Pokemon to bench
    // - Attach ONE energy (from hand)
    // - Evolve Pokemon (not first turn, not just played)
    // - Play Trainer cards
    // - Use Pokemon Powers
    // - Retreat active Pokemon

    // This is typically driven by player input
    // The engine validates and executes actions
    return nil
}

func (gs *GameState) AttackPhase() error {
    player := gs.CurrentPlayer
    active := player.Active

    if active == nil {
        return fmt.Errorf("no active Pokemon")
    }

    // Player chooses attack (or passes)
    // Validate attack can be used
    // Execute attack
    // Handle damage, effects, knockouts

    return nil
}

func (gs *GameState) EndPhase() error {
    player := gs.CurrentPlayer

    // Reset Energy Burn effects
    for _, pokemon := range player.GetAllPokemon() {
        if pokemon.EnergyBurnActive {
            ResetEnergyBurn(pokemon)
        }
    }

    // Remove end-of-turn trainer attachments
    var remaining []*TrainerAttachment
    for _, attachment := range player.ActiveAttachments {
        if !attachment.ExpiresEndOfTurn {
            remaining = append(remaining, attachment)
        }
    }
    player.ActiveAttachments = remaining

    return nil
}

func (gs *GameState) BetweenTurnsPhase() error {
    // Process for BOTH players
    for _, player := range []*Player{gs.Player1, gs.Player2} {
        for _, pokemon := range player.GetAllPokemon() {
            // Process status conditions
            gs.ProcessStatusConditions(pokemon)
        }
    }

    // Check Goop Gas expiry
    if gs.GoopGasActive && gs.TurnNumber > gs.GoopGasExpiresEndOf {
        gs.GoopGasActive = false
    }

    return nil
}

func (gs *GameState) ProcessStatusConditions(pokemon *GamePokemon) {
    for i := len(pokemon.StatusConditions) - 1; i >= 0; i-- {
        status := pokemon.StatusConditions[i]

        switch status.Type {
        case "Asleep":
            // Flip coin - heads = wake up
            if gs.FlipCoin() {
                pokemon.StatusConditions = removeStatus(pokemon.StatusConditions, i)
            }

        case "Poisoned":
            // Take 10 damage between turns
            pokemon.TakeDamage(10)

        case "Burned":
            // Flip coin - tails = 20 damage
            if !gs.FlipCoin() {
                pokemon.TakeDamage(20)
            }

        case "Paralyzed":
            // Remove at end of affected player's next turn
            status.TurnsRemaining--
            if status.TurnsRemaining <= 0 {
                pokemon.StatusConditions = removeStatus(pokemon.StatusConditions, i)
            }

        case "Confused":
            // Confusion doesn't do anything between turns
            // It affects attack execution
        }
    }

    // Check for knockout from poison/burn
    if pokemon.IsKnockedOut() {
        gs.HandleKnockout(pokemon)
    }
}
```

## Combat System

```go
// ExecuteAttack processes an attack
func (gs *GameState) ExecuteAttack(
    attacker *GamePokemon,
    attack *Attack,
    defender *GamePokemon,
) error {
    // Validate attack can be used
    if err := gs.ValidateAttack(attacker, attack); err != nil {
        return err
    }

    // Pay costs (energy discard, etc.)
    if err := gs.PayAttackCosts(attacker, attack); err != nil {
        return err
    }

    // Calculate damage
    damage := gs.CalculateDamage(attacker, attack, defender)

    // Apply damage prevention (Invisible Wall, etc.)
    damage = gs.ApplyDamagePrevention(defender, damage)

    // Deal damage
    if damage > 0 {
        defender.TakeDamage(damage)
    }

    // Apply attack effects
    gs.ApplyAttackEffects(attacker, attack, defender)

    // Check for knockout
    if defender.IsKnockedOut() {
        gs.HandleKnockout(defender)
    }

    return nil
}

func (gs *GameState) ValidateAttack(attacker *GamePokemon, attack *Attack) error {
    // Check status conditions
    if attacker.HasStatus("Asleep") {
        return fmt.Errorf("cannot attack while Asleep")
    }
    if attacker.HasStatus("Paralyzed") {
        return fmt.Errorf("cannot attack while Paralyzed")
    }

    // Check energy requirements
    if !attacker.HasEnoughEnergy(attack.Cost) {
        return fmt.Errorf("not enough energy for attack")
    }

    return nil
}

func (gs *GameState) CalculateDamage(
    attacker *GamePokemon,
    attack *Attack,
    defender *GamePokemon,
) int {
    // Base damage
    damage := attack.BaseDamage

    // Apply scaling effects
    if attack.Effect != nil {
        damage = gs.ApplyScalingEffects(attacker, defender, attack.Effect, damage)
    }

    // Apply damage modifiers (PlusPower)
    attackerOwner := gs.GetPokemonOwner(attacker)
    for _, attachment := range attackerOwner.ActiveAttachments {
        if attachment.Target == attacker {
            damage += attachment.DamageBoost
        }
    }

    // Apply weakness
    defenderStats := gs.GetEffectiveStats(defender)
    if defenderStats.Weakness != nil {
        attackerType := gs.GetAttackerType(attacker)
        if attackerType == defenderStats.Weakness.Type {
            if defenderStats.Weakness.Value == "x2" {
                damage *= 2
            }
        }
    }

    // Apply resistance
    if defenderStats.Resistance != nil {
        attackerType := gs.GetAttackerType(attacker)
        if attackerType == defenderStats.Resistance.Type {
            // Parse "-30" to get 30
            resistance := 30 // Default for Base Set era
            damage -= resistance
        }
    }

    // Minimum 0 damage
    if damage < 0 {
        damage = 0
    }

    // Apply Defender trainer card reduction
    defenderOwner := gs.GetPokemonOwner(defender)
    for _, attachment := range defenderOwner.ActiveAttachments {
        if attachment.Target == defender {
            damage -= attachment.DamageReduction
        }
    }

    if damage < 0 {
        damage = 0
    }

    return damage
}

func (gs *GameState) HandleKnockout(pokemon *GamePokemon) {
    owner := gs.GetPokemonOwner(pokemon)
    opponent := gs.GetOpponent(owner)

    // Check if it's a trainer-as-Pokemon (Clefairy Doll)
    if pokemon.IsTrainerCard {
        // No prize taken
        owner.DiscardPile = append(owner.DiscardPile, pokemon.OriginalTrainer)
    } else {
        // Normal knockout - opponent takes prize
        if len(opponent.Prizes) > 0 {
            prize := opponent.Prizes[0]
            opponent.Prizes = opponent.Prizes[1:]
            opponent.Hand = append(opponent.Hand, prize)
        }

        // Check win condition
        if len(opponent.Prizes) == 0 {
            gs.GameOver = true
            gs.Winner = opponent
            gs.WinCondition = WinByPrizes
        }
    }

    // Discard Pokemon and all attached cards
    owner.DiscardPile = append(owner.DiscardPile, pokemon.Card)
    for _, energy := range pokemon.AttachedEnergy {
        owner.DiscardPile = append(owner.DiscardPile, energy.Card)
    }

    // Remove from play
    if pokemon.IsActive {
        owner.Active = nil
        // Owner must promote a benched Pokemon
        if len(owner.Bench) > 0 {
            // Player chooses which Pokemon to promote
            // (In implementation, prompt player)
        } else {
            // No benched Pokemon - opponent wins
            gs.GameOver = true
            gs.Winner = opponent
            gs.WinCondition = WinByNoBasicPokemon
        }
    } else {
        owner.Bench = removePokemonFromSlice(owner.Bench, pokemon)
    }
}
```

## Evolution System

```go
// ExecuteEvolution evolves a Pokemon
func (gs *GameState) ExecuteEvolution(
    player *Player,
    basePokemon *GamePokemon,
    evolutionCard *PokemonCard,
) error {
    // Validate evolution
    if err := gs.ValidateEvolution(player, basePokemon, evolutionCard); err != nil {
        return err
    }

    // Remove evolution card from hand
    player.RemoveCardFromHand(evolutionCard)

    // Store old state
    oldCard := basePokemon.Card
    oldAttachedEnergy := basePokemon.AttachedEnergy

    // Apply evolution
    basePokemon.Card = evolutionCard
    basePokemon.CurrentHP = evolutionCard.HP - (basePokemon.DamageCounters * 10)

    // Remove status conditions
    basePokemon.StatusConditions = []StatusCondition{}

    // Mark as evolved this turn
    basePokemon.EvolvedThisTurn = true
    player.EvolvedPokemonThisTurn = append(player.EvolvedPokemonThisTurn, basePokemon)

    // Discard old card (goes under evolution - but for simplicity, discard)
    // Note: Some abilities care about cards "under" evolved Pokemon
    player.DiscardPile = append(player.DiscardPile, oldCard)

    return nil
}

func (gs *GameState) ValidateEvolution(
    player *Player,
    basePokemon *GamePokemon,
    evolutionCard *PokemonCard,
) error {
    // Cannot evolve on first turn
    if gs.TurnNumber == 1 && gs.CurrentPlayer == player {
        return fmt.Errorf("cannot evolve on first turn")
    }

    // Cannot evolve Pokemon played this turn
    if basePokemon.TurnPlayed == gs.TurnNumber {
        return fmt.Errorf("cannot evolve Pokemon played this turn")
    }

    // Cannot evolve Pokemon that already evolved this turn
    if basePokemon.EvolvedThisTurn {
        return fmt.Errorf("cannot evolve Pokemon that evolved this turn")
    }

    // Check evolution chain
    if evolutionCard.EvolvesFrom != basePokemon.Card.Name {
        return fmt.Errorf("%s does not evolve from %s",
            evolutionCard.Name, basePokemon.Card.Name)
    }

    return nil
}
```

## Retreat System

```go
// ExecuteRetreat retreats the active Pokemon
func (gs *GameState) ExecuteRetreat(
    player *Player,
    newActive *GamePokemon,
    energyToDiscard []*AttachedEnergy,
) error {
    active := player.Active

    // Validate retreat
    if err := gs.ValidateRetreat(active, energyToDiscard); err != nil {
        return err
    }

    // Discard energy for retreat cost
    for _, energy := range energyToDiscard {
        active.RemoveEnergy(energy)
        player.DiscardPile = append(player.DiscardPile, energy.Card)
    }

    // Swap Pokemon
    active.IsActive = false
    newActive.IsActive = true

    // Remove new active from bench
    player.Bench = removePokemonFromSlice(player.Bench, newActive)

    // Add old active to bench
    player.Bench = append(player.Bench, active)

    player.Active = newActive

    return nil
}

func (gs *GameState) ValidateRetreat(
    pokemon *GamePokemon,
    energyToDiscard []*AttachedEnergy,
) error {
    // Cannot retreat if Asleep or Paralyzed
    if pokemon.HasStatus("Asleep") {
        return fmt.Errorf("cannot retreat while Asleep")
    }
    if pokemon.HasStatus("Paralyzed") {
        return fmt.Errorf("cannot retreat while Paralyzed")
    }

    // Check retreat cost
    retreatCost := len(pokemon.Card.RetreatCost)

    // Count energy value of discarded energy
    energyValue := 0
    for _, energy := range energyToDiscard {
        energyValue += energy.ProvidedAmount
    }

    if energyValue < retreatCost {
        return fmt.Errorf("not enough energy for retreat cost")
    }

    return nil
}
```

## Confused Attack Handling

```go
func (gs *GameState) HandleConfusedAttack(
    attacker *GamePokemon,
    attack *Attack,
    defender *GamePokemon,
) error {
    if !attacker.HasStatus("Confused") {
        return gs.ExecuteAttack(attacker, attack, defender)
    }

    // Flip coin
    if gs.FlipCoin() {
        // Heads - attack proceeds normally
        return gs.ExecuteAttack(attacker, attack, defender)
    }

    // Tails - deal 30 damage to self (3 damage counters)
    attacker.TakeDamage(30)

    // Check for self-knockout
    if attacker.IsKnockedOut() {
        gs.HandleKnockout(attacker)
    }

    // Attack fails
    return nil
}
```

## Win Condition Checks

```go
func (gs *GameState) CheckWinConditions() {
    // Check after every action

    // 1. All prizes taken
    if len(gs.Player1.Prizes) == 0 {
        gs.GameOver = true
        gs.Winner = gs.Player1
        gs.WinCondition = WinByPrizes
        return
    }
    if len(gs.Player2.Prizes) == 0 {
        gs.GameOver = true
        gs.Winner = gs.Player2
        gs.WinCondition = WinByPrizes
        return
    }

    // 2. Opponent has no Pokemon in play
    if gs.Player1.Active == nil && len(gs.Player1.Bench) == 0 {
        gs.GameOver = true
        gs.Winner = gs.Player2
        gs.WinCondition = WinByNoBasicPokemon
        return
    }
    if gs.Player2.Active == nil && len(gs.Player2.Bench) == 0 {
        gs.GameOver = true
        gs.Winner = gs.Player1
        gs.WinCondition = WinByNoBasicPokemon
        return
    }

    // 3. Deck out (checked during draw phase)
}
```

## Complete Card Loading System

```go
package cardloader

import (
    "encoding/json"
    "os"
    "path/filepath"
    "strings"
)

type CardDatabase struct {
    Pokemon  map[string]*PokemonCard
    Trainers map[string]TrainerCard  // Interface for Item/Supporter
    Energy   map[string]*EnergyCard

    // Indexes for efficient lookup
    ByName   map[string][]Card
    BySet    map[string][]Card
    ByType   map[string][]Card
}

func LoadCardDatabase(baseDir string) (*CardDatabase, error) {
    db := &CardDatabase{
        Pokemon:  make(map[string]*PokemonCard),
        Trainers: make(map[string]TrainerCard),
        Energy:   make(map[string]*EnergyCard),
        ByName:   make(map[string][]Card),
        BySet:    make(map[string][]Card),
        ByType:   make(map[string][]Card),
    }

    setDirs := []string{
        "01 - Base Set 1 (BS)",
        "02 - Jungle (JU)",
        "03 - Fossil (FO)",
        "04 - Base Set 2 (B2)",
        "05 - Team Rocket (RO)",
    }

    for _, setDir := range setDirs {
        cardPath := filepath.Join(baseDir, setDir, "card_details")

        files, err := os.ReadDir(cardPath)
        if err != nil {
            return nil, err
        }

        for _, file := range files {
            if !strings.HasSuffix(file.Name(), ".json") {
                continue
            }

            data, err := os.ReadFile(filepath.Join(cardPath, file.Name()))
            if err != nil {
                continue
            }

            // Determine card type
            var baseCard struct {
                CardType string `json:"cardType"`
            }
            json.Unmarshal(data, &baseCard)

            switch baseCard.CardType {
            case "pokemon":
                var card PokemonCard
                if err := json.Unmarshal(data, &card); err == nil {
                    db.Pokemon[card.ID] = &card
                    db.addToIndexes(&card)
                }

            case "trainer", "trainer-item":
                // Try item first, then supporter
                var itemCard TrainerItemCard
                if err := json.Unmarshal(data, &itemCard); err == nil {
                    if containsSubtype(itemCard.Subtypes, "Item") {
                        db.Trainers[itemCard.ID] = &itemCard
                        db.addToIndexes(&itemCard)
                    } else {
                        var supporterCard TrainerSupporterCard
                        json.Unmarshal(data, &supporterCard)
                        db.Trainers[supporterCard.ID] = &supporterCard
                        db.addToIndexes(&supporterCard)
                    }
                }

            case "energy":
                var card EnergyCard
                if err := json.Unmarshal(data, &card); err == nil {
                    db.Energy[card.ID] = &card
                    db.addToIndexes(&card)
                }
            }
        }
    }

    return db, nil
}

func (db *CardDatabase) GetPokemonByID(id string) *PokemonCard {
    return db.Pokemon[id]
}

func (db *CardDatabase) GetCardsByName(name string) []Card {
    return db.ByName[strings.ToLower(name)]
}

func (db *CardDatabase) GetCardsBySet(setID string) []Card {
    return db.BySet[setID]
}

func (db *CardDatabase) GetPokemonByType(typeName string) []*PokemonCard {
    var result []*PokemonCard
    for _, card := range db.Pokemon {
        for _, t := range card.Types {
            if strings.EqualFold(t, typeName) {
                result = append(result, card)
                break
            }
        }
    }
    return result
}
```

## Example: Complete Game Loop

```go
func RunGame(deck1, deck2 []Card) (*Player, error) {
    // Initialize game
    gs, err := SetupGame(deck1, deck2, time.Now().UnixNano())
    if err != nil {
        return nil, err
    }

    // Game loop
    for !gs.GameOver {
        // Execute turn
        if err := gs.ExecuteTurn(); err != nil {
            return nil, err
        }

        // Check win conditions
        gs.CheckWinConditions()
    }

    return gs.Winner, nil
}

// Example AI player turn (simplified)
func AIPlayTurn(gs *GameState, player *Player) {
    // Main phase actions
    for {
        actions := GetValidActions(gs, player)
        if len(actions) == 0 {
            break
        }

        // Choose best action (AI logic)
        action := ChooseBestAction(actions, gs)

        if action.GetType() == ActionAttack {
            // Attack ends turn
            action.Execute(gs)
            break
        }

        action.Execute(gs)
    }
}
```

This game engine guide provides the foundation for implementing a complete Pokemon TCG digital game. The actual implementation would require additional UI components, network code for multiplayer, and more sophisticated AI for computer opponents.
