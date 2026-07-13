# Phase 5: Verify (if --apply ran OR --visual-check passed in)

```bash
# Reload atlas (Mac Mini only)
launchctl bootout gui/$(id -u)/com.user.atlas
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.atlas.plist
sleep 4

# HTTP smoke-test (necessary but not sufficient — see Playwright check below)
curl -s --max-time 8 -o /dev/null -w "references: %{http_code}\n" \
    "http://localhost:8770/book/${SLUG}/references"

# Spot-check that any new figure URL serves
for fig in $figs_paper_only; do
    name=$(basename "$fig")
    curl -s --max-time 5 -o /dev/null -w "figures/${name}: %{http_code}\n" \
        "http://localhost:8770/book/${SLUG}/figures/${name}"
done
```

## Visual smoke-test via Playwright (MANDATORY when --apply ran)

A 200 HTTP code only confirms the page served — it does NOT confirm math rendered, callouts rendered, figures resolved, citations linked. Use the shared `visual_check.mjs` script from `init-paper-book` (same invariants — single H1, no raw mystmd, math rendering, callout rendering, figures resolve, citations link, sidebar chapter list, no console errors):

```bash
node <skills-root>/init-paper-book/references/visual_check.mjs \
    --slug "${SLUG}" \
    --base-url "http://localhost:8770" \
    --output /tmp/audit-paper-book-visual-${SLUG}.json
```

Output JSON: `{chapter: {pass: bool, failures: [<list>], screenshot: "<path>"}}`. Any chapter with `pass: false` is added to the audit report's `accessibility` / `rendering_drift` bucket. The visual check NEVER auto-fixes — failures require user judgement (could be a converter regression, a missing figure, a broken cite key, or intended layout).
