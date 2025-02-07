import asyncio
import json
from database.database_service import DatabaseService
from database.repository.explanation_version import ExplanationRepository
from database.run_alembic_migrations import run_alembic_migrations
import os

db_service = DatabaseService()
explanation_repository = ExplanationRepository(db_service)

EXPLANATION_SCALES = [
    {
        "version_number": 1,
        "scale_name": "casualness",
        "description": "Controls how formal or relaxed the tone is.",
        "examples": json.dumps({
            "0": "Greetings, I require assistance.",
            "5": "Hey, could you help me out?",
            "10": "Yo, can you gimme a hand?"
        })
    },
    {
        "version_number": 1,
        "scale_name": "humor",
        "description": "Adjusts the level of wit and fun in the response.",
        "examples": json.dumps({
            "0": "That’s incorrect.",
            "5": "Well, that’s one way to look at it!",
            "10": "Oh wow, that’s like trying to toast bread with a flashlight!"
        })
    },
    {
        "version_number": 1,
        "scale_name": "conciseness",
        "description": "Controls verbosity (length of responses).",
        "examples": json.dumps({
            "0": "Certainly! Here is a detailed explanation with every possible nuance...",
            "5": "Sure! Here’s a summary of the key points...",
            "10": "Yes."
        })
    },
    {
        "version_number": 1,
        "scale_name": "punctuation_errors",
        "description": "Introduces mistakes in punctuation placement.",
        "examples": json.dumps({
            "0": "Sure, I can help you with that.",
            "5": "Sure; I can help you with that.",
            "10": "Sure I can, help... you with that!"
        })
    },
    {
        "version_number": 1,
        "scale_name": "typos",
        "description": "Adds misspellings to simulate human mistakes.",
        "examples": json.dumps({
            "0": "Absolutely! I'd be happy to help.",
            "5": "Absolutly! I’d be happy too help.",
            "10": "Absolutly! Id be hapyy to help!"
        })
    },
    {
        "version_number": 1,
        "scale_name": "grammatical_imperfections",
        "description": "Introduces grammar mistakes.",
        "examples": json.dumps({
            "0": "She doesn’t know where he went.",
            "5": "She don’t know where he went.",
            "10": "She no know where he go."
        })
    },
    {
        "version_number": 1,
        "scale_name": "redundancy",
        "description": "Inserts unnecessary words or repetitive phrases.",
        "examples": json.dumps({
            "0": "That’s a good idea.",
            "5": "That’s actually a pretty good idea, I think.",
            "10": "That’s, like, actually a really good idea, you know, I think."
        })
    },
    {
        "version_number": 1,
        "scale_name": "informal_contractions",
        "description": "Introduces slang, informal contractions, and text-like speech.",
        "examples": json.dumps({
            "0": "I am going to visit the store.",
            "5": "I’m gonna visit the store.",
            "10": "Gonna hit up the store, brb."
        })
    }
]

async def insert_explanation_scales():
    """Insert predefined explanation scales into the database."""
    print("[initialize_db] Inserting explanation scales...", flush=True)
    for scale in EXPLANATION_SCALES:
        existing = await explanation_repository.get_explanation(scale_name=scale["scale_name"], version_number=scale["version_number"])
        if not existing:
            await explanation_repository.create_explanation(
                version_number=scale["version_number"],
                scale_name=scale["scale_name"],
                description=scale["description"],
                examples=json.dumps(scale["examples"])  # Convert dict to JSON string
            )
            print(f"Inserted scale {scale['scale_name']} (version {scale['version_number']})", flush=True)
        else:
            print(f"Scale {scale['scale_name']} (version {scale['version_number']}) already exists.", flush=True)

async def initialize_db():
    print("[initialize_db] Starting database initialization...", flush=True)
    await run_alembic_migrations()
    await insert_explanation_scales()
    print("[initialize_db] Database initialization complete!", flush=True)

if __name__ == "__main__":
    asyncio.run(initialize_db())