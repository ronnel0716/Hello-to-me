# IT asset inventory checker

Read-only Python automation that reviews an exported asset CSV and produces HTML, JSON and CSV findings. The eight supplied records are fictional. It does not connect to or scan computers.

![Actual generated audit report](../docs/screenshots/asset-audit.png)

## Run

Python 3.10+; standard library only. From the repository root:

```sh
python asset-check/check_inventory.py asset-check/sample.csv --output-dir output/assets
python -m unittest discover -s asset-check -p "test_*.py" -v
```

Open `output/assets/audit.html`. Expected result: **8 records, 4 flagged records, 4 clean records and 6 findings**. A row may have multiple findings. Choose a new output directory for each repeat run; existing reports are preserved. The input CSV is not changed.

## Rules

- Required columns: `asset_tag`, `device_type`, `serial_number`, `assigned_to`, `location`, `status`.
- All fields except assignee must have a value. Active devices also require an assignee.
- Duplicate asset tags and serial numbers are flagged after trimming whitespace and ignoring case. Every affected row is flagged.
- Accepted status values: `active`, `spare`, `repair`, `retired` (case insensitive).
- HTML output escapes input text. CSV output prefixes formula-like labels with an apostrophe for spreadsheet safety.

Confirm these rules with a client: shared devices may need different assignee logic. “Clean” only means no issues under these rules; it does not prove that records match physical equipment. Large datasets, device discovery, warranties, compliance certification and automated record changes are outside scope. Real exports can contain employee names and asset identifiers: use fictional or sanitized inputs when demonstrating or sharing reports.

## Contribution

Ronnel Patubo supplies the IT-support background and owns the portfolio. He requested another sample to demonstrate his services. Codex authored the new implementation, fixture, tests and documentation and generated/captured the output with AI assistance. This is an independent demonstration, not a historical paid-client engagement or proof that Ronnel independently authored every line. He should walk through and adapt the rules before offering this workflow to a client.
