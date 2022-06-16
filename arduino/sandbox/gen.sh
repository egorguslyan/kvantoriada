#!/bin/bash
RANDOM=$(date +%s%N | cut -b10-19)
cat "#pragma once" > random_key.h
cat "const uint8_t eeprom_key" = >> random_key.h
cat "${RANDOM}" >> random_key.h
cat ";" >> random_key.h