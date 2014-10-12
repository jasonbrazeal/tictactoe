# .bashrc

# to customize prompt
PS1="\n\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h\[\033[m\]:\[\033[33;1m\][\w]\[\033[m\]
\[\033[35m\]\t\[\033[m\]->"

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# for history command
export HISTSIZE=10000                   # 500 is default
export HISTFILESIZE=1000000
export HISTTIMEFORMAT='%b %d %I:%M %p ' # using strftime format
export HISTCONTROL=ignoreboth           # ignoredups:ignorespace
export HISTIGNORE="history:pwd:exit"

# GREP_COLOR codes
# Attributes:   Text color:    Background:
#   0 reset all   30 black       40 black
#   1 bright      31 red         41 red
#   2 dim         32 green       42 green
#   4 underscore  33 yellow      43 yellow
#   5 blink       34 blue        44 blue
#   7 reverse     35 purple      45 purple
#   8 hidden      36 cyan        46 cyan
#                 37 white       47 white
# foreground only
#
export GREP_COLOR="32"
#
# foreground and background
#
# export GREP_COLOR="34;47"

# Specify options grep should use by default
export GREP_OPTIONS="--color=auto -E"

# aliases
alias ll='ls -lahG'
alias home='cd ~'
alias up='cd ..'
alias back='cd -'
alias h='history'
alias mv='mv -i'
alias cp='cp -i'
alias rm='rm -i'
alias mkdir='mkdir -p'
alias df='df -h'
alias du='du -h'

# for python
export WORKON_HOME=/opt/.virtualenvs
export VIRTUALENVWRAPPER_HOOK_DIR=$WORKON_HOME
export VIRTUALENVWRAPPER_TMPDIR=$WORKON_HOME
export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python2.7
export PIP_VIRTUALENV_BASE=$WORKON_HOME
export PIP_RESPECT_VIRTUALENV=true
export VIRTUALENVWRAPPER_PROJECT_FILENAME=.project_virtualenv
if [ -f /usr/local/bin/virtualenvwrapper.sh ]; then
    source /usr/local/bin/virtualenvwrapper.sh
fi
