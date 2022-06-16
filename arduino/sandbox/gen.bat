@echo off
set /a rng=%RANDOM% * 127 / 32768
echo #pragma once > random_key.h
echo const uint8_t eeprom_key = >> random_key.h
echo %rng% >> random_key.h
echo ; >> random_key.h