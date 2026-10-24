"""File-only v7 adapter: physical inventory does not grant editorial approval."""
from core.content_delivery.delivery_validation import validate as legacy_validate, LABELS
from core.content_delivery.validation_media import PhotoIdentity


def physical_photo_counts(photos):
    groups = PhotoIdentity()
    for index, photo in enumerate(photos):
        groups.add(index, photo)
    roles = {'Mekân': set(), 'Kapak': set()}
    for index, photo in enumerate(photos):
        if photo.get('role') in roles:
            roles[photo['role']].add(groups.root(index))
    return {'photos': len(roles['Mekân']), 'hero_photos': len(roles['Kapak'])}


def validate_files(data, assets_root):
    result = legacy_validate(data, mode='draft', assets_root=assets_root)
    result['legacy_row_credit_counts'] = {key: result['counts'][key] for key in ('photos', 'hero_photos')}
    result['counts'].update(physical_photo_counts(data.get('photos', [])))
    prefixes = tuple(LABELS[key] + ':' for key in ('photos', 'hero_photos'))
    result['warnings'] = [w for w in result['warnings'] if not w.startswith(prefixes)]
    for key in ('photos', 'hero_photos'):
        actual, minimum = result['counts'][key], result['minimum'][key]
        if actual < minimum:
            result['warnings'].append(f'{LABELS[key]}: {actual} / asgari {minimum}; hedef {result["target"][key]}.')
    result['counting_note'] = 'Fiziksel SHA veya aynı kanonik kaynak tek kare sayılır. Rol ayrıdır. Satır onay/kredi bayrağı miktarı sıfırlamaz; insan onayı ayrıca bütün pakete verilir.'
    return result
