import requests
import re
import time
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{BASE_DIR}/lab.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

from db import Base, Chemical, Scientist, Storage, Robot

PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

scientists = [
    {"name": "Dr. Smith", "email": "smith@lab.com"},
    {"name": "Dr. Jones", "email": "jones@lab.com"},
    {"name": "Dr. Patel", "email": "patel@lab.com"},
]

LAB_SEARCH_TERMS = [
    "hydrochloric acid", "sulfuric acid", "nitric acid", "acetic acid",
    "phosphoric acid", "sodium hydroxide", "ammonia", "potassium hydroxide",
    "ethanol", "methanol", "acetone", "benzene", "chloroform",
    "sodium chloride", "potassium permanganate", "calcium carbonate",
    "sodium bicarbonate", "hydrogen peroxide", "iodine", "water",
    "sodium sulfate", "magnesium sulfate", "copper sulfate", "zinc chloride",
    "potassium chloride", "calcium chloride", "sodium carbonate",
    "ethyl acetate", "diethyl ether", "toluene",
]

def fetch_pubchem_details(name: str, timeout: int = 15) -> dict | None:
    """Fetch formula, IUPAC name, and CAS barcode for a chemical by name."""
    try:
        encoded = requests.utils.quote(name)
        props = requests.get(
            f"{PUBCHEM_BASE}/compound/name/{encoded}/property/MolecularFormula,IUPACName/JSON",
            timeout=timeout,
        ).json()
        prop = props["PropertyTable"]["Properties"][0]
        formula = prop.get("MolecularFormula", "N/A")
        iupac = prop.get("IUPACName", name)
        time.sleep(0.4)

        synonyms = requests.get(
            f"{PUBCHEM_BASE}/compound/name/{encoded}/synonyms/JSON",
            timeout=timeout,
        ).json()
        syn_list = synonyms["InformationList"]["Information"][0]["Synonym"]
        cas = next(
            (s for s in syn_list if re.match(r"^\d+-\d+-\d+$", s)),
            None,
        )
        time.sleep(0.4)

        return {"name": name.title(), "iupac": iupac, "formula": formula, "barcode": cas}

    except Exception as e:
        print(f"   '{name}' failed: {e}")
        return None

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("Seeding chemicals...")
    print("  (Resolving names, formulas and CAS numbers from PubChem — no hardcoded data)\n")

    seeded = 0
    for term in LAB_SEARCH_TERMS:
        if seeded >= 20:
            break

        details = fetch_pubchem_details(term)
        if not details:
            continue

        if not details["barcode"]:
            print(f"   Skipping '{term}' — no CAS number found")
            continue

        if db.query(Chemical).filter(Chemical.barcode == details["barcode"]).first():
            print(f"   Skipping '{term}' — already in DB")
            continue

        db.add(Chemical(
            name=details["name"],
            iupac=details["iupac"],
            formula=details["formula"],
            barcode=details["barcode"],
        ))
        try:
            db.commit()
            print(f"   {details['name']} | {details['formula']} | CAS {details['barcode']}")
            seeded += 1
        except Exception as e:
            db.rollback()
            print(f"   DB error for '{term}': {e}")

    print(f"\n  {seeded} chemicals seeded.")

    print("\nSeeding scientists...")
    for s in scientists:
        if not db.query(Scientist).filter(Scientist.email == s["email"]).first():
            db.add(Scientist(name=s["name"], email=s["email"]))
    db.commit()
    print("   Scientists added")

    print("\nSeeding storage slots...")
    existing_slots = db.query(Storage).count()
    slots_needed = max(0, seeded - existing_slots)
    for _ in range(slots_needed):
        db.add(Storage(capacity=1, occupied=0))
    db.commit()
    print(f"   {db.query(Storage).count()} storage slots total")

    print("\nSeeding robot...")
    if not db.query(Robot).first():
        db.add(Robot(name="RoboArm-1", status="idle", position="home"))
        db.commit()
        print("   Robot added")
    else:
        print("   Robot already exists, skipping")

    db.close()
    print("\n--- Seeding Complete ---")


if __name__ == "__main__":
    seed()