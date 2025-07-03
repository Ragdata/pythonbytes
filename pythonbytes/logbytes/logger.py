#!/usr/bin/env python3
####################################################################
# logbytes/logger.py
####################################################################
# Author:       Ragdata
# Date:         02/07/2025
# License:      MIT License
# Repository:	https://github.com/Ragdata/.dotfiles
# Copyright:    Copyright © 2024 Redeyed Technologies
####################################################################

from __future__ import annotations

import logging

from typing import Optional

from pythonbytes.config import *


#---------------------------------------------------------------------------
#   LOGGER CLASS (Multiton Pattern)
#---------------------------------------------------------------------------
class Logger(logging.Logger):
	"""
    A custom logger class extending logging.Logger with a multiton pattern.
    """

	_instances = {}


	def __new__(cls, name: str, level: int = logging.INFO) -> Logger:
		"""
		Create a new instance of Logger or return an existing one (multiton pattern).

		:param name:  The name of the logger.
		:param level: The logging level (default = logging.INFO).

		:return: A Logger instance.
		"""
		# Return existing instance
		if name in cls._instances:
			return cls._instances[name]

		# Create new instance
		instance = super().__new__(cls)
		instance.__init__(name, level)
		cls._instances[name] = instance
		return instance


	def __init__(self, name: str, level: int = logging.INFO):
		"""
		Initialize the Logger class.

		:param name:  The name of the logger.
		:param level: The logging level (default = logging.INFO).
		"""
		# Prevent re-initialization of existing instances
		if name in self._instances:
			return

		# Initialize the parent logging.Logger
		super().__init__(name, level)

		# Set up handler if none exists
		if not self.hasHandlers():
			handler = logging.StreamHandler()
			handler.setLevel(level)
			self.addHandler(handler)
			self.setLevel(level)


	def __call__(self, name: str, level: int = logging.INFO) -> Logger:
		"""
		Call method to get a Logger instance (multiton access method).

		:param name:  The name of the logger.
		:param level: The logging level.

		:return: A Logger instance.
		"""
		return self.__new__(self.__class__, name, level)


	def getLogger(self, name: str, level: int = logging.INFO) -> Logger:
		"""
		Get a Logger instance (explicit multiton access method).

		:param name:  The name of the logger.
		:param level: The logging level.

		:return: A Logger instance.
		"""
		return self(name, level)




