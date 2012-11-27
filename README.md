tmux-modality
=============

Vi-like modal key bindings for tmux


Description
------------------
It's a script to implement modal key bindings for tmux.
The script produces a file of bind-key commands corresponding to the key bindings for a given mode, and then invokes the tmux source-file command on the file.

By default, tmux starts in insert mode, where all non-prefixed keys are sent to the current pane, and the default tmux key bindings are available via the prefix key (C-b).
An additional (non-prefixed) binding on C-\ switches to command mode, where vim-like key bindings are available without a prefix.
For example, 'h', 'j', 'k' and 'l' keys can be used to navigate panes, 'q' detaches the client, and so on.
Use 'i' to return to insert mode.
Mode switches are optionally accompanied by changes to the status bar and pane border colors, to provide visual indication of the current mode.

Also available (on by default) is a "pass-through" feature to enable quick access to the default tmux bindings from command mode.
Any prefixed default binding that does not have a corresponding non-prefixed command-mode binding will be made available in command mode without a prefix.
For example, '[' enters copy mode from command mode.


Dependencies
------------------
- Python 2


Install
--------------
- Put location to python and tmux binaries in modality.py
- Store modality script where you want it (e.g., ~/.tmux/)
- Remove all bind-key commands from your .tmux.conf
- Add the following to .tmux.conf:
```
# Start tmux in insert mode:
run-shell "/usr/bin/python2 /home/.../.tmux/modality.py -c -p empty insert"

# Start tmux in command mode:
#run-shell "/usr/bin/python2 /home/.../.tmux/modality.py -t -p empty command"
```


Customize
--------------
- Edit mode colors in modality.py, or disable color changing by removing -c argument to modality.py.
- Edit key bindings in modality.py
- Disable tmux default (prefixed) bindings by starting tmux-modality from the default state ("-p default" instead of "-p empty").
- Disable command-mode pass-through feature by removing -t arguments to modality.py script in files .tmux.conf and modality.py.


Use
--------------
See the Description section.
See the mode_command() function in modality.py for a listing of command-mode key bindings.


