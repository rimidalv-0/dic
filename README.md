# DIC - Declerative-Imperative configmanager

i have that vision that i can configure all my apps to behave toghether. if i have a prefered editor i want this editor to be recognized by every atom on my computer.

nixos gave me the opartunity. i could just write config and nixos would fill out the blanks.
but then came the problem of permissions. 
When nix did my dotfiles they were in the store and i would only get a symlink. so something like zed where i wanted to change the font size was imposible withouth home-manager switch.
i hate that but i love that.

so this is my idea that i randomly though. its not finished by any mean. i dont know where it will land

## the idea

the way i was solving the colors problem on my nix machine gave me an idea. i can have a single config of truth.
in that case a json file where i can write every config imaginable and let python and jinja render the configs.

that solves a problem of ownership. i own the configs even though they are rendered by a tool. home-manager can have the templates thats okey i dont care cause the writen configs are in the right places anyway. so i can change the configs on runtime withouth rebuilding my system for font size changes.

the idea as for now look like this

i have a single (or composed) file of truth. 
example:
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

there isnt a validator cause the last thing i want to is another abstraction that expects things their way.
so its a simple json. also a nix expression can easiliy be turned into json.

with jinja i can write a config in its native language.
nvim in lua
bash in ... well bash

and jinja will just replace the parts
so to configure a global theme i just write a normal config for each app

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

and all apps take the values from a single source of truth.

so also further changes becomes easy. like change browser? no problem edit one entry in the json file and thats it all configs that are tracked by dic will use the new browser. as simple as that.

## where its at now

ok so this actually works now, its not just an idea anymore. everything lives under `~/.config/dic`, theres a `state.json` (the source of truth), a `mappings.json` (which bundle owns which paths) and a `templates/` folder with one subfolder per bundle.

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
