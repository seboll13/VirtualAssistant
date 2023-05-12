# VirtualAssistant
A personalised virtual assistant using openAI's GPT-3.5 API.

### Usage
1. Clone the repository
2. Create a virtual environment using the following syntax: ```python3 -m venv py311_*```, where * is the name of your virtual environment. Note that the project is made to work with Python 3.11.
3. Activate the virtual environment using the following syntax: ```source py311_*/bin/activate```
4. Install the requirements in the root directory with: ```pip3 install -r requirements.txt```
5. Depending on your configuration, you may need to install ```portaudio```, ```mpg123``` and ```flac```.
6. Execute the program with: ```python3 main.py``` and give your computer access to your microphone. Everything should then work.

### Home assistant (with IKEA Tradfri)
In order for your virtual assistant to be able to interact with your home, you will need to proceed to a few installations and configurations. The process is described below.
1. Install ```pytradfri``` by typing ```pip install pytradfri``` in your terminal.
2. Install ```libcoap``` by typing ```pip install aiocoap``` in your terminal.
3. Run the command ```python3 -i -m pytradfri IP```, where ```IP``` is the IP address of your gateway. The first time this command executes, you will have to enter the security code of your gateway, which can be found on the back of it.
4. From there on, follow the example commands you can use to test your connection to the gateway. If everything works, you can now use the virtual assistant to control your lights.

### Troubleshooting
One common issue with troubleshooting the installation of the pytradfri package can be due to the libcoap library being not properly installed. To deal with this problem, follow the steps below.
1. Go to https://github.com/obgm/libcoap and download the latest release of the library.
2. At the root of the directory, type ```./autogen.sh``` and then ```./configure --disable-documentation --disable-shared```.
3. Finally, type in ```make``` and ```sudo make install```.

If you get an error during the process, you may need to install ```autoconf, automake``` and ```libtool``` using ```brew``` on mac or ```apt-get``` on linux. After that, repeat the process from step 2.