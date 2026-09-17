"""Read-only discovery and original-PDF verification for the supplied FDE edition."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

BASE = Path(__file__).resolve().parents[1]


def parse_pages(spec, count):
    result = set()
    for part in spec.split(','):
        bounds = part.strip().split('-')
        if len(bounds) == 1:
            start = end = int(bounds[0])
        elif len(bounds) == 2:
            start, end = map(int, bounds)
        else:
            raise ValueError('Use PDF page numbers such as 61-62 or 72,101.')
        if not 1 <= start <= end <= count:
            raise ValueError(f'PDF pages must be between 1 and {count}.')
        result.update(range(start, end + 1))
    if len(result) > 12:
        raise ValueError('Read at most 12 PDF pages per call; narrow the evidence first.')
    return sorted(result)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--search', help='Literal keyword in your local PDF; discovery only')
    mode.add_argument('--pages', help='Original PDF page numbers, e.g. 61-62 or 72,101')
    mode.add_argument('--info', action='store_true', help='Edition identity and integrity')
    ap.add_argument('--pdf', type=Path, help='Path to your legally obtained source PDF; never uploaded by this script')
    ap.add_argument('--case', type=int, choices=range(1,25), help='Restrict keyword search')
    args = ap.parse_args()
    if args.case and not args.search:
        ap.error('--case is only used with --search')
    try:
        payload = json.loads((BASE / 'references/source-manifest.json').read_text(encoding='utf-8'))
        pdf = args.pdf or BASE / 'references/source.pdf'
        if not pdf.is_file():
            raise ValueError('Optional source PDF not found. Supply your own authorized copy with --pdf PATH or references/source.pdf. Core consultation works without it; do not claim original-source verification.')
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        if digest != payload['source']['sha256']:
            raise ValueError('PDF edition hash mismatch; rebuild and review references before citing.')
        if args.info:
            print(json.dumps(payload['source'], ensure_ascii=False, indent=2))
            print('PDF SHA-256 verified. This verifies file identity, not business claims.')
            return 0
        if args.search:
            if not args.search.strip():
                raise ValueError('Search keyword must not be empty.')
            from pypdf import PdfReader
            reader = PdfReader(pdf)
            if len(reader.pages) != payload['source']['page_count']:
                raise ValueError('PDF page count mismatch.')
            candidates = [{'pdf_page': n + 1, 'printed_page': str(n) if 1 <= n <= 243 else '无正文页码', 'text': page.extract_text() or ''} for n, page in enumerate(reader.pages)]
            if args.case:
                case = next(c for c in payload['cases'] if c['id'] == args.case)
                candidates = [p for p in candidates if case['pdf_start'] <= p['pdf_page'] <= case['pdf_end']]
            hits = 0
            print('DISCOVERY ONLY: snippets extracted from your local PDF. Use --pages to read full original pages before formal citation.')
            keyword = ''.join(args.search.split()).casefold()
            for page in candidates:
                # PDF line wraps can split Chinese terms (for example 预\n计).
                # Preserve original offsets so snippets remain faithful to the page.
                characters, offsets = [], []
                for offset, char in enumerate(page['text']):
                    if not char.isspace():
                        folded = char.casefold()
                        characters.extend(folded)
                        offsets.extend([offset] * len(folded))
                match = ''.join(characters).find(keyword)
                pos = offsets[match] if match >= 0 else -1
                if pos >= 0:
                    hits += 1
                    if hits <= 20:
                        snippet = page['text'][max(0,pos-60):pos+180].replace('\n',' ')
                        print(f"PDF {page['pdf_page']} / 书内 {page['printed_page']}: {snippet}")
            print(f'Matches: {hits}; shown: {min(hits,20)}. Narrow by --case if needed.')
            return 0
        numbers = parse_pages(args.pages, payload['source']['page_count'])
        try:
            from pypdf import PdfReader
        except ImportError:
            print('Original verification needs pypdf. Use an available PDF reader on references/source.pdf; do not treat cached search as a verified citation.', file=sys.stderr)
            return 3
        reader = PdfReader(pdf)
        if len(reader.pages) != payload['source']['page_count']:
            raise ValueError('PDF page count mismatch.')
        print('ORIGINAL PDF READ; file identity verified; outcomes remain interview self-reports.')
        for n in numbers:
            printed = str(n-1) if 2 <= n <= 244 else '无正文页码'
            print(f'\n=== PDF第{n}页 / 书内第{printed}页 ===')
            text = reader.pages[n-1].extract_text() or ''
            print(text if text.strip() else '[No extractable text. Inspect this PDF page visually.]')
        return 0
    except ImportError:
        print('PDF search needs pypdf. Use an available PDF reader instead; nothing is installed automatically.', file=sys.stderr)
        return 3
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        print(f'Source read failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
