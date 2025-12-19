# Pokemon TCG Classic Card Data

A comprehensive database of Pokemon Trading Card Game cards from the original Classic era (1999-2000), designed for building digital implementations of the Pokemon TCG.

## Overview

This repository contains complete card data for the first five sets of the Pokemon TCG Original Series, totaling **441 unique cards**. Each card includes:

- Complete gameplay mechanics (attacks, abilities, costs, effects)
- High-quality card images
- Competitive analysis and historical context
- Official rulings and errata

## Card Sets

| Set | Code | Cards | Release Date |
|-----|------|-------|--------------|
| [Base Set](01%20-%20Base%20Set%201%20(BS)/README.md) | base1 | 102 | January 9, 1999 |
| [Jungle](02%20-%20Jungle%20(JU)/README.md) | jungle | 64 | June 16, 1999 |
| [Fossil](03%20-%20Fossil%20(FO)/README.md) | fossil | 62 | October 10, 1999 |
| [Base Set 2](04%20-%20Base%20Set%202%20(B2)/README.md) | base2 | 130 | February 24, 2000 |
| [Team Rocket](05%20-%20Team%20Rocket%20(RO)/README.md) | rocket | 83 | April 24, 2000 |

## Repository Structure

```
pokemon-tcg-classic-card-data/
├── README.md                          # This file
├── 00 - Set Index/
│   ├── README.md                      # Full repository index
│   ├── card_data_schemas/             # JSON Schema definitions
│   │   ├── pokemon-card-schema.json
│   │   ├── trainer-item-card-schema.json
│   │   ├── trainer-support-card-schema.json
│   │   ├── energy-card-schema.json
│   │   └── validate_cards.py
│   └── data_definitions/              # Comprehensive documentation
│       ├── 01_pokemon_cards.md
│       ├── 02_trainer_cards.md
│       ├── 03_energy_cards.md
│       ├── 04_card_sets.md
│       ├── 05_abilities_and_effects.md
│       ├── 06_shared_cards.md
│       └── 07_game_engine.md
├── 01 - Base Set 1 (BS)/
│   ├── card_details/                  # 102 JSON card files
│   └── card_images/                   # 102 card images
├── 02 - Jungle (JU)/
│   ├── card_details/                  # 64 JSON card files
│   └── card_images/                   # 64 card images
├── 03 - Fossil (FO)/
│   ├── card_details/                  # 62 JSON card files
│   └── card_images/                   # 62 card images
├── 04 - Base Set 2 (B2)/
│   ├── card_details/                  # 130 JSON card files
│   └── card_images/                   # 130 card images
└── 05 - Team Rocket (RO)/
    ├── card_details/                  # 83 JSON card files
    └── card_images/                   # 83 card images
```

## Card Data Format

Each card is stored as a JSON file with comprehensive gameplay data:

```json
{
  "id": "base1-004",
  "name": "Charizard",
  "number": 4,
  "set": {
    "id": "base1",
    "name": "Base Set",
    "series": "Original",
    "releaseDate": "1999-01-09"
  },
  "cardType": "pokemon",
  "hp": 120,
  "types": ["Fire"],
  "stage": "Stage 2",
  "attacks": [...],
  "abilities": [...],
  "weakness": { "type": "Water", "value": "x2" },
  "resistance": { "type": "Fighting", "value": "-30" },
  "retreatCost": ["Colorless", "Colorless", "Colorless"],
  "imageUrl": "004_charizard.jpg"
}
```

### Card Types

- **Pokemon Cards** (`cardType: "pokemon"`) - Basic, Stage 1, and Stage 2 Pokemon with HP, attacks, abilities, weakness, and resistance
- **Trainer Cards** (`cardType: "trainer"`) - Item and Supporter cards that provide various effects
- **Energy Cards** (`cardType: "energy"`) - Basic and Special Energy cards that power attacks

## File Naming Convention

Card files follow the format: `{paddedNumber}_{card-name-lowercase-hyphenated}.json`

Examples:
- `004_charizard.json`
- `058_pikachu.json`
- `096_double-colorless-energy.json`

## Quick Start

### Loading Cards (Go)

```go
cards, err := LoadAllCards("/path/to/pokemon-tcg-classic-card-data")
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Loaded %d cards\n", len(cards))
```

See [data_definitions/README.md](00%20-%20Set%20Index/data_definitions/README.md) for complete code examples.

### Validating Card Data

```bash
cd "00 - Set Index/card_data_schemas"
python3 validate_cards.py
```

## Documentation

Comprehensive documentation is available in the `00 - Set Index/data_definitions/` directory:

| Document | Description |
|----------|-------------|
| [01_pokemon_cards.md](00%20-%20Set%20Index/data_definitions/01_pokemon_cards.md) | Pokemon card schema and implementation |
| [02_trainer_cards.md](00%20-%20Set%20Index/data_definitions/02_trainer_cards.md) | Trainer Item and Supporter schemas |
| [03_energy_cards.md](00%20-%20Set%20Index/data_definitions/03_energy_cards.md) | Energy card schema (Basic and Special) |
| [04_card_sets.md](00%20-%20Set%20Index/data_definitions/04_card_sets.md) | Individual set details and characteristics |
| [05_abilities_and_effects.md](00%20-%20Set%20Index/data_definitions/05_abilities_and_effects.md) | Programming Pokemon Powers and effects |
| [06_shared_cards.md](00%20-%20Set%20Index/data_definitions/06_shared_cards.md) | Reprinted cards across sets |
| [07_game_engine.md](00%20-%20Set%20Index/data_definitions/07_game_engine.md) | Complete game engine implementation guide |

## License & Attribution

This data is intended for educational and personal use in creating digital implementations of the Pokemon Trading Card Game. Pokemon and Pokemon TCG are trademarks of Nintendo, Creatures Inc., and GAME FREAK Inc.
