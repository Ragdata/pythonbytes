#!/usr/bin/env python3
####################################################################
# logbytes/handler.py
####################################################################
# Author:       Ragdata
# Date:         02/07/2025
# License:      MIT License
# Repository:	https://github.com/Ragdata/.dotfiles
# Copyright:    Copyright © 2024 Redeyed Technologies
####################################################################

from __future__ import annotations

import io
import sys
import logging

from typing import Optional

from pythonbytes.config import *



#---------------------------------------------------------------------------
#   HANDLER CLASSES (Multiton Pattern)
#---------------------------------------------------------------------------
class Handler(logging.Handler):
	"""
	A custom logging handler class extending logging.Handler with a multiton pattern.
	"""

	_instances = {}


	def __new__(cls, name: str, level: int = logging.NOTSET) -> Handler:
		"""
		Create a new instance of Handler or return an existing one (multiton pattern).

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).

		:return: A Handler instance.
		"""

		# Return existing instance
		if name in cls._instances:
			return cls._instances[name]

		# Create new instance
		instance = super().__new__(cls)
		instance.__init__(name, level)

		return instance


	def __init__(self, name: str, level: int = logging.NOTSET):
		"""
		Initialize the Handler class.

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).
		"""
		# Prevent re-initialization of existing instances
		if name in self._instances:
			return

		# Initialize the parent logging.Handler
		instance = super().__init__(level)
		self._instances[name] = instance

		# Set up the handler's name and level
		self.name = name
		self.setLevel(level)


	def __call__(self, name: str, level: int = logging.NOTSET) -> Handler:
		"""
		Call method to get a Handler instance (multiton access method).

		:param name:  The name of the logger.
		:param level: The logging level.

		:return: A Handler instance.
		"""
		# Return existing instance
		if name in self._instances:
			return self._instances[name]
		# Create new instance
		return self.__new__(self.__class__, name, level)


	def getHandler(self, name: str, level: int = logging.NOTSET) -> Handler:
		"""
		Get a Handler instance (explicit multiton access method).

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).

		:return: A Handler instance.
		"""
		# Return existing instance
		if name in self._instances:
			return self._instances[name]
		# Create new instance
		return self.__new__(self.__class__, name, level)


class StreamHandler(Handler):
	"""
	A custom stream handler class extending Handler for logging to a stream.
	"""

	terminator = "\n"

	def __init__(self, name: str, level: int = logging.NOTSET, stream: Optional[object] = None):
		"""
		Initialize the StreamHandler class.

		:param name:   The name of the handler.
		:param level:  The logging level (default = logging.NOTSET).
		:param stream: The stream to log to (default = None).
		"""
		# Prevent re-initialization of existing instances
		if name in self._instances:
			return
		if stream is None:
			stream = sys.stdout

		self.stream = stream if stream else None

		self._instances[name] = Handler.__init__(self, name, level)


class FileHandler(StreamHandler):
	"""
	A custom file handler class extending Handler for logging to a file.
	"""

	def __init__(self, name: str, filename: str = "logfile.log", mode: str = 'a', encoding: Optional[str] = None, delay: bool = False, errors: bool = False):
		"""
		Initialize the FileHandler class.

		:param name:     The name of the handler.
		:param level:    The logging level (default = logging.NOTSET).
		:param filename: The name of the file to log to (default = "logfile.log").
		"""
		# Prevent re-initialization of existing instances
		if name in self._instances:
			return

		filename = os.fspath(filename)

		self.basefilename = os.path.abspath(filename)
		self.mode = mode
		self.encoding = encoding
		if "b" not in mode:
			self.encoding = io.text_encoding(encoding)
		self.errors = errors
		self.delay = delay
		self._builtin_open = open

		self._instances[name] = Handler.__init__(self, name, logging.NOTSET)


class StdErrHandler(StreamHandler):
	"""
	A custom stderr handler class extending StreamHandler for logging to stderr.
	"""

	def __init__(self, name: str, level: int = logging.NOTSET):
		"""
		Initialize the _StderrHandler class.

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).
		"""
		# Prevent re-initialization of existing instances
		if name in self._instances:
			return
		# Create & save the new instance
		self._instances[name] = Handler.__init__(self, name, level)

	@property
	def stream(self):
		"""
		Get the stream for this handler.
		"""
		# Return the standard error stream
		return sys.stderr
