import os
import json
from schema import AccountMemo


# -----------------------------
# Build System Prompt
# -----------------------------
def build_system_prompt(memo: AccountMemo) -> str:
    company = memo.company_name or "the company"
    services = ", ".join(memo.services_supported) if memo.services_supported else "their services"

    business_hours_text = "Business hours not confirmed."
    if memo.business_hours:
        business_hours_text = (
            f"{memo.business_hours.days} "
            f"{memo.business_hours.start_time} to {memo.business_hours.end_time}"
        )

    emergency_list = (
        ", ".join(memo.emergency_definition)
        if memo.emergency_definition
        else "any urgent service issue"
    )

    prompt = f"""
You are an AI voice assistant for {company}.

They provide: {services}.

Business Hours: {business_hours_text}

Emergency situations include: {emergency_list}.

--- BUSINESS HOURS FLOW ---
1. Greet caller professionally.
2. Ask how you can help.
3. Collect caller's full name and callback number.
4. Determine if the issue is emergency or non-emergency.
5. If emergency, transfer immediately to dispatch.
6. If non-emergency, route according to company rules.
7. If transfer fails, apologize and assure callback.
8. Ask if they need anything else.
9. Close politely.

--- AFTER HOURS FLOW ---
1. Greet caller.
2. Ask reason for call.
3. Confirm if it is an emergency.
4. If emergency:
   - Immediately collect name, phone number, and service address.
   - Attempt transfer to on-call technician.
   - If transfer fails, reassure caller of urgent follow-up.
5. If non-emergency:
   - Collect name, phone number, and brief details.
   - Inform them the office will follow up during business hours.
6. Ask if they need anything else.
7. Close politely.

IMPORTANT:
- Only collect necessary information.
- Do not mention internal systems or tools.
- Keep conversation efficient and professional.
"""

    return prompt.strip()


# -----------------------------
# Build Agent Spec JSON
# -----------------------------
def build_agent_spec(memo: AccountMemo):
    return {
        "agent_name": f"{memo.company_name} Voice Assistant",
        "voice_style": "Professional and calm",
        "version": "v1",
        "timezone": memo.business_hours.timezone if memo.business_hours else None,
        "business_hours": memo.business_hours.model_dump()
        if memo.business_hours
        else None,
        "system_prompt": build_system_prompt(memo),
        "call_transfer_protocol": {
            "timeout_seconds": 60,
            "retry_attempts": 1,
            "on_failure_message": "We are unable to connect you right now. A team member will contact you shortly."
        },
        "fallback_protocol": {
            "action": "Collect details and assure callback"
        }
    }


# -----------------------------
# Save Agent Spec
# -----------------------------
def save_agent_spec(account_id: str, agent_spec: dict):
    base_path = f"outputs/accounts/{account_id}/v1"
    os.makedirs(base_path, exist_ok=True)

    with open(f"{base_path}/agent_spec.json", "w") as f:
        json.dump(agent_spec, f, indent=2)


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    memo_path = "outputs/accounts/ABC_FIRE_PROTECTION/v1/account_memo.json"

    with open(memo_path, "r") as f:
        memo_data = json.load(f)

    memo = AccountMemo(**memo_data)

    agent_spec = build_agent_spec(memo)
    save_agent_spec(memo.account_id, agent_spec)

    print(" v1 Agent Spec generated successfully.")