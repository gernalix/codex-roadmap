PROMPT_ID=652361
PROJECT=livinggaul-x-downloader
MODEL=GPT-5.6 Terra
REASONING=medium
MegaVault=FAST

GOAL
Install and validate the resilient hourly Fedora systemd user service for LivingGaul source-availability refresh. Remote implementation and CI are already PASS at commit 6eaed2991840836ddaa8e3130ae3b62cc07962cc. The service must keep running across logout/reboot via linger, execute hourly, catch missed calendar runs, avoid overlap, retry failures, time out hung runs, and journal output.

STARTING POINT
- Repo: ~/projects/livinggaul-x-downloader
- Required commit or descendant: 6eaed2991840836ddaa8e3130ae3b62cc07962cc
- Installed CLI target: ~/.local/bin/livinggaul-x-downloader
- systemd assets: systemd/livinggaul-x-source-availability.service, systemd/livinggaul-x-source-availability.timer, systemd/install-user-service.sh
- Target user is the current non-root desktop user.
- Remote CI for 6eaed299 already passed.

SCOPE
Do only local checkout/install/systemd activation and verification. Do not download X videos, reboot the machine, scan unrelated repos, refactor unrelated code, or change cadence away from hourly.

EXECUTION
1. Claim this prompt with the canonical roadmap_start.py command and continue only if state becomes running.
2. Bring only this repo checkout to current master safely, preserving unrelated local work.
3. Install/update the repository CLI to ~/.local/bin/livinggaul-x-downloader with executable permissions and verify version 0.4.1.
4. Run targeted local syntax/unit checks only if needed; do not repeat broad audits because remote CI is PASS.
5. Run systemd/install-user-service.sh as the current user, not root.
6. Ensure linger is enabled for the current user. Prefer the installer path; if it cannot enable linger automatically, try a bounded safe local authorization path. Do not weaken persistence by omitting linger.
7. Verify the installed user units exactly implement:
   - timer OnCalendar=hourly;
   - Persistent=true;
   - timer enabled and active;
   - service Type=oneshot;
   - Restart=on-failure and RestartSec=5min;
   - TimeoutStartSec=50min;
   - flock overlap protection;
   - command is only --check-source-availability --cookies-mode auto;
   - journal logging.
8. Run systemd-analyze --user verify on the installed unit files if supported by this Fedora/systemd version; otherwise use systemctl --user cat/show as authoritative validation.
9. Start the service once manually through systemctl --user and wait for completion. Require Result=success. The DB currently may contain zero downloaded rows; that is valid.
10. Verify journalctl --user -u livinggaul-x-source-availability.service contains the smoke run output and no media-download invocation.
11. Verify:
    - loginctl show-user "$USER" -p Linger --value => yes;
    - systemctl --user is-enabled livinggaul-x-source-availability.timer => enabled;
    - systemctl --user is-active livinggaul-x-source-availability.timer => active;
    - systemctl --user list-timers shows a next hourly trigger;
    - installed service/timer files match the repo assets.
12. Do not reboot merely to test persistence. Linger=yes + enabled persistent timer + valid units are the acceptance evidence for logout/reboot survival.
13. If a local systemd/install defect blocks the goal, fix the smallest necessary in-scope code/unit/installer in this repo, run targeted tests, push the fix, reinstall, and repeat the failed gate. No unrelated cleanup.

ACCEPTANCE CRITERIA
- Checkout contains 6eaed299 or a descendant.
- Installed CLI is executable and version 0.4.1.
- Linger=yes.
- Timer is enabled+active, hourly, Persistent=true, and has a next trigger.
- Service properties confirm retry, timeout, flock, and journal safeguards.
- Manual systemd smoke run completes Result=success without downloading media.
- Installed unit files match the repo.
- Final report first line exactly PROMPT_ID=652361, followed by concise RESULT, checkout/version, linger, timer enabled/active/next trigger, service Result, journal evidence, and any fix commit.
- Finalize PASS only after all mandatory criteria pass; otherwise BLOCKED/FAIL with the concrete external blocker. Stop immediately after finalization.
