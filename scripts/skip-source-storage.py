#!/usr/bin/env python3
"""Keep the sheng source-storage archive out of the kernel while it is not qualified.

board.toml lists component:ShengUfs after the archive steps. On iPadOS 27 that
catalog entry runs scripts/build-sheng-source-storage.py, which only proceeds when
a signed root policy for the selected IPSW build (for example 24A446) is shipped in
the build tree as scripts/policies/*<build>. This board has no such policy yet, so
the step fails with "no policy directory for 24A446" and the whole kernel job stops
before the final link.

Passing the catalog entry through this script records a skip in the build log and
exits 0. Nothing is linked into the kernel, which is correct for a board without a
root volume; it is NOT a substitute for the first line of defence, the
scripts/policies directory or --policy-dir that the storage team will ship.

Pass --allow to let a real build through, or simply drop the entry from
board.toml once the policy directory exists.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    argv = sys.argv[1:]
    name = argv.pop(0) if argv and not argv[0].startswith('-') else 'ShengUfs'
    allow = '--allow' in argv
    policy = sorted(ROOT.glob('scripts/policies/*'))
    if allow or policy:
        target = ROOT / 'scripts/build-sheng-source-storage.py'
        if not target.is_file():
            raise SystemExit('scripts/build-sheng-source-storage.py is missing')
        print('== component %s: running the upstream builder (%d policy directories)'
              % (name, len(policy)), flush=True)
        return subprocess.call([sys.executable, str(target)])
    print('== component %s: skipped, no signed root policy (scripts/policies/*<build>)' % name,
          flush=True)
    print('   the archive is not linked; the kernel gets no UFS root this build', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
