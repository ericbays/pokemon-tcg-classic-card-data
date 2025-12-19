#!/usr/bin/env python3
"""
Pokemon TCG Card Data Validator
Validates all card JSON files against their appropriate schemas.
"""

import json
import os
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import validate, ValidationError, SchemaError
except ImportError:
    print("Error: jsonschema library required. Install with: pip install jsonschema")
    sys.exit(1)

# Base directory (script is now in 00 - Set Index/card_data_schemas/)
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent.parent  # Go up two levels to project root

# Schema paths (schemas are in same directory as script)
SCHEMA_DIR = SCRIPT_DIR
SCHEMAS = {
    "pokemon": SCHEMA_DIR / "pokemon-card-schema.json",
    "trainer-item": SCHEMA_DIR / "trainer-item-card-schema.json",
    "trainer-support": SCHEMA_DIR / "trainer-support-card-schema.json",
    "energy": SCHEMA_DIR / "energy-card-schema.json",
}

# Set directories
SET_DIRS = [
    BASE_DIR / "01 - Base Set 1 (BS)" / "card_details",
    BASE_DIR / "02 - Jungle (JU)" / "card_details",
    BASE_DIR / "03 - Fossil (FO)" / "card_details",
    BASE_DIR / "04 - Base Set 2 (B2)" / "card_details",
    BASE_DIR / "05 - Team Rocket (RO)" / "card_details",
]


def load_schema(schema_path):
    """Load a JSON schema from file."""
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_card(card_path):
    """Load a card JSON file."""
    with open(card_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def determine_schema_type(card_data):
    """Determine which schema should be used for a card based on its cardType."""
    card_type = card_data.get("cardType", "").lower()
    supertype = card_data.get("supertype", "")
    subtypes = card_data.get("subtypes", [])

    if card_type == "pokemon":
        return "pokemon"
    elif card_type == "energy":
        return "energy"
    elif card_type in ["trainer", "trainer-item"]:
        # Check subtypes to determine if Item or Supporter
        if "Supporter" in subtypes:
            return "trainer-support"
        else:
            return "trainer-item"
    else:
        return None


def validate_card(card_path, schemas):
    """Validate a single card against its appropriate schema."""
    errors = []

    try:
        card_data = load_card(card_path)
    except json.JSONDecodeError as e:
        return [f"JSON parse error: {e}"]
    except Exception as e:
        return [f"Error loading file: {e}"]

    schema_type = determine_schema_type(card_data)

    if schema_type is None:
        return [f"Unknown card type: {card_data.get('cardType', 'missing')}"]

    if schema_type not in schemas:
        return [f"No schema loaded for type: {schema_type}"]

    schema = schemas[schema_type]

    try:
        validate(instance=card_data, schema=schema)
    except ValidationError as e:
        # Get the path to the error
        path = " -> ".join([str(p) for p in e.absolute_path]) if e.absolute_path else "root"
        errors.append(f"Validation error at '{path}': {e.message}")
    except SchemaError as e:
        errors.append(f"Schema error: {e.message}")

    return errors


def main():
    """Main validation function."""
    print("=" * 70)
    print("Pokemon TCG Card Data Validator")
    print("=" * 70)
    print()

    # Load all schemas
    print("Loading schemas...")
    schemas = {}
    for schema_name, schema_path in SCHEMAS.items():
        if not schema_path.exists():
            print(f"  WARNING: Schema not found: {schema_path}")
            continue
        try:
            schemas[schema_name] = load_schema(schema_path)
            print(f"  Loaded: {schema_name}")
        except Exception as e:
            print(f"  ERROR loading {schema_name}: {e}")

    print()

    # Validate all cards
    total_cards = 0
    valid_cards = 0
    invalid_cards = 0
    all_errors = []

    for set_dir in SET_DIRS:
        if not set_dir.exists():
            print(f"WARNING: Set directory not found: {set_dir}")
            continue

        set_name = set_dir.parent.name
        card_files = sorted(set_dir.glob("*.json"))
        set_errors = []

        print(f"Validating {set_name}...")

        for card_file in card_files:
            total_cards += 1
            errors = validate_card(card_file, schemas)

            if errors:
                invalid_cards += 1
                for error in errors:
                    set_errors.append(f"  {card_file.name}: {error}")
            else:
                valid_cards += 1

        if set_errors:
            print(f"  Found {len(set_errors)} error(s) in {set_name}")
            all_errors.extend(set_errors)
        else:
            print(f"  All {len(card_files)} cards valid")

    # Summary
    print()
    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total cards checked: {total_cards}")
    print(f"Valid cards: {valid_cards}")
    print(f"Invalid cards: {invalid_cards}")
    print()

    if all_errors:
        print("ERRORS FOUND:")
        print("-" * 70)
        for error in all_errors:
            print(error)
        print()
        return 1
    else:
        print("All cards passed validation!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
