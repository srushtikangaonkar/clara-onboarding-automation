import os
import subprocess
import sys


DEMO_DIR = "transcripts/demo"
ONBOARDING_DIR = "transcripts/onboarding"


def run_command(command):
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f" Command failed: {command}")
        sys.exit(1)


def get_account_id_from_demo(demo_path):
    # Run extract_demo.py and capture output
    result = subprocess.run(
        f"python scripts/extract_demo.py {demo_path}",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        sys.exit(1)

    print(result.stdout.strip())

    # Extract account_id from output
    # Expected format: " v1 generated for account: ACCOUNT_ID"
    parts = result.stdout.strip().split(":")
    if len(parts) < 2:
        print(" Could not determine account_id from demo output.")
        sys.exit(1)

    return parts[-1].strip()


def main():
    if not os.path.exists(DEMO_DIR):
        print(" Demo directory not found.")
        sys.exit(1)

    demo_files = [
        f for f in os.listdir(DEMO_DIR)
        if f.endswith(".txt")
    ]

    if not demo_files:
        print(" No demo files found.")
        return

    print(f" Found {len(demo_files)} demo file(s). Starting pipeline...\n")

    for demo_file in demo_files:
        demo_path = os.path.join(DEMO_DIR, demo_file)

        print(f" Processing Demo: {demo_file}")

        # Step 1: Generate v1
        account_id = get_account_id_from_demo(demo_path)

        # Step 2: Check if onboarding exists
        onboarding_path = os.path.join(ONBOARDING_DIR, demo_file)

        if os.path.exists(onboarding_path):
            print(f" Found matching onboarding file: {demo_file}")

            run_command(
                f"python scripts/update_onboarding.py {account_id} {onboarding_path}"
            )
        else:
            print(" No onboarding file found. Skipping v2.")

        print("--------------------------------------------------")

    print("\n Pipeline execution complete.")


if __name__ == "__main__":
    main()