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
import weakref
import threading
import traceback

from typing import Optional, Any
from logging import Filterer

from pythonbytes.config import *


_lock = threading.RLock()
_handlers = weakref.WeakValueDictionary()
_handlerList = []

#---------------------------------------------------------------------------
#   THREAD FUNCTIONS
#---------------------------------------------------------------------------
def _acquireLock() -> None:
	"""
	Acquire the global logging lock to ensure thread-safe operations.

	This should be released with _releaseLock() after the operation is complete.
	"""
	if _lock:
		_lock.acquire()


def _releaseLock() -> None:
	"""
	Release the global logging lock to allow other threads to proceed.

	This should be called after _acquireLock() when the operation is complete.
	"""
	if _lock:
		_lock.release()


#---------------------------------------------------------------------------
#   HELPER FUNCTIONS
#---------------------------------------------------------------------------
def _removeHandlerRef(weakref_ref: weakref.ref) -> None:
	"""
	Remove a weak reference to a handler from the global _handlerList.

	This is called when the handler is garbage collected.

	:param weakref_ref: The weak reference to the handler.
	"""
	global _handlerList
	_acquireLock()
	try:
		_handlerList.remove(weakref_ref)
	except ValueError:
		pass  # The handler was already removed or never existed
	finally:
		_releaseLock()


def _addHandlerRef(handler: Handler) -> None:
	"""
	Add a reference to the handler in the global _handlerList for cleanup on shutdown.

	:param handler: The Handler instance to add.
	"""
	_acquireLock()
	try:
		_handlerList.append(weakref.ref(handler, _removeHandlerRef))
	finally:
		_releaseLock()


def _checkLevel(level: int) -> int:
	"""
	Check if the provided logging level is valid.

	:param level: The logging level to check.

	:return: The validated logging level.
	"""
	if isinstance(level, int):
		return level
	elif isinstance(level, str):
		if level not in logging._nameToLevel:
			raise ValueError(f"Invalid logging level: {level}. Must be a valid string or integer.")
		return logging._nameToLevel[level]
	else:
		raise ValueError(f"Invalid logging level: {level}. Must be an integer or a valid string.")


_defaultFormatter = logging.Formatter()


#---------------------------------------------------------------------------
#   HANDLER CLASSES (Multiton Pattern)
#---------------------------------------------------------------------------
class Handler(logging.Handler):
	"""
	A custom logging handler class extending logging.Filterer with a multiton pattern.
	"""

	_instances = {}

	_lock = threading.RLock()


	def __new__(cls, name: str, level: int = logging.NOTSET) -> Handler:
		"""
		Create a new instance of Handler or return an existing one (multiton pattern).

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).

		:return: A Handler instance.
		"""

		with cls._lock:
			if name not in cls._instances:
				# Create new instance
				instance = super(Handler, cls).__new__(cls)
				instance.__init__(name, level)
				cls._instances[name] = instance

			return cls._instances[name]


	def __init__(self, name: str, level: int = logging.NOTSET, formatter: Optional[logging.Formatter] = None):
		"""
		Initialize the Handler class.

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).
		"""
		# Prevent re-initialization of existing instances
		if name in self._instances:
			return

		# Initialize the parent logging.Filterer
		logging.Filterer.__init__(self)

		self._name = name
		self.level = _checkLevel(level)
		self.formatter = formatter
		self._closed = False

		# Add the handler to the global _handlerList (for cleanup on shutdown)
		_addHandlerRef(self)
		self.createLock()


	def __call__(self, record: logging.LogRecord) -> bool:
		"""
		Make the handler callable - directly handle a log record

		This allows the handler to be used as a callable object that
		processes log records directly.  Useful for functional programming
		patterns or when the handler needs to be passed as a callback.

		Args:
			record (logging.LogRecord): The log record to process

		Returns:
			Thr result of handle(record) - the log record if it was emitted,
			or False if it was filtered out.
		"""
		return self.handle(record) # type: ignore


	def __repr__(self):
		"""
		Return a string representation of the Handler instance.
		"""
		level = logging.getLevelName(self.level)
		return '<%s (%s)>' % (self.__class__.__name__, level)


	@classmethod
	def getHandler(cls, name: str, level: int = logging.NOTSET) -> Handler:
		"""
		Get a Handler instance (explicit multiton access method).
		"""
		return cls(name, level)

	@classmethod
	def clearInstances(cls) -> None:
		"""
		Clear all instances of the Handler class.
		"""
		with cls._lock:
			cls._instances.clear()
			global _handlerList
			_handlerList.clear()

	@classmethod
	def countInstances(cls) -> int:
		"""
		Count the number of cached instances
		"""
		with cls._lock:
			return len(cls._instances)



class StreamHandler(logging.StreamHandler):
	"""
	A custom stream handler class extending logging.StreamHandler with a multiton pattern.
	"""

	_instances = {}
	_lock = threading.RLock()
	terminator = "\n"

	def __new__(cls, name: str, level: int = logging.NOTSET, stream: Optional[object] = None) -> StreamHandler:
		"""
		Create a new instance of StreamHandler or return an existing one (multiton pattern).

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).
		:param stream: The stream to log to (default = None, which uses sys.stdout).

		:return: A StreamHandler instance.
		"""

		if name in cls._instances:
			return cls._instances[name]

		with cls._lock:
			if name not in cls._instances:
				# Create new instance
				instance = super(StreamHandler, cls).__new__(cls)
				cls._instances[name] = instance

			return instance


	def __init__(self, name: str, level: int = logging.NOTSET, stream: Optional[object] = None):
		"""
		Initialize the StreamHandler class.

		:param name:   The name of the handler.
		:param level:  The logging level (default = logging.NOTSET).
		:param stream: The stream to log to (default = None, which uses sys.stdout).
		"""
		if name in self._instances:
			return

		if stream is None:
			stream = sys.stdout

		if name not in self._instances:
			super().__init__(stream)
			self._name = name
			self.setLevel(_checkLevel(level))
			self._closed = False
			self._instances[name] = self


	def __call__(self, record: logging.LogRecord) -> bool:
		"""
		Make the handler callable - directly handle a log record.

		This allows the handler to be used as a callable object that
		processes log records directly. Useful for functional programming
		patterns or when the handler needs to be passed as a callback.

		:param record: (logging.LogRecord): The log record to process.

		:return: The result of handle(record) - the log record if it was
				 emitted, or False if it was filtered out.
		"""
		return self.handle(record)


	@classmethod
	def getHandler(cls, name: str, level: int = logging.NOTSET, stream: Optional[object] = None) -> StreamHandler:
		"""
		Get a StreamHandler instance (explicit multiton access method).

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).
		:param stream: The stream to log to (default = None, which uses sys.stdout).

		:return: A StreamHandler instance.
		"""
		return cls(name, level, stream)


	@classmethod
	def clearInstances(cls) -> None:
		"""
		Clear all instances of the StreamHandler class.
		"""
		with cls._lock:
			cls._instances.clear()
			global _handlerList
			_handlerList.clear()


	@classmethod
	def countInstances(cls) -> int:
		"""
		Count the number of cached instances of the StreamHandler class.

		:return: The number of instances.
		"""
		with cls._lock:
			return len(cls._instances)



class FileHandler(logging.FileHandler):
	"""
	A custom file handler class extending logging.FileHandler with a multiton pattern.
	"""

	_instances = {}
	_lock = threading.RLock()

	def __new__(cls, name: str, level: int = logging.NOTSET, filename: str = "logfile.log",
			 	mode: str = 'a', encoding: Optional[str] = None, delay: bool = False,
				errors: Optional[str] = None) -> FileHandler:
		"""
		Create a new instance of FileHandler or return an existing one (multiton pattern).

		:param name:     The name of the handler.
		:param level:    The logging level (default = logging.NOTSET).
		:param filename: The name of the file to log to (default = "logfile.log").
		:param mode:     The mode in which to open the file (default = 'a').
		:param encoding: The encoding to use for the file (default = None).
		:param delay:    If True, the file is opened only when the first log message is emitted (default = False).
		:param errors:   If True, errors are ignored when opening the file (default = False).

		:return: A FileHandler instance.
		"""

		if name in cls._instances:
			return cls._instances[name]

		instance = super(FileHandler, cls).__new__(cls)

		return instance


	def __init__(self, name: str, level: int = logging.NOTSET, filename: str = "logfile.log",
				mode: str = 'a', encoding: Optional[str] = None, delay: bool = False,
				errors: Optional[str] = None):
		"""
		Initialize the FileHandler class.

		:param name:     The name of the handler.
		:param level:    The logging level (default = logging.NOTSET).
		:param filename: The name of the file to log to (default = "logfile.log").
		:param mode:     The mode in which to open the file (default = 'a').
		:param encoding: The encoding to use for the file (default = None).
		:param delay:    If True, the file is opened only when the first log message is emitted (default = False).
		:param errors:   If True, errors are ignored when opening the file (default = False).
		"""

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

		super().__init__(filename, mode, encoding, delay, errors)

		self._name = name
		self.setLevel(_checkLevel(level))
		self._closed = False
		self._instances[name] = self


	def __call__(self, record: logging.LogRecord) -> bool:
		"""
		Make the handler callable - directly handle a log record.

		This allows the handler to be used as a callable object that
		processes log records directly. Useful for functional programming
		patterns or when the handler needs to be passed as a callback.

		:param record: (logging.LogRecord): The log record to process.

		:return: The result of handle(record) - the log record if it was
				 emitted, or False if it was filtered out.
		"""
		return self.handle(record)


	@classmethod
	def getHandler(cls, name: str, level: int = logging.NOTSET, filename: str = "logfile.log",
				   mode: str = 'a', encoding: Optional[str] = None, delay: bool = False,
				   errors: Optional[str] = None) -> FileHandler:
		"""
		Get a FileHandler instance (explicit multiton access method).

		:param name:     The name of the handler.
		:param level:    The logging level (default = logging.NOTSET).
		:param filename: The name of the file to log to (default = "logfile.log").
		:param mode:     The mode in which to open the file (default = 'a').
		:param encoding: The encoding to use for the file (default = None).
		:param delay:    If True, the file is opened only when the first log message is emitted (default = False).
		:param errors:   If True, errors are ignored when opening the file (default = False).

		:return: A FileHandler instance.
		"""
		return cls(name, level, filename, mode, encoding, delay, errors)


	@classmethod
	def clearInstances(cls) -> None:
		"""
		Clear all instances of the FileHandler class.
		"""
		with cls._lock:
			cls._instances.clear()
			global _handlerList
			_handlerList.clear()


	@classmethod
	def countInstances(cls) -> int:
		"""
		Count the number of cached instances of the FileHandler class.

		:return: The number of instances.
		"""
		with cls._lock:
			return len(cls._instances)



class StdErrHandler(logging.StreamHandler):
	"""
	A custom stderr handler class extending logging.StreamHandler with a multiton pattern.
	"""

	_instances = {}
	_lock = threading.RLock()

	def __new__(cls, name: str, level: int = logging.NOTSET) -> StdErrHandler:
		"""
		Create a new instance of StdErrHandler or return an existing one (multiton pattern).

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).

		:return: A StdErrHandler instance.
		"""
		if name in cls._instances:
			return cls._instances[name]

		instance = super(StdErrHandler, cls).__new__(cls)

		return instance


	def __init__(self, name: str, level: int = logging.NOTSET):
		"""
		Initialize the StdErrHandler class.

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).
		"""

		if name in self._instances:
			return

		super().__init__(sys.stderr)

		self._name = name
		self.setLevel(_checkLevel(level))

		self._closed = False
		self._instances[name] = self


	def __call__(self, record: logging.LogRecord) -> bool:
		"""
		Make the handler callable - directly handle a log record.

		This allows the handler to be used as a callable object that
		processes log records directly. Useful for functional programming
		patterns or when the handler needs to be passed as a callback.

		:param record: (logging.LogRecord): The log record to process.

		:return: The result of handle(record) - the log record if it was
				 emitted, or False if it was filtered out.
		"""
		return self.handle(record)


	@property
	def stream(self) -> Any:
		"""
		Get the stream for this handler.

		:return: The standard error stream (sys.stderr).
		"""
		return sys.stderr

	@classmethod
	def getHandler(cls, name: str, level: int = logging.NOTSET) -> StdErrHandler:
		"""
		Get a StdErrHandler instance (explicit multiton access method).

		:param name:  The name of the handler.
		:param level: The logging level (default = logging.NOTSET).

		:return: A StdErrHandler instance.
		"""
		return cls(name, level)


	@classmethod
	def clearInstances(cls) -> None:
		"""
		Clear all instances of the StdErrHandler class.
		"""
		with cls._lock:
			cls._instances.clear()
			global _handlerList
			_handlerList.clear()


	@classmethod
	def countInstances(cls) -> int:
		"""
		Count the number of cached instances of the StdErrHandler class.

		:return: The number of instances.
		"""
		with cls._lock:
			return len(cls._instances)
