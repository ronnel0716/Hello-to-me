"""Audit a local asset CSV without modifying its source or connecting to devices."""
import argparse
import csv
import html
import json
from collections import Counter
from pathlib import Path

FIELDS = ('asset_tag', 'device_type', 'serial_number', 'assigned_to', 'location', 'status')
STATUSES = {'active', 'spare', 'repair', 'retired'}


def audit(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as source:
        reader = csv.DictReader(source)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise ValueError('Required CSV columns: ' + ', '.join(FIELDS))
        records = []
        for line, row in enumerate(reader, 2):
            if None in row:
                raise ValueError(f'Row {line} has extra columns; check CSV quoting')
            records.append({'line': line, **{key: (row.get(key) or '').strip() for key in FIELDS}})
    if not records:
        raise ValueError('CSV contains no asset records')
    tags = Counter(r['asset_tag'].casefold() for r in records if r['asset_tag'])
    serials = Counter(r['serial_number'].casefold() for r in records if r['serial_number'])
    findings = []
    for record in records:
        issues = []
        for key in ('asset_tag', 'device_type', 'serial_number', 'location', 'status'):
            if not record[key]:
                issues.append('Missing ' + key.replace('_', ' '))
        if record['asset_tag'] and tags[record['asset_tag'].casefold()] > 1:
            issues.append('Duplicate asset tag')
        if record['serial_number'] and serials[record['serial_number'].casefold()] > 1:
            issues.append('Duplicate serial number')
        status = record['status'].casefold()
        if status and status not in STATUSES:
            issues.append('Unknown status')
        if status == 'active' and not record['assigned_to']:
            issues.append('Active asset has no assignee')
        if issues:
            findings.append({**record, 'issues': issues})
    return {'total_records': len(records), 'flagged_records': len(findings),
            'clean_records': len(records) - len(findings),
            'issue_count': sum(len(r['issues']) for r in findings), 'findings': findings}


def html_report(result):
    esc = html.escape
    rows = ''.join('<tr><td>' + str(r['line']) + '</td><td>' + esc(r['asset_tag'] or '(missing)') +
                   '</td><td>' + esc(r['device_type']) + '</td><td>' +
                   '<br>'.join(esc(issue) for issue in r['issues']) + '</td></tr>' for r in result['findings'])
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>IT Asset Inventory Audit</title><style>body{margin:0;background:#edf3f1;color:#173c36;font:17px/1.6 system-ui}'
            'main{max-width:1040px;margin:32px auto;padding:36px;background:white;border-radius:22px}h1{font-size:38px;margin:12px 0}'
            'small,footer{color:#52716a}.stats{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0}.stats div{flex:1;background:#edf3f1;border-radius:12px;padding:18px}'
            'strong{font-size:30px;display:block}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:12px;border-bottom:1px solid #d6e3de;vertical-align:top}'
            '.table-wrap{overflow-x:auto}footer{margin-top:20px;font-size:14px}@media(max-width:600px){main{padding:18px;margin:12px}h1{font-size:28px}}</style>'
            '<main><small>RONNEL PATUBO / PYTHON + IT SUPPORT SAMPLE</small><h1>IT asset inventory audit</h1>'
            '<p>Find missing details and duplicate identifiers before updating your records.</p><div class="stats">'
            f'<div>Records checked<strong>{result["total_records"]}</strong></div><div>Flagged records<strong>{result["flagged_records"]}</strong></div>'
            f'<div>Clean records<strong>{result["clean_records"]}</strong></div><div>Issues found<strong>{result["issue_count"]}</strong></div></div>'
            '<div class="table-wrap"><table><thead><tr><th>CSV row</th><th>Asset tag</th><th>Device</th><th>Findings</th></tr></thead><tbody>' +
            (rows or '<tr><td colspan="4">No issues found under the configured rules.</td></tr>') + '</tbody></table></div>'
            '<footer>Independent demo · fictional records · AI-assisted implementation. Read-only CSV checks; no device scan, repairs or inventory changes. Human review required.</footer></main></html>')


def write_reports(result, directory):
    directory = Path(directory)
    targets = [directory/name for name in ('audit.html', 'audit.json', 'findings.csv')]
    if any(path.exists() for path in targets):
        raise ValueError('Output already exists; choose a fresh output directory')
    directory.mkdir(parents=True, exist_ok=True)
    targets[0].write_text(html_report(result), encoding='utf-8')
    targets[1].write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    with targets[2].open('w', encoding='utf-8-sig', newline='') as output:
        writer = csv.writer(output)
        writer.writerow(['csv_row', 'asset_tag', 'device_type', 'issues'])
        for record in result['findings']:
            values = [str(record['line']), record['asset_tag'], record['device_type'], '; '.join(record['issues'])]
            writer.writerow(["'" + v if v.lstrip().startswith(('=', '+', '-', '@')) else v for v in values])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('output/assets'))
    args = parser.parse_args(argv)
    try:
        result = audit(args.input)
        write_reports(result, args.output_dir)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))
    print(f"Checked {result['total_records']} records: {result['flagged_records']} flagged, {result['issue_count']} issues. Output: {args.output_dir}")


if __name__ == '__main__':
    main()
