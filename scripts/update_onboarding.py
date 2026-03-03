import os
import json
import re
import sys
from deepdiff import DeepDiff
from schema import AccountMemo
from generate_agent_spec import build_agent_spec


# -----------------------------
# Extract Onboarding Updates
# -----------------------------
def extract_onboarding_updates(text: str):
    updates = {}

    # Extract timezone (CST, EST, PST, MST etc.)
    tz_match = re.search(r"\b(CST|EST|PST|MST)\b", text, re.IGNORECASE)
    if tz_match:
        updates["timezone"] = tz_match.group(1).upper()

    # Emergency routing rule
    if "transferred directly to dispatch" in text.lower():
        updates["emergency_routing"] = True

    # Extract timeout (e.g., 60 seconds)
    timeout_match = re.search(r"(\d+)\s*seconds", text.lower())
    if timeout_match:
        updates["timeout"] = int(timeout_match.group(1))

    # Integration constraint
    if "never create sprinkler jobs" in text.lower():
        updates["integration_constraint"] = "Never create sprinkler jobs in ServiceTrade"

    return updates


# -----------------------------
# Apply Updates to v1 Memo
# -----------------------------
def apply_updates(v1_memo: AccountMemo, updates: dict):
    v2_data = v1_memo.model_dump()

    # Update timezone
    if "timezone" in updates and v2_data.get("business_hours"):
        v2_data["business_hours"]["timezone"] = updates["timezone"]

    # Update integration constraints (avoid duplicates)
    if "integration_constraint" in updates:
        if updates["integration_constraint"] not in v2_data["integration_constraints"]:
            v2_data["integration_constraints"].append(
                updates["integration_constraint"]
            )

    # Update emergency routing
    if "emergency_routing" in updates:
        v2_data["emergency_routing_rules"].append({
            "description": "Emergency sprinkler calls",
            "transfer_to": "Dispatch",
            "order": 1,
            "fallback_action": "Notify dispatch manually"
        })

    # Update transfer rules
    if "timeout" in updates:
        v2_data["call_transfer_rules"] = {
            "timeout_seconds": updates["timeout"],
            "retry_attempts": 1,
            "failure_message": "Dispatch will be notified immediately."
        }

    return AccountMemo(**v2_data)


# -----------------------------
# Save v2 Outputs + Diff
# -----------------------------
def save_v2_outputs(account_id: str, v2_memo: AccountMemo, v1_data: dict):
    base_path = f"outputs/accounts/{account_id}/v2"
    os.makedirs(base_path, exist_ok=True)

    # Save updated memo
    with open(f"{base_path}/account_memo.json", "w", encoding="utf-8") as f:
        json.dump(v2_memo.model_dump(), f, indent=2)

    # Save updated agent spec
    agent_spec = build_agent_spec(v2_memo)
    agent_spec["version"] = "v2"

    with open(f"{base_path}/agent_spec.json", "w", encoding="utf-8") as f:
        json.dump(agent_spec, f, indent=2)

    # Generate JSON-safe diff
    raw_diff = DeepDiff(
        v1_data,
        v2_memo.model_dump(),
        ignore_order=True
    )

    safe_diff = json.loads(raw_diff.to_json())

    with open(f"{base_path}/changes.json", "w", encoding="utf-8") as f:
        json.dump(safe_diff, f, indent=2)


# -----------------------------
# Entry Point (Dynamic)
# -----------------------------
if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python update_onboarding.py <account_id> <onboarding_transcript_path>")
        sys.exit(1)

    account_id = sys.argv[1]
    onboarding_file = sys.argv[2]

    if not os.path.exists(onboarding_file):
        print(" Onboarding file not found.")
        sys.exit(1)

    v1_path = f"outputs/accounts/{account_id}/v1/account_memo.json"

    if not os.path.exists(v1_path):
        print(" v1 not found for this account.")
        sys.exit(1)

    # Load onboarding transcript
    with open(onboarding_file, "r", encoding="utf-8") as f:
        onboarding_text = f.read()

    updates = extract_onboarding_updates(onboarding_text)

    # Load v1 memo
    with open(v1_path, "r", encoding="utf-8") as f:
        v1_data = json.load(f)

    v1_memo = AccountMemo(**v1_data)

    # Apply updates
    v2_memo = apply_updates(v1_memo, updates)

    # Save outputs
    save_v2_outputs(account_id, v2_memo, v1_data)

    print(f" v2 generated successfully for account: {account_id}")