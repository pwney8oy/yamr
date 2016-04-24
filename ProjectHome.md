YAMR is another build system that does approximately the same thing as Make, CMake, OMake, Ant, SConstruct, and Waf.

What YAMR does:
  * Is small but extensible
  * Only rebuilds what is necessary
  * Automatically detects dependencies for C and C++ files
  * Makes it easy to automate repetitive parts of the build process

What YAMR doesn't do:
  * No parallel building
  * Dependency calculation is done using timestamps, not hashes
  * Only builds, does not configure

How is it different:
  * YAMR is a Python module, not a tool
  * YAMR intermediate build products are not identified by names - they are anonymous Python objects.

YAMR has only been tested on Mac OS.