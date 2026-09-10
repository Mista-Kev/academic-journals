"""Fetch verified research inputs or stage a mirrored SharePoint handover. Stdlib only."""
import sys

if sys.version_info < (3, 12):
    raise SystemExit("Python 3.12 or newer is required. Run with a supported interpreter.")

from pathlib import Path, PurePosixPath
import argparse
import hashlib
import io
import json
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
BLOCK = 1024 * 1024


class DataError(RuntimeError):
    pass


def safe_path(root, relative):
    parts = PurePosixPath(relative)
    if (not relative or parts.is_absolute() or '\\' in relative or
            any(p in ('..', '.', '') or ':' in p for p in relative.split('/'))):
        raise DataError('Invalid manifest path')
    root = Path(root).expanduser().resolve()
    path = root.joinpath(*parts.parts)
    if not path.resolve().is_relative_to(root):
        raise DataError('Path leaves the configured data folder')
    for parent in [path, *path.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise DataError('Symlinks are not supported for managed data files')
    return path


def load_manifest(root=ROOT):
    manifest = json.loads((Path(root) / 'data-manifest.json').read_text(encoding='utf8'))
    if manifest.get('format') != 1:
        raise DataError('Unsupported manifest format')
    seen = set()
    for item in manifest['files']:
        name = item['path']
        safe_path(root, name)
        if 'shared_path' in item:
            safe_path(root, item['shared_path'])
        if name in seen or not re.fullmatch(r'[0-9a-f]{64}', item['sha256']):
            raise DataError('Invalid or duplicate manifest entry')
        if type(item['bytes']) is not int or item['bytes'] < 0:
            raise DataError('Invalid file size')
        seen.add(name)
    return manifest


def selected(manifest, group):
    if group == 'all':
        return manifest['files']
    rows = [x for x in manifest['files'] if group in x['groups']]
    if not rows:
        raise DataError('Unknown or empty data group: ' + group)
    return rows


def matches(path, item):
    if not path.is_file() or path.stat().st_size != item['bytes']:
        return False
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest() == item['sha256']


class HttpsRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        url = urllib.parse.urlparse(newurl)
        if url.scheme != 'https' or url.username or url.password:
            raise DataError('Refusing a non-HTTPS download redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password:
        raise DataError('A direct HTTPS file URL is required')
    # No browser cookies or authorization headers are exported to this process.
    response = urllib.request.build_opener(HttpsRedirects()).open(url, timeout=60)
    if response.headers.get_content_type() in ('text/html', 'application/xhtml+xml'):
        response.close()
        raise DataError('Received a login/web page. Use a synced SharePoint folder or a permitted direct file link.')
    return response


def install(stream, target, item):
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.' + target.name + '-', delete=False) as out:
            tmp = Path(out.name)
            digest = hashlib.sha256()
            size = 0
            while chunk := stream.read(BLOCK):
                size += len(chunk)
                if size > item['bytes']:
                    raise DataError('Download larger than expected: ' + item['path'])
                digest.update(chunk)
                out.write(chunk)
        if size != item['bytes'] or digest.hexdigest() != item['sha256']:
            raise DataError('Size/checksum mismatch: ' + item['path'])
        # Never silently replace somebody's generated or modified file.
        if target.exists():
            if matches(target, item):
                return
            raise DataError('Destination already contains a different file: ' + item['path'])
        # Atomic create-if-absent, unlike replace(). Temporary file is on the same volume.
        try:
            os.link(tmp, target)
        except FileExistsError:
            if not matches(target, item):
                raise DataError('Destination changed while downloading: ' + item['path'])
        except OSError as exc:
            raise DataError('Could not publish verified file: ' + item['path'] +
                            '. Atomic publication requires hard-link support and write permission. '
                            'Use a writable local APFS/NTFS folder for the cache or release, '
                            'then upload through SharePoint. OS error code: ' + str(exc.errno)) from None
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


def configuration(root):
    path = Path(root) / '.shared-data.local.json'
    config = json.loads(path.read_text(encoding='utf8')) if path.exists() else {}
    if os.environ.get('ACADEMIC_JOURNALS_SHARED_ROOT'):
        config['shared_root'] = os.environ['ACADEMIC_JOURNALS_SHARED_ROOT']
    return config


def shared_file(source, item):
    current = safe_path(source, item['path'])
    if current.exists():
        return current
    return safe_path(source, item.get('shared_path', item['path']))


def configure(shared_root, group='all', root=ROOT):
    """Verify the selected shared inputs before saving this machine's source."""
    root = Path(root).resolve()
    source = Path(shared_root).expanduser().resolve()
    if source == root:
        raise DataError('Choose the shared/downloaded folder, not the repository itself')
    override = os.environ.get('ACADEMIC_JOURNALS_SHARED_ROOT')
    if override and Path(override).expanduser().resolve() != source:
        raise DataError('ACADEMIC_JOURNALS_SHARED_ROOT points elsewhere. Unset it or select that same folder before configuring.')
    for item in selected(load_manifest(root), group):
        if not matches(shared_file(source, item), item):
            raise DataError('Shared file missing or different: ' + item['path'] + '. Select the shared release root, in the existing or A/B/C layout.')
    path = root / '.shared-data.local.json'
    config = json.loads(path.read_text(encoding='utf8')) if path.exists() else {}
    config['shared_root'] = str(source)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf8', dir=root,
                                         prefix='.shared-data-config-', delete=False) as out:
            tmp = Path(out.name)
            json.dump(config, out, ensure_ascii=False, indent=2)
            out.write('\n')
        os.replace(tmp, path)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    print('Shared source verified and saved in .shared-data.local.json for group', group)


def ensure_data(group, root=ROOT, shared_root=None, verify_only=False):
    root = Path(root).resolve()
    manifest = load_manifest(root)
    config = configuration(root)
    source = shared_root or config.get('shared_root')
    rows = selected(manifest, group)
    for item in rows:
        target = safe_path(root, item['path'])
        if target.exists():
            if not matches(target, item):
                raise DataError('Existing file differs from the manifest: ' + item['path'] + '. Preserve it and reconcile the version before retrying.')
            print('verified', item['path'])
            continue
        if verify_only:
            raise DataError('Missing local file: ' + item['path'])
        try:
            if source:
                origin = shared_file(source, item)
                with origin.open('rb') as stream:
                    install(stream, target, item)
            else:
                urls = config.get('urls', {})
                # An explicitly configured new key wins, even if invalid.
                url = urls.get(item['path']) if item['path'] in urls else urls.get(item.get('shared_path', item['path']))
                if not url:
                    raise DataError('Missing ' + item['path'] + '. Configure shared_root or its direct link in .shared-data.local.json; see D_results/methods/shared-data.md.')
                with download(url) as stream:
                    install(stream, target, item)
        except DataError:
            raise
        except (OSError, urllib.error.URLError) as exc:
            # Do not include signed links or credentials from exception messages.
            raise DataError('Could not retrieve ' + item['path'] + '; check access and source configuration (' + type(exc).__name__ + ').') from None
        print('fetched and verified', item['path'])
    return [safe_path(root, item['path']) for item in rows]


def stage(target_root, group='all', root=ROOT):
    """Copy only declared, verified artifacts. Never walk arbitrary user folders."""
    root = Path(root).resolve()
    target_root = Path(target_root).expanduser().resolve()
    if target_root == root or target_root.is_relative_to(root) or root.is_relative_to(target_root):
        raise DataError('Choose a staging folder outside the repository, not its parent')
    manifest = load_manifest(root)
    rows = selected(manifest, group)
    # Preflight every source before writing anything to the destination.
    for item in rows:
        if not matches(safe_path(root, item['path']), item):
            raise DataError('Missing/changed source: ' + item['path'])
        target = safe_path(target_root, item['path'])
        if target.exists() and not matches(target, item):
            raise DataError('Destination contains a different version: ' + item['path'])
    for item in rows:
        target = safe_path(target_root, item['path'])
        if not target.exists():
            with safe_path(root, item['path']).open('rb') as stream:
                install(stream, target, item)
        print('staged', item['path'])
    # A receipt identifies exactly what this invocation delivered, even for one group.
    receipt = {'release': manifest['release'], 'group': group, 'files': rows}
    raw = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    name = 'delivery-' + hashlib.sha256(raw).hexdigest()[:16] + '.json'
    install(io.BytesIO(raw), safe_path(target_root, name), {'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    print('Delivery receipt:', name)


def release_metadata(manifest):
    """Recipient instructions and inventory derived from the reviewed manifest."""
    start = f'''APPLIED AI GROUP · GEMEINSAME DATEN
Release: {manifest['release']} | Layout: {manifest.get('layout', 'unspecified')}

Dieser Ordner enthält Daten, nicht den ausführbaren Projektcode.
Verwende dazu den Repository-Stand mit A_data_and_rules,
B_opportunities_and_analysis, C_topic_match und D_results.
Die data-manifest.json im Repository und hier müssen übereinstimmen.

1. Diesen gesamten Release-Ordner herunterladen und entpacken oder über
   OneDrive lokal verfügbar machen. Die Unterordner beibehalten.
2. Im Repository Python 3.12+ und requirements.txt installieren.
3. Im Repository-Terminal den tatsächlichen Pfad dieses Ordners einsetzen:

   python3 project_data.py verify-release --target "/Pfad/zum/Release-Ordner"
   python3 project_data.py configure --shared-root "/Pfad/zum/Release-Ordner"
   python3 demo.py q1-q2
   python3 demo.py q3

Der Loader kopiert benötigte Dateien in einen lokalen Repository-Cache und
prüft Größe und SHA-256. Vorhandene passende Dateien werden wiederverwendet.
Das ist kein direkter Login bei Microsoft und keine automatische Veröffentlichung
neuer Ergebnisse. Ein Browserdownload bleibt eine feste Kopie. OneDrive muss
separat eingerichtet sein; jeder benötigt eigenen Zugriff auf den Datenordner.
Für Daten plus vollständigen Cache werden etwa {2 * sum(x['bytes'] for x in manifest['files']) / 1e9:.2f} GB benötigt.

A: Paperdaten, Publikationspfade und unabhängige Prolog-Gegenprüfung.
B: Jährliche Gelegenheitentabellen und externe Q3-Referenzergebnisse.
C: Historisches T für Q3 und beschreibende Q1-Intra-Ergebnisse.
D: Ergebnisinterpretation bleibt im Repository unter D_results.
FILES.md nennt für jede Datei Zweck und Erzeuger, jeweils relativ zum Repository.
Q1-Intra ist keine historische T-Adjustierung. Die Min-3-Datei ist nur der
historische Vergleich für Q3-Schritt 8. Der GPU-/DuckDB-Neuaufbau von C ist
nicht in diesem Datenpaket enthalten. Siehe die jeweiligen Repository-READMEs.

Ergebnisse lokal erzeugen. Diese Referenzdateien nicht durch Experimente ersetzen.
Bei anderer Version stoppt die Prüfung; nicht einfach die Prüfsumme ändern.
'''
    lines = ['# Dateiverzeichnis', '',
             f"Release: `{manifest['release']}`. Pfade entsprechen dem Repository.", '',
             '| Datei | Bytes | Zweck (Manifest, Englisch) | Erzeuger im Repository oder Herkunft |',
             '|---|---:|---|---|']
    for item in manifest['files']:
        values = [item['path'], str(item['bytes']), item.get('purpose', ''),
                  item.get('produced_by', '')]
        lines.append('| ' + ' | '.join(v.replace('|', '\\|').replace('\n', ' ') for v in values) + ' |')
    receipt = {'release': manifest['release'], 'group': 'all', 'files': manifest['files']}
    receipt_raw = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    return {
        'START_HERE.txt': start.encode(),
        'FILES.md': ('\n'.join(lines) + '\n').encode(),
        'data-manifest.json': (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode(),
        'delivery-' + hashlib.sha256(receipt_raw).hexdigest()[:16] + '.json': receipt_raw,
    }


def release_folder(target_root, root=ROOT, verify_only=False):
    """Prepare or check a complete, allowlisted folder without calling a cloud API."""
    root = Path(root).resolve()
    target_root = Path(target_root).expanduser().resolve()
    if target_root == root or target_root.is_relative_to(root) or root.is_relative_to(target_root):
        raise DataError('Choose a release folder outside the repository, not its parent')
    manifest = load_manifest(root)
    metadata = release_metadata(manifest)
    items = manifest['files'] + [
        {'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        for name, raw in metadata.items()]
    allowed = {item['path'] for item in items}
    allowed_dirs = {str(p) for name in allowed for p in PurePosixPath(name).parents if str(p) != '.'}
    # A dedicated folder avoids accidentally uploading private files left beside data.
    for path in target_root.rglob('*'):
        name = path.relative_to(target_root).as_posix()
        # Browsing a downloaded folder can create these OS housekeeping files.
        # Ignore regular files only: a same-named directory or symlink is not metadata.
        if (path.name in {'.DS_Store', 'desktop.ini', 'Thumbs.db'} and
                not path.is_symlink() and path.is_file()):
            continue
        if (path.is_file() and not path.is_symlink() and path.parent == target_root
                and re.fullmatch(r'delivery-[0-9a-f]{16}\.json', name) and name not in allowed):
            raise DataError('Release contains a receipt from another manifest or staging group. '
                            'Preserve this folder and prepare the complete release in a new empty folder.')
        if path.is_symlink() or (name not in allowed and name not in allowed_dirs):
            raise DataError('Unexpected release content: ' + name + '. Use a dedicated release folder.')
    for item in items:
        target = safe_path(target_root, item['path'])
        if (verify_only or target.exists()) and not matches(target, item):
            raise DataError('Release file missing or different: ' + item['path'])
    if not verify_only:
        stage(target_root, 'all', root)
        for item in items[len(manifest['files']):]:
            install(io.BytesIO(metadata[item['path']]), safe_path(target_root, item['path']), item)
        release_folder(target_root, root, verify_only=True)
    else:
        print('Release verified:', manifest['release'], '|', len(manifest['files']),
              'data files and', len(metadata), 'metadata files')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['list', 'configure', 'fetch', 'verify', 'stage',
                                         'prepare-release', 'verify-release'])
    parser.add_argument('--group', default='all')
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository/cache root containing data-manifest.json')
    parser.add_argument('--shared-root', type=Path, help='Synced or downloaded SharePoint release root')
    parser.add_argument('--target', type=Path, help='Staging or release folder; may be a synced folder')
    args = parser.parse_args()
    try:
        if args.action == 'list':
            rows = selected(load_manifest(args.root), args.group)
            for item in rows:
                print(f"{item['bytes']/1e6:9.1f} MB  {item['path']}  [{item['owner']}]")
            print(f"Total: {sum(x['bytes'] for x in rows)/1e9:.2f} GB")
        elif args.action == 'configure':
            if args.shared_root is None:
                parser.error('configure requires --shared-root')
            configure(args.shared_root, args.group, args.root)
        elif args.action in ('prepare-release', 'verify-release'):
            if args.target is None or args.group != 'all':
                parser.error('release commands require --target and the complete group all')
            release_folder(args.target, args.root, args.action == 'verify-release')
        elif args.action == 'stage':
            if args.target is None:
                parser.error('stage requires --target')
            stage(args.target, args.group, args.root)
        else:
            ensure_data(args.group, args.root, args.shared_root, args.action == 'verify')
    except (DataError, OSError, ValueError, KeyError) as exc:
        # DataError messages are intentionally safe; other errors may contain a local config path.
        parser.exit(1, str(exc) + '\n' if isinstance(exc, DataError) else 'Invalid or unreadable data manifest/configuration.\n')


if __name__ == '__main__':
    main()
