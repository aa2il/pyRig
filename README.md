# pyRig

GUI for remote rig and rotor control.
      
![Screen Shot]( Docs/pyRig.png)

# Installation under Linux using uv:

0) This seems to be the easiest/best solution.  uv is relatively new and is fast and easy compared to other solutions.  However, it does have a a problem running some tkinter gui apps with recent versions of python.  Of course, to use uv, you need to have it installed on your system:

        curl -LsSf https://astral.sh/uv/install.sh | sh      
        rehash     

1) Clone gitub repositories

        cd
        mkdir Python
        cd Python
        git clone https://github.com/aa2il/pyRig
        git clone https://github.com/aa2il/libs
        git clone https://github.com/aa2il/data
      
2) One of the features of uv is that the virtual environment (a.k.a. container or sandbox) is included in the github repository.  You should NOT have to do anything since uv will install the environment and required packages the first time you run any of these codes.

   For the record, here is how I set up the environment:

        cd ~/Python/pyRig
        uv init --python 3.12
        rm main.py
        uv add -r requirements.txt
   
   *** There is a problem with python 3.13 & tk under uv - use 3.12 until we figure this out ***
   *** It is a known issue and hopefully will get resolved b4 we fall too far behind ***
   
        https://github.com/astral-sh/python-build-standalone/issues/146  7036  and  11942
   
3) Make sure its executable and set PYTHON PATH so os can find libraries:

        cd ~/Python/pyKeyer
        chmod +x pyKeyer.py start start_cw

        - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
        - Under bash:      export PYTHONPATH="$HOME/Python/libs"
   
4) Bombs away:

        uv run pyKeyer.py
        uv run paddling.py
        uv run qrz.py

   or, 

        ./pyKeyer.py
        ./paddling.py
        ./qrz.py

# Installation under Linux:

1) Uses python3 and tkinter
2) Clone gitub pyRig, libs and data repositories
    - cd
    - mkdir Python
    - cd Python
    - git clone https://github.com/aa2il/pyRig
    - git clone https://github.com/aa2il/libs
    - git clone https://github.com/aa2il/data
3) Install packages needed for pyRig:
   - cd ~/Python/pyRig
   - pip3 install -r requirements.txt
4) Make sure its executable:
   - chmod +x pyRig.py start start_cw
5) Set PYTHON PATH so os can find libraries:
   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"
6) Bombs away:
   - ./pyRig.py

# Installation under Mini-conda:

0) Good video:  https://www.youtube.com/watch?v=23aQdrS58e0&t=552s

1) Point browser to https://docs.conda.io/en/latest/miniconda.html
2) Download and install latest & greatest Mini-conda for your particular OS:
   - I used the bash installer for linux
   - As of July 2023: Conda 23.5.2 Python 3.11.3 released July 13, 2023
   - cd ~/Downloads
   - bash Miniconda3-latest-Linux-x86_64.sh
   - Follow the prompts

   - If you'd prefer that conda's base environment not be activated on startup, 
      set the auto_activate_base parameter to false: 

      conda config --set auto_activate_base false

   - To get it to work under tcsh:
       - bash
       - conda init tcsh
       - This creates ~/.tcshrc - move its contents to .cshrc if need be
       - relaunch tcsh and all should be fine!
       - Test with:
           - conda list

3) Create a working enviroment for ham radio stuff:
   - Check which python version we have:
       - conda list   
   - conda create --name aa2il python=3.11

   - To activate this environment, use:
       - conda activate aa2il
   - To deactivate an active environment, use:
       - conda deactivate

   - conda env list
   - conda activate aa2il

4) Clone gitub pyRig, libs and data repositories:
    - cd
    - mkdir Python
    - cd Python
    - git clone https://github.com/aa2il/pyRig
    - git clone https://github.com/aa2il/libs
    - git clone https://github.com/aa2il/data

5) Install packages needed by pyRig:
   - cd ~/Python/pyRig
   - pip3 install -r requirements.txt

6) Set PYTHON PATH so os can find libraries:
   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"

7) To run pyRig, we need to specify python interpreter so it doesn't run in
   the default system environment:
   - cd ~/Python/pyRig
   - conda activate aa2il
   - python pyRig.py

8) Known issues using this (as of July 2023):
   - None

# Installation for Windoz:

1) Best bet is to use mini-conda and follow the instructions above.
2) If you want/need a more recent binary, email me.
