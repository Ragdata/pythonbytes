#!/usr/bin/env python3
####################################################################
# messages.py
####################################################################
# Author:       Ragdata
# Date:         28/06/2025
# License:      MIT License
# Repository:	https://github.com/Ragdata/.dotfiles
# Copyright:    Copyright © 2024 Redeyed Technologies
####################################################################

import os
import sys
import typer

from pythonbytes import config

from rich.console import Console

app = typer.Typer()
console = Console()
errconsole = Console(stderr=True)


class Message():
	"""
		A class to represent a formatted message with optional color, prefix, suffix, and stream options.
	"""
	def __init__(self, msg: str = "", color: str = "", prefix: str = "", suffix: str = "", err: bool = False, code: int = 1, noline: bool = False):
		self.msg = msg
		self.color = color
		self.prefix = prefix
		self.suffix = suffix
		self.err = err
		self.code = code
		self.noline = noline


	def _format(self):
		"""
			Returns the formatted message based on the provided attributes.
		"""
		self._get_msg()

		if self.err:
			self.msg = typer.color(self.msg, fg=config.COLOR_ERROR, bold=True)
			if self.noline:
				errconsole.print(self.msg, end="")
			else:
				errconsole.print(self.msg)
			sys.exit(self.code)
		else:
			self.msg = typer.color(self.msg, fg=self.color, bold=True)
			if self.noline:
				console.print(self.msg, end="")
			else:
				console.print(self.msg)

		return self.msg


	def _get_msg(self):
		"""
			Returns the message with applied formatting, color, prefix, and suffix.
		"""
		if self.msg == "":
			raise ValueError("Message cannot be empty")

		if self.msg == "divider":
			self.msg = "=" * 68
			return 0
		elif self.msg == "line":
			self.msg = "-" * 68
			return 0

		if self.prefix:
			self.msg = f"{self.prefix} {self.msg}"

		if self.suffix:
			self.msg = f"{self.msg} {self.suffix}"

		return 0

#
# COLOR ALIASES
#
def echoBlack(): lambda msg: Message(msg, color="black")._format()
def echoRed(): lambda msg: Message(msg, color="red")._format()
def echoGreen(): lambda msg: Message(msg, color="green")._format()
def echoGold(): lambda msg: Message(msg, color="yellow")._format()
def echoBlue(): lambda msg: Message(msg, color="blue")._format()
def echoMagenta(): lambda msg: Message(msg, color="magenta")._format()
def echoCyan(): lambda msg: Message(msg, color="cyan")._format()
def echoLtGrey(): lambda msg: Message(msg, color="white")._format()
def echoGrey(): lambda msg: Message(msg, color="bright_black")._format()
def echoPink(): lambda msg: Message(msg, color="bright_red")._format()
def echoLtGreen(): lambda msg: Message(msg, color="bright_green")._format()
def echoYellow(): lambda msg: Message(msg, color="bright_yellow")._format()
def echoLtBlue(): lambda msg: Message(msg, color="bright_blue")._format()
def echoPurple(): lambda msg: Message(msg, color="bright_magenta")._format()
def echoLtCyan(): lambda msg: Message(msg, color="bright_cyan")._format()
def echoWhite(): lambda msg: Message(msg, color="bright_white")._format()

#
# SPECIAL STYLES
#
def echoDivider(): lambda: Message("divider")._format()
def echoLine(): lambda: Message("line")._format()
def echoDebug(): lambda msg: Message(msg, color="white", prefix="DEBUG:")._format()

#
# TERMINAL MESSAGE ALIASES
#
def echoError(): lambda msg: Message(msg, color=config.COLOR_ERROR, prefix=config.SYMBOL_ERROR + " ERROR:", err=True)._format()
def echoWarning(): lambda msg: Message(msg, color=config.COLOR_WARNING, prefix=config.SYMBOL_WARNING + " WARNING:")._format()
def echoInfo(): lambda msg: Message(msg, color=config.COLOR_INFO, prefix=config.SYMBOL_INFO + " INFO:")._format()
def echoSuccess(): lambda msg: Message(msg, color=config.COLOR_SUCCESS, prefix=config.SYMBOL_SUCCESS + " SUCCESS:")._format()
def echoTip(): lambda msg: Message(msg, color=config.COLOR_TIP, prefix=config.SYMBOL_TIP + " TIP:")._format()
def echoImportant(): lambda msg: Message(msg, color=config.COLOR_IMPORTANT, prefix=config.SYMBOL_IMPORTANT + " IMPORTANT:")._format()
