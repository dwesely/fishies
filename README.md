# fishies
Game of chomping fishies

**background and references**

This game was built on top of the Arcade v2.0.9 package for Python, using Python 3.7.1.

I used the procedural_caves_cellular.py example (available here: http://arcade.academy/examples/procedural_caves_cellular.html#procedural-caves-cellular) as a basis for the map and the movement.

The tiles referenced are from this top-down tileset: https://opengameart.org/content/topdown-tileset

The sprites referenced are from this asset pack: https://www.kenney.nl/assets/fish-pack

The maps are generated and get larger after each level. The fishies move randomly, and there are more each level.

**Controls**

WASD or arrow keys to move

M to teleport back to the center of the map

Y to go to the next level (available only after all the fishies are chomped

**Known Issues**

The game is not optimized at all, and slows down after not many levels

Your fish jumps after a collision, which can send it out of the tank. Press "M" to get back to the middle.

The sprites are just rotated, so sometimes they look upside down.

The map might trap some fishies in rooms instead of everything being connected. Exploiting the collision-jump bug is just about the funnest thing about the game right now, so I don't plan on fixing that.
