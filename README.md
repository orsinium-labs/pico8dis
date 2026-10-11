# pico8dis

Disassembler for [PICO-8](https://www.lexaloffle.com/pico-8.php) binary distribution. Given a JS file of a game, extracts its source code and spritesheet according to the [PICO-8 data format](https://pico-8.fandom.com/wiki/P8PNGFileFormat).

## Usage

```bash
git clone https://github.com/orsinium-labs/pico8dis
cd pico8dis
cat some_game.js | python3 pico8dis --output some_game
cat some_game/code.lua
```
