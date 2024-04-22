#!/bin/bash

echo "=========================================="
echo "== Install development utilities to Go1 =="
echo "=========================================="

# Install libmsgpack (for unitree sdk python bindings)
echo
echo "--- Installing libmsgpack"
cd ~/go1_gym/msgpack-c*
cmake .
sudo cmake --build . --target install

# Build unitree sdk
echo
echo "--- Building unitree sdk
cd ~/go1_gym/unitree_legged_sdk*
sh build.sh

# Install libevent (for tmux)
echo
echo "--- Installing libevent"
cd ~/go1_gym/libevent*
sh autogen.sh
./configure
make -j4
sudo make install

# Install ncurses (for tmux)
echo
echo "--- Installing ncurses"
cd ~/go1_gym/ncurses*
./configure
make -j4
sudo make install

# Install tmux
echo
echo "--- Installing tmux"
cd ~/go1_gym/tmux*
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
