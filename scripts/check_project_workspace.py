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
    'Gate CVF-DG-INST-01', 'Gate CVF-DG-CONT-01', 'Gate CVF-DG-COV-01',
]


def legacy_compatible(output, code):
    """Accept only the documented legacy failure and the complete expected check set."""
    rows = []
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith('-> '):
            continue
        match = re.fullmatch(r'(.+?)\s+\[([A-Z][A-Z_]*)\]', stripped)
        if match:
            rows.append(match.groups())
    cov_failed = ('Gate CVF-DG-COV-01', 'FAIL') in rows
    expected = [(name, 'FAIL' if name == 'Gate CVF-DG-INST-01' or (cov_failed and name == 'Gate CVF-DG-COV-01') else 'PASS') for name in CHECKS]
    details = re.findall(r'^\s*-> (.+)$', output, re.M)
    expected_details = ['LOCK_INVALID@.cvf/gate-profile.lock.json [FAIL]']
    if cov_failed:
        expected_details.append('COV_OBJECT_SHAPE@docs/roadmaps/WORKSPACE_ACTIVATION.md; COV_OBJECT_SHAPE@docs/work_orders/WO_WORKSPACE_ACTIVATION.md [FAIL]')
    summary = 'RESULT: FAIL (26/28 checks passed, 2 failed)' if cov_failed else 'RESULT: FAIL (27/28 checks passed, 1 failed)'
    summaries = [line.strip() for line in output.splitlines() if line.strip().startswith('RESULT:')]
    return code == 1 and rows == expected and details == expected_details and summaries == [summary]



def digest(path, normalized=True):
    data = path.read_bytes()
    return hashlib.sha256(data.replace(b'\r\n', b'\n') if normalized else data).hexdigest()


def invoke(args):
    proc = subprocess.run(args, cwd=ROOT, text=True, encoding='utf-8', errors='replace',
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    return {'exitCode': proc.returncode, 'output': proc.stdout}


def run():
    report = {'status': 'FAIL'}
    try:
        manifest = json.loads((ROOT / '.cvf/manifest.json').read_text(encoding='utf-8-sig'))
        policy = json.loads((ROOT / '.cvf/policy.json').read_text(encoding='utf-8-sig'))
        activation = invoke([sys.executable, '-B', str(WORKSPACE / 'Check-CVF-Project-Activation.py'), '--project', str(ROOT)])
        report['activation'] = activation
        result = json.loads(activation['output'])
        if activation['exitCode'] != 0 or result.get('status') != 'CURRENT_ASSESSED' or result.get('identity', {}).get('sourceRoute') != 'AUTHORIZED_SUPPLEMENTAL':
            raise ValueError('Activation is not CURRENT_ASSESSED on the authorized supplemental route')
        upgrade_ref = policy['workspaceActivationUpgrade']
        upgrade_path = (ROOT / upgrade_ref['path']).resolve()
        if not upgrade_path.is_relative_to(ROOT) or digest(upgrade_path, normalized=False) != upgrade_ref['sha256']:
            raise ValueError('Upgrade authority hash or path mismatch')
        upgrade = json.loads(upgrade_path.read_text(encoding='utf-8-sig'))
        if upgrade.get('decision') != 'ACCEPTED':
            raise ValueError('Upgrade authority is not accepted')
        expected = upgrade['expected']
        identity = result['identity']
        if (expected['projectCoreCommit'] != manifest['cvfCoreCommit'] or identity['coreCommit'] != manifest['cvfCoreCommit']
            or expected['deliveryManifestSha256'] != result['delivery']['manifestSha256']
            or expected['profileSha256'] != identity['profileSha256']):
            raise ValueError('Upgrade source identity mismatch')
        runner = WORKSPACE / 'CVF_RULE_PACKS/operator-local/source/scripts/lib/downstream_governance/cvf_downstream_gate_runner.py'
        if digest(runner) != expected['runnerSha256']:
            raise ValueError('Supplemental runner hash mismatch')
        core = (ROOT / manifest['cvfCoreRelativePath']).resolve()
        doctor = core / 'scripts/check_cvf_workspace_agent_enforcement.ps1'
        report['legacyDoctor'] = invoke(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(doctor), '-ProjectPath', str(ROOT)])
        if not legacy_compatible(report['legacyDoctor']['output'], report['legacyDoctor']['exitCode']):
            raise ValueError('Unexpected legacy doctor result; no compatibility disposition')
        bootstrap = invoke([sys.executable, '-B', str(runner), 'run', '--phase', 'bootstrap', '--project-root', str(ROOT),
                            '--trusted', '--expect-profile-sha256', expected['profileSha256'],
                            '--expect-runner-sha256', expected['runnerSha256'], '--expect-bundle-sha256', expected['bundleSha256'],
                            '--no-receipt', '--json'])
        report['supplementalBootstrap'] = bootstrap
        data = json.loads(bootstrap['output'])
        controls = data.get('results', [])
        if (bootstrap['exitCode'] != 0 or data.get('exitCode') != 0 or data.get('phase') != 'bootstrap'
            or [c.get('controlId') for c in controls] != ['CVF-DG-INST-01', 'CVF-DG-CONT-01', 'CVF-DG-COV-01', 'CVF-DG-ACT-01']
            or any(c.get('ok') is not True or c.get('outcome') != 'PASS' or c.get('findings') != [] for c in controls)):
            raise ValueError('Supplemental bootstrap failed or control set changed')
        report['status'] = 'COMPATIBLE_ASSESSED'
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        report['error'] = str(exc)
    return report


def main():
    parser = argparse.ArgumentParser(description='Project-owned compatibility assessment; preserves the original Core doctor result.')
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
        print(result.get('legacyDoctor', {}).get('output', ''), end='')
        print('Project compatibility result:', result['status'])
        if 'error' in result:
            print('Reason:', result['error'])
        print('Original Core doctor result remains unchanged; no live governance or hosted CI claim.')
    return 0 if result['status'] == 'COMPATIBLE_ASSESSED' else 1


if __name__ == '__main__':
    sys.exit(main())

