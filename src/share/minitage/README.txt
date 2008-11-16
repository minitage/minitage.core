Short introduction
**********************

This documentation abstract is far from complete and can be out dated.

Please refer to: http://www.minitage.org/doc/rst  for further information.


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

History
=======

Project was initialized at Makina Corpus (http://www.makina-corpus.com), the firm 
where i am actually working. 

We have projects that need a lot of dependencies. so, in the one hand, it was hard to deploy
them in all of eterogeneous production servers. And on the other hand, setup
developers box cost us a lot of time.

So we started to use sh, inmaintenable!

We went on builout, but monolothic/extended buildout were hard to maintain too
and their impacts on already installed stuff were difficult to predict (oups
it has done rm -rf parts !).

So, i started to think to a tool that allow us to use multiple buildouts and
let us deal with dependencies. Minitage was born.

Up to 0.3, the implementation was in bash, that was well working but because
of the language, it was quite limited/restrictive. We got also problems
inherent to bash. Errors handling is painfull. It is all but user friendly.

With the 0.4, i had in mind to rewrite it in python and to integrate a lot of
QA in the build process. A lot of things were added too like metadata in
minibuilds, execution logging. I have done also a total migration to mercurial
which allow more flexibility and yes, mercurial is in python.

Credits
========

    - For the moment, i (kiorky) am the only developer of minitage.

    - It is licensed under the GPL-2 license.

    - You can have more information:

        - on http://trac.minitage.org
        - on irc : #minitage @ irc.freenode.net


