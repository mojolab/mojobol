
import os, sys

INSTALLDEPSCOMMAND = "apt install -y python3 python3-pip python3-dev ipython3 zsh git vim curl sudo wget build-essential libssl-dev net-tools openssh-server lame asterisk gcc g++ bison zlib1g openssl python-setuptools espeak"

STATUSDICT={
    "install-deps": False,
    "directory-structure": False,
    "configure-asterisk": False,
    "check-softlinks": False,
    "install-callflow": False,
}

# Try to run INSTALLDEPSCOMMAND using os.system call - if it fails print the exception
try:
    os.system(INSTALLDEPSCOMMAND)
    STATUSDICT["install-deps"] = True
except Exception as e:
    print(e)
    

# Create a soft link "/opt/mojobol" to the current directory
try:
    os.system("ln -s $(pwd) /opt/mojobol")
    STATUSDICT["directory-structure"] = True    


os.system(INSTALLDEPSCOMMAND)
