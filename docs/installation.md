# Install OpenEvalGate and run an offline review

OpenEvalGate supports Python 3.10–3.14. The first review uses a checked-in,
synthetic subscription-support package. No model API key is needed.

## Install from a source checkout

On macOS or Linux:

```bash
git clone https://github.com/charliechenye/OpenEvalGate.git
cd OpenEvalGate
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
openevalgate --version
openevalgate check examples/subscription_support_assistant/
openevalgate report examples/subscription_support_assistant/ --format card
```

On Windows PowerShell:

```powershell
git clone https://github.com/charliechenye/OpenEvalGate.git
Set-Location OpenEvalGate
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .
openevalgate --version
openevalgate check examples/subscription_support_assistant/
openevalgate report examples/subscription_support_assistant/ --format card
```

Expected decision: `Ready for bounded controlled launch`, without blockers.
This demonstrates the format and workflow; it is not deployment approval.
The target is roughly five minutes including installation, subject to Python
availability and download speed. The review itself runs offline.

For a reproducible CI installation, check out a reviewed **full commit SHA**
before installing. A branch name is useful for exploration but can move.
Use [GitHub Actions](integrations/github-actions.md) or the
[Promptfoo integration](integrations/promptfoo.md) for consumer-repository examples.

## Install a GitHub Release artifact

There is no PyPI publication in this release plan. Download the wheel and
`SHA256SUMS` from the **same** [GitHub Release](https://github.com/charliechenye/OpenEvalGate/releases).
Use this path only when those assets are attached; `v0.1.0` was published
without package assets. `0.1.1` assets are a release handoff, not a claim that
they are already publicly available.

In a directory containing the downloaded files, verify each downloaded asset
against `SHA256SUMS`, then install:

```bash
# GNU/Linux, after downloading both the wheel and source archive:
sha256sum --check SHA256SUMS
# macOS equivalent: shasum -a 256 --check SHA256SUMS
python -m pip install ./openevalgate-0.1.1-py3-none-any.whl
openevalgate --version
```

PowerShell: `Get-FileHash .\openevalgate-0.1.1-py3-none-any.whl -Algorithm SHA256`,
then compare with the wheel entry in `SHA256SUMS` before installation.
The source archive can also be installed with
`python -m pip install ./openevalgate-0.1.1.tar.gz`.

The wheel contains the CLI and packaged schemas. Examples, tutorials, and
experimental producer scripts live in the source checkout. Install the
package from the **same checkout** when using the Promptfoo example because
its internal Python imports are experimental.

## Use your own evidence

Follow [Getting Started](00_getting_started_for_practitioners.md) to fill a
review workspace, or [Promptfoo](integrations/promptfoo.md) to convert existing
results. Supply real control evidence, a selected run/candidate, and current
review context. A `pass` does not independently verify claims or guarantee
fresh evidence: V1 freshness/expiry authorization enforcement is incomplete.
