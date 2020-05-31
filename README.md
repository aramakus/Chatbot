# Python conversational/goal oriented Chatbot

This is the folder with a locally run version of my Coursera final project - chatbot and stackoverflow assistant. Original bot was deployed on AWS EC2. The bot supports a casual conversation, as well as a range of questions related to programming. The conversation may look something like this

<p align="left">
<img width=50% src="supplementary/sample_chat_small.png" alt="Featuretools" />
</p>
<p align="left">


### Running the bot

To run the program in [Docker](https://www.docker.com/get-started) a following commands should be executed in the project folder<br>
`docker build -t fastapi_conda .`<br>
`docker run -it -p 5000:5000 -v $PWD/files:/home -t fastapi_conda`<br>
or if Docker-Compose is availabale, simply `docker-compose up` (`docker-compose down --rmi all --remove-orphans` to clean everything up).
