#!/bin/bash

echo "=========================================="
echo "== Install development utilities to Go1 =="
echo "=========================================="

# Install libevent
echo
echo "--- Installing libevent"
cd ../../libevent*
sh autogen.sh
./configure
make -j4
sudo make install

# Install ncurses
echo
echo "--- Installing ncurses"
cd ../../ncurses*
./configure
make -j4
sudo make install

# Install tmux
echo
echo "--- Installing tmux"
cd ../../tmux*
# Prevent infinite loop with modify times...
touch Makefile.am
touch configure.ac
sh autogen.sh
./configure
make -j4
sudo make install
echo "set -g mouse on" > ~/.tmux.conf

# Modify LD_LIBRARY_PATH so tmux can find ncurses and libevent
echo
echo "--- Add LD_LIBRARY_PATH modification to bashrc"
echo "# Modify LD_LIBRARY_PATH to find user installed libraries" >> ~/.bashrc
echo "LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/usr/local/lib" >> ~/.bashrc
