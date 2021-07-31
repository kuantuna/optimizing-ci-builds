#!/bin/bash

inotifywait -mr $1 | grep "CREATE" | tee $2.txt
