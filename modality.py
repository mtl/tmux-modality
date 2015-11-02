#!/usr/bin/python2
#----------------------------------------------------------------------------
# tmux-modality - Vi-like modal key bindings for tmux
#
# Written in 2012 by Mike Ter Louw
#
#    To the extent possible under law, the author has dedicated all
# copyright and related and neighboring rights to this software to the public
# domain worldwide. This software is distributed without any warranty. 
#
#    You should have received a copy of the CC0 Public Domain Dedication
# along with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>. 
#
#----------------------------------------------------------------------------

import argparse
import os
from pprint import pprint
from sets import Set
import subprocess
import tempfile


#----------------------------------------------------------------------------

python = "/usr/bin/python2"
tmux = "/usr/bin/tmux"

command_mode_colors = {
    "pane-active-border-bg": "colour16",
    "pane-active-border-fg": "colour127",
    "pane-border-bg": "colour16",
    "pane-border-fg": "colour127",
    "status-bg": "colour127",
    "status-fg": "colour225",
}

insert_mode_colors = {
    "pane-active-border-bg": "colour16",
    "pane-active-border-fg": "colour24",
    "pane-border-bg": "colour16",
    "pane-border-fg": "colour24",
    "status-bg": "colour24",
    "status-fg": "colour230",
}


#----------------------------------------------------------------------------

parser = argparse.ArgumentParser(
    description = 'modal tmux bindings generator'
)
parser.add_argument(
    '-p', '--prior', dest = 'prior_mode', default = None,
    action = 'store', required = False,
    help = 'name of prior mode'
)
parser.add_argument(
    '-o', '--output', dest = 'filename', default = None,
    action = 'store', required = False,
    help = 'output script to the given file'
)
parser.add_argument(
    '-t', '--pass-through', dest = 'pass_through', default = False,
    action = 'store_const', const = True, required = False,
    help = 'enable pass-through to tmux defaults'
)
parser.add_argument(
    '-c', '--color', dest = 'use_mode_colors', default = False,
    action = 'store_const', const = True, required = False,
    help = 'change colors with mode'
)
parser.add_argument(
    '-n', '--no-temp', dest = 'no_temp_file', default = False,
    action = 'store_const', const = True, required = False,
    help = 'disable use of a temp file (may be slower)'
)
parser.add_argument(
    'mode', metavar = 'mode', nargs = 1,
    help = 'mode to set'
)

args = parser.parse_args()
#print(args.accumulate(args.arguments))


#----------------------------------------------------------------------------

batch_mode = None
use_mode_colors = None
pass_through = None
modality = os.path.abspath( __file__ )


#----------------------------------------------------------------------------

def main( args ):

    global batch_mode, pass_through, use_mode_colors

    batch_mode = not args.no_temp_file
    pass_through = args.pass_through
    use_mode_colors = args.use_mode_colors

    modes = {
        "command": mode_command(),
        "default": mode_default(),
        "empty": mode_empty(),
        "insert": mode_insert(),
    }

    Binding.default_bindings = modes[ "default" ].bound

    binder = modes[ args.mode[ 0 ] ]

    if args.prior_mode is not None:
        binder.set_prior_mode( modes[ args.prior_mode ] )

    if args.filename is not None:
        binder.write( args.filename )
    else:
        binder.execute()


#----------------------------------------------------------------------------

def mode_command():

    binder = Binder( batch_mode )

    mc = " -c"
    if not use_mode_colors:
        mc = ""

    binder.disable_all_keys()

    # "Pass-through" tmux defaults.  If pass-through feature is chosen,
    # these are inherited from the default mode, so no need to define
    # them here.
    if not pass_through:
        binder.bind( "!", [ "break-pane" ] )
        binder.bind( "[", [ "copy-mode" ] )
        binder.bind( "{", [ "swap-pane", "-U" ] )
        binder.bind( "}", [ "swap-pane", "-D" ] )
        binder.bind( ":", [ "command-prompt" ] )
        #binder.bind( ",", [ "rename-window" ] )
        binder.bind( "c", [ "new-window" ] )
        binder.bind( "o", [ "select-pane", "-t", ":.+" ] )
        binder.bind( "Space", [ "next-layout" ] )

    # Convenience bindings:
    binder.bind( "|", [ "split-window", "-h" ] )
    binder.bind( "-", [ "split-window", "-v" ] )
    #binder.bind( "<", [ "rename-session" ] )
    binder.bind( "1", [ "select-pane", "-t", "1" ] )
    binder.bind( "2", [ "select-pane", "-t", "2" ] )
    binder.bind( "3", [ "select-pane", "-t", "3" ] )
    binder.bind( "4", [ "select-pane", "-t", "4" ] )
    binder.bind( "5", [ "select-pane", "-t", "5" ] )
    binder.bind( "6", [ "select-pane", "-t", "6" ] )
    binder.bind( "7", [ "select-pane", "-t", "7" ] )
    binder.bind( "8", [ "select-pane", "-t", "8" ] )
    binder.bind( "9", [ "select-pane", "-t", "9" ] )
    binder.bind( "0", [ "select-pane", "-t", "10" ] )
    binder.bind( "n", [ "select-window", "-n" ] )
    binder.bind( "p", [ "select-window", "-p" ] )
    binder.bind( "t", [ "clock-mode" ] )
    binder.bind( "M-1", [ "select-window", "-t", ":1" ] )
    binder.bind( "M-2", [ "select-window", "-t", ":2" ] )
    binder.bind( "M-3", [ "select-window", "-t", ":3" ] )
    binder.bind( "M-4", [ "select-window", "-t", ":4" ] )
    binder.bind( "M-5", [ "select-window", "-t", ":5" ] )
    binder.bind( "M-6", [ "select-window", "-t", ":6" ] )
    binder.bind( "M-7", [ "select-window", "-t", ":7" ] )
    binder.bind( "M-8", [ "select-window", "-t", ":8" ] )
    binder.bind( "M-9", [ "select-window", "-t", ":9" ] )
    binder.bind( "M-0", [ "select-window", "-t", ":10" ] )

    # Vim-like bindings:
    binder.bind( "a", [ "run-shell", python + ' ' + modality + mc + ' insert -p command' ] )
    binder.bind( "h", [ "select-pane", "-L" ] )
    binder.bind( "H", [ "resize-pane", "-L", "1" ] )
    binder.bind( "i", [ "run-shell", python + ' ' + modality + mc + ' insert -p command' ] )
    binder.bind( "j", [ "select-pane", "-D" ] )
    binder.bind( "J", [ "resize-pane", "-D", "1" ] )
    binder.bind( "k", [ "select-pane", "-U" ] )
    binder.bind( "K", [ "resize-pane", "-U", "1" ] )
    binder.bind( "l", [ "select-pane", "-R" ] )
    binder.bind( "L", [ "resize-pane", "-R", "1" ] )
    binder.bind( "q", [ "detach-client" ] )
    binder.bind( "x", [ "confirm-before", "-p", "kill-pane #P? (y/n)", "kill-pane" ] )
    binder.bind( "Z", [ "confirm-before", "-p", "kill-window #W? (y/n)", "kill-window" ] )
    binder.bind( "Down", [ "select-pane", "-D" ] )
    binder.bind( "Left", [ "select-pane", "-L" ] )
    binder.bind( "Right", [ "select-pane", "-R" ] )
    binder.bind( "Up", [ "select-pane", "-U" ] )
    #binder.bind( "C-6", [ "select-window", "-l" ] )

    if use_mode_colors:
        binder.set_colors( command_mode_colors )
    #binder.add_command( [ "display-message", "'[Command Mode]'" ] )
    return binder


#----------------------------------------------------------------------------

def mode_default():

    binder = Binder( batch_mode )

    binder.bind( "C-b", [ "send-prefix" ], use_prefix = True )
    binder.bind( "C-o", [ "rotate-window" ], use_prefix = True )
    binder.bind( "C-z", [ "suspend-client" ], use_prefix = True )
    binder.bind( "Space", [ "next-layout" ], use_prefix = True )
    binder.bind( "!", [ "break-pane" ], use_prefix = True )
    binder.bind( "'", [ "split-window" ], use_prefix = True )
    binder.bind( "#", [ "list-buffers" ], use_prefix = True )
    binder.bind( "$", [ "command-prompt", "-I", "'#S'", "rename-session '%%'" ], use_prefix = True )
    binder.bind( "%", [ "split-window", "-h" ], use_prefix = True )
    binder.bind( "&", [ "confirm-before", "-p", "kill-window #W? (y/n)", "kill-window" ], use_prefix = True )
    binder.bind( "'", [ "command-prompt", "-p", "index", "select-window -t ':%%'" ], use_prefix = True )
    binder.bind( "(", [ "switch-client", "-p" ], use_prefix = True )
    binder.bind( ")", [ "switch-client", "-n" ], use_prefix = True )
    binder.bind( ",", [ "command-prompt", "-I", "'#W'", "rename-window '%%'" ], use_prefix = True )
    binder.bind( "-", [ "delete-buffer" ], use_prefix = True )
    binder.bind( ".", [ "command-prompt", "move-window -t '%%'" ], use_prefix = True )
    binder.bind( "0", [ "select-window", "-t :0" ], use_prefix = True )
    binder.bind( "1", [ "select-window", "-t :1" ], use_prefix = True )
    binder.bind( "2", [ "select-window", "-t :2" ], use_prefix = True )
    binder.bind( "3", [ "select-window", "-t :3" ], use_prefix = True )
    binder.bind( "4", [ "select-window", "-t :4" ], use_prefix = True )
    binder.bind( "5", [ "select-window", "-t :5" ], use_prefix = True )
    binder.bind( "6", [ "select-window", "-t :6" ], use_prefix = True )
    binder.bind( "7", [ "select-window", "-t :7" ], use_prefix = True )
    binder.bind( "8", [ "select-window", "-t :8" ], use_prefix = True )
    binder.bind( "9", [ "select-window", "-t :9" ], use_prefix = True )
    binder.bind( ":", [ "command-prompt" ], use_prefix = True )
    binder.bind( ";", [ "last-pane" ], use_prefix = True )
    binder.bind( "=", [ "choose-buffer" ], use_prefix = True )
    binder.bind( "?", [ "list-keys" ], use_prefix = True )
    binder.bind( "D", [ "choose-client" ], use_prefix = True )
    binder.bind( "L", [ "switch-client", "-l" ], use_prefix = True )
    binder.bind( "[", [ "copy-mode" ], use_prefix = True )
    binder.bind( "]", [ "paste-buffer" ], use_prefix = True )
    binder.bind( "c", [ "new-window" ], use_prefix = True )
    binder.bind( "d", [ "detach-client" ], use_prefix = True )
    binder.bind( "f", [ "command-prompt", "find-window '%%'" ], use_prefix = True )
    binder.bind( "i", [ "display-message" ], use_prefix = True )
    binder.bind( "l", [ "last-window" ], use_prefix = True )
    binder.bind( "n", [ "next-window" ], use_prefix = True )
    binder.bind( "o", [ "select-pane", "-t", ":.+" ], use_prefix = True )
    binder.bind( "p", [ "previous-window" ], use_prefix = True )
    binder.bind( "q", [ "display-panes" ], use_prefix = True )
    binder.bind( "r", [ "refresh-client" ], use_prefix = True )
    binder.bind( "s", [ "choose-session" ], use_prefix = True )
    binder.bind( "t", [ "clock-mode" ], use_prefix = True )
    binder.bind( "w", [ "choose-window" ], use_prefix = True )
    binder.bind( "x", [ "confirm-before", "-p", "kill-pane #P? (y/n)", "kill-pane" ], use_prefix = True )
    binder.bind( "{", [ "swap-pane", "-U" ], use_prefix = True )
    binder.bind( "}", [ "swap-pane", "-D" ], use_prefix = True )
    binder.bind( "~", [ "show-messages" ], use_prefix = True )
    binder.bind( "PPage", [ "copy-mode", "-u" ], use_prefix = True )
    binder.bind( "Up", [ "select-pane", "-U" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "Down", [ "select-pane", "-D" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "Left", [ "select-pane", "-L" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "Right", [ "select-pane", "-R" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "M-1", [ "select-layout", "even-horizontal" ], use_prefix = True )
    binder.bind( "M-2", [ "select-layout", "even-vertical" ], use_prefix = True )
    binder.bind( "M-3", [ "select-layout", "main-horizontal" ], use_prefix = True )
    binder.bind( "M-4", [ "select-layout", "main-vertical" ], use_prefix = True )
    binder.bind( "M-5", [ "select-layout", "tiled" ], use_prefix = True )
    binder.bind( "M-n", [ "next-window", "-a" ], use_prefix = True )
    binder.bind( "M-o", [ "rotate-window", "-D" ], use_prefix = True )
    binder.bind( "M-p", [ "previous-window", "-a" ], use_prefix = True )
    binder.bind( "M-Up", [ "resize-pane", "-U", "5" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "M-Down", [ "resize-pane", "-D", "5" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "M-Left", [ "resize-pane", "-L", "5" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "M-Right", [ "resize-pane", "-R", "5" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "C-Up", [ "resize-pane", "-U" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "C-Down", [ "resize-pane", "-D" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "C-Left", [ "resize-pane", "-L" ], use_prefix = True ) # Needs repeat (-r)
    binder.bind( "C-Right", [ "resize-pane", "-R" ], use_prefix = True ) # Needs repeat (-r)

    #binder.add_command( [ "display-message", "'[Default Mode]'" ] )
    return binder


#----------------------------------------------------------------------------

def mode_empty():

    return Binder( batch_mode )


#----------------------------------------------------------------------------

def mode_insert():

    binder = Binder( batch_mode )

    pt = " -t"
    #if not pass_through:
        #pt = ""

    mc = " -c"
    if not use_mode_colors:
        mc = ""

    binder.bind( "C-\\", [
        "run-shell",
        python + ' ' + modality + pt + mc + ' -p insert command'
    ] )

    if use_mode_colors:
        binder.set_colors( insert_mode_colors )

    #binder.add_command( [ "display-message", "'[Insert Mode]'" ] )
    return binder


#----------------------------------------------------------------------------

class Binding( object ):

    cli_escape_chars = Set( [ ";", ">", "<", "&", "|" ] )
    default_disabled_command = [ "display-message", "Unrecognized input." ]
    default_bindings = None


    #------------------------------------------------------------------------

    # Constructor.
    def __init__(
        self,
        key,
        command = None,
        use_prefix = False,
        disabled = False
    ):

        self.command = command or []
        self.disabled = disabled
        self.key = key
        self.use_prefix = use_prefix


    #------------------------------------------------------------------------

    # Get the bind-key command for the command line.
    def bind_key_cli( self ):

        if self.disabled:
            self.command = self.get_disabled_command()

        cmd_parts = []
        if not self.use_prefix:
            cmd_parts.append( "-n" )

        # Escape special shell characters in the key:
        key_parts = []
        for char in self.key:
            if char in self.cli_escape_chars:
                key_parts.append( "\\" )
            key_parts.append( char )
        cmd_parts.append( "".join( key_parts ) )

        # Add command parts:
        for part in self.command:
            cmd_parts.append( part )

        return cmd_parts


    #------------------------------------------------------------------------

    # Get the bind-key command for writing to a file.
    def bind_key_file( self ):

        escape_chars = r"\$"

        if self.disabled:
            self.command = self.get_disabled_command()

        cmd_parts = []
        if not self.use_prefix:
            cmd_parts.append( "-n" )

        quote_char = '"'
        key_parts = []
        for char in self.key:
            if char == '"':
                quote_char = "'"
            elif char == ';':
                char = r'\\;'
            elif char in escape_chars:
                char = '\\' + char 
            key_parts.append( char )
        cmd_parts.append( quote_char + "".join( key_parts ) + quote_char )

        # Quote any arguments that contain spaces:
        for part in self.command:

            if part.find( " " ) == -1:
                cmd_parts.append( part )
            else:
                cmd_parts.append( '"' + part + '"' )

        return cmd_parts


    #------------------------------------------------------------------------

    # Copy constructor.
    def copy( self ):

        return Binding(
            self.key, self.command, self.use_prefix, self.disabled
        )


    #------------------------------------------------------------------------

    # Get the command to use if this key is disabled.
    def get_disabled_command( self ):

        global pass_through

        if pass_through and self.key in self.default_bindings:
            return self.default_bindings[ self.key ].command

        return self.default_disabled_command


    #------------------------------------------------------------------------

    def unbind( self ):
        self.command = []
        self.disabled = False


    #------------------------------------------------------------------------


#----------------------------------------------------------------------------

class Binder( object ):

    no_prefix_single_keys = (
        "~!@#$%^&*()_+" +
        "`1234567890-=" +
        "qwertyuiop[]\\" +
        "QWERTYUIOP{}|" +
        "asdfghjkl;'" +
        "ASDFGHJKL:\"" +
        "zxcvbnm,./" +
        "ZXCVBNM<>?"
    )
    no_prefix_special_keys = [
        "BSpace", "BTab", "DC", "Down", "End", "Enter", "Escape",
        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10",
        "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20",
        "Home", "IC", "Left", "PageDown", "PageUp", "Right", "Space", "Tab", "Up",
        "KP*", "KP+", "KP-", "KP.", "KP/",
        "KP0", "KP1", "KP2", "KP3", "KP4", "KP5", "KP6", "KP7", "KP8", "KP9",
        "KPEnter",
    ]


    #------------------------------------------------------------------------

    # Constructor.
    def __init__( self, use_tempfile = True ):

        self.bound = {}
        self.extra_commands = []
        self.script = None
        self.unbound = {}
        self.use_tempfile = use_tempfile
        

    #------------------------------------------------------------------------

    # Add an extra command.
    def add_command( self, command ):
        self.extra_commands.append( command )

    #------------------------------------------------------------------------

    # Add a binding.
    def bind( self, key, command = None, use_prefix = False, disabled = False ):

        self.bound[ key ] = Binding( key, command, use_prefix, disabled )


    #------------------------------------------------------------------------

    # Emit a key (un)binding.
    def _emit_binding( self, binding, unbind = False ):

        global tmux

        command_name = "bind-key"
        if unbind:
            command_name = "un" + command_name

        if self.use_tempfile:
            self.script.write (
                command_name + " " +
                " ".join( binding.bind_key_file() ) +
                "\n"
            )
        else:
            command = binding.bind_key_cli()
            command.insert( 0, command_name )
            command.insert( 0, tmux )
            subprocess.call( command )


    #------------------------------------------------------------------------

    # Emit all key (un)bindings.
    def _emit_bindings( self ):

        # Emit bindings:
        for key, binding in self.bound.iteritems():
            self._emit_binding( binding )

        # Emit un-bindings if not masked by a binding:
        for key, binding in self.unbound.iteritems():
            if key not in self.bound:
                self._emit_binding( binding, unbind = True )


    #------------------------------------------------------------------------

    # Emit a command.
    def _emit_command( self, command ):

        global tmux

        if self.use_tempfile:
            self.script.write (
                " ".join( command ) + "\n"
            )
        else:
            command.insert( 0, tmux )
            subprocess.call( command )


    #------------------------------------------------------------------------

    # Disable all keys.
    def disable_all_keys( self ):

        for key in self.no_prefix_single_keys:
            self.bind( key, disabled = True )

        for key in self.no_prefix_special_keys:
            self.bind( key, disabled = True )


    #------------------------------------------------------------------------

    # Execute the bindings and unbindings.
    def execute( self ):

        global tmux

        # Create the script file:
        if self.use_tempfile:
            self.script = tempfile.NamedTemporaryFile( delete = False )
            #print( "Script file: " + self.script.name )

        # Emit key bindings:
        self._emit_bindings()

        # Emit extra commands:
        for command in self.extra_commands:
            self._emit_command( command )

        # Execute the script file, then delete it:
        if self.use_tempfile:
            self.script.close()
            subprocess.call( [ tmux, "source-file", self.script.name ] )
            os.unlink( self.script.name )
            self.script = None


    #------------------------------------------------------------------------

    # Add commands to set tmux colors.
    def set_colors( self, colors ):

        for name, value in colors.iteritems():
            self.add_command( [ "set-option", "-q", "-g", name, value ] )


    #------------------------------------------------------------------------

    # Mask the bindings of another binder.
    def set_prior_mode( self, binder ):

        for key, binding in binder.bound.iteritems():

            #if binding.use_prefix:
                #continue

            unbinding = binding.copy()
            unbinding.unbind()
            self.unbound[ key ] = unbinding


    #------------------------------------------------------------------------

    # Add an unbinding.
    def unbind( self, key, use_prefix = False, disabled = False ):

        self.unbound[ key ] = Binding( key, use_prefix = use_prefix, disabled = disabled )


    #------------------------------------------------------------------------

    # Write binding commands out to a file.
    def write( self, filename ):

        # Create the script file:
        self.script = open( filename, "w" )

        # Emit key bindings:
        self._emit_bindings()

        # Emit extra commands:
        for command in self.extra_commands:
            self._emit_command( command )

        self.script.close()


    #------------------------------------------------------------------------


#----------------------------------------------------------------------------

main( args )


#----------------------------------------------------------------------------


# vi: set filetype=python shiftwidth=4 tabstop=4 expandtab:
