"""Offline city package entrypoint. Never authenticates, uploads, or writes a DB."""
import argparse
import json
from pathlib import Path
from read_delivery_v7 import read
from delivery_tools import audit, create_web_copy, export_attributions
from v7_validation import validate_files


def main():
    parser = argparse.ArgumentParser(description='Corteqs v7 yerel dosya kontrolü')
    parser.add_argument('workbook', type=Path)
    parser.add_argument('assets_root', type=Path)
    parser.add_argument('--new-content', action='store_true')
    parser.add_argument('--web-copies', action='store_true')
    args = parser.parse_args()
    data, provenance, archives = read(args.workbook)
    root = args.assets_root.resolve()
    if args.web_copies:
        provenance = [create_web_copy(root, row) for row in provenance]
    media = audit(root, data['photos'], provenance, require_new_chain=args.new_content)
    structure = validate_files(data, assets_root=root)
    missing = {key: {'actual': structure['counts'][key], 'minimum': count} for key, count in structure['minimum'].items() if structure['counts'][key] < count}
    result = {
        'version': '7.0',
        'media': media,
        'structure': structure,
        'minimum_gaps': missing,
        'long_values_restored': len(archives),
        'technically_complete': media['structural_passed'] and structure['valid'] and not missing,
        'whole_package_human_approval': 'Not granted by this tool',
        'database_written': False,
        'published': False,
    }
    output = root / 'Teslimler'; output.mkdir(exist_ok=True)
    (output / 'photo-provenance-v7.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2))
    (output / 'normalized-tables-v7.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
    (output / 'paket-kontrol-v7.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    export_attributions(root, data['photos'], provenance)
    print(json.dumps({'technically_complete': result['technically_complete'], 'photos': len(data['photos']), 'media_errors': len(media['errors']), 'structure_errors': len(structure['errors']), 'minimum_gaps': missing}, ensure_ascii=False))
    if not result['technically_complete']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
