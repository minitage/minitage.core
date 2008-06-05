
Short introduction
**********************


What is minitage
=================
Minitage is a meta package manager. It's goal is to integrate build systems
or other package manager together to make them install in a 'well known'
layout. In other terms, it install its stuff in 'prefix'.

Moreover, this tool will make you forget compilation and other crazy stuff
that put your mind away from your real project needs.


What will it allow to
=====================

    - Deploy a project from start to end.
    - Reproduce the same environement everywhere (on UNIX platforms). It is
      known to work on:

        - Linux
        - MacOSX but at least OSX Leopard is required.
        - FreeBSD (not tested recently)

    - Isolate all the needed boilerplate from the host system. All stuff in
      minitage is supposed to be independant from the host base system.
      Compiled stuff is interlinked as much as possible.
    - Control all the build process.
    - Fix buildout leaks :) or at least try to.

        - Upgrades can be painful to predict
        - Offline mode is problematic
        - We can play with dependencies tree more easily


What will it never do
======================

    - The coffee
    - Windows implementation seems to be difficult. Some effort may be done
      to try but it's not the priority

Credits
========

    - For the moment, i (kiorky) am the only developer of minitage.

    - It is licensed under the GPL-2 license.

    -You can have more information:

        - on http://trac.minitage.org
        - on irc : #minitage @ irc.freenode.net


