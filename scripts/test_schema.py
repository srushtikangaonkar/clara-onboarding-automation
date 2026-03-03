from schema import AccountMemo

sample = AccountMemo(
    account_id="ACC001",
    company_name="ABC Fire Protection"
)

print(sample.model_dump_json(indent=2))
