import os
import re
import json
import sys
from schema import AccountMemo, BusinessHours


# -----------------------------
# Utility: Generate Account ID
# -----------------------------
def generate_account_id(company_name: str) -> str:
    return re.sub(r"\s+", "_", company_name.strip()).upper()


# -----------------------------
# Extract Company Name (More Robust)
# -----------------------------
def extract_company_name(text: str) -> str:
    patterns = [
        r"(?:this is|we are|you're speaking with|hello from)\s+([A-Za-z\s]+)",
        r"([A-Za-z\s]+)\s+(?:speaking|here)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return "UNKNOWN_COMPANY"


# -----------------------------
# Extract Business Hours (More Flexible)
# -----------------------------
def extract_business_hours(text: str):
    # Match Mon-Fri or Monday to Friday etc.
    day_pattern = r"(Mon(?:day)?\s*(?:to|-)\s*Fri(?:day)?)"
    time_pattern = r"(\d{1,2}\s*(?:AM|PM|am|pm))\s*(?:to|-)\s*(\d{1,2}\s*(?:AM|PM|am|pm))"

    day_match = re.search(day_pattern, text, re.IGNORECASE)
    time_match = re.search(time_pattern, text)

    if day_match and time_match:
        return BusinessHours(
            days="Monday-Friday",
            start_time=time_match.group(1).upper(),
            end_time=time_match.group(2).upper(),
            timezone=None
        )

    return None


# -----------------------------
# Extract Emergency Definitions (Expanded)
# -----------------------------
def extract_emergency_definition(text: str):
    text_lower = text.lower()
    emergencies = []

    emergency_keywords = {
        "sprinkler leak": ["sprinkler leak", "leaking sprinkler", "sprinkler leaking"],
        "fire alarm triggered": ["fire alarm triggered", "alarm going off", "alarm activation"],
        "fire suppression issue": ["fire suppression", "suppression failure"]
    }

    for label, variations in emergency_keywords.items():
        for phrase in variations:
            if phrase in text_lower:
                emergencies.append(label)
                break

    return list(set(emergencies))


# -----------------------------
# Extract Supported Services (Improved)
# -----------------------------
def extract_services(text: str):
    text_lower = text.lower()
    services = []

    if "sprinkler" in text_lower:
        services.append("Sprinkler Services")

    if "alarm" in text_lower:
        services.append("Fire Alarm Services")

    if "inspection" in text_lower or "inspect" in text_lower:
        services.append("Inspection Scheduling")

    if "extinguisher" in text_lower:
        services.append("Fire Extinguisher Services")

    return list(set(services))


# -----------------------------
# Main Extraction Logic
# -----------------------------
def extract_demo(transcript_path: str):
    with open(transcript_path, "r", encoding="utf-8") as f:
        text = f.read()

    company_name = extract_company_name(text)
    account_id = generate_account_id(company_name)

    business_hours = extract_business_hours(text)

    memo = AccountMemo(
        account_id=account_id,
        company_name=company_name,
        business_hours=business_hours,
        services_supported=extract_services(text),
        emergency_definition=extract_emergency_definition(text),
        questions_or_unknowns=[],
    )

    # Flag missing fields explicitly
    if memo.business_hours is None:
        memo.questions_or_unknowns.append(
            "Business hours not clearly defined in demo call"
        )

    if memo.company_name == "UNKNOWN_COMPANY":
        memo.questions_or_unknowns.append(
            "Company name not clearly identified in demo call"
        )

    return memo


# -----------------------------
# Save Output
# -----------------------------
def save_output(memo: AccountMemo):
    base_path = f"outputs/accounts/{memo.account_id}/v1"
    os.makedirs(base_path, exist_ok=True)

    with open(f"{base_path}/account_memo.json", "w", encoding="utf-8") as f:
        json.dump(memo.model_dump(), f, indent=2)


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python extract_demo.py <demo_transcript_path>")
        sys.exit(1)

    transcript_file = sys.argv[1]

    if not os.path.exists(transcript_file):
        print("Transcript file not found.")
        sys.exit(1)

    memo = extract_demo(transcript_file)
    save_output(memo)

    print(f"v1 generated for account: {memo.account_id}")