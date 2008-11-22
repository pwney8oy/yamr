#!/usr/bin/env python

from distutils.core import setup

setup(name = "yamr",
	  version = '1.0',
	  description = "Yet Another Make Replacement - Python-scripted build tool",
	  author = "Tim Maxwell",
	  author_email = "timmaxw@gmail.com",
	  packages = ["yamr"],
	  package_dir = {"yamr":""}
	  )