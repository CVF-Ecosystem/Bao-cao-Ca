import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
CHECKS = [
    'Project folder exists', 'Project isolated from CVF core', '.cvf/manifest.json exists',
    '.cvf/manifest.json is valid', '.cvf/policy.json exists', 'Live governance evidence mandatory',
    'AGENTS.md exists', 'Bootstrap log exists', 'CVF core path reachable',
    'Workspace rules file exists', 'CVF core origin is public remote',
    'Public workspace kit is complete', 'CVF public core matches origin/main',
    'CVF public core worktree clean', 'CVF core commit matches manifest',
    'Required docs referenced by manifest exist', 'knowledge/ folder present (optional)',
    'Seven-step phase model is canonical', 'Project continuity and catalog front doors exist',
    'Active session state resolves its handoff', 'Implementation status and module registry are valid JSON',
    'AGENTS contract defines roles and seven steps', 'Pinned CVF core commit is public-remote reachable',
    'Session and tranche continuity rehydration required', 'Governed downstream catalog validates (--check)',
    'Gate CVF-DG-INST-01', 'Gate CVF-DG-CONT-01', 'Gate CVF-DG-COV-01', 'Gate CVF-DG-ACT-01',
]
BOOTSTRAP_CONTROLS = ['CVF-DG-INST-01', 'CVF-DG-CONT-01', 'CVF-DG-COV-01', 'CVF-DG-ACT-01']
CORE_FILES = ['scripts/lib/downstream_governance/cvf_workspace_activation.py',
              'scripts/lib/downstream_governance/cvf_downstream_gate_runner.py',
              'scripts/check_cvf_workspace_agent_enforcement.ps1']


def invoke(args):
    proc = subprocess.run(args, cwd=ROOT, text=True, encoding='utf-8', errors='replace',
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
    return {'exitCode': proc.returncode, 'output': proc.stdout}


def git(core, *args):
    proc = subprocess.run(['git', '-C', str(core), *args], cwd=ROOT, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=30)
    if proc.returncode:
        raise ValueError('Core Git identity or tracked source unavailable')
    return proc.stdout


def verify_core(manifest):
    pin = manifest.get('cvfCoreCommit')
    relative = manifest.get('cvfCoreRelativePath')
    origin = manifest.get('cvfCoreRepository')
    if not isinstance(pin, str) or not re.fullmatch(r'[0-9a-f]{40}', pin):
        raise ValueError('Full lowercase Core pin required')
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or not isinstance(origin, str) or not origin:
        raise ValueError('Core path or origin invalid')
    core = (ROOT / relative).resolve()
    if (Path(git(core, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != core
            or git(core, 'rev-parse', 'HEAD').decode().strip() != pin
            or git(core, 'status', '--porcelain', '--untracked-files=normal').strip()
            or git(core, 'remote', 'get-url', 'origin').decode().strip() != origin):
        raise ValueError('Core identity, origin, or clean checkout mismatch')
    for name in CORE_FILES:
        if git(core, 'ls-files', '--', name).decode().strip() != name:
            raise ValueError('Core source is not tracked: ' + name)
        actual = (core / name).read_bytes().replace(b'\r\n', b'\n')
        committed = git(core, 'show', 'HEAD:' + name).replace(b'\r\n', b'\n')
        if hashlib.sha256(actual).digest() != hashlib.sha256(committed).digest():
            raise ValueError('Core source differs from tracked commit: ' + name)
    return core


def native_pass(output, code):
    rows = []
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith('-> '):
            return False
        match = re.fullmatch(r'(.+?)\s+\[([^\]\r\n]+)\]', stripped)
        if match:
            rows.append(match.groups())
        elif (re.search(r'\[(?:pass|warn|fail|fatal|error)\b', stripped, re.IGNORECASE)
              or re.search(r'\b(?:warning|error|fatal)\s*:', stripped, re.IGNORECASE)):
            return False
    summaries = [line.strip() for line in output.splitlines()
                 if re.match(r'^RESULT\s*:', line.strip(), re.IGNORECASE)]
    return (code == 0 and rows == [(name, 'PASS') for name in CHECKS]
            and summaries == ['RESULT: PASS (29/29 checks passed)'])


def bootstrap_pass(result):
    if result.get('exitCode') != 0:
        return False
    data = json.loads(result['output'])
    rows = data.get('results')
    return (data.get('exitCode') == 0 and data.get('phase') == 'bootstrap'
            and isinstance(rows, list) and [r.get('controlId') for r in rows] == BOOTSTRAP_CONTROLS
            and all(r.get('ok') is True and r.get('outcome') == 'PASS' and r.get('findings') == [] for r in rows))


def run():
    report = {'status': 'FAIL'}
    try:
        manifest = json.loads((ROOT / '.cvf/manifest.json').read_text(encoding='utf-8-sig'))
        policy = json.loads((ROOT / '.cvf/policy.json').read_text(encoding='utf-8-sig'))
        if policy.get('workspaceActivationSourcePolicy') != 'CORE_AND_SUPPLEMENTAL' or policy.get('workspaceActivationExecutableSource') != 'PINNED_CORE':
            raise ValueError('Project source policy or execution route differs')
        core = verify_core(manifest)
        activation = invoke([sys.executable, '-B', str(core / 'scripts/lib/downstream_governance/cvf_workspace_activation.py'), '--project', str(ROOT)])
        report['activation'] = activation
        observed = json.loads(activation['output'])
        if (activation['exitCode'] != 0 or observed.get('status') != 'CURRENT_ASSESSED'
                or observed.get('identity', {}).get('sourceRoute') != 'PINNED_CORE'
                or observed.get('identity', {}).get('coreCommit') != manifest['cvfCoreCommit']
                or observed.get('sourcePolicy') != 'CORE_AND_SUPPLEMENTAL'
                or observed.get('delivery', {}).get('mode') != 'CORE_AND_SUPPLEMENTAL'
                or observed.get('supplementalRequirement', {}).get('mode') != 'INSPECTED'
                or observed.get('findings') != []):
            raise ValueError('Core activation or supplemental inspection is not currently assessed')
        report['executionSource'] = 'PINNED_CORE'
        doctor = invoke(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                         str(core / 'scripts/check_cvf_workspace_agent_enforcement.ps1'), '-ProjectPath', str(ROOT)])
        report['nativeDoctor'] = doctor
        if not native_pass(doctor['output'], doctor['exitCode']):
            raise ValueError('Native doctor incomplete, inconsistent, or failed')
        receipt = json.loads((ROOT / '.cvf/workspace-activation.json').read_text(encoding='utf-8-sig'))
        actions = receipt.get('actions')
        if not isinstance(actions, list) or not actions:
            raise ValueError('Assessed action packets are missing')
        packets = [action.get('packet') if isinstance(action, dict) else None for action in actions]
        if any(not isinstance(p, str) or not p for p in packets) or len(set(packets)) != len(packets):
            raise ValueError('Assessed action packet list is invalid')
        lock = json.loads((ROOT / '.cvf/gate-profile.lock.json').read_text(encoding='utf-8-sig'))
        pins = [lock[k] for k in ('profileSha256', 'runnerSha256', 'bundleSha256')]
        if any(not isinstance(p, str) or not re.fullmatch(r'[0-9a-f]{64}', p) for p in pins):
            raise ValueError('Profile, runner or bundle pin invalid')
        packet_args = [arg for packet in packets for arg in ('--packet', packet)]
        bootstrap = invoke([sys.executable, '-B', str(core / 'scripts/lib/downstream_governance/cvf_downstream_gate_runner.py'),
                            'run', '--phase', 'bootstrap', '--project-root', str(ROOT), '--trusted',
                            '--expect-profile-sha256', pins[0], '--expect-runner-sha256', pins[1],
                            '--expect-bundle-sha256', pins[2], '--no-receipt', '--json'] + packet_args)
        report['trustedBootstrap'] = bootstrap
        if not bootstrap_pass(bootstrap):
            raise ValueError('Trusted bootstrap failed, incomplete, or control set changed')
        report['status'] = 'CORE_ASSESSED'
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.TimeoutExpired, UnicodeError) as exc:
        report['error'] = str(exc)
    return report


def main():
    parser = argparse.ArgumentParser(description='Project assessment using the pinned Core doctor and activation.')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--evidence', type=Path, help='Write full result JSON to a project-relative path')
    args = parser.parse_args()
    result = run()
    serialized = json.dumps(result, ensure_ascii=False, indent=2)
    if args.evidence:
        destination = (ROOT / args.evidence).resolve()
        if not destination.is_relative_to(ROOT):
            parser.error('Evidence path must stay within the project')
        destination.write_text(serialized + '\n', encoding='utf-8')
    if args.json:
        print(serialized)
    else:
        print(result.get('nativeDoctor', {}).get('output', ''), end='')
        print('Project Core assessment:', result['status'])
        if 'error' in result:
            print('Reason:', result['error'])
        print('Native doctor output preserved; no live governance or hosted CI claim.')
    return 0 if result['status'] == 'CORE_ASSESSED' else 1


if __name__ == '__main__':
    sys.exit(main())
