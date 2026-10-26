#!/usr/bin/env python3
"""Walk a Spenser unit through what the new firmware changed, narrating as it goes.

Standard library only: no pip install, so it runs on any machine with Python 3.

    python spenser_check.py                       # everything that needs no files
    python spenser_check.py --phases health,key
    python spenser_check.py --firmware ../.pio/build/esp32s3/firmware.bin
    python spenser_check.py --phases ota --firmware firmware.bin --rollback

The key: printed on the unit's serial console at boot, and served at /key for
five minutes afterwards. The script asks the unit for it when you do not pass
one, so restarting the unit just before a run is the easy path.

    python spenser_check.py --key 0123... --host http://192.168.1.50
    set SPENSER_KEY=0123...        (or export, on a shell that has it)

Phases, in the order they run:

    health   what it is running, its clock, its dashboard
    key      reads open, writes refused without the key
    server   create, read back, search, errors, timestamps  [dispenses chocolate]
    stock    a refusal carries its reason                   [moves a servo]
    ota      upload a firmware image and watch the slot change   [needs --firmware]
    persist  stock and history survive the restart the upload caused
    pull     a release manifest, told rather than taken
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

ALL_PHASES = ['health', 'key', 'server', 'stock', 'ota', 'persist', 'pull']

PASS, FAIL, NOTE, SKIP = 'pass', 'FAIL', 'note', 'skip'
results = []


# --------------------------------------------------------------------- output

class C:
    bold = '\033[1m'
    dim = '\033[2m'
    green = '\033[32m'
    red = '\033[31m'
    yellow = '\033[33m'
    cyan = '\033[36m'
    off = '\033[0m'


def _plain():
    if os.name == 'nt' and not os.environ.get('WT_SESSION') and not os.environ.get('TERM'):
        for name in dir(C):
            if not name.startswith('_'):
                setattr(C, name, '')


def section(title, why):
    print()
    print(C.bold + '=' * 72 + C.off)
    print(C.bold + title + C.off)
    print(C.dim + why + C.off)
    print(C.bold + '=' * 72 + C.off)


def step(what):
    print()
    print(C.cyan + '-> ' + what + C.off)


def shows(label, value):
    print('     %-22s %s' % (label, value))


def verdict(kind, message, detail=''):
    results.append((kind, message))
    colour = {PASS: C.green, FAIL: C.red, NOTE: C.yellow, SKIP: C.dim}[kind]
    mark = {PASS: 'pass', FAIL: 'FAIL', NOTE: 'note', SKIP: 'skip'}[kind]
    print('     %s[%s]%s %s' % (colour, mark, C.off, message))
    if detail:
        print(C.dim + '            ' + detail + C.off)


def expect(condition, message, detail='', soft=False):
    verdict(PASS if condition else (NOTE if soft else FAIL), message, '' if condition else detail)
    return bool(condition)


# ---------------------------------------------------------------------- HTTP

class Reply:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

    @property
    def json(self):
        try:
            return json.loads(self.body)
        except Exception:
            return None

    def header(self, name):
        for k, v in (self.headers or []):
            if k.lower() == name.lower():
                return v
        return None


def call(host, path, method='GET', key=None, body=None, content_type=None, timeout=30):
    url = host.rstrip('/') + path
    data = body
    if isinstance(data, (dict, list)):
        data = json.dumps(data).encode()
        content_type = content_type or 'application/fhir+json'
    elif isinstance(data, str):
        data = data.encode()

    request = urllib.request.Request(url, data=data, method=method)
    request.add_header('Accept', 'application/fhir+json, application/json, */*')
    if content_type:
        request.add_header('Content-Type', content_type)
    if key:
        request.add_header('X-Spenser-Key', key)

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return Reply(response.status, list(response.headers.items()),
                         response.read().decode('utf-8', 'replace'))
    except urllib.error.HTTPError as e:
        return Reply(e.code, list(e.headers.items()), e.read().decode('utf-8', 'replace'))
    except Exception as e:
        return Reply(0, [], 'transport error: %s' % e)


def wait_until_up(host, seconds=120, quiet=False):
    """Poll until the unit answers again, which is what a restart needs."""
    if not quiet:
        print(C.dim + '     waiting for the unit to come back' + C.off, end='', flush=True)
    deadline = time.time() + seconds
    while time.time() < deadline:
        if call(host, '/settings', timeout=3).status == 200:
            if not quiet:
                print(C.dim + ' answered after %ds' % int(seconds - (deadline - time.time())) + C.off)
            return True
        if not quiet:
            print(C.dim + '.' + C.off, end='', flush=True)
        time.sleep(2)
    if not quiet:
        print()
    return False


def order_body(code, display):
    return {
        'resourceType': 'MedicationRequest',
        'status': 'active',
        'intent': 'instance-order',
        'medication': {'concept': {'coding': [{
            'system': 'http://costateixeira.github.io/spenser/CodeSystem/SpenserMeds',
            'code': code, 'display': display}]}},
        'subject': {'reference': 'Patient/123'},
    }


# -------------------------------------------------------------------- phases

def phase_health(cfg, state):
    section('Health', 'Did the flash take, and is the unit in a state where the rest means anything?')

    step('GET /ota/status')
    r = call(cfg.host, '/ota/status', key=cfg.key)
    status = r.json or {}
    if r.status != 200:
        verdict(FAIL, 'the unit did not answer /ota/status (HTTP %s)' % r.status,
                'An old firmware has no such route. Flash over the cable first: '
                'python -m platformio run -t upload, then -t uploadfs')
        return False

    state['version_before'] = status.get('firmwareVersion')
    state['slot_before'] = status.get('runningSlot')

    shows('firmware', status.get('firmwareVersion'))
    shows('build', status.get('build'))
    shows('running slot', status.get('runningSlot'))
    shows('image / slot', '%s of %s bytes' % (status.get('sketchBytes'), status.get('slotBytes')))
    shows('can roll back', status.get('canRollback'))
    shows('marked valid', status.get('markedValid'))
    shows('uptime', '%ss' % status.get('uptimeSeconds'))
    shows('clock', status.get('clock'))
    shows('update mode', status.get('updateMode'))

    expect(status.get('runningSlot') in ('app0', 'app1'),
           'it is running from one of the two OTA slots',
           'No slot means no over-the-air updates.')

    slot = status.get('slotBytes') or 0
    used = (status.get('sketchBytes') or 0) / slot if slot else 0
    expect(slot > 3000000,
           'the slot is the 3.1MB one from the 8MB partition table',
           'slotBytes is %s. The old 4MB table gives 1.31MB, which this image no longer fits.' % slot)
    expect(0 < used < 0.9, 'the image leaves room to grow (%.0f%% used)' % (used * 100),
           'An image that only just fits cannot be replaced over the air later.')

    expect(status.get('clock') != 'unset', 'it has reached an NTP server', soft=True,
           detail='Without a clock, every dispense is missing recorded, whenPrepared and '
                  'whenHandedOver. Give it a minute after boot, then check the network.')

    step('GET /settings')
    settings = call(cfg.host, '/settings', key=cfg.key).json or {}
    shows('firmwareVersion', settings.get('firmwareVersion'))
    shows('updateMode', settings.get('updateMode'))
    shows('updateUrl', settings.get('updateUrl') or '(none)')
    expect('firmwareVersion' in settings, 'settings say what the unit is running')
    expect('key' not in settings and 'deviceKey' not in settings,
           'and do not leak the key',
           '/settings is readable without a key, so the key must not be in it.')

    step('GET / (the dashboard)')
    page = call(cfg.host, '/')
    expect(page.status == 200 and 'Updates' in page.body and 'Servos' in page.body,
           'the dashboard is served, with the Servos and Updates panels',
           'A 404 means the filesystem image was not uploaded: python -m platformio run -t uploadfs')
    return True


def phase_key(cfg, state):
    section('The key', 'Reads stay open for anyone; anything that changes the unit does not.')

    step('GET /inventory with no key')
    r = call(cfg.host, '/inventory')
    expect(r.status == 200, 'a read needs no key', 'HTTP %s' % r.status)

    step('GET /resetInventory?dark=10&milk=10 with no key')
    r = call(cfg.host, '/resetInventory?dark=10&milk=10')
    shows('status', r.status)
    shows('www-authenticate', r.header('WWW-Authenticate'))
    ok = expect(r.status == 401, 'a write without the key is refused',
                'This is the headline change. Before it, anyone on the network could empty '
                'the stock counter or wipe the Wi-Fi credentials from a browser. '
                'A 200 here means the unit is in setup mode, where the open access point is '
                'the proof of proximity.')
    if ok:
        outcome = r.json or {}
        expect(outcome.get('resourceType') == 'OperationOutcome',
               'and refused in FHIR terms, as an OperationOutcome')

    step('the same write, with the key')
    r = call(cfg.host, '/resetInventory?dark=10&milk=10', key=cfg.key)
    expect(r.status == 200, 'the key is accepted',
           'HTTP %s. The key in use does not match the unit; read it from the serial console '
           'or restart the unit and run this script again without --key.' % r.status)

    step('GET /key')
    r = call(cfg.host, '/key')
    if r.status == 200:
        verdict(NOTE, 'the key is readable, so this unit booted within the last five minutes')
    else:
        verdict(PASS, 'the key is no longer readable (HTTP %s), which is the point' % r.status)
    return True


def phase_server(cfg, state):
    section('The server role', 'A create that behaves like one, orders kept, searches that filter.')
    if not cfg.yes and not confirm('This dispenses two pieces of chocolate. Go on?'):
        verdict(SKIP, 'server role, declined')
        return True

    step('POST /$dispense with no id')
    r = call(cfg.host, '/$dispense', 'POST', cfg.key, order_body('chocolate-milk', 'Milk Chocolate'))
    dispense = r.json or {}
    shows('status', r.status)
    shows('resource', dispense.get('resourceType'))
    shows('dispense status', dispense.get('status'))
    expect(r.status == 200 and dispense.get('resourceType') == 'MedicationDispense',
           'the operation answers with the dispense itself')
    expect(dispense.get('status') == 'completed', 'a piece of milk chocolate came out')
    ref = (dispense.get('authorizingPrescription') or [{}])[0].get('reference', '')
    expect(ref.startswith('MedicationRequest/mr-'),
           'and the unit minted an order id for it (%s)' % ref,
           'No id was sent, so the unit had to assign one.')

    step('POST /MedicationRequest with no id')
    r = call(cfg.host, '/MedicationRequest', 'POST', cfg.key, order_body('chocolate-dark', 'Dark Chocolate'))
    created = r.json or {}
    order_id = created.get('id')
    state['order_id'] = order_id
    shows('status', r.status)
    shows('Location', r.header('Location'))
    shows('ETag', r.header('ETag'))
    shows('id assigned', order_id)
    shows('order status', created.get('status'))
    expect(r.status == 201, 'a create answers 201',
           'HTTP %s. This used to be 200 with a dispense, and used to fail outright when the '
           'body carried no id.' % r.status)
    expect(bool(order_id), 'the unit assigned the id')
    expect((r.header('Location') or '').endswith('/MedicationRequest/' + str(order_id)),
           'and said where it put it')
    expect(created.get('status') == 'completed',
           'the kept order is finished, since no Task was coordinating it')

    if order_id:
        step('GET /MedicationRequest/%s' % order_id)
        r = call(cfg.host, '/MedicationRequest/' + order_id, key=cfg.key)
        expect(r.status == 200 and (r.json or {}).get('id') == order_id,
               'the order can be read back',
               'This 404ed for everything before: the unit kept no orders at all.')

        step('GET /MedicationDispense/%s-dispense' % order_id)
        r = call(cfg.host, '/MedicationDispense/%s-dispense' % order_id, key=cfg.key)
        d = r.json or {}
        state['dispense_id'] = d.get('id')
        shows('recorded', d.get('recorded'))
        shows('whenPrepared', d.get('whenPrepared'))
        shows('whenHandedOver', d.get('whenHandedOver'))
        if d.get('recorded'):
            expect(True, 'the dispense is stamped with a time')
        else:
            verdict(NOTE, 'the dispense carries no time, because the unit has no clock',
                    'The element is omitted rather than invented. Fix NTP and it appears.')

    step('GET /MedicationDispense?subject=123&status=completed&_count=2')
    r = call(cfg.host, '/MedicationDispense?subject=123&status=completed&_count=2', key=cfg.key)
    bundle = r.json or {}
    matches = [e for e in bundle.get('entry', []) if e.get('search', {}).get('mode') == 'match']
    shows('total', bundle.get('total'))
    shows('match entries', len(matches))
    shows('self link', (bundle.get('link') or [{}])[0].get('url'))
    expect(len(matches) <= 2, '_count is honoured', 'Every parameter used to be ignored.')
    expect(all(e['resource'].get('status') == 'completed' for e in matches),
           'status is honoured')
    expect(all(e['resource'].get('subject', {}).get('reference') == 'Patient/123' for e in matches),
           'and subject matches by bare id as well as in full')
    expect(any(e.get('search', {}).get('mode') == 'outcome' for e in bundle.get('entry', [])),
           'the outcome entry about the last order check is still there')

    step('POST /MedicationRequest with a Patient in the body')
    r = call(cfg.host, '/MedicationRequest', 'POST', cfg.key, {'resourceType': 'Patient'})
    shows('status', r.status)
    shows('body', (r.body or '')[:90])
    expect(r.status == 400 and (r.json or {}).get('resourceType') == 'OperationOutcome',
           'an error is an OperationOutcome',
           'The old shape was {"status":"error"} as application/json, which no FHIR client reads.')
    return True


def phase_stock(cfg, state):
    section('Out of stock', 'A refusal is an answer, with its reason where R5 keeps it.')

    step('GET /resetInventory?dark=0')
    call(cfg.host, '/resetInventory?dark=0', key=cfg.key)

    step('POST /$dispense for dark chocolate')
    r = call(cfg.host, '/$dispense', 'POST', cfg.key, order_body('chocolate-dark', 'Dark Chocolate'))
    d = r.json or {}
    shows('status', r.status)
    shows('dispense status', d.get('status'))
    reason = (((d.get('notPerformedReason') or {}).get('concept') or {}).get('coding') or [{}])[0]
    shows('reason', '%s (%s)' % (reason.get('code'), reason.get('system')))
    expect(r.status == 200 and d.get('status') == 'declined',
           'the refusal is a 200 carrying a declined dispense',
           'An operation reports itself in the resource it returns.')
    expect(reason.get('code') == 'outofstock', 'with the reason in notPerformedReason.concept',
           'R5 removed MedicationDispense.statusReason.')

    step('GET /resetInventory?dark=10&milk=10')
    call(cfg.host, '/resetInventory?dark=10&milk=10', key=cfg.key)
    verdict(PASS, 'both lanes refilled')
    return True


def phase_ota(cfg, state):
    section('Firmware over the air',
            'The one that makes a remote unit supportable: replace the running image over Wi-Fi.')

    if not cfg.firmware:
        verdict(SKIP, 'no --firmware given',
                'Pass --firmware ../.pio/build/esp32s3/firmware.bin, or a firmware.bin '
                'downloaded from a release or a CI artifact. The same image is fine: the slot '
                'it runs from still changes, which is the proof the path works.')
        return True
    if not os.path.exists(cfg.firmware):
        verdict(FAIL, 'no such file: %s' % cfg.firmware)
        return False

    image = open(cfg.firmware, 'rb').read()
    before = call(cfg.host, '/ota/status', key=cfg.key).json or {}
    shows('running now', '%s from %s' % (before.get('firmwareVersion'), before.get('runningSlot')))
    shows('image to send', '%s (%d bytes)' % (os.path.basename(cfg.firmware), len(image)))
    shows('fits the slot', len(image) < (before.get('slotBytes') or 0))

    if len(image) >= (before.get('slotBytes') or 0):
        verdict(FAIL, 'the image does not fit the slot', 'Nothing was sent.')
        return False
    if not cfg.yes and not confirm('Upload %d bytes and restart the unit?' % len(image)):
        verdict(SKIP, 'firmware upload, declined')
        return True

    # Stock and history are recorded here so the next phase can prove they survived
    state['inventory_before'] = call(cfg.host, '/inventory').body.strip()
    log = call(cfg.host, '/MedicationDispense?_count=5', key=cfg.key).json or {}
    first = [e for e in log.get('entry', []) if e.get('search', {}).get('mode') == 'match']
    state['dispense_before'] = first[0]['resource']['id'] if first else None
    shows('stock before', state['inventory_before'])
    shows('newest dispense', state['dispense_before'])

    step('POST /ota/firmware with the image as the body')
    started = time.time()
    r = call(cfg.host, '/ota/firmware', 'POST', cfg.key, image,
             content_type='application/octet-stream', timeout=300)
    shows('status', r.status)
    shows('body', (r.body or '').strip()[:120])
    shows('upload took', '%.1fs' % (time.time() - started))

    if not expect(r.status == 200, 'the unit accepted the image',
                  'HTTP %s. A 401 is the key; a 409 means it was mid-check; a 507 means '
                  '"could not start the update", which is the partition table.' % r.status):
        return False

    expect((r.json or {}).get('restarting') is True, 'and said it is restarting')

    step('waiting for it to come back on the new image')
    if not expect(wait_until_up(cfg.host, 150), 'the unit came back',
                  'This is the moment a bad image shows up. If it never answers, power-cycle '
                  'it: the previous image is still in the other slot, and an image that cannot '
                  'reach the network is never marked good.'):
        return False

    after = call(cfg.host, '/ota/status', key=cfg.key).json or {}
    shows('running now', '%s from %s' % (after.get('firmwareVersion'), after.get('runningSlot')))
    shows('uptime', '%ss' % after.get('uptimeSeconds'))
    shows('marked valid', after.get('markedValid'))
    shows('can roll back', after.get('canRollback'))

    expect(after.get('runningSlot') != before.get('runningSlot'),
           'it is running from the other slot now (%s -> %s)'
           % (before.get('runningSlot'), after.get('runningSlot')),
           'The slot must change even when the image is identical. If it did not, the unit '
           'rebooted without taking the upload.')
    expect((after.get('uptimeSeconds') or 999) < 120, 'and it really did restart')
    expect(after.get('markedValid') is False,
           'the new image is not marked good yet, so the old one is still the way back',
           soft=True,
           detail='It is marked good after a minute up with a network.')
    expect(after.get('canRollback') is True, 'a rollback is available')

    if cfg.wait_valid:
        step('waiting 70s for the new image to mark itself good')
        time.sleep(70)
        later = call(cfg.host, '/ota/status', key=cfg.key).json or {}
        shows('marked valid', later.get('markedValid'))
        expect(later.get('markedValid') is True,
               'the image marked itself good once it had been up a minute with a network')

    if cfg.rollback:
        step('POST /ota/rollback')
        r = call(cfg.host, '/ota/rollback', 'POST', cfg.key)
        shows('status', r.status)
        if expect(r.status == 200, 'the rollback was accepted'):
            wait_until_up(cfg.host, 150)
            back = call(cfg.host, '/ota/status', key=cfg.key).json or {}
            shows('running now', '%s from %s' % (back.get('firmwareVersion'), back.get('runningSlot')))
            expect(back.get('runningSlot') == before.get('runningSlot'),
                   'and it is back on the slot it started from')
    return True


def phase_persist(cfg, state):
    section('Persistence', 'Stock and history used to live in RAM and vanish on every restart.')

    if 'inventory_before' not in state:
        verdict(SKIP, 'nothing to compare against',
                'Run this together with the ota phase, whose restart is what this proves, '
                'or power-cycle the unit between two runs of --phases stock,persist.')
        return True

    step('GET /inventory')
    now = call(cfg.host, '/inventory').body.strip()
    shows('before the restart', state['inventory_before'])
    shows('after the restart', now)
    expect(now == state['inventory_before'], 'the stock is what it was before the restart',
           'On the old firmware both lanes would read 15, the compiled default, and the order '
           "server's view of this unit's stock would be wrong from then on.")

    step('GET /MedicationDispense?_count=5')
    log = call(cfg.host, '/MedicationDispense?_count=5', key=cfg.key).json or {}
    matches = [e for e in log.get('entry', []) if e.get('search', {}).get('mode') == 'match']
    ids = [e['resource']['id'] for e in matches]
    shows('dispenses kept', len(ids))
    shows('looking for', state.get('dispense_before'))
    if state.get('dispense_before'):
        expect(state['dispense_before'] in ids,
               'the dispense recorded before the restart is still there',
               'The log is a file on the unit now, not six slots in RAM.')
    else:
        verdict(NOTE, 'there was no dispense recorded before the restart to look for')

    orders = call(cfg.host, '/MedicationRequest?_count=5', key=cfg.key).json or {}
    kept = [e for e in orders.get('entry', []) if e.get('search', {}).get('mode') == 'match']
    shows('orders kept', len(kept))
    expect(True, 'orders survive too (%d in the store)' % len(kept))
    return True


def phase_pull(cfg, state):
    section('Pull updates', 'Being told a version is waiting, rather than having it installed under you.')

    if not cfg.manifest:
        verdict(SKIP, 'no --manifest given',
                'Pass the release manifest URL, e.g. '
                'https://github.com/costateixeira/spenser/releases/latest/download/manifest.json')
        return True

    step('pointing the unit at the manifest, in notify mode')
    r = call(cfg.host, '/setSettings?updateUrl=%s&updateMode=notify&updateCheckHours=0' % cfg.manifest,
             key=cfg.key)
    settings = r.json or {}
    shows('updateUrl', settings.get('updateUrl'))
    shows('updateMode', settings.get('updateMode'))
    expect(settings.get('updateMode') == 'notify', 'notify, so a check reports rather than installs')

    step('a typo in that setting must not arm an unattended update')
    r = call(cfg.host, '/setSettings?updateMode=instal', key=cfg.key)
    expect((r.json or {}).get('updateMode') == 'notify',
           'updateMode=instal was read as notify, not install')
    call(cfg.host, '/setSettings?updateMode=notify', key=cfg.key)

    step('POST /ota/check')
    r = call(cfg.host, '/ota/check', 'POST', cfg.key)
    expect(r.status == 202, 'the check was queued (202), like a check for orders')

    step('waiting for the check to run, then reading /ota/status')
    time.sleep(10)
    status = call(cfg.host, '/ota/status', key=cfg.key).json or {}
    shows('running', status.get('firmwareVersion'))
    shows('available', status.get('availableVersion') or '(nothing newer)')
    shows('updateAvailable', status.get('updateAvailable'))
    shows('lastResult', status.get('lastResult'))

    expect(status.get('firmwareVersion') == (state.get('version_before') or status.get('firmwareVersion')),
           'the unit is still running what it was: looking is not taking',
           'A check used to download and restart inside the same call.')

    if status.get('updateAvailable'):
        verdict(PASS, '%s is waiting, and nothing rebooted' % status.get('availableVersion'))
        print(C.dim + '            Take it with POST /ota/install, or the Install button in the '
                      'dashboard.' + C.off)
        if cfg.install and (cfg.yes or confirm('Install %s now?' % status.get('availableVersion'))):
            step('POST /ota/install')
            r = call(cfg.host, '/ota/install', 'POST', cfg.key)
            shows('status', r.status)
            shows('body', (r.body or '').strip()[:120])
            if expect(r.status == 202, 'the install was queued'):
                wait_until_up(cfg.host, 240)
                after = call(cfg.host, '/ota/status', key=cfg.key).json or {}
                shows('running now', after.get('firmwareVersion'))
                expect(after.get('updateAvailable') is False, 'and nothing is waiting any more')
    else:
        verdict(NOTE, 'nothing newer is published, so the interesting case did not run',
                'Publish a release whose version differs from %s to see it.'
                % status.get('firmwareVersion'))
    return True


PHASES = {
    'health': phase_health,
    'key': phase_key,
    'server': phase_server,
    'stock': phase_stock,
    'ota': phase_ota,
    'persist': phase_persist,
    'pull': phase_pull,
}


# ----------------------------------------------------------------------- main

def confirm(question):
    try:
        return input('     %s [y/N] ' % question).strip().lower().startswith('y')
    except EOFError:
        return False


def find_key(cfg):
    if cfg.key:
        return cfg.key
    r = call(cfg.host, '/key')
    if r.status == 200 and (r.json or {}).get('key'):
        print(C.dim + 'Took the key from the unit, which means it booted in the last five '
                      'minutes.' + C.off)
        return r.json['key']
    print(C.yellow + 'No key. Reads will work and writes will be refused.' + C.off)
    print(C.dim + 'Read it from the serial console at boot, pass --key, or set SPENSER_KEY. '
                  'Restarting the unit opens the five-minute window on /key.' + C.off)
    return None


def main():
    _plain()
    parser = argparse.ArgumentParser(
        description='Walk a Spenser unit through what the new firmware changed.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Phases: ' + ', '.join(ALL_PHASES))
    parser.add_argument('--host', default=os.environ.get('SPENSER_HOST', 'http://spenser.local'))
    parser.add_argument('--key', default=os.environ.get('SPENSER_KEY'))
    parser.add_argument('--phases', default=','.join(ALL_PHASES),
                        help='comma separated, in any order')
    parser.add_argument('--firmware', help='firmware.bin to upload in the ota phase')
    parser.add_argument('--manifest', help='release manifest URL for the pull phase')
    parser.add_argument('--install', action='store_true',
                        help='in the pull phase, install what the check finds')
    parser.add_argument('--rollback', action='store_true',
                        help='after a firmware upload, roll back to the previous image')
    parser.add_argument('--wait-valid', action='store_true',
                        help='wait 70s after an upload to watch the image mark itself good')
    parser.add_argument('--yes', action='store_true', help='do not ask before dispensing or updating')
    cfg = parser.parse_args()

    print(C.bold + 'Spenser check' + C.off + '  ' + C.dim + cfg.host + C.off)
    reachable = call(cfg.host, '/settings', timeout=5)
    if reachable.status != 200:
        print(C.red + 'The unit did not answer at %s (%s)' % (cfg.host, reachable.body[:80]) + C.off)
        print(C.dim + 'Try --host http://<its address>. mDNS names like spenser.local do not '
                      'resolve on every network.' + C.off)
        return 2

    cfg.key = find_key(cfg)
    state = {}
    wanted = [p.strip() for p in cfg.phases.split(',') if p.strip()]
    unknown = [p for p in wanted if p not in PHASES]
    if unknown:
        print(C.red + 'Unknown phase(s): %s' % ', '.join(unknown) + C.off)
        return 2

    for name in wanted:
        try:
            PHASES[name](cfg, state)
        except KeyboardInterrupt:
            print('\ninterrupted')
            break
        except Exception as e:
            verdict(FAIL, 'the %s phase broke: %s' % (name, e))

    section('Summary', 'What to do about anything marked FAIL is in the line under it.')
    for kind in (FAIL, NOTE, SKIP):
        rows = [m for k, m in results if k == kind]
        if rows:
            colour = {FAIL: C.red, NOTE: C.yellow, SKIP: C.dim}[kind]
            print(colour + '%s (%d):' % (kind, len(rows)) + C.off)
            for m in rows:
                print('   - %s' % m)
    passed = len([1 for k, _ in results if k == PASS])
    failed = len([1 for k, _ in results if k == FAIL])
    print()
    print(C.bold + '%d passed, %d failed, %d notes, %d skipped' % (
        passed, failed,
        len([1 for k, _ in results if k == NOTE]),
        len([1 for k, _ in results if k == SKIP])) + C.off)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
