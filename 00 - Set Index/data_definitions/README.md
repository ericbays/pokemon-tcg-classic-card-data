# Pokemon TCG Card Data - Documentation & Implementation Guide

This directory contains comprehensive documentation for the Pokemon TCG card data, designed to enable developers to build a fully functional digital version of the Pokemon Trading Card Game.

## Overview

The card database covers the first five sets of the Original Series (1999-2000):

| Set | Code | Name | Release Date | Cards |
|-----|------|------|--------------|-------|
| 01 | base1 | Base Set | 1999-01-09 | 102 |
| 02 | jungle | Jungle | 1999-06-16 | 64 |
| 03 | fossil | Fossil | 1999-10-10 | 62 |
| 04 | base2 | Base Set 2 | 2000-02-24 | 130 |
| 05 | rocket | Team Rocket | 2000-04-24 | 83 |

**Total Cards: 441**

## Documentation Structure

| Document | Description |
|----------|-------------|
| [01_pokemon_cards.md](01_pokemon_cards.md) | Pokemon card schema, Go structures, and implementation |
| [02_trainer_cards.md](02_trainer_cards.md) | Trainer Item and Supporter card schemas |
| [03_energy_cards.md](03_energy_cards.md) | Energy card schema (Basic and Special) |
| [04_card_sets.md](04_card_sets.md) | Individual set details and unique characteristics |
| [05_abilities_and_effects.md](05_abilities_and_effects.md) | Programming Pokemon Powers and attack effects |
| [06_shared_cards.md](06_shared_cards.md) | Cards reprinted across sets with mechanical differences |
| [07_game_engine.md](07_game_engine.md) | Complete game engine implementation guide |

## Data File Structure

```
Pokemon TCG - Card Sets/
├── 00 - Set Index/
│   ├── card_data_schemas/          # JSON Schema definitions
│   │   ├── pokemon-card-schema.json
│   │   ├── trainer-item-card-schema.json
│   │   ├── trainer-support-card-schema.json
│   │   ├── energy-card-schema.json
│   │   └── validate_cards.py
│   └── data_definitions/           # This documentation
├── 01 - Base Set 1 (BS)/
│   ├── card_details/               # 102 JSON card files
│   └── card_images/
├── 02 - Jungle (JU)/
│   ├── card_details/               # 64 JSON card files
│   └── card_images/
├── 03 - Fossil (FO)/
│   ├── card_details/               # 62 JSON card files
│   └── card_images/
├── 04 - Base Set 2 (B2)/
│   ├── card_details/               # 130 JSON card files
│   └── card_images/
└── 05 - Team Rocket (RO)/
    ├── card_details/               # 83 JSON card files
    └── card_images/
```

## Card File Naming Convention

Card JSON files follow the format: `{paddedNumber}_{card-name-lowercase-hyphenated}.json`

Examples:
- `004_charizard.json`
- `058_pikachu.json`
- `006_mr.-mime.json`
- `096_double-colorless-energy.json`

## Card ID Format

All cards have a unique identifier: `{setCode}-{paddedNumber}`

Examples:
- `base1-004` (Base Set Charizard)
- `jungle-060` (Jungle Pikachu)
- `fossil-003` (Fossil Ditto)
- `rocket-004` (Dark Charizard)

## Quick Start - Loading Cards in Go

```go
package main

import (
    "encoding/json"
    "fmt"
    "os"
    "path/filepath"
)

// Simplified card structure for quick loading
type Card struct {
    ID        string   `json:"id"`
    Name      string   `json:"name"`
    CardType  string   `json:"cardType"`
    Supertype string   `json:"supertype"`
    HP        int      `json:"hp,omitempty"`
    Types     []string `json:"types,omitempty"`
}

func LoadAllCards(baseDir string) ([]Card, error) {
    var cards []Card

    setDirs := []string{
        "01 - Base Set 1 (BS)",
        "02 - Jungle (JU)",
        "03 - Fossil (FO)",
        "04 - Base Set 2 (B2)",
        "05 - Team Rocket (RO)",
    }

    for _, setDir := range setDirs {
        cardDetailsPath := filepath.Join(baseDir, setDir, "card_details")

        files, err := os.ReadDir(cardDetailsPath)
        if err != nil {
            return nil, fmt.Errorf("reading %s: %w", setDir, err)
        }

        for _, file := range files {
            if filepath.Ext(file.Name()) != ".json" {
                continue
            }

            data, err := os.ReadFile(filepath.Join(cardDetailsPath, file.Name()))
            if err != nil {
                return nil, fmt.Errorf("reading %s: %w", file.Name(), err)
            }

            var card Card
            if err := json.Unmarshal(data, &card); err != nil {
                return nil, fmt.Errorf("parsing %s: %w", file.Name(), err)
            }

            cards = append(cards, card)
        }
    }

    return cards, nil
}

func main() {
    cards, err := LoadAllCards("/path/to/Pokemon TCG - Card Sets")
    if err != nil {
        panic(err)
    }

    fmt.Printf("Loaded %d cards\n", len(cards))

    // Count by type
    typeCounts := make(map[string]int)
    for _, card := range cards {
        typeCounts[card.CardType]++
    }

    for cardType, count := range typeCounts {
        fmt.Printf("  %s: %d\n", cardType, count)
    }
}
```

## Card Types

The data contains three main card types:

### Pokemon Cards (`cardType: "pokemon"`)
- Basic, Stage 1, and Stage 2 Pokemon
- Include HP, types, attacks, abilities, weakness, resistance
- May have evolution chains

### Trainer Cards (`cardType: "trainer"`)
- **Item** cards: Can be played multiple times per turn
- **Supporter** cards: Limited to one per turn (modern rules)

### Energy Cards (`cardType: "energy"`)
- **Basic Energy**: Provides one energy of a specific type
- **Special Energy**: Provides energy with additional effects

## Key Implementation Considerations

### 1. Turn Structure
The game follows a specific turn sequence:
1. Draw a card
2. Perform actions (any order, any number):
   - Attach ONE energy from hand
   - Play Trainer cards
   - Use Pokemon Powers (if not blocked)
   - Evolve Pokemon (not first turn, not just played)
   - Retreat active Pokemon (pay retreat cost)
   - Play Basic Pokemon to bench
3. Attack (ends turn)

### 2. Damage Calculation
```
Final Damage = (Base Damage + Modifiers) * Weakness - Resistance
```
- Weakness: Multiplies damage (usually x2)
- Resistance: Subtracts from damage (usually -30)
- Damage is applied in multiples of 10 (damage counters)

### 3. Status Conditions
Five status conditions affect Pokemon:
- **Asleep**: Cannot attack/retreat; flip coin to wake up between turns
- **Confused**: Flip coin to attack; if tails, damage self
- **Paralyzed**: Cannot attack/retreat; removed after next turn
- **Poisoned**: Take 10 damage between turns
- **Burned**: Flip coin; if tails, take 20 damage between turns

### 4. Evolution Rules
- Cannot evolve on the first turn of the game
- Cannot evolve a Pokemon the same turn it was played
- Cannot evolve a Pokemon the same turn it already evolved
- Stage 2 Pokemon evolve from Stage 1 (except with Pokemon Breeder)

## Validation

Use the provided validation script to verify card data integrity:

```bash
cd "00 - Set Index/card_data_schemas"
python3 validate_cards.py
```

This validates all card JSON files against their respective schemas.

## License & Attribution

This data is intended for educational and personal use in creating digital implementations of the Pokemon Trading Card Game. Pokemon and Pokemon TCG are trademarks of Nintendo, Creatures Inc., and GAME FREAK Inc.
