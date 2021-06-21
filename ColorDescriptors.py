"""
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
    A transmit module defines 6 modes that it can transmit (e.g. based on the
    sides of a cube), and a receive module is configured to parse those values.
    If more, or different, modes are desired on the receive side, it can be as
    easy as changing the transmit descriptor words instead of having to
    reprogram the receive module.
    
    
Package classes:
    ColorSolid - basic color information in 8-bit RGBW or 12-bit HSI hex ('cff00ff00' or 'h12c0ff1fe')
    ColorGradient - creation of gradients via color nodes and steps between nodes
    ColorSpecial - special color modes (rainbow, gradient, etc.)
    ColorMode - method to display the color (e.g. flat color, blinking, etc)
    
"""

### Import modules
from math import pi, sqrt, cos, acos, atan, radians, degrees

### Initialize classes
# Base color class for object checking
class BaseColor(object):
    pass

# Color class to store RGB/W or HIS values and convert from/to a hex string
class ColorSolid(BaseColor):
    def __init__(self, red=None, green=None, blue=None, white=None, hue=0, saturation=1.0, intensity=1.0, enableWhite=True):
        # Pre allocate private variables
        self._red        = None # [0 - 255]
        self._green      = None # [0 - 255]
        self._blue       = None # [0 - 255]
        self._white      = None # [0 - 255]
        self._hue        = None # [0 - 360]
        self._saturation = None # [0.0 - 1.0]
        self._intensity  = None # [0.0 - 1.0]
        self._enableWhite = enableWhite # [bool] is there an additional white LED installed?

        self._inputType  = None # configured automatically
        
        ### Check what values where input
        # RGB[W] input
        if red is not None and green is not None and blue is not None:
            self._red   = red
            self._green = green
            self._blue  = blue
            self._inputType = 'rgb'

            if self._enableWhite:
                self._inputType = 'rgbw'
                self._white = white
                
            # Convert RGB[W] input to HSI
            if self._enableWhite:
                self._hue, self._saturation, self._intensity = ColorSolid.rgbw2hsi(red,green,blue,white)
            else:
                self._hue, self._saturation, self._intensity = ColorSolid.rgb2hsi(red,green,blue)
        
        # HSI input
        elif hue is not None and saturation is not None and intensity is not None:
            self._hue = hue
            self._saturation = saturation
            self._intensity = intensity
            self._inputType = 'hsi'
            
            # Convert HSI input to RGB[W]
            if not self._enableWhite:
                self._red, self._green, self._blue = ColorSolid.hsi2rgb(hue,saturation,intensity)
            else:
                self._red, self._green, self._blue, self._white = ColorSolid.hsi2rgbw(hue,saturation,intensity)
        
        else:
            print('Must input either rgb[w] or hsi; output object not configured correctly')
            
    def copy(self, forceMode=None): # no copy module in circuitpython, so this'll have to do
        if (forceMode is not None and forceMode=='rgb') or self._inputType=='rgb':
            return type(self)(red=self.red, green=self.green, blue=self.blue)
        elif (forceMode is not None and forceMode=='rgbw') or self._inputType=='rgbw':
            return type(self)(red=self.red, green=self.green, blue=self.blue, white=self.white)
        elif (forceMode is not None and forceMode=='hsi') or self._inputType=='hsi':
            return type(self)(hue=self.hue, saturation=self.saturation, intensity=self.intensity)

    def toString(self, forceMode=None): # "crrggbb[ww]" or "hhhhsssiii[w]" in hex
        if (forceMode is not None and forceMode=='rgb') or self._inputType=='rgb':
            return "c{:02x}{:02x}{:02x}".format(round(self.red),round(self.green),round(self.blue))
        elif (forceMode is not None and forceMode=='rgbw') or self._inputType=='rgbw':
            white = self.white if self.white is not None else 0
            return "c{:02x}{:02x}{:02x}{:02x}".format(round(self.red),round(self.green),round(self.blue),round(white))
        elif (forceMode is not None and forceMode=='hsi') or self._inputType=='hsi':
            hue = self.hue % 360 if not self.hue == 360 else 360 # allow '360' output, but mod otherwise, allowing for full circle interpolations
            if self._enableWhite == True: # add 'w' to the end to indicate this is a white-enabled hsi
                return "h{:03x}{:03x}{:03x}w".format(round(hue),round(self.saturation*255),round(self.intensity*255))
            else:
                return "h{:03x}{:03x}{:03x}".format(round(hue),round(self.saturation*255),round(self.intensity*255))
    
    @property
    def red(self):
        return self._red
    @red.setter
    def red(self, valIn):
        self._red = valIn
        if self._enableWhite:
            self._inputType = 'rgbw'
            self._hue, self._saturation, self._intensity = ColorSolid.rgbw2hsi(self.red,self.green,self.blue,self.white)
        else:
            self._inputType = 'rgb'
            self._hue, self._saturation, self._intensity = ColorSolid.rgb2hsi(self.red,self.green,self.blue)
        
    @property
    def green(self):
        return self._green
    @green.setter
    def green(self, valIn):
        self._green = valIn
        if self._enableWhite:
            self._inputType = 'rgbw'
            self._hue, self._saturation, self._intensity = ColorSolid.rgbw2hsi(self.red,self.green,self.blue,self.white)
        else:
            self._inputType = 'rgb'
            self._hue, self._saturation, self._intensity = ColorSolid.rgb2hsi(self.red,self.green,self.blue)
        
    @property
    def blue(self):
        return self._blue
    @blue.setter
    def blue(self, valIn):
        self._blue = valIn
        if self._enableWhite:
            self._inputType = 'rgbw'
            self._hue, self._saturation, self._intensity = ColorSolid.rgbw2hsi(self.red,self.green,self.blue,self.white)
        else:
            self._inputType = 'rgb'
            self._hue, self._saturation, self._intensity = ColorSolid.rgb2hsi(self.red,self.green,self.blue)
        
    @property
    def white(self):
        if self._enableWhite == True:
            return self._white
        else:
            return None
    @white.setter
    def white(self, valIn):
        if self._enableWhite == False and valIn is not None:
            print("Unable to configure white color; enable the white LED first (via obj.enableWhite)")
            return
        self._white = valIn
        self._inputType = 'rgbw'
        self._hue, self._saturation, self._intensity = ColorSolid.rgbw2hsi(self.red,self.green,self.blue,self.white)
        
    @property
    def hue(self):
        return self._hue
    @hue.setter
    def hue(self, valIn):
        self._hue = valIn
        self._inputType = 'hsi'
        if self._enableWhite:
            self._red, self._green, self._blue, self._white = ColorSolid.hsi2rgbw(self.hue,self.saturation,self.intensity)
        else:
            self._red, self._green, self._blue = ColorSolid.hsi2rgb(self.hue,self.saturation,self.intensity)
        
    @property
    def saturation(self):
        return self._saturation
    @saturation.setter
    def saturation(self, valIn):
        self._saturation = valIn
        self._inputType = 'hsi'
        if self._enableWhite:
            self._red, self._green, self._blue, self._white = ColorSolid.hsi2rgbw(self.hue,self.saturation,self.intensity)
        else:
            self._red, self._green, self._blue = ColorSolid.hsi2rgb(self.hue,self.saturation,self.intensity)
        
    @property
    def intensity(self):
        return self._intensity
    @intensity.setter
    def intensity(self, valIn):
        self._intensity = valIn
        self._inputType = 'hsi'
        if self._enableWhite:
            self._red, self._green, self._blue, self._white = ColorSolid.hsi2rgbw(self.hue,self.saturation,self.intensity)
        else:
            self._red, self._green, self._blue = ColorSolid.hsi2rgb(self.hue,self.saturation,self.intensity)
        
    @property
    def enableWhite(self):
        return self._enableWhite
    @enableWhite.setter
    def enableWhite(self, valIn):
        self._enableWhite = valIn

    def __repr__(self):
        return self.toString()
    
    def __eq__(self, other):
        if not isinstance(other, ColorSolid):
            return NotImplemented # don't attempt to compare against unrelated types
        return self.toString() == other.toString()
        
    @staticmethod
    def parse(strIn):
        if type(strIn) != str or len(strIn)<=1:
            raise Exception('Invalid input, needs to be an input string')
        # Check for first character
        if strIn.lower().startswith('c'): # RGB color
            # Check for valid input
            if not (len(strIn) == 6+1 or len(strIn) == 8+1):
                print('Invalid input length, rgb[w] must be 6 or 8 characters')
                return None
            # Split string, convert to int, and return a new object
            splitStr = [int(strIn[i:i+2],16) for i in range(1, len(strIn), 2)]
            if len(splitStr) == 3:
                return ColorSolid(*splitStr, enableWhite=False)
            elif len(splitStr) == 4:
                return ColorSolid(*splitStr)
        elif strIn.lower().startswith('h') and strIn.lower().endswith('w'): # HSI with white LED enabled
            if not len(strIn) == 10+1:
                print('Invalid input length, hsi[w] must be 9 characters')
                return None
            strIn = strIn[0:-1] # remove the last 'w'
            # Split string, convert to int, and return a new object
            splitStr = [int(strIn[i:i+3],16) for i in range(1, len(strIn), 3)]
            return ColorSolid(hue=splitStr[0], saturation=splitStr[1]/255, intensity=splitStr[2]/255, enableWhite=True)
        elif strIn.lower().startswith('h') and not strIn.lower().endswith('w'): # HSI with the white LED disabled
            # Check for valid input
            if not len(strIn) == 9+1:
                print('Invalid input length, hsi must be 9 characters')
                return None
            # Split string, convert to int, and return a new object
            splitStr = [int(strIn[i:i+3],16) for i in range(1, len(strIn), 3)]
            return ColorSolid(hue=splitStr[0], saturation=splitStr[1]/255, intensity=splitStr[2]/255, enableWhite=False)
        else:  
            print('Unable to parse input string ''%s''' % strIn)
            return None
        
    @staticmethod
    def rgbw2hsi(red, green, blue, white):
        # Seemingly done here in this ColorDescriptors::ColorSolid code for the first time, for all I can tell!
        # Convert all input none's to zeros
        if red is None: red = 0
        if green is None: green = 0
        if blue is None: blue = 0
        if white is None: white = 0
        
        # Check for no-white condition
        if white == 0:
            return ColorSolid.rgb2hsi(red, green, blue)
        
        # Calculate the saturation and intensity
        saturation = (red + green + blue) / (red + green + blue + white) # based on the amount of white
        intensity = (red + green + blue + white) / 255 # up to x1.0 for each LED
        
        # Check if all the colors are zero
        if red == 0 and green == 0 and blue == 0:
            return 0, saturation, intensity # hue doesn't matter!
            
        # Check if all-but-one of the colors are zero
        if red == 0 and green == 0:
            hue = 240 # in color-wheel degrees, blue
            return hue, saturation, intensity
        if green == 0 and blue == 0:
            hue = 0 # in color-wheel degrees, red
            return hue, saturation, intensity
        if blue == 0 and red == 0:
            hue = 120 # in color-wheel degrees, green
            return hue, saturation, intensity
            
        # Check if just one color is zero (often generated via the hsi2rgbw)
        if red == 0:
            hue = 2 * atan((2*sqrt(pow(blue,2) - blue * green + pow(green,2)) - 2*green + blue) / (sqrt(3) * blue))
            hue = hue + (2/3 * pi)
            hue = hue * 180/pi;
            return hue, saturation, intensity
        if green == 0:
            hue = 2 * atan((2*sqrt(pow(blue,2) - blue * red + pow(red,2)) - 2*blue + red) / (sqrt(3) * red))
            hue = hue + (4/3 * pi)
            hue = hue * 180/pi;
            return hue, saturation, intensity
        if blue == 0:
            hue = 2 * atan((2*sqrt(pow(green,2) - green * red + pow(red,2)) - 2*red + green) / (sqrt(3) * green))
            hue = hue * 180/pi;
            return hue, saturation, intensity
        
        # If none of the colors are zero, the solution will be similar to the
        # simple rgb2hsi case, except with modified intensity and saturation
        
        # Convert to range 0-1:
        r = red / 255.0
        g = green / 255.0
        b = blue / 255.0
        
        hue = acos((r-g + r-b)/2 * sqrt((r-g)*(r-g) + (r-b)*(g-b)));
        if blue > green:
            hue = 2*pi - hue; # if b > g, hue = 360 degrees
        hue = hue * 180/pi;
        
        # Calculate saturation
        intensity = (red + green + blue) / (255 * 3)
        saturation = 1.0 - min(r, min(g, b))/intensity # rgb saturation
        saturation = saturation * (255 - white)/255 # scale with white value
        
        # Recalculate intensity based on all colors again
        intensity = (red + green + blue + white) / 255
        return hue, saturation, intensity
        
    @staticmethod
    def rgb2hsi(red, green, blue):
        # From: https://github.com/tigoe/ColorConverter/blob/b18d355863483ec61400a2f671136dbccc6ac2ac/src/ColorConverter.cpp
        # Convert input values to range 0-1:
        r = red / 255.0
        g = green / 255.0
        b = blue / 255.0
        
        # find minimum and maximum of the three:
        minimum = min(r, min(g, b))
        maximum = max(r, max(g, b))
        
        # find intensity:
        intensity = (r + g + b) / 3.0
        
        # find saturation:
        if intensity == 0:
            saturation = 0
        else:
            saturation = 1.0 - minimum/intensity
        
        # find hue:
        hue = acos((r-g + r-b)/2 * sqrt((r-g)*(r-g) + (r-b)*(g-b)));
        # if b > g, hue = 360 degrees - hue:
        if b > g:
            hue = 2*pi - hue;
        #  if all colors equal, hue is irrelevant:
        if minimum == maximum:
            hue = 0;
        
        # convert to degrees
        hue = hue * 180/pi;

        intensity = (r + g + b)
        return hue, saturation, intensity
        
    @staticmethod
    def hsi2rgbw(hue, saturation, intensity):
        # From: http://blog.saikoled.com/post/44677718712/how-to-convert-from-hsi-to-rgb-white
        hue = hue % 360 # cycle H around to 0-360 degrees
        hue = pi*hue/180 # Convert to radians.
        
        # Clamp S to interval [0,1] and I to interval [0,4] (because RBW can be full 'white' too)
        saturation = (saturation if saturation<1 else 1) if saturation>0 else 0
        intensity = (intensity if intensity<4 else 4) if intensity>0 else 0

        if hue < (2/3 * pi): # First third
            r = saturation*intensity/3*(1+   cos(hue)/cos((pi/3)-hue))  * 255
            g = saturation*intensity/3*(1+(1-cos(hue)/cos((pi/3)-hue))) * 255
            b = 0
        elif hue < (4/3 * pi): # Second third
            hue = hue - (2/3 * pi)
            r = 0
            g = saturation*intensity/3*(1+   cos(hue)/cos((pi/3)-hue))  * 255
            b = saturation*intensity/3*(1+(1-cos(hue)/cos((pi/3)-hue))) * 255
        else: # Third section
            hue = hue - (4/3 * pi)
            r = saturation*intensity/3*(1+(1-cos(hue)/cos((pi/3)-hue))) * 255
            g = 0
            b = saturation*intensity/3*(1+   cos(hue)/cos((pi/3)-hue))  * 255
            
        w = (1-saturation)*intensity * 255
        
        # Clamp rgbw to valid ranges
        r = (r if r<255 else 255) if r>0 else 0
        g = (g if g<255 else 255) if g>0 else 0
        b = (b if b<255 else 255) if b>0 else 0
        w = (w if w<255 else 255) if w>0 else 0
        
        return r, g, b, w
        
    @staticmethod
    def hsi2rgb(hue, saturation, intensity):
        # From: https://blog.saikoled.com/post/43693602826/why-every-led-light-should-be-using-hsi
        hue = hue % 360 # cycle H around to 0-360 degrees
        hue = pi*hue/180 # Convert to radians.
        
        # Clamp S to interval [0,1] and I to interval [0,3] (because RBW can be full 'white' too)
        saturation = (saturation if saturation<1 else 1) if saturation>0 else 0
        intensity = (intensity if intensity<3 else 3) if intensity>0 else 0

        if hue < (2/3 * pi): # First third
            r = saturation*intensity/3*(1+   saturation*cos(hue)/cos((pi/3)-hue))  * 255
            g = saturation*intensity/3*(1+saturation*(1-cos(hue)/cos((pi/3)-hue))) * 255
            b = intensity/3 * (1-saturation) * 255
        elif hue < (4/3 * pi): # Second third
            hue = hue - (2/3 * pi)
            r = intensity/3 * (1-saturation) * 255
            g = saturation*intensity/3*(1+   saturation*cos(hue)/cos((pi/3)-hue))  * 255
            b = saturation*intensity/3*(1+saturation*(1-cos(hue)/cos((pi/3)-hue))) * 255
        else: # Third section
            hue = hue - (4/3 * pi)
            r = saturation*intensity/3*(1+saturation*(1-cos(hue)/cos((pi/3)-hue))) * 255
            g = intensity/3 * (1-saturation) * 255
            b = saturation*intensity/3*(1+   saturation*cos(hue)/cos((pi/3)-hue))  * 255
        
        # Clamp rgb to valid ranges
        r = (r if r<255 else 255) if r>0 else 0
        g = (g if g<255 else 255) if g>0 else 0
        b = (b if b<255 else 255) if b>0 else 0
        
        return r, g, b

# Color gradients
class ColorGradient(BaseColor):
    def __init__(self, nodes=None, steps=0, interpMode='hsi'):
        self._nodes = None # initialize private property
        self._steps = steps # steps between EACH color (not total), val of 0 returns just list of nodes
        self.interpMode = interpMode # method of interpolating, either 'hsi' or 'rgbw'

        self.nodes  = nodes # auto-generate gradient, via property setter

    @property
    def nodes(self):
        return self._nodes
        
    @property
    def steps(self):
        return self._steps
        
    @nodes.setter
    def nodes(self, valIn):
        # Check for valid input node type (needs to be ColorSolid(BaseColor))
        if valIn is not None and (((not isinstance(valIn,list) and not isinstance(valIn,tuple)) and not isinstance(valIn,ColorSolid)) or ((isinstance(valIn,list) or isinstance(valIn,tuple)) and not all(isinstance(x,ColorSolid) for x in valIn))):
            print('Invalid nodes input, needs to be of class ColorSolid')
            return
        self._nodes = valIn
        self.gradient = self.generate()
        
    @steps.setter
    def steps(self, valIn):
        self._steps = valIn
        self.gradient = self.generate()
    
    def toString(self): # "color1,color2,colorN;steps" where 'color' is using ColorSolid's toString "rrggbb[ww]"
        if self.nodes is None:
            return ""
        return (",".join([x.toString() for x in self.nodes]) + ";" + str(self.steps))
        
    def __repr__(self):
        return self.toString()
    
    def __eq__(self, other):
        if not isinstance(other, ColorGradient):
            return NotImplemented # don't attempt to compare against unrelated types
        return self.toString() == other.toString()
    
    def generate(self):
        if self.interpMode == 'hsi':
            return linearInterpHsi(self.nodes, self.steps)
        elif self.interpMode == 'rgbw':
            return linearInterpRgbw(self.nodes, self.steps)
    
    @staticmethod
    def parse(strIn):
        # Check for valid input
        if type(strIn) != str:
            raise Exception('Invalid input, needs to be an input string')
        # Try to match our format by looking for an ';'
        strColors, strSteps = strIn.replace("(","").replace(")","").split(";",1)
        colors = [ColorSolid.parse(x) for x in strColors.split(',')]
        steps = int(strSteps)
        return ColorGradient(colors,steps)

# Special color definitions
class ColorSpecial(BaseColor):
    allModes = []
    
    def __init__(self, name, func=None):
        self.name = name
        self.func = func
        ColorSpecial.allModes.append(self)
    
    @staticmethod
    def parse(strIn):
        # Check for valid input
        if type(strIn) != str:
            raise Exception('Invalid input, needs to be an input string')
        
        # Load in stored modes
        allModeNames = [p.name for p in ColorSpecial.allModes]


# Class to control the mode of the lights
class ColorMode(object):
    allModes = []
    
    def __init__(self, name, func=None):
        self.name = name
        self.func = func
        ColorMode.allModes.append(self)
    
    @staticmethod
    def parse(strIn):
        # Check for valid input
        if type(strIn) != str:
            raise Exception('Invalid input, needs to be an input string')
        
        # Load in stored modes
        allModeNames = [p.name for p in ColorMode.allModes]


### Private functions
# Define the linear interpolation function (just off the web somewhere)
def lerp(x, x0, x1, y0, y1):
    if x > x1:
        x = x1
    if x < x0:
        x = x0
    # Calculate linear interpolation of y value.
    return y0 + (y1 - y0) * ((x - x0) / (x1 - x0))

def linearInterpHsi(nodes, steps, interpIntensity=False):
    # Check if the output is invalid (none or a single color)
    if nodes is None:
        return None
    elif (not isinstance(nodes,list) and not isinstance(nodes,tuple)) and isinstance(nodes,ColorSolid):
        return nodes # return the one and only color
    elif steps == 0:
        return nodes # just return the list of colors, if no steps were requested
    
    # Check if there any enable white LEDs in the node list
    whiteEnabled = any([color.enableWhite for color in nodes])

    # Loop over each sequential pair of colors
    steps = steps + 1
    outputList = []
    for curColor, nextColor in zip(nodes, nodes[1:]):
        # Calculate steps between the current and next color
        for idx in range(1,steps+1):
            curPos = (idx-1.0)/steps # effective percent
            newTheta = lerp(curPos,0.0,1.0,curColor.hue,nextColor.hue)
            newSat   = lerp(curPos,0.0,1.0,curColor.saturation,nextColor.saturation)
            newRho   = lerp(curPos,0.0,1.0,curColor.intensity,nextColor.intensity)
            
            # Generate new color
            intermediateColor = ColorSolid(
                hue         = newTheta,
                saturation  = newSat,
                intensity   = newRho,
                enableWhite = whiteEnabled
            )

            # Add color to the list
            outputList.append(intermediateColor)
            
    # From my https://github.com/nm3210/ArudinoRgbController/blob/master/ArudinoRgbController/ArudinoRgbController.cpp
    # # Loop over each sequential pair of colors
    # outputList = []
    # for curColor, nextColor in zip(nodes, nodes[1:]):
    #     # Check directions and lengths
    #     isCcw = (nextColor.hue - curColor.hue + 360) % 360 < 180.0
    #     gamma = 180 - abs(abs(curColor.hue - nextColor.hue) % 360 - 180)
    #     length = sqrt(pow(curColor.intensity,2) - 2*curColor.intensity*nextColor.intensity*cos(radians(gamma)) + pow(nextColor.intensity,2))
    #     if curColor.intensity == 0:
    #         alpha = acos((pow(nextColor.intensity,2)+pow(length,2))/(2.0*nextColor.intensity*length));
    #     else:
    #         alpha = acos((pow(curColor.intensity,2)+pow(length,2)-pow(nextColor.intensity,2))/(2.0*curColor.intensity*length))

    #     steps = steps + 1
    #     # Calculate steps between the current and next color
    #     for idx in range(1,steps+2):
    #         tempRho = length*((idx-1.0)/(steps+1)); # calculate one part of the line
    #         if tempRho == 0:
    #             newRho = curColor.intensity
    #         else:
    #             newRho = sqrt(pow(curColor.intensity,2) - 2.0*curColor.intensity*tempRho*cos(alpha)+pow(tempRho,2))

    #         if curColor.intensity == 0 or newRho == 0:
    #             if (curColor.hue - nextColor.hue) % 360 < 180:
    #                 newTheta = (curColor.hue - nextColor.hue) % 360
    #             else:
    #                 newTheta = -((curColor.hue - nextColor.hue) % 360)
    #         else:
    #             acosarg = (pow(curColor.intensity,2)+pow(newRho,2)+-pow(tempRho,2))/(2.0*curColor.intensity*newRho)
    #             newTheta = 0 if (round(acosarg*1000000)/1000000 == 1) else acos(acosarg)
    #             newTheta = round(degrees(newTheta)*1000)/1000

    #         if isCcw:
    #             newTheta = (curColor.hue+newTheta) % 360
    #         else:
    #             newTheta = (curColor.hue-newTheta+360) % 360
            
    #         if interpIntensity == False:
    #             newRho = (curColor.intensity + nextColor.intensity) / 2
            
    #         newSat = curColor.saturation+(nextColor.saturation-curColor.saturation)*((idx-1.0)/(steps+1)); # simple interpolation

    #         # Generate new color
    #         intermediateColor = ColorSolid(
    #             hue         = newTheta,
    #             saturation  = newSat,
    #             intensity   = newRho,
    #             enableWhite = whiteEnabled
    #         )

    #         # Add color to the list
    #         outputList.append(intermediateColor)
        
    lastColor = (nodes[-1].copy()) # dereference input color
    lastColor._inputType = 'hsi'
    outputList.append(lastColor) # add the last node

    return outputList

def linearInterpRgbw(nodes, steps):
    # Check if the output is invalid (none or a single color)
    if nodes is None:
        return None
    elif (not isinstance(nodes,list) and not isinstance(nodes,tuple)) and isinstance(nodes,ColorSolid):
        return nodes # return the one and only color
    elif steps == 0:
        return nodes # just return the list of colors, if no steps were requested
    
    # Check if there any enable white LEDs in the node list
    whiteEnabled = any([color.enableWhite for color in nodes])
    
    # Loop over each sequential pair of colors
    outputList = []
    for curColor, nextColor in zip(nodes, nodes[1:]):
        # Add the initial color
        outputList.append(curColor)
        
        # Calculate steps between the current and next color
        for idx in range(steps):
            curPos = (idx+1) / (steps+1) # effective percent
            intermediateColorR = round(lerp(curPos,0.0,1.0,curColor.red,nextColor.red))
            intermediateColorG = round(lerp(curPos,0.0,1.0,curColor.green,nextColor.green))
            intermediateColorB = round(lerp(curPos,0.0,1.0,curColor.blue,nextColor.blue))
            
            # Figure out the white
            if curColor.white is None and nextColor.white is not None:
                intermediateColorW = round(lerp(curPos,0.0,1.0,0,nextColor.white))
            elif curColor.white is not None and nextColor.white is None:
                intermediateColorW = round(lerp(curPos,0.0,1.0,curColor.white,0))
            elif curColor.white is not None and nextColor.white is not None:
                intermediateColorW = round(lerp(curPos,0.0,1.0,curColor.white,nextColor.white))
            else:
                intermediateColorW = None
                
            # Create the new color
            intermediateColor = ColorSolid(
                red   = intermediateColorR,
                green = intermediateColorG,
                blue  = intermediateColorB,
                white = intermediateColorW,
                enableWhite = whiteEnabled)
            
            # Add color to the list
            outputList.append(intermediateColor)
        
    lastColor = (nodes[-1].copy()) # dereference input color
    lastColor._inputType = 'rgbw'
    outputList.append(lastColor) # add the last node

    return outputList