# Scanner Paper Artifacts
This goal of this repository is to provide implementation details for different sections of the paper.

## Captcha Solver
The Captcha solver is a trained object detection model able to crack differnet Captcha schemes.

## Dataset
Dataset directory includes differnet Captcha schemes used for the train and test process of the Captcha solver. We have included the data we generated ourselves and added links to those from other research.

## Case-Study 1
In the first case study, we have used the Captcha solver on a sample login page and successfully logged into the page.

## Case-Study 2
The second case study shows that how the same crawler can be minimally modified which enables is to exploit a sample java application using the log4j vulnerability.

## In-Application Sensors
This directory includes the codes that can be used to track user interactions with a web page. We use a client-server architecture where the tracker works as the client and sends the recorded events to the server though a web socket. 

## Custom Crawler
Custom crawler includes different scenarios we have implemented to interact with a webpage as a bot. The results are then used to compare with human interactions and other bots.