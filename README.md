# Slipper

> This stuff is under development. Not functional yet.

Slipper is core of task orchestration systems.

## Problem 

Many distributed systems needs to run expensive tasks. This in itself is not 
a problem. However, very often, these tasks are dependent on one another. 
Moreover, the execution of one task may depend on several others.

*Slipper* is dead simple solution. It uses "contracts" to watch over reports 
in AMQP queue. When contract complete or fail - *Slipper* send report.

For example. We need an archive of files that are downloaded from external 
sources. Let's raise bets: each file must be converted into two formats.

## Contracts and points

Contracts holds Points. Point is simple thing. Minimal info for Point is
hash (SHA1) from message data which used as Point ID. Contract ID is hash 
too which calculated from sorted point IDs.


