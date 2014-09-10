#!/bin/bash

read -p 'Do you want to create users db? ' -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	echo "{}" > users.yaml
fi

read -p 'Do you want to create experiments db? ' -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	echo "{}" > experiments.yaml
fi

read -p 'Do you want to create candidates db? ' -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	echo "{}" > candidates.yaml
fi

read -p 'Do you want to create answers db? ' -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	echo "{}" > answers.yaml
fi
