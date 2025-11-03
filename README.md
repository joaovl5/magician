# The Magician 🧙

> Do you seek it too, traveler? The power to see your computer bend to your will? Have you too many projects, where opening each takes such toll?

The Magician is a work-in-progress CLI tool for autostarting pre-defined apps in a certain layout, by way of a YAML configuration file. It currently supports kitty + tmux layouts, and is meant to save time when faced with situations like below:

- You want to start the editors and terminals for your project 
- You have to open a tmux session for the different Neovim instances to follow:
  - Backend API
  - Frontend
  - ABC service
  - XYZ service
  - ...
- You open a new kitty tab w/ another tmux session to house all run scripts for each app:
  - Backend start docker compose
  - Backend "run dev" script
  - Frontend watch script
  - ...

In Magic, we'd use the following config for such setup:

<details open>
<summary>Open for seeing example YAML</summary>

```yaml
wizard:
  root: # pane management settings
    backend: kitty
    nested: # nested, child pane management settings
      backend:
        name: tmux
        options:
          # pane numbers will start counting at 0 as per tmux's defaults
          # toggle this if your tmux configs make window indexes start at 1 instead of 0
          start_count_at_one: true

project:
  # name: my-project
  # description: This is my project and an optional field.
  dir: ~/code/my-project/ # default working directory root for commands and settings
  setup:
    project_code: # 1st kitty pane in this case
      # specifies we'll use nested logic for this window instead of just using it
      nested: true
      run: # default commands that will run for pane or, in this case, every child pane
        - nvim .
      panes:
        backend: # 1st tmux tab in this case
          dir: ./backend/ # uses project dir as basis
          run: # runs *AFTER* parent commands (neovim in this case)
            - echo "You successfully exited neovim!"
        frontend:
          dir: ./frontend/
        notifications-service:
          dir: ./notifications-service/ 
          run-before: # runs BEFORE parent commands
            - echo "Starting nvim in 1 second..."
            - sleep 1
    project_run:
      nested: true
      panes:
        backend:
          dir: ./backend/
          run:
            - macro: python-activate-venv # special macro for detecting and activating virtual environment in directory
            - ./start_server.sh local
        frontend:
          dir: ./frontend/
          run:
            - pnpm run start-local
        notifications-service:
          dir: ./notifications-service/
          run:
            - macro: python-activate-venv
            - fastapi run api/app.py --port 8000 --host 0.0.0.0
```

</details>

## Disclaimer 

This is mostly a prototype which, although I use everyday, may or may not work for your purposes, so be advised: should you want to try this, expect to deal w/ the code yourself, since I haven't extensively tested this nor have ample time for that.
