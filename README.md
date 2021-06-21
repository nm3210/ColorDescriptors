# Color Descriptors

The purpose of this package is to allow easily defined descriptor words to be
passed from one node to another without the need to pre-parse all of the
information. This requires both the sender and receiver to be in agreement
about the information being passed, but should allow for semi-complex patterns
to be sent in small packets.

Specifically, the intent is to send color modes and colors from a transmit
module to a receive module so that a transmitter can be updated with new
colors/modes, but the receiver does NOT have to be updated (granted it has all
the prerequisite information to parse the colors/modes).

Example use case:

* A transmit module defines 6 modes that it can transmit (e.g. based on the sides of a cube), and a receive module is configured to parse those values. If more, or different, modes are desired on the receive side, it  can be as easy as changing the transmit descriptor words instead of having to
    reprogram the receive module.

Package classes:

* `ColorSolid` - basic color information in 8-bit RGBW or 12-bit HSI  *hex ('cff00ff00' or 'h12c0ff1fe')
* `ColorGradient` - creation of gradients via color nodes and steps  *between nodes
* `ColorSpecial` - special color modes (rainbow, gradient, etc.)
* `ColorMode` - method to display the color (e.g. stationary, marquee, blinking, etc)
* `ColorMethod` - combination of a 'mode' and a 'color' that can be transmitted and parsed together
