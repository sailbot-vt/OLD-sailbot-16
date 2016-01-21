# SailBOT

[![GitHub license](https://img.shields.io/github/license/VT-SailBOT/sailbot.svg)]()

## Introduction

SailBOT is a competition to build and program an autonomous sailing robot capable of navigating obstacles in a dynamic, real-world sailing environment. The robot uses on-board sensor input to effectively sail towards marked latitude and longitude coordinate locations and avoid obstacles.

The majority of code for SailBOT is written in Python due to vast library support. All code is designed to run on the boat on a [Raspberry Pi](http://www.raspberrypi.org/). As such, the code also utilizes the [Tornado web server API](http://www.tornadoweb.org/) to host a landing page containing a map view of the boat's location and real-time stats of the boat as read-in by sensors and sent through a web socket. Ideally, this is the primary way of interfacing / communicating with the boat.

The goal of the project is to build upon the SailBOT foundation laid in previous years. It should be extensible, modular, verbose, and minimalistic.

