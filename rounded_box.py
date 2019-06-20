#!/usr/bin/env python
# coding: utf8
# We will use the inkex module with the predefined Effect base class.
import inkex
# The simplestyle module provides functions for style parsing.

import simplestyle
import math

objStyle = simplestyle.formatStyle(
    {'stroke': '#000000',
    'stroke-width': 0.1,
    'fill': 'none'
    })

class inkcape_path:
    def __init__(self, Offset, group):
        self.offsetX = Offset[0]
        self.offsetY = Offset[1]
        self.Path = ''
        self.group = group
    
    def MoveTo(self, x, y):
    #Return string 'M X Y' where X and Y are updated values from parameters
        self.Path += ' M ' + str(round(x-self.offsetX, 3)) + ',' + str(round(y-self.offsetY, 3))

    def LineTo(self, x, y):
    #Return string 'L X Y' where X and Y are updated values from parameters
        self.Path += ' L ' + str(round(x-self.offsetX, 3)) + ',' + str(round(y-self.offsetY, 3))


    def LineToRel(self, x, y):
    #Return string 'L X Y' where X and Y are updated values from parameters
        self.Path += ' l ' + str(round(x, 3)) + ',' + str(round(y, 3))

    def LineToHRel(self, x):
    #Return string 'h X' where X are updated values from parameters
        self.Path += ' h ' + str(round(x, 3)) 

    def LineToVRel(self, y):
    #Return string 'v Y' where X and Y are updated values from parameters
        self.Path += ' v ' + str(round(y, 3)) 

    def Line(self, x1, y1, x2, y2):
    #Return string M X1 Y1 L X2 Y2
        self.Path += ' L ' + str(round(x1-self.offsetX, 3)) + ',' + str(round(y1-self.offsetY, 3)) + ' L ' + str(round(x2-self.offsetX, 3)) + ',' + str(round(y2-self.offsetY, 3))
    
    def LineRel(self, x1, y1, x2, y2):
    #Return string M X1 Y1 L X2 Y2
        self.Path += ' l ' + str(round(x1, 3)) + ',' + str(round(y1, 3)) + ' L ' + str(round(x2, 3)) + ',' + str(round(y2, 3))
    

    def Bezier(self, xc1, yc1, xc2, yc2, x, y):
    #Return string C XC1 YC1 XC2 YC2 X Y
        self.Path += ' C ' + str(round(xc1-self.offsetX, 3)) + ',' + str(round(yc1-self.offsetY, 3)) + ' ' + str(round(xc2-self.offsetX, 3)) + ',' + str(round(yc2-self.offsetY, 3))+ ' ' + str(round(x-self.offsetX, 3)) + ',' + str(round(y-self.offsetY, 3))
    

    def BezierRel(self, xc1, yc1, xc2, yc2, x, y):
    #Return string c XC1 YC1 XC2 YC2 X Y
        self.Path += ' c ' + str(round(xc1, 3)) + ',' + str(round(yc1, 3)) + ' ' + str(round(xc2, 3)) + ',' + str(round(yc2, 3))+ ' ' + str(round(x, 3)) + ',' + str(round(y, 3))
    

    def Close(self):
        self.Path += ' z'

    def GenPath(self):
        line_attribs = {'style': objStyle, 'd': self.Path}
        inkex.etree.SubElement(self.group, inkex.addNS('path', 'svg'), line_attribs)
        



class RoundedBox(inkex.Effect):
    """
    Creates a new layer with the drawings for a parametrically generaded box.
    """
    def __init__(self):
        inkex.Effect.__init__(self)
        self.knownUnits = ['in', 'pt', 'px', 'mm', 'cm', 'm', 'km', 'pc', 'yd', 'ft']

        self.OptionParser.add_option('--unit', action = 'store',
          type = 'string', dest = 'unit', default = 'mm',
          help = 'Unit, should be one of ')

        self.OptionParser.add_option('--top_type', action = 'store',
          type = 'string', dest = 'top_type', default = 'Lid',
          help = 'Box top type ')

        self.OptionParser.add_option('--thickness', action = 'store',
          type = 'float', dest = 'thickness', default = '3.0',
          help = 'Material thickness')

        self.OptionParser.add_option('--x', action = 'store',
          type = 'float', dest = 'x', default = '100.0',
          help = 'Length')

        self.OptionParser.add_option('--y', action = 'store',
          type = 'float', dest = 'y', default = '100.0',
          help = 'width of the box')

        self.OptionParser.add_option('--z', action = 'store',
          type = 'float', dest = 'z', default = '100.0',
          help = 'Height')

        self.OptionParser.add_option('--radius', action = 'store',
          type = 'float', dest = 'radius', default = '100.0',
          help = 'Radius rounded edge')

        self.OptionParser.add_option('--burn', action = 'store',
          type = 'float', dest = 'burn', default = '50.0',
          help = 'laser burn size')

        self.OptionParser.add_option('--notch_size', action = 'store',
          type = 'float', dest = 'notch_size', default = '50.0',
          help = 'Size of notches')

        self.OptionParser.add_option('--inner_size', action = 'store',
          type = 'inkbool', dest = 'inner_size', default = 'true',
          help = 'Dimensions are internal')
        
        # Debug Output file
        self.fDebug = None        

    try:
        inkex.Effect.unittouu   # unitouu has moved since Inkscape 0.91
    except AttributeError:
        try:
            def unittouu(self, unit):
                return inkex.unittouu(unit)
        except AttributeError:
            pass
    def DebugMsg(self, s):
        if self.fDebug:
            self.fDebug.write(s)
    
    def drawHNotch(self, path, notch_length, notch_height, burn, startinternal, delta_first=0):
        ''' 
        Draw an hozizontal single notch with size notch_length and height notch_height
        given startinternal, we know if the starting point is "inside" (startinternal==1) or outside
        to move backwards or forward, change sign of sizenotch
        '''
        if startinternal != 1:
            startinternal = -1
        if notch_length < 0:
            startinternal = startinternal * -1
        path.LineToHRel(delta_first+notch_length - burn * startinternal)
        path.LineToVRel(notch_height)
        path.LineToHRel(notch_length + burn * startinternal)
        path.LineToVRel(-notch_height)
     
    def drawVNotch(self, path, notch_length, notch_height, burn, startinternal, delta_first=0):
        ''' 
        Draw a vertical single notch with size notch_length and height notch_height
        given startinternal, we know if the starting point is "inside" (startinternal==1) or outside
        to move backwards or forward, change sign of sizenotch
        '''
        if startinternal != 1:
            startinternal = -1
        if notch_length < 0:
            startinternal = startinternal * -1
        path.LineToVRel(delta_first+notch_length - burn * startinternal)
        path.LineToHRel(notch_height)
        path.LineToVRel(notch_length + burn * startinternal)
        path.LineToHRel(-notch_height)


    def gen_top_bottom(self, length, width, notch_size, round_radius, thickness, burn, has_hole, xOffset, yOffset, parent):
        '''
        Generate bottom or top element. Xhen the box is closed, these elements are identical.
        When the box is open or with a lid, the top has a rounded rectangle cut.
        '''
        #First compute the size of the straight lines
        straight_x = length - 2*round_radius
        if straight_x < 4*notch_size:
            inkex.errormsg('Largeur boite trop faible, doit avoir au moins 2 encoches')
            return
        straight_y = width - 2*round_radius
        if straight_y < 4*notch_size:
            inkex.errormsg('Profondeur boite trop faible, doit avoir au moins 2 encoches')
            return
        #Compute number of notches (x)
        nb_notches_x = int((straight_x / notch_size) + 0.5)
        self.DebugMsg("length="+str(length)+" straight_x="+str(straight_x)+" nb_notches_x="+str(nb_notches_x)+"\n")
        if nb_notches_x % 2 == 0:       #  Should be odd
            nb_notches_x += 1
        size_notches_x = straight_x / nb_notches_x
        #Compute number of notches (y)
        nb_notches_y = int((straight_y / notch_size) + 0.5)
        if nb_notches_y % 2 == 0:       #  Should be odd
            nb_notches_y += 1
        size_notches_y = straight_y / nb_notches_y
        self.DebugMsg("Notches x : NB="+str(nb_notches_x)+" Size="+str(size_notches_x)+'\n')
        self.DebugMsg("Notches y : NB="+str(nb_notches_y)+" Size="+str(size_notches_y)+'\n')
        path = inkcape_path((xOffset, yOffset), parent)

        # goto origin (round_radius, 0)
        path.MoveTo(round_radius, 0)
        self.DebugMsg("Start en "+str((round_radius, 0))+'\n')
        path.LineTo(round_radius+burn/4,0)  #Small movement to center notches
        #Then draw the notches (x)
        for i in range(nb_notches_x//2):
            #If number of notches is odd, skip the middle one
            if (nb_notches_x//2)%2 and i == (nb_notches_x//4):
                path.LineTo(round_radius+2*(i+1)*size_notches_x+burn/2, 0)
            else:
                self.drawHNotch(path, size_notches_x, -thickness, burn/2, 1)
        path.LineTo(straight_x+round_radius, 0)
        
        path.Bezier(straight_x+round_radius+round_radius*0.551916, 0, length, round_radius*(1-0.551916), length, round_radius)
        #Draw right most lline with notches
        self.DebugMsg("Right most line\n")
        path.LineTo(length, round_radius+burn/4)  #Small movement to center notches
        #Then draw the notches (y)
        for i in range(nb_notches_y//2):
            self.drawVNotch(path, size_notches_y, thickness, burn/2, 1)
        path.LineTo(length, straight_y+round_radius)

        path.Bezier(length, straight_y+round_radius+round_radius*0.551916, length-round_radius*(1-0.551916), width, length-round_radius, width)
        #Then draw the notches (x), return towards x=0
        self.DebugMsg("Horizontal return\n")
        path.LineTo(length-round_radius-burn/4,width)  #Small movement to center notches
        for i in range(nb_notches_x//2):
            self.drawHNotch(path, -size_notches_x, thickness, burn/2, 1)
        path.LineTo(round_radius, width)
        
        path.Bezier(round_radius*(1-0.551916), width, 0, width - round_radius*(1-0.551916), 0, width-round_radius)
        
        #Draw last line towards origin 
        self.DebugMsg("Vertical return, last line\n")
        path.LineTo(0, width-round_radius-burn/4)  #Small movement to center notches
        #Then draw the notches (y)
        for i in range(nb_notches_y//2):
            self.drawVNotch(path, -size_notches_y, -thickness, burn/2, 1)
        path.LineTo(0, round_radius)
        
        path.Bezier(0, round_radius*(1-0.551916), round_radius*(1-0.551916), 0, round_radius, 0)
        
        # Now draw hole if any
        if has_hole:
            delta = 6       #distance is 6mm by default
            if straight_x < 35 or straight_y < 35:
                delta = 4           #For small box, make it 4
            elif straight_x > 200 and straight_y > 200:
                delta = 10         #And for large 10
            round_radius_hole = round_radius - delta
            if round_radius_hole < round_radius / 4:
                round_radius_hole = round_radius/4
            straight_x_hole = length - 2*delta - 2*round_radius_hole
            straight_y_hole = width - 2*delta - 2*round_radius_hole

            path.MoveTo(delta+round_radius_hole, delta)
            path.LineTo(delta+straight_x_hole+round_radius_hole, delta)
            path.Bezier(delta+straight_x_hole+round_radius_hole+round_radius_hole*0.551916, delta, length - delta, delta+round_radius_hole*(1-0.551916), length - delta, delta+round_radius_hole)
            path.LineTo(length-delta, delta+straight_y_hole+round_radius_hole)
            path.Bezier(length-delta, delta+straight_y_hole+round_radius_hole+round_radius_hole*0.551916, length-delta-round_radius_hole*(1-0.551916), width-delta, length-delta-round_radius_hole, width-delta)
            path.LineTo(delta+round_radius_hole, width-delta)
            path.Bezier(delta+round_radius_hole*(1-0.551916), width-delta, delta, width - delta - round_radius_hole*(1-0.551916), delta, width-delta-round_radius_hole)
            path.LineTo(delta, delta+round_radius_hole)
            path.Bezier(delta, delta+round_radius_hole*(1-0.551916), delta+round_radius_hole*(1-0.551916), delta, delta+round_radius_hole, delta)


        path.Close()
        path.GenPath()

    def gen_lid(self, length, width, round_radius, xOffset, yOffset, parent):
        '''
        Generate lid, it is a simple rounded box
        '''
        #First compute the size of the straight lines
        straight_x = length - 2*round_radius
        straight_y = width - 2*round_radius
        path = inkcape_path((xOffset, yOffset), parent)

        # goto Origin (round_radius, 0)
        path.MoveTo(round_radius, 0)
        path.LineTo(straight_x+round_radius, 0)
        path.Bezier(straight_x+round_radius+round_radius*0.551916, 0, length, round_radius*(1-0.551916), length, round_radius)
        path.LineTo(length, straight_y+round_radius)
        path.Bezier(length, straight_y+round_radius+round_radius*0.551916, length-round_radius*(1-0.551916), width, length-round_radius, width)
        path.LineTo(round_radius, width)
        path.Bezier(round_radius*(1-0.551916), width, 0, width - round_radius*(1-0.551916), 0, width-round_radius)
        path.LineTo(0, round_radius)
        path.Bezier(0, round_radius*(1-0.551916), round_radius*(1-0.551916), 0, round_radius, 0)
        path.Close()
        path.GenPath()
        
    def drawClip(self, path, size_clip, UpDown):
        ''' Draw a single clip pattern
            The clip is vertical, with length size_clip and width size_clip/4
            Add clip to current path, use LineTo
            New path position will be end of clip
            If draw up, UpDown should be 1
        '''
        if UpDown != 1:
            UpDown=-1       #Will draw negative
        #First draw vertical line which is .31*size
        path.LineToVRel(size_clip*0.3075*UpDown)
        #Then small bezier curve
        path.BezierRel(0, size_clip*0.036241333*UpDown, size_clip*0.045356111, size_clip*0.052734333*UpDown, size_clip*0.0685556, size_clip*0.025*UpDown)
        #then line 
        path.LineToRel(size_clip*0.132166667, size_clip*-0.157555556*UpDown)
        #then bezier
        path.BezierRel(size_clip*0.016710556, size_clip*-0.02*UpDown, size_clip*0.05, size_clip*-0.008*UpDown, size_clip*0.05, size_clip*0.017795167*UpDown)
        #Then vertical line
        path.LineToVRel(size_clip*0.615*UpDown)
        #then bezier
        path.BezierRel(0, size_clip*0.026*UpDown, size_clip*-0.032335, size_clip*0.037760389*UpDown, size_clip*-0.05, size_clip*0.017795167*UpDown)
        #Then line
        path.LineToRel(size_clip*-0.132166667, size_clip*-0.157555556*UpDown)
        #then last bezier
        #c -0.42188,0.5 -1.23438,0.203125 -1.23438,-0.449219
        path.BezierRel(size_clip*-0.023437778, size_clip*-0.027777778*UpDown, size_clip*-0.068576667, size_clip*-0.011284722*UpDown, size_clip*-0.068576667, size_clip*0.025*UpDown)
        #then last line
        path.LineToVRel(size_clip*0.3075*UpDown)

    def gen_flex(self, xbox, ybox, zbox, notch_size, rounded_radius, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate Flex band. 
        '''
        #First compute the size of the straight lines
        straight_x = xbox - 2*rounded_radius
        if straight_x < 4*notch_size:
            inkex.errormsg('Largeur boite trop faible, doit avoir au moins 2 encoches')
            return
        straight_y = ybox - 2*rounded_radius
        if straight_y < 4*notch_size:
            inkex.errormsg('Profondeur boite trop faible, doit avoir au moins 2 encoches')
            return
        #Compute number of notches (x)
        nb_notches_x = int((straight_x / notch_size) + 0.5)
        if nb_notches_x % 2 == 0:       #  Should be odd
            nb_notches_x += 1
        size_notches_x = straight_x / nb_notches_x
        #Compute number of notches (y)
        nb_notches_y = int((straight_y / notch_size) + 0.5)
        if nb_notches_y % 2 == 0:       #  Should be odd
            nb_notches_y += 1
        size_notches_y = straight_y / nb_notches_y
        self.DebugMsg("Notches x : NB="+str(nb_notches_x)+" Size="+str(size_notches_x)+'\n')
        self.DebugMsg("Notches y : NB="+str(nb_notches_y)+" Size="+str(size_notches_y)+'\n')
        #Open the path which will be used
        path = inkcape_path((xOffset, yOffset), parent)
        #The path will start at the middle of longest side.
        StartX = straight_x > straight_y
        if StartX:
            nb1 = nb_notches_x
            sz1 = size_notches_x
            nb2 = nb_notches_y
            sz2 = size_notches_y
            firstrounded = straight_x/2
            secondrounded = firstrounded + rounded_radius*math.pi / 2 + straight_y
            thirdrounded = secondrounded + rounded_radius*math.pi / 2 + straight_x
            fourthrounded = thirdrounded + rounded_radius*math.pi / 2 + straight_y
        else:
            nb1 = nb_notches_y
            sz1 = size_notches_y
            nb2 = nb_notches_x
            sz2 = size_notches_x
            firstrounded = straight_y/2
            secondrounded = firstrounded + rounded_radius*math.pi / 2 + straight_x
            thirdrounded = secondrounded + rounded_radius*math.pi / 2 + straight_y
            fourthrounded = thirdrounded + rounded_radius*math.pi / 2 + straight_x


        #Begin path at lower left, then draw the clips
        path.MoveTo( 0, 0)
        #Compute clips number and position, zone with clips will be between thickness and zbox - thickness 
        zoneclips = zbox - 2*thickness
        #Size of clips is dependant to size of zoneclips
        if zoneclips < 50:
            sizeclips = 10
        else:
            sizeclips = 18
        nbclips = int(zoneclips // sizeclips)
        if nbclips == 0:
            inkex.errormsg('Hauteur boite trop faible, pas possible de positionner les attaches')
            return
        path.LineToVRel((zoneclips - nbclips*sizeclips)/2 + thickness)
        for i in range(nbclips):
            self.drawClip(path, sizeclips, 1)
        path.LineToVRel((zoneclips - nbclips*sizeclips)/2 + thickness)
        #Now draw the top horizontal line with notches 
        if ( (nb1//2) % 2 ):     #Odd, one notch removed in bottom / top
            path.LineToHRel(sz1)
            self.DebugMsg("nb1="+str(nb1)+" odd, skip one notch, so move HRel="+str(sz1)+"\n")
        for i in range(nb1//4):
            if i == 0:
                self.drawHNotch(path, sz1, -thickness, burn/2, 0, -sz1/2)       #First notch is shifted to make space for clips
            else:
                self.drawHNotch(path, sz1, -thickness, burn/2, 0)
        #Then H Line for remaining notches + round
        path.LineToHRel(sz1+burn/4+rounded_radius*math.pi/2)
        #Then notches for vertical line
        for i in range(nb2//2):
            self.drawHNotch(path, sz2, -thickness, burn/2, 0)
        #Then H Line to remaining notch and round    
        path.LineToHRel(sz2+burn/4+rounded_radius*math.pi/2)
        #Then notches for opposite H line
        for i in range(nb1//2):
            self.drawHNotch(path, sz1, -thickness, burn/2, 0)
        #Then H Line to remaining notch and round    
        path.LineToHRel(sz1+burn/4+rounded_radius*math.pi/2)
        #Then notches for opposite vertical line
        for i in range(nb2//2):
            self.drawHNotch(path, sz2, -thickness, burn/2, 0)
        #Then H Line to remaining notch and round    
        path.LineToHRel(sz2+burn/4+rounded_radius*math.pi/2)
        #Then one half line of notches
        for i in range(nb1//4):
            self.drawHNotch(path, sz1, -thickness, burn/2, 0)
        #Line to end of strip
        path.LineTo(straight_x*2+straight_y*2+2*math.pi*rounded_radius, zbox)
        #and vertical trip (reverse)
        path.LineToVRel(-1.0*((zoneclips - nbclips*sizeclips)/2 + thickness))
        for i in range(nbclips):
            self.drawClip(path, sizeclips, -1)
        path.LineTo(straight_x*2+straight_y*2+2*math.pi*rounded_radius, 0)
        #Then go back to starting point
        #Now draw the top horizontal line with notches 
        if ( (nb1//2) % 2 ):     #Odd, one notch removed in bottom / top
            path.LineToHRel(-sz1)
        for i in range(nb1//4):
            if i == 0:
                self.drawHNotch(path, -sz1, thickness, burn/2, 0, sz1/2)       #First notch is shifted to make space for clips
            else:
                self.drawHNotch(path, -sz1, thickness, burn/2, 0)
        #Then H Line for remaining notches + round
        path.LineToHRel(-sz1-burn/4-rounded_radius*math.pi/2)
        #Then notches for vertical line
        for i in range(nb2//2):
            self.drawHNotch(path, -sz2, thickness, burn/2, 0)
        #Then H Line to remaining notch and round    
        path.LineToHRel(-sz2-burn/4-rounded_radius*math.pi/2)
        #Then notches for opposite H line
        for i in range(nb1//2):
            self.drawHNotch(path, -sz1, thickness, burn/2, 0)
        #Then H Line to remaining notch and round    
        path.LineToHRel(-sz1-burn/4-rounded_radius*math.pi/2)
        #Then notches for opposite vertical line
        for i in range(nb2//2):
            self.drawHNotch(path, -sz2, thickness, burn/2, 0)
        #Then H Line to remaining notch and round    
        path.LineToHRel(-sz2-burn/4-rounded_radius*math.pi/2)
        #Then one half line of notches
        for i in range(nb1//4):
            self.drawHNotch(path, -sz1, thickness, burn/2, 0)
        #Line to end of strip
        path.LineTo(0, 0)

        # Now generate flex lines
        #First compute how many segment per line. Segment length should be kept short, < 50mm or so
        if zbox < 30:
            nSegmentFLex = 1
        elif zbox < 80:
            nSegmentFlex = 2
        elif zbox < 150:
            nSegmentFlex = 3
        else:
            nSegmentFlex = zbox // 50
        #Then compute distance between flex lines. The basic idea is to have a minimum of 15 lines per corner, with lines distant at least of 1mm
        round_distance = rounded_radius*math.pi/2
        flex_line_spacing = round_distance / 14
        flex_line_spacing = max(flex_line_spacing, 1.0)
        nb_flex_lines =  int(round(round_distance / flex_line_spacing,0))
        self.DebugMsg("sizeround ="+str(round_distance)+" flex_line_spacing="+str(flex_line_spacing)+" nb_flex_lines="+str(nb_flex_lines)+" size="+str(nb_flex_lines*flex_line_spacing)+"\n")        
        if nb_flex_lines > 29:
            nb_flex_lines = 29
        #nb_flex_lines should be odd
        nb_flex_lines |= 1 
        flex_line_spacing = round_distance / (nb_flex_lines-1)
        length_flex_segment_odd = (zbox - 2*nSegmentFlex) / nSegmentFlex
        length_flex_segment_even = (zbox - 2*(nSegmentFlex+1)) / nSegmentFlex
        self.DebugMsg("nSegmentFlex="+str(nSegmentFlex)+" sizeround ="+str(round_distance)+" flex_line_spacing="+str(flex_line_spacing)+" nb_flex_lines="+str(nb_flex_lines)+" size="+str(nb_flex_lines*flex_line_spacing)+"\n")
        #First set of flex lines
        for i in range(nb_flex_lines):
            if i % 2:
                for j in range(nSegmentFlex):
                    path.MoveTo(firstrounded + i * flex_line_spacing, zbox-2-j * (length_flex_segment_even+2) )
                    path.LineToVRel(-length_flex_segment_even)
            else:
                path.MoveTo(firstrounded + i * flex_line_spacing, 0 )
                path.LineToVRel(length_flex_segment_even/2)
                for j in range(nSegmentFlex-1):
                    path.MoveTo(firstrounded + i * flex_line_spacing, j * (length_flex_segment_odd+2) + length_flex_segment_odd/2 + 2 )
                    path.LineToVRel(length_flex_segment_odd)
                path.MoveTo(firstrounded + i * flex_line_spacing, zbox - length_flex_segment_odd/2)
                path.LineTo(firstrounded + i * flex_line_spacing, zbox )
        #Second set of flex lines
        for i in range(nb_flex_lines):
            if i % 2:
                for j in range(nSegmentFlex):
                    path.MoveTo(secondrounded + i * flex_line_spacing, zbox-2-j * (length_flex_segment_even+2) )
                    path.LineToVRel(-length_flex_segment_even)
            else:
                path.MoveTo(secondrounded + i * flex_line_spacing, 0 )
                path.LineToVRel(length_flex_segment_even/2)
                for j in range(nSegmentFlex-1):
                    path.MoveTo(secondrounded + i * flex_line_spacing, j * (length_flex_segment_odd+2) + length_flex_segment_odd/2 + 2 )
                    path.LineToVRel(length_flex_segment_odd)
                path.MoveTo(secondrounded + i * flex_line_spacing, zbox - length_flex_segment_odd/2)
                path.LineTo(secondrounded + i * flex_line_spacing, zbox )
        #Third set of flex lines
        for i in range(nb_flex_lines):
            if i % 2:
                for j in range(nSegmentFlex):
                    path.MoveTo(thirdrounded + i * flex_line_spacing, zbox-2-j * (length_flex_segment_even+2) )
                    path.LineToVRel(-length_flex_segment_even)
            else:
                path.MoveTo(thirdrounded + i * flex_line_spacing, 0 )
                path.LineToVRel(length_flex_segment_even/2)
                for j in range(nSegmentFlex-1):
                    path.MoveTo(thirdrounded + i * flex_line_spacing, j * (length_flex_segment_odd+2) + length_flex_segment_odd/2 + 2 )
                    path.LineToVRel(length_flex_segment_odd)
                path.MoveTo(thirdrounded + i * flex_line_spacing, zbox - length_flex_segment_odd/2)
                path.LineTo(thirdrounded + i * flex_line_spacing, zbox )
        #Last set of flex lines
        for i in range(nb_flex_lines):
            if i % 2:
                for j in range(nSegmentFlex):
                    path.MoveTo(fourthrounded + i * flex_line_spacing, zbox-2-j * (length_flex_segment_even+2) )
                    path.LineToVRel(-length_flex_segment_even)
            else:
                path.MoveTo(fourthrounded + i * flex_line_spacing, 0 )
                path.LineToVRel(length_flex_segment_even/2)
                for j in range(nSegmentFlex-1):
                    path.MoveTo(fourthrounded + i * flex_line_spacing, j * (length_flex_segment_odd+2) + length_flex_segment_odd/2 + 2 )
                    path.LineToVRel(length_flex_segment_odd)
                path.MoveTo(fourthrounded + i * flex_line_spacing, zbox - length_flex_segment_odd/2)
                path.LineTo(fourthrounded + i * flex_line_spacing, zbox )
        path.GenPath()

    
    def effect(self):
        """
        Draws a conic box, based on provided parameters
        """

        # input sanity check
        error = False
        if self.options.radius < 10:
            inkex.errormsg('Error: radius should be at least 10mm')
            error = True

        if self.options.notch_size < 2 or self.options.notch_size > self.options.x / 3:
            inkex.errormsg('bad value for notch size')
            error = True

        if self.options.thickness <  1 or self.options.thickness >  10:
            inkex.errormsg('Error: thickness should be at least 1mm and less than 10mm')
            error = True

        if error:
            exit()


        # convert units
        unit = self.options.unit
        xbox = self.unittouu(str(self.options.x) + unit)
        ybox = self.unittouu(str(self.options.y) + unit)
        zbox = self.unittouu(str(self.options.z) + unit)
        thickness = self.unittouu(str(self.options.thickness) + unit)
        burn = self.unittouu(str(self.options.burn) + unit)
        rounded_radius = self.unittouu(str(self.options.radius) + unit)
        notch_size = self.unittouu(str(self.options.notch_size) + unit)
        box_top_type = self.options.top_type

        # Select final dimensions, using inner_size variables. If Outer_size, decrease dimensions.
        if self.options.inner_size == False:
            xbox -= 2*thickness
            ybox -= 2*thickness
            zbox -= 2*thickness
            
        # Decide if the top should have a hole, and a lid is needed
        has_hole = box_top_type != 'Closed'
        has_lid = box_top_type == 'Lid'
            
        svg = self.document.getroot()
        docWidth = self.unittouu(svg.get('width'))
        docHeigh = self.unittouu(svg.attrib['height'])

        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'Rounded Box')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        group = inkex.etree.SubElement(layer, 'g')
        try:
            self.fDebug = open( 'DebugRoundedBox.txt', 'w')
        except IOError:
            print ('cannot open debug output file')
        self.DebugMsg("Start processing\n")        
        #generate top
        self.gen_top_bottom(xbox, ybox, notch_size, rounded_radius, thickness, burn, has_hole, 0, 0, group)
        #generate bottom
        self.gen_top_bottom(xbox, ybox, notch_size, rounded_radius, thickness, burn, 0, 0, -ybox-2*thickness-2, group)
        #Then lid if needed
        if has_lid:
            self.gen_lid(xbox+2*thickness, ybox+2*thickness, rounded_radius+thickness, -xbox-2*thickness-2, 0, group)
        #And flex 
        self.gen_flex(xbox, ybox, zbox, notch_size, rounded_radius, thickness, burn, 0, zbox+2*thickness+2, group)
        #Close Debug file if open
        if self.fDebug:
            self.fDebug.close()


# Create effect instance and apply it.
effect = RoundedBox()
effect.affect()
