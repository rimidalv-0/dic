# DIC - Declerative-Imperative configmanager

so it all started from frustration with nixos
have a consistent config but it isnt owned by me.

i love that i can let nix write the configs for my apps. by that i mean have jinja style like placeholders.
used it a lot for a consistent theme across all apps.

but the issue is the store. if done that way the configs land in store and i cant change them on runtime. so something like font size change becomes imposible without home-manager switch.

also i hate the 7 layers of hell (abstraction of abstraction of abstraction)
so my idea was. keep the format of configs native - but declerative - but imperative.

## idea

u have a single (or composed) config of truth. 
json format was chosen cause of the nice middle ground bettween nix and python dict.

```
{
    "theme": {
        "name": "gruvbox",
        "fg": "#ffffff",
        ...
    },
    "browser": "brave"
    ...
}
```

so there you can have arbitrary configs. whatever you want how you want.
and let jinja replace the parts in you configs.

[kitty.conf]
```
foreground {{ theme.fg }}
...
```

[nvim.lua]
```
local M = {
  normal = { bg = {{ theme.bg }}, fg = {{ theme.fg }} },

  ellipsis = { fg = {{ theme.colors.05 }} },
  separator = { fg = {{ theme.colors.green }} },
  modified = { fg = {{ theme.colors.warning }} },
}
```

so then you have a store of configs, written in native config format, only with values placeholders you want to change.
dic with jinja will render those configs and write them to the right places.
a cutsom diff engine will check for drifts since the configs written in place will be editable, so runtime changes are still possible.
the diff engine will ensure what should be kept and what is machiene specific.

## where its at now

ok so this actually works now. everything lives under `~/.config/dic`, theres a `state.json` (the source of truth), a `mappings.json` (which bundle owns which paths) and a `templates/` folder with one subfolder per bundle.

a bundle is just a name for one app, like `nvim` or `kitty`, and it can point at more then one real path at once. nvim for example needs both `~/.config/nvim` and `~/.local/state/nvim`.

commands so far:

```
dic init                    set up ~/.config/dic
dic add <bundle> <path>     register a path under a bundle, copies whats already there in as a starting template
dic remove <bundle>         unregister a bundle, templates stay on disk, nothing gets deleted
dic list                    show registered bundles and there paths
dic status [bundle]         quick summary, how many files in sync / drifted / missing
dic render [bundle]         preview what would get rendered, doesnt touch anything
dic diff [bundle]           full diff between rendered output and whats actually on disk
dic sync [bundle]           the real deal, walks you through every drifted file git add -p style and writes on yes
dic edit <bundle>           opens $EDITOR on the bundle's templates
```

one thing that bit me: some configs use `{{` or `}}` for there own stuff that has nothing to do with jinja. kitty.conf for example ships with vim fold markers like `#: Fonts {{{` by default and that straight up crashes jinja cause it thinks its the start of a variable. so now when `dic add` copies a file in it automatically wraps anything that looks like jinja syntax in `{% raw %}` so it renders back out exactly like it was, untill you go add your own real `{{ theme.x }}` by hand somewhere else in the file.

theres also a `.dicignore` per bundle now, same idea as gitignore, for lock files caches and all that stuff you dont actually want copied in.

if your on nixos theres a `flake.nix` too now. `nix build` / `nix run` both work, or just throw it into your system flake as an input.

## still to come

sync could be smarter, diff is still just line based, no real tests yet. but the core loop, add a config, template the parts you care about, sync when it drifts, works end to end right now.

i hope this idea becomes something. cause i want my computer and my software play by my rules. and not b 100000 levels of abstructuions and 100000 different formats i cant remember.
