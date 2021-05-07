# ee250-final
Catana is a Discord-based cat helper that assists in automating and simplifying the feeding process.

## Setup:
* Set up your RPi with the ultrasonic ranger on D4 and a LED on D3. You will also need a single servo motor on port 17.

## Running the scripts:
* First, clone the repo and run `cd ee250-final; python3 -m pip install .` to install all dependencies and set up module paths.
* Launch the Discord bot with the MQTT host and port as command line args: `python3 scripts/catana_bot.py <host> <port>`
* On your RPi, run `rpi_node.py` with your Discord username and the MQTT host and port as command line args: `python3 scripts/rpi_node.py <your username> <host> <port>`

## Key questions
<b>Motivation</b>: Not particularly profound, but this product simply helps alleviate the burden on a user when it comes to scheduled feedings of their feline companion. Both being cat owners ourselves, this choice was motivated by its readily apparent applicability in our day to day lives.

<b>Ethics</b>: The ethical implications of such a product are not too far reaching, but one potential issue is ensuring foolproof performance (especially when a customer cannot be there to manually check that feeding is working as scheduled). This is in part why we have chosen to implement a system “check,” i.e. an automated real-time image capture system that notifies the user of when the cat has actually approached the food bowl to eat. 

<b>Economics</b>: We’ve designed an extremely low cost prototype (using cardboard and common household plastic, at the cost of precision), but anticipate that a design with sturdier materials would not be much more expensive. In future development/deployment, it could potentially be an affordable and viable automated, hands off feeding system for any individuals with pets.

<b>Data analysis</b>: Data flow in this system primarily characterizes when the feeding schedule is set and when the cat has approached the bowl (corollary: eating). A more advanced tracking of such data could drive a model to determine the best feeding times and amounts throughout the day, and carry that out in actuation. 

<b>Self-directed learning</b>: To set up our implementation, we both drew from some high level previous background knowledge on topics such as basic servo mechanics or Discord server interfacing. However, the implementation of each action required new understanding, which we were able to tease out on our own through resources available on the internet (think Stack Overflow and RPi community forums), as well as educated trial and error.

## Mechanics of implementation
Catana has an ultrasonic ranger to detect nearby objects and a USB webcam that provides automated image capture within a proximity threshold (this capture has a built-in delay so as to not spam the channel). The body includes a servo motor to release kibble into the attached cat bowl at a specified time, and an LED as a reminder to clean the litter box. Multi-node communication is achieved through the paho-mqtt Python library, as well as Discord’s Python API. 

By interfacing MQTT with Discord, we’re able to remove some of the complexity and allow anyone to set up the same system whether or not they’re familiar with MQTT. A particular design choice we made was to have each script run with the user’s Discord username because this is what allows the app to scale up beyond a single user. Instead of hard-coding the LED and feeder topics, during runtime, a User class is created per Discord channel member, and their customized topic is dynamically set. As long as the same username is passed to their RPi, the same code will work. 

Since we needed to keep track of and save information for more than one user (set feeding times, personalized topics, etc), we used object-oriented programming. This choice fits well with the Discord API, which provides the commands.Cog class as a way to organize related commands. 

## System block diagram

![Catana system](https://user-images.githubusercontent.com/55266635/117482783-b7586980-af19-11eb-9393-12bba409005f.png)

## Reflection
In the process of development, we have noted a few limitations and possible issues to address in the future:

One difficulty we ran into was incompatibility between different packages we used. Python’s schedule library was used to schedule the cat feeder to release food at set times, but schedule doesn’t work with asynchronous methods, which is what the Discord API relies on. The current fix for this is to have the Discord cog spin up a separate thread to manage the scheduler, separating it from the async Discord command methods. We’re not sure how scalable this is if we were to implement other features based on scheduling times; something to look into in the future is to completely separate the scheduled actions to a different node. 

Some additions we’d like to make are potentially implementing both image processing and voice recognition. Specifically, we would like to improve the image publishing by detecting a cat as a prerequisite for image capture, so as to avoid false readings where a person might accidentally get too close to the sensor. For voice recognition, we would like the RPi to be able to recognize certain voice commands to activate the feeder and toggle the LED. We weren’t able to include that in this project due to time constraints and lack of equipment - only one of us had a webcam, and the other had a microphone so it was difficult coordinating the software development and testing. 


## Link to demo video:
* https://drive.google.com/file/d/1LrGXez5aX4buRPkPfVqsNW1muaPkPUAs/view?usp=sharing
