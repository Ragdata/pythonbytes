#!/usr/bin/env python3
####################################################################
# config.py
####################################################################
# Author:       Ragdata
# Date:         28/06/2025
# License:      MIT License
# Repository:	https://github.com/Ragdata/.dotfiles
# Copyright:    Copyright © 2024 Redeyed Technologies
####################################################################

import os

from pathlib import Path



SYMBOL_ERROR = "✘"
SYMBOL_WARNING = "🛆"
SYMBOL_INFO = "✚"
SYMBOL_SUCCESS = "✔"
SYMBOL_TIP = "★"
SYMBOL_IMPORTANT = "⚑"

COLOR_ERROR = "red"
COLOR_WARNING = "yellow"
COLOR_INFO = "blue"
COLOR_SUCCESS = "green"
COLOR_TIP = "cyan"
COLOR_IMPORTANT = "magenta"

INSTALL_DIR = Path.home() / '.dotfiles'
LOG_LEVEL = 'INFO'
LOG_DIR = Path.home() / '.dotfiles' / 'logs'


def loadEnv():
	"""
	Load environment variables from the env list.
	"""

	envfile = Path(os.environ.get('LOG_DIR', Path.home() / '.dotfiles' / 'logs')) / '.env'

	if envfile.exists():
		with open(envfile, 'r') as f:
			for line in f:
				if line.strip() and not line.startswith('#'):
					key, value = line.strip().split('=', 1)
					os.environ[key.strip()] = value.strip()
