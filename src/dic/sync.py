from . import diff as diff_mod

HELP_TEXT = (
    "y - write rendered output to this file\n"
    "n - skip this file\n"
    "a - write this and all remaining changes\n"
    "d - show the diff again\n"
    "q - quit sync"
)


def sync_bundle(bundle, data=None, input_func=input, output=print):
    results = diff_mod.diff_bundle(bundle, data=data)
    drifted = [r for r in results if r[1] != "in-sync"]

    if not drifted:
        output(f"[dic] {bundle}: in sync")
        return

    apply_all = False
    for target_path, status, diff_lines, expected in drifted:
        if not apply_all:
            output(f"\n--- {target_path} ({status}) ---")
            output("".join(diff_lines))

        while True:
            answer = "y" if apply_all else input_func(
                f"Apply this change to {target_path}? [y,n,a,d,q,?] "
            ).strip().lower()

            if answer in ("?", "h", "help"):
                output(HELP_TEXT)
                continue
            if answer == "d":
                output("".join(diff_lines))
                continue
            if answer == "q":
                output("[dic] sync aborted")
                return
            if answer == "a":
                apply_all = True
                answer = "y"

            if answer == "y":
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(expected)
                output(f"[dic] wrote {target_path}")
            elif answer == "n":
                output(f"[dic] skipped {target_path}")
            else:
                output("unrecognized answer, try again (? for help)")
                continue

            break
