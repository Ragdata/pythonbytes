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

import typer

from rich.console import Console

from pythonbytes import config

app = typer.Typer()
console = Console()
errconsole = Console(stderr=True)


class Message():
	"""
	A class to represent a formatted message with optional color, prefix, suffix, and stream options.
	"""

	def __init__(self, msg: str = "", color: str | None = None, prefix: str | None = None, suffix: str | None = None, err: bool = False, code: int = 1, noline: bool = False):
		"""
		Initialise the Mesage class

		:param msg:      The message to be formatted.
		:param color:    The color of the message (default = None).
		:param prefix:   Optional prefix to be added to the message.
		:param suffix:   Optional suffix to be added to the message.
		:param err:      If True, the message will be printed to stderr.
		:param code:     The exit code to be used when printing the message (default = 1).
		:param noline:   If True, the message will not end with a newline character.
		"""
		self.msg = msg
		self.color = color
		self.prefix = prefix
		self.suffix = suffix
		self.err = err
		self.code = code
		self.noline = noline


	def __str__(self) -> str:
		return f"{self.format()}"


	def format(self):
		"""
		Returns the formatted message based on the provided attributes.
		"""
		self.get_msg()

		if self.err:
			self.msg = typer.style(self.msg, fg=config.COLOR_ERROR, bold=True)
		elif self.color:
			self.msg = typer.style(self.msg, fg=self.color)

		return self.msg


	def get_msg(self):
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


	def output(self):
		"""
		Prints the formatted message to the console.
		"""
		if self.err:
			if self.noline:
				errconsole.print(self.msg, end="")
			else:
				errconsole.print(self.msg)
		else:
			if self.noline:
				console.print(self.msg, end="")
			else:
				console.print(self.msg)


	def print(self):
		"""
		Prints the formatted message to the console with applied formatting.
		"""
		self.format()
		self.output()


#
# COLOR ALIASES
#
def echoBlack(): lambda msg: Message(msg, color="black").print()
def echoRed(): lambda msg: Message(msg, color="red").print()
def echoGreen(): lambda msg: Message(msg, color="green").print()
def echoGold(): lambda msg: Message(msg, color="yellow").print()
def echoBlue(): lambda msg: Message(msg, color="blue").print()
def echoMagenta(): lambda msg: Message(msg, color="magenta").print()
def echoCyan(): lambda msg: Message(msg, color="cyan").print()
def echoLtGrey(): lambda msg: Message(msg, color="white").print()
def echoGrey(): lambda msg: Message(msg, color="bright_black").print()
def echoPink(): lambda msg: Message(msg, color="bright_red").print()
def echoLtGreen(): lambda msg: Message(msg, color="bright_green").print()
def echoYellow(): lambda msg: Message(msg, color="bright_yellow").print()
def echoLtBlue(): lambda msg: Message(msg, color="bright_blue").print()
def echoPurple(): lambda msg: Message(msg, color="bright_magenta").print()
def echoLtCyan(): lambda msg: Message(msg, color="bright_cyan").print()
def echoWhite(): lambda msg: Message(msg, color="bright_white").print()

#
# SPECIAL STYLES
#
def echoDivider(): lambda: Message("divider").print()
def echoLine(): lambda: Message("line").print()
def echoDebug(): lambda msg: Message(msg, color="white", prefix="DEBUG: ").print()

#
# TERMINAL MESSAGE ALIASES
#
def echoError(): lambda msg: Message(msg, color=config.COLOR_ERROR, prefix=config.SYMBOL_ERROR + " ERROR: ", err=True).print()
def echoWarning(): lambda msg: Message(msg, color=config.COLOR_WARNING, prefix=config.SYMBOL_WARNING + " WARNING: ").print()
def echoInfo(): lambda msg: Message(msg, color=config.COLOR_INFO, prefix=config.SYMBOL_INFO + " INFO: ").print()
def echoSuccess(): lambda msg: Message(msg, color=config.COLOR_SUCCESS, prefix=config.SYMBOL_SUCCESS + " SUCCESS: ").print()
def echoTip(): lambda msg: Message(msg, color=config.COLOR_TIP, prefix=config.SYMBOL_TIP + " TIP: ").print()
def echoImportant(): lambda msg: Message(msg, color=config.COLOR_IMPORTANT, prefix=config.SYMBOL_IMPORTANT + " IMPORTANT: ").print()
