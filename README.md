# ee250-final

## Instructions:
* Set up your RPi with the ultrasonic ranger on D4 and a LED on D3.

## Running the scripts:
* First, clone the repo and run `cd ee250-final; python3 -m pip install .` to install all dependencies and set up module paths.
* Launch the Discord bot with the MQTT host and port as command line args: `python3 scripts/catana_bot.py <host> <port>`
* On your RPi, run `rpi_node.py` with your Discord username and the MQTT host and port as command line args: `python3 scripts/rpi_node.py <your username> <host> <port>`

## Link to demo video:
* https://drive.google.com/file/d/1Le-p9hBEgUKTVIAEHEqqtnntRediQS29/view?usp=sharing
