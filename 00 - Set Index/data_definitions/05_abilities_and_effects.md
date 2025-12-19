# Pokemon Abilities and Attack Effects - Programming Guide

This document provides detailed implementation guidance for programming Pokemon Powers, abilities, and attack effects in a digital Pokemon TCG implementation.

## Pokemon Powers Overview

Pokemon Powers are special abilities that can be used outside of attacks. They come in different categories based on trigger timing and restrictions.

### Power Classification

| Type | Trigger | Frequency | Example |
|------|---------|-----------|---------|
| Activated | Player choice | Once/Unlimited per turn | Damage Swap, Rain Dance |
| Passive | Automatic | Continuous | Mr. Mime's Invisible Wall |
| Reactive | On event | When triggered | On-damage effects |

## Go Type System for Abilities

```go
package abilities

// AbilityHandler defines the interface for ability implementations
type AbilityHandler interface {
    CanUse(pokemon *GamePokemon, gameState *GameState) bool
    Execute(pokemon *GamePokemon, gameState *GameState, params map[string]interface{}) error
    GetTrigger() AbilityTrigger
}

// AbilityTrigger defines when an ability can be used
type AbilityTrigger int

const (
    TriggerOncePerTurn AbilityTrigger = iota
    TriggerUnlimitedPerTurn
    TriggerPassive
    TriggerOnDamage
    TriggerOnAttack
    TriggerWhileActive
    TriggerBetweenTurns
)

// RegisteredAbilities maps ability names to their handlers
var RegisteredAbilities = map[string]AbilityHandler{
    "Damage Swap":    &DamageSwapHandler{},
    "Rain Dance":     &RainDanceHandler{},
    "Energy Burn":    &EnergyBurnHandler{},
    "Invisible Wall": &InvisibleWallHandler{},
    "Transform":      &TransformHandler{},
    // ... more abilities
}
```

## Detailed Ability Implementations

### Alakazam's Damage Swap

**Effect:** Move 1 damage counter from one of your Pokemon to another (unlimited times per turn, before attack).

```go
package abilities

type DamageSwapHandler struct{}

func (h *DamageSwapHandler) GetTrigger() AbilityTrigger {
    return TriggerUnlimitedPerTurn
}

func (h *DamageSwapHandler) CanUse(pokemon *GamePokemon, gameState *GameState) bool {
    // Check status conditions
    if pokemon.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
        return false
    }

    // Check for Goop Gas Attack
    if gameState.GoopGasActive {
        return false
    }

    // Check if there are valid targets (Pokemon with damage)
    hasDamagedPokemon := false
    for _, poke := range gameState.GetPlayerPokemon(pokemon.Owner) {
        if poke.DamageCounters > 0 {
            hasDamagedPokemon = true
            break
        }
    }

    return hasDamagedPokemon
}

func (h *DamageSwapHandler) Execute(
    pokemon *GamePokemon,
    gameState *GameState,
    params map[string]interface{},
) error {
    source := params["source"].(*GamePokemon)
    destination := params["destination"].(*GamePokemon)

    // Validate source has damage
    if source.DamageCounters == 0 {
        return fmt.Errorf("source Pokemon has no damage counters")
    }

    // Validate destination won't be knocked out
    // (Cannot use Damage Swap to KO your own Pokemon)
    destMaxHP := destination.Card.HP
    destCurrentDamage := destination.DamageCounters * 10
    if destCurrentDamage + 10 >= destMaxHP {
        return fmt.Errorf("cannot knock out your own Pokemon with Damage Swap")
    }

    // Move one damage counter
    source.DamageCounters--
    source.CurrentHP += 10
    destination.DamageCounters++
    destination.CurrentHP -= 10

    return nil
}
```

### Blastoise's Rain Dance

**Effect:** Attach any number of Water Energy to your Water Pokemon (unlimited times per turn, doesn't use normal energy attachment).

```go
type RainDanceHandler struct{}

func (h *RainDanceHandler) GetTrigger() AbilityTrigger {
    return TriggerUnlimitedPerTurn
}

func (h *RainDanceHandler) CanUse(pokemon *GamePokemon, gameState *GameState) bool {
    // Check status conditions
    if pokemon.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
        return false
    }

    // Check Goop Gas
    if gameState.GoopGasActive {
        return false
    }

    // Check player has Water Energy in hand
    player := gameState.GetPlayer(pokemon.Owner)
    for _, card := range player.Hand {
        if energy, ok := card.(*EnergyCard); ok {
            if energy.IsBasicEnergy() && energy.EnergyType == "Water" {
                return true
            }
        }
    }

    return false
}

func (h *RainDanceHandler) Execute(
    pokemon *GamePokemon,
    gameState *GameState,
    params map[string]interface{},
) error {
    waterEnergy := params["energy"].(*EnergyCard)
    target := params["target"].(*GamePokemon)

    // Validate energy is Water
    if waterEnergy.EnergyType != "Water" {
        return fmt.Errorf("Rain Dance can only attach Water Energy")
    }

    // Validate target is Water type
    if !target.HasType("Water") {
        return fmt.Errorf("Rain Dance can only attach to Water Pokemon")
    }

    // Attach energy (does NOT count as normal energy attachment)
    player := gameState.GetPlayer(pokemon.Owner)
    player.RemoveFromHand(waterEnergy)
    target.AttachEnergy(waterEnergy)

    // Note: Can be used multiple times per turn
    // Note: Player can STILL use their normal energy attachment

    return nil
}
```

### Charizard's Energy Burn

**Effect:** Convert all attached energy to Fire type until end of turn.

```go
type EnergyBurnHandler struct{}

func (h *EnergyBurnHandler) GetTrigger() AbilityTrigger {
    return TriggerUnlimitedPerTurn
}

func (h *EnergyBurnHandler) CanUse(pokemon *GamePokemon, gameState *GameState) bool {
    if pokemon.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
        return false
    }
    if gameState.GoopGasActive {
        return false
    }
    return len(pokemon.AttachedEnergy) > 0
}

func (h *EnergyBurnHandler) Execute(
    pokemon *GamePokemon,
    gameState *GameState,
    params map[string]interface{},
) error {
    // Convert all attached energy to Fire type
    for i := range pokemon.AttachedEnergy {
        energy := &pokemon.AttachedEnergy[i]

        // Store original type for end-of-turn reset
        if energy.ConversionOriginalType == "" {
            energy.ConversionOriginalType = energy.EffectiveType
        }

        // Set to Fire
        energy.EffectiveType = "Fire"
    }

    // Mark that Energy Burn is active (for end-of-turn cleanup)
    pokemon.EnergyBurnActive = true

    return nil
}

// ResetEnergyBurn is called at end of turn
func ResetEnergyBurn(pokemon *GamePokemon) {
    if !pokemon.EnergyBurnActive {
        return
    }

    for i := range pokemon.AttachedEnergy {
        energy := &pokemon.AttachedEnergy[i]
        if energy.ConversionOriginalType != "" {
            energy.EffectiveType = energy.ConversionOriginalType
            energy.ConversionOriginalType = ""
        }
    }

    pokemon.EnergyBurnActive = false
}
```

### Mr. Mime's Invisible Wall

**Effect:** Prevent all damage from attacks that deal 30 or more (after weakness/resistance).

```go
type InvisibleWallHandler struct{}

func (h *InvisibleWallHandler) GetTrigger() AbilityTrigger {
    return TriggerOnDamage // Reactive trigger
}

func (h *InvisibleWallHandler) CanUse(pokemon *GamePokemon, gameState *GameState) bool {
    if pokemon.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
        return false
    }
    if gameState.GoopGasActive {
        return false
    }
    return true
}

// ApplyInvisibleWall is called during damage calculation
func ApplyInvisibleWall(mrMime *GamePokemon, incomingDamage int, gameState *GameState) int {
    handler := &InvisibleWallHandler{}

    if !handler.CanUse(mrMime, gameState) {
        return incomingDamage // Power disabled
    }

    // Check if damage is 30 or more (AFTER weakness/resistance)
    if incomingDamage >= 30 {
        return 0 // Damage completely prevented
    }

    return incomingDamage
}

// Important distinction: Invisible Wall only blocks DAMAGE from attacks
// It does NOT block:
// - Damage counter placement effects
// - Damage from Pokemon Powers (like Damage Swap)
// - Rainbow Energy's attachment damage
// - Self-damage from attacks
```

### Ditto's Transform

**Effect:** While Active, Ditto copies the Defending Pokemon's stats and attacks.

```go
type TransformHandler struct{}

func (h *TransformHandler) GetTrigger() AbilityTrigger {
    return TriggerWhileActive // Passive while active
}

type TransformState struct {
    IsTransformed   bool
    CopiedFrom      *PokemonCard
    OriginalHP      int
    OriginalType    []string
    OriginalWeakness *TypeModifier
    OriginalResistance *TypeModifier
}

func (h *TransformHandler) CanUse(pokemon *GamePokemon, gameState *GameState) bool {
    // Transform is always "on" while Ditto is active and not affected by status
    if !pokemon.IsActive {
        return false
    }
    if pokemon.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
        return false
    }
    if gameState.GoopGasActive {
        return false
    }
    return true
}

func (h *TransformHandler) Execute(
    pokemon *GamePokemon,
    gameState *GameState,
    params map[string]interface{},
) error {
    defender := gameState.GetOpponentActive(pokemon.Owner)

    if defender == nil {
        return fmt.Errorf("no defending Pokemon to transform into")
    }

    pokemon.TransformState = &TransformState{
        IsTransformed:   true,
        CopiedFrom:      defender.Card,
        OriginalHP:      pokemon.Card.HP,
        OriginalType:    pokemon.Card.Types,
        OriginalWeakness: pokemon.Card.Weakness,
        OriginalResistance: pokemon.Card.Resistance,
    }

    return nil
}

// GetDittoEffectiveStats returns what stats Ditto currently has
func GetDittoEffectiveStats(ditto *GamePokemon, gameState *GameState) *EffectiveStats {
    handler := &TransformHandler{}

    if !handler.CanUse(ditto, gameState) || ditto.TransformState == nil {
        // Return base Ditto stats
        return &EffectiveStats{
            HP:         50,
            Types:      []string{"Colorless"},
            Weakness:   &TypeModifier{Type: "Fighting", Value: "x2"},
            Resistance: &TypeModifier{Type: "Psychic", Value: "-30"},
            Attacks:    []Attack{}, // No attacks
            RetreatCost: []string{"Colorless"},
        }
    }

    // Return transformed stats
    copied := ditto.TransformState.CopiedFrom
    return &EffectiveStats{
        HP:         copied.HP, // Uses copied Pokemon's MAX HP
        Types:      copied.Types,
        Weakness:   copied.Weakness,
        Resistance: copied.Resistance,
        Attacks:    copied.Attacks,
        RetreatCost: copied.RetreatCost,
        // Note: Does NOT copy abilities/Pokemon Powers
    }
}

// Ditto's energy counts as any type for attacks
func DittoCanPayEnergyCost(ditto *GamePokemon, attackCost []string) bool {
    if ditto.TransformState == nil || !ditto.TransformState.IsTransformed {
        return false // Can't use attacks when not transformed
    }

    // Count total energy attached
    totalEnergy := 0
    for _, energy := range ditto.AttachedEnergy {
        totalEnergy += energy.Amount
    }

    // Any energy can pay any cost requirement
    return totalEnergy >= len(attackCost)
}
```

### Venusaur's Energy Trans

**Effect:** Move Grass Energy between your Pokemon (unlimited times per turn).

```go
type EnergyTransHandler struct{}

func (h *EnergyTransHandler) GetTrigger() AbilityTrigger {
    return TriggerUnlimitedPerTurn
}

func (h *EnergyTransHandler) CanUse(pokemon *GamePokemon, gameState *GameState) bool {
    if pokemon.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
        return false
    }
    if gameState.GoopGasActive {
        return false
    }

    // Need at least one Pokemon with Grass Energy
    player := gameState.GetPlayer(pokemon.Owner)
    for _, poke := range player.GetAllPokemon() {
        for _, energy := range poke.AttachedEnergy {
            if energy.EffectiveType == "Grass" {
                return true
            }
        }
    }
    return false
}

func (h *EnergyTransHandler) Execute(
    pokemon *GamePokemon,
    gameState *GameState,
    params map[string]interface{},
) error {
    source := params["source"].(*GamePokemon)
    destination := params["destination"].(*GamePokemon)
    energyIndex := params["energyIndex"].(int)

    // Validate energy is Grass type
    if energyIndex >= len(source.AttachedEnergy) {
        return fmt.Errorf("invalid energy index")
    }

    energy := source.AttachedEnergy[energyIndex]
    if energy.EffectiveType != "Grass" {
        return fmt.Errorf("Energy Trans can only move Grass Energy")
    }

    // Move energy
    source.AttachedEnergy = append(
        source.AttachedEnergy[:energyIndex],
        source.AttachedEnergy[energyIndex+1:]...,
    )
    destination.AttachedEnergy = append(destination.AttachedEnergy, energy)

    // Note: Moving Rainbow Energy does NOT trigger its damage
    // (Damage only occurs when attached from hand)

    return nil
}
```

## Attack Effect Implementations

### Status Condition Effects

```go
// StatusConditionEffect handles attacks that inflict status
type StatusConditionEffect struct {
    Condition     string // Asleep, Confused, Paralyzed, Poisoned, Burned
    RequiresCoinFlip bool
}

func ApplyStatusCondition(
    target *GamePokemon,
    condition string,
    requiresCoinFlip bool,
) bool {
    if requiresCoinFlip {
        if !flipCoin() {
            return false // Tails, no effect
        }
    }

    // Add status condition
    target.StatusConditions = append(target.StatusConditions, StatusCondition{
        Type: condition,
        TurnsRemaining: -1, // Handled by specific condition rules
    })

    return true
}

// Status condition rules:
// Asleep: Cannot attack/retreat. Flip coin between turns - heads = wake up
// Confused: Flip coin to attack. Tails = deal 30 damage to self, attack fails
// Paralyzed: Cannot attack/retreat. Removed at end of owner's next turn
// Poisoned: Take 10 damage between turns (does not wear off)
// Burned: Flip coin between turns. Tails = 20 damage
```

### Coin Flip Damage

```go
// CoinFlipDamageEffect handles attacks with coin flip mechanics
type CoinFlipDamageEffect struct {
    BaseDamage     int
    DamagePerHeads int
    NumberOfFlips  int // -1 means flip until tails
    OnTailsSelfDamage int
}

func ExecuteCoinFlipDamage(attacker *GamePokemon, effect CoinFlipDamageEffect) int {
    headsCount := 0

    if effect.NumberOfFlips == -1 {
        // Flip until tails
        for flipCoin() {
            headsCount++
        }
    } else {
        // Fixed number of flips
        for i := 0; i < effect.NumberOfFlips; i++ {
            if flipCoin() {
                headsCount++
            }
        }
    }

    // Calculate damage
    totalDamage := effect.BaseDamage + (headsCount * effect.DamagePerHeads)

    return totalDamage
}

// Example: Pikachu's Thunder Jolt
// Base damage 30, but flip coin - if tails, 10 damage to self
func ThunderJolt(attacker *GamePokemon, defender *GamePokemon) int {
    damage := 30 // Always does 30 to defender

    if !flipCoin() { // Tails
        attacker.TakeDamage(10) // Self-damage on tails
    }

    return damage
}

// Example: Dark Charizard's Continuous Fireball
// Flip coins equal to Fire Energy, 50 damage per heads, discard that many Fire Energy
func ContinuousFireball(attacker *GamePokemon) int {
    fireEnergyCount := countFireEnergy(attacker)

    headsCount := 0
    for i := 0; i < fireEnergyCount; i++ {
        if flipCoin() {
            headsCount++
        }
    }

    // Discard Fire Energy equal to heads
    for i := 0; i < headsCount; i++ {
        discardOneFireEnergy(attacker)
    }

    return headsCount * 50
}
```

### Bench Damage Effects

```go
// BenchDamageEffect handles attacks that hit benched Pokemon
type BenchDamageEffect struct {
    Target        string // "opponent_bench", "all_bench", "your_bench"
    Damage        int
    SelectTarget  bool   // If true, player chooses which bench Pokemon
    DamageCount   string // "one", "all", "up_to_X"
}

func ExecuteBenchDamage(
    attacker *GamePokemon,
    gameState *GameState,
    effect BenchDamageEffect,
) error {
    var targets []*GamePokemon

    switch effect.Target {
    case "opponent_bench":
        targets = gameState.GetOpponentBench(attacker.Owner)
    case "your_bench":
        targets = gameState.GetPlayerBench(attacker.Owner)
    case "all_bench":
        targets = append(
            gameState.GetOpponentBench(attacker.Owner),
            gameState.GetPlayerBench(attacker.Owner)...,
        )
    }

    if effect.SelectTarget && len(targets) > 0 {
        // Player chooses one target
        selected := selectBenchTarget(targets)
        // Bench damage does NOT apply weakness/resistance
        selected.TakeDamageRaw(effect.Damage)
    } else {
        // Damage all targets
        for _, target := range targets {
            target.TakeDamageRaw(effect.Damage)
        }
    }

    return nil
}

// Example: Pikachu's Spark (Jungle)
// Does 20 to defender, and 10 to one benched Pokemon (your choice)
func Spark(attacker *GamePokemon, defender *GamePokemon, gameState *GameState) {
    // Main damage
    defender.TakeDamage(20) // Apply weakness/resistance

    // Bench damage
    oppBench := gameState.GetOpponentBench(attacker.Owner)
    if len(oppBench) > 0 {
        selected := selectBenchTarget(oppBench)
        selected.TakeDamageRaw(10) // NO weakness/resistance for bench
    }
}

// Example: Zapdos's Thunderstorm (Fossil)
// Does 70 to defender, 10 to all other Pokemon (both players)
func Thunderstorm(attacker *GamePokemon, defender *GamePokemon, gameState *GameState) {
    defender.TakeDamage(70) // Apply weakness/resistance

    // Damage ALL other Pokemon (including your own bench)
    for _, poke := range gameState.GetAllPokemonExcept(defender) {
        if poke != attacker { // Don't damage yourself
            poke.TakeDamageRaw(10)
        }
    }
}
```

### Energy Discard Costs

```go
// EnergyDiscardCost handles attacks that require discarding energy
type EnergyDiscardCost struct {
    Count       int    // Number to discard
    Type        string // "any", "Fire", "Water", etc.
    Timing      string // "cost" (before damage), "effect" (after damage)
}

func PayEnergyDiscardCost(attacker *GamePokemon, cost EnergyDiscardCost) error {
    validEnergy := []*AttachedEnergy{}

    for _, energy := range attacker.AttachedEnergy {
        if cost.Type == "any" || energy.EffectiveType == cost.Type {
            validEnergy = append(validEnergy, energy)
        }
    }

    if len(validEnergy) < cost.Count {
        return fmt.Errorf("not enough energy to discard")
    }

    // Let player choose which to discard (if multiple valid options)
    for i := 0; i < cost.Count; i++ {
        selected := selectEnergyToDiscard(validEnergy)
        discardEnergy(attacker, selected)

        // Remove from valid options
        validEnergy = removeFromSlice(validEnergy, selected)
    }

    return nil
}

// Example: Charizard's Fire Spin
// Cost: [Fire, Fire, Fire, Fire], Damage: 100
// Effect: Discard 2 Energy cards
func FireSpin(attacker *GamePokemon, defender *GamePokemon) (int, error) {
    // Must discard 2 energy as part of attack cost
    err := PayEnergyDiscardCost(attacker, EnergyDiscardCost{
        Count:  2,
        Type:   "any",
        Timing: "cost",
    })
    if err != nil {
        return 0, err
    }

    return 100, nil // Base damage
}
```

### Scaling Damage Effects

```go
// ScalingDamageEffect handles attacks where damage varies
type ScalingDamageEffect struct {
    BaseDamage      int
    ScalingType     string // "energy", "damage_counters", "bench_count", "cards_in_hand"
    BonusDamage     int    // Damage per scaling unit
    MaxBonus        int    // Maximum bonus damage (-1 for unlimited)
}

func CalculateScalingDamage(
    attacker *GamePokemon,
    defender *GamePokemon,
    effect ScalingDamageEffect,
    gameState *GameState,
) int {
    bonus := 0

    switch effect.ScalingType {
    case "energy":
        // Damage based on energy attached
        // Example: Blastoise's Hydro Pump
        baseRequired := 3 // Attack cost
        totalAttached := len(attacker.AttachedEnergy)
        extraEnergy := totalAttached - baseRequired
        if extraEnergy > 0 {
            bonus = extraEnergy * effect.BonusDamage
        }

    case "damage_counters":
        // Damage based on damage on target
        // Example: Mr. Mime's Meditate
        bonus = defender.DamageCounters * effect.BonusDamage

    case "bench_count":
        // Damage based on bench size
        // Example: Wigglytuff's Do the Wave
        benchCount := len(gameState.GetPlayerBench(attacker.Owner))
        bonus = benchCount * effect.BonusDamage

    case "cards_in_hand":
        // Damage based on cards in hand
        handSize := len(gameState.GetPlayer(attacker.Owner).Hand)
        bonus = handSize * effect.BonusDamage
    }

    // Apply max bonus
    if effect.MaxBonus >= 0 && bonus > effect.MaxBonus {
        bonus = effect.MaxBonus
    }

    return effect.BaseDamage + bonus
}

// Example: Wigglytuff's Do the Wave
// 10 damage + 10 for each benched Pokemon (both sides? - check ruling)
// Actually: 10 + 10 for each of YOUR benched Pokemon
func DoTheWave(attacker *GamePokemon, gameState *GameState) int {
    baseDamage := 10
    benchCount := len(gameState.GetPlayerBench(attacker.Owner))
    return baseDamage + (benchCount * 10)
}

// Example: Mr. Mime's Meditate
// 10 damage + 10 for each damage counter on defender
func Meditate(defender *GamePokemon) int {
    baseDamage := 10
    return baseDamage + (defender.DamageCounters * 10)
}
```

### Attack Copying Effects

```go
// AttackCopyEffect handles attacks like Metronome and Mirror Move
type AttackCopyEffect struct {
    CopyFrom     string // "defender", "last_attack"
    UseOwnEnergy bool   // If true, use attacker's energy
}

func ExecuteMetronome(attacker *GamePokemon, defender *GamePokemon, gameState *GameState) error {
    // Get available attacks from defender
    availableAttacks := defender.Card.Attacks

    if len(availableAttacks) == 0 {
        return fmt.Errorf("defender has no attacks to copy")
    }

    // Player selects which attack to copy
    selectedAttack := selectAttack(availableAttacks)

    // Execute the selected attack AS IF attacker had it
    // Energy cost is paid using attacker's attached energy
    // Colorless can satisfy any requirement (flexible energy matching)

    return executeAttack(attacker, defender, selectedAttack, true) // true = flexible energy
}

// Clefable's Metronome
// Copy any of defender's attacks without paying its energy cost
func ClefableMetronome(clefable *GamePokemon, defender *GamePokemon, gameState *GameState) error {
    // Metronome costs [Colorless, Colorless, Colorless]
    // After paying this, you can use ANY attack the defender has
    // WITHOUT paying that attack's energy cost

    availableAttacks := defender.Card.Attacks
    selectedAttack := selectAttack(availableAttacks)

    // Execute attack - damage is dealt by Clefable
    // Effects that reference "this Pokemon" refer to Clefable
    return executeAttackAsCopy(clefable, defender, selectedAttack)
}
```

## Power Shutdown Effects

### Goop Gas Attack

```go
// GoopGasAttack disables all Pokemon Powers until end of opponent's next turn
func ExecuteGoopGasAttack(gameState *GameState) {
    gameState.GoopGasActive = true
    gameState.GoopGasExpiresEndOf = gameState.CurrentTurn + 1 // End of opponent's next turn
}

// Call this at end of each turn
func CheckGoopGasExpiry(gameState *GameState) {
    if gameState.GoopGasActive && gameState.CurrentTurn > gameState.GoopGasExpiresEndOf {
        gameState.GoopGasActive = false
    }
}
```

### Muk's Toxic Gas

```go
// MukToxicGas is a passive Pokemon Power that disables all other Pokemon Powers
// while Muk is in play (and not affected by status)
func CheckToxicGas(gameState *GameState) bool {
    for _, player := range gameState.Players {
        for _, pokemon := range player.GetAllPokemon() {
            if pokemon.Card.Name == "Muk" {
                if !pokemon.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
                    return true // Toxic Gas is active
                }
            }
        }
    }
    return false
}

// Modify all power checks to include this
func CanUsePokemonPower(pokemon *GamePokemon, gameState *GameState) bool {
    // Muk shuts down ALL powers (including itself)
    if CheckToxicGas(gameState) && pokemon.Card.Name != "Muk" {
        return false
    }

    // Normal status checks
    if pokemon.HasAnyStatus("Asleep", "Confused", "Paralyzed") {
        return false
    }

    // Goop Gas check
    if gameState.GoopGasActive {
        return false
    }

    return true
}
```

## Effect Resolution Order

When multiple effects apply, resolve in this order:

1. **Attack declaration** - Announce attack, pay energy costs
2. **Pre-attack abilities** - Effects that trigger before attack
3. **Base damage calculation**
4. **Damage modifiers** (PlusPower, Defender, abilities)
5. **Weakness application** (x2)
6. **Resistance application** (-30)
7. **Damage prevention** (Invisible Wall, etc.)
8. **Damage application**
9. **Post-damage effects** (status conditions, etc.)
10. **Between-turn effects** (poison damage, sleep check, etc.)

```go
func ResolveCombat(attacker, defender *GamePokemon, attack *Attack, gameState *GameState) {
    // 1. Pay costs
    if attack.Effect != nil && attack.Effect.EnergyDiscard != nil {
        payEnergyDiscardCost(attacker, attack.Effect.EnergyDiscard)
    }

    // 2. Calculate base damage
    damage := attack.BaseDamage

    // 3. Apply scaling effects
    if attack.Effect != nil {
        damage = applyScalingEffects(attacker, defender, attack.Effect, damage)
    }

    // 4. Apply modifiers (PlusPower, abilities)
    damage = applyDamageModifiers(attacker, damage, gameState)

    // 5. Apply weakness
    if defender.Card.Weakness != nil && attackTypeMatches(attacker, defender.Card.Weakness.Type) {
        if defender.Card.Weakness.Value == "x2" {
            damage *= 2
        }
    }

    // 6. Apply resistance
    if defender.Card.Resistance != nil && attackTypeMatches(attacker, defender.Card.Resistance.Type) {
        damage -= 30 // Typically -30 in Base Set era
        if damage < 0 {
            damage = 0
        }
    }

    // 7. Apply damage prevention (Invisible Wall, etc.)
    damage = applyDamagePrevention(defender, damage, gameState)

    // 8. Apply damage
    defender.TakeDamage(damage)

    // 9. Apply post-damage effects
    if attack.Effect != nil && attack.Effect.StatusCondition != "" {
        applyStatusCondition(defender, attack.Effect)
    }

    // 10. Check for knock-out
    if defender.IsKnockedOut() {
        handleKnockOut(defender, attacker, gameState)
    }
}
```
