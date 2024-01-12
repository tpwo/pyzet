# Supported editors

CLI editors like vim or nano should work out of the box without the need
of passing any `editor_args`. For GUI editors you almost always are
expected to pass some args. Below is the list with some tested editors.

> 💡 **TIP:** if your editor is not listed, you can search how to set it
> up as Git's commit message editor. Very likely if an editor works with
> Git with certain args, it should work with pyzet when the same args are
> used.

## [VS Code](https://code.visualstudio.com/)

* If `code` is not available in your `PATH`, you need to pass the full
  path to it (it's in `bin/` folder of VS Code installation)

* If you open VS Code instance in your `zet` folder, then this instance
  will always be preferred

* You can add `--new-window` arg to always open a new VS Code instance,
  but this might be a bit slow

* Works well with WSL2

```yaml
editor: code
editor_args: [--wait]
```

## [Notepad++](https://notepad-plus-plus.org/)

* Works well with WSL2

```yaml
editor: C:/Program Files/Notepad++/notepad++.exe
editor_args: [-multiInst, -notabbar, -nosession, -noPlugin]
```

## [Geany](https://www.geany.org/)

```yaml
editor: C:/Program Files/Geany/bin/geany.exe
editor_args: [--new-instance, --no-msgwin, --no-ctags, --no-session]
```
