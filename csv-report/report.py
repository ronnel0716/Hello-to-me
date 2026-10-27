"""Validate sales CSV and write a local summary; Python standard library only."""
import argparse
import csv
import html
from decimal import Decimal, InvalidOperation
from pathlib import Path


def summarize(path):
    totals = {}
    with Path(path).open(encoding='utf-8-sig', newline='') as source:
        reader = csv.DictReader(source)
        required = {'category', 'quantity', 'unit_price'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('CSV requires category, quantity, unit_price columns')
        for line, row in enumerate(reader, 2):
            try:
                category = (row['category'] or '').strip()
                quantity = int(row['quantity'])
                price = Decimal(row['unit_price'])
                if not category or quantity < 1 or not price.is_finite() or price < 0 or price != price.quantize(Decimal('.01')):
                    raise ValueError('invalid value')
                totals[category] = totals.get(category, Decimal('0')) + quantity * price
            except (ValueError, TypeError, InvalidOperation, KeyError) as exc:
                raise ValueError(f'Invalid CSV row {line}: category, positive whole quantity and non-negative two-decimal price required') from exc
    if not totals:
        raise ValueError('CSV contains no sales rows')
    return dict(sorted(totals.items()))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('output'))
    args = parser.parse_args(argv)
    try:
        totals = summarize(args.input)
        destinations = [args.output_dir / 'summary.csv', args.output_dir / 'report.html']
        if any(p.exists() for p in destinations):
            raise ValueError('Output exists; choose a new output directory')
        args.output_dir.mkdir(parents=True, exist_ok=True)
        with destinations[0].open('w', encoding='utf-8-sig', newline='') as target:
            writer = csv.writer(target)
            writer.writerow(['category', 'revenue_php'])
            # Prevent spreadsheet formula interpretation of imported category names.
            for category, value in totals.items():
                safe = "'" + category if category.lstrip().startswith(('=', '+', '-', '@')) else category
                writer.writerow([safe, f'{value:.2f}'])
        rows = ''.join(f'<tr><td>{html.escape(k)}</td><td>₱{v:,.2f}</td></tr>' for k,v in totals.items())
        page = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
                '<title>Sales CSV report</title><style>body{font:18px/1.6 system-ui;background:#eef3f2;color:#173c36}main{max-width:760px;margin:50px auto;padding:40px;background:white;border-radius:20px}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:16px;border-bottom:1px solid #d7e5df}h1{font-size:42px}small{color:#52716a}</style>'
                '<main><small>RONNEL PATUBO / PYTHON AUTOMATION SAMPLE</small><h1>Sales summary</h1><p>Fictional input · amounts in PHP · revenue before expenses and tax</p>'
                '<table><thead><tr><th>Category</th><th>Revenue</th></tr></thead><tbody>'+rows+
                f'</tbody></table><h2>Total ₱{sum(totals.values()):,.2f}</h2><p>Validated CSV → category totals → spreadsheet and HTML outputs.</p></main></html>')
        destinations[1].write_text(page, encoding='utf-8')
        print(f'Processed {len(totals)} categories. Total PHP {sum(totals.values()):.2f}. Reports: {args.output_dir}')
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
