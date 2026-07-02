import argparse

from . import manager


def main():
    parser = argparse.ArgumentParser(
        prog="dic",
        description="Declarative Imperative Configs",
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init")
    sub.add_parser("list")

    p_add = sub.add_parser("add")
    p_add.add_argument("bundle")
    p_add.add_argument("path")

    p_remove = sub.add_parser("remove")
    p_remove.add_argument("bundle")

    p_status = sub.add_parser("status")
    p_status.add_argument("bundle", nargs="?")

    p_render = sub.add_parser("render")
    p_render.add_argument("bundle", nargs="?")

    p_diff = sub.add_parser("diff")
    p_diff.add_argument("bundle", nargs="?")

    p_sync = sub.add_parser("sync")
    p_sync.add_argument("bundle", nargs="?")

    p_edit = sub.add_parser("edit")
    p_edit.add_argument("bundle")

    args = parser.parse_args()

    match args.command:
        case "init":
            manager.init()
        case "list":
            manager.list_bundles()
        case "add":
            manager.add(args.bundle, args.path)
        case "remove":
            manager.remove(args.bundle)
        case "status":
            manager.status(args.bundle)
        case "render":
            manager.render(args.bundle)
        case "diff":
            manager.diff(args.bundle)
        case "sync":
            manager.sync(args.bundle)
        case "edit":
            manager.edit(args.bundle)
        case _:
            parser.print_help()
