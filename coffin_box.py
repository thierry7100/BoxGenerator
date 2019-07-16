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

objStyleEngraving = simplestyle.formatStyle(
    {'stroke': '#ff0000',
    'stroke-width': 0.1,
    'fill': 'none'
    })

SteelHingeSpacing = 0.3
RadiusSteelHingeAxis = 1.3      #Use axis about 2.4mm diameter, I use nails 2.3mmx70mm

HiddenSteelAxisSize = 1.5       #I use steel wire, 1mm diameter

class inkcape_path:
    def __init__(self, Offset, group, Label=None, Style=None):
        self.offsetX = Offset[0]
        self.offsetY = Offset[1]
        self.Path = ''
        self.group = group
        self.Label = Label
        if Style:
            self.Style = Style
        else:
            self.Style = objStyle
    
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
    
    def drawCircle(self, xc, yc, radius):
    #Draw a circle, with 4 Bezier paths
        self.MoveTo(xc+radius, yc)    #R, 0
        self.Bezier(xc+radius, yc + radius*0.551916, xc + radius*0.551916, yc+radius, xc, yc+radius)  #1er quater, lower right
        self.Bezier(xc+radius*-0.551916, yc + radius, xc - radius, yc+radius*0.551916, xc-radius, yc)  #2nd quater, lower left
        self.Bezier(xc-radius, yc - radius*0.551916, xc - radius*0.551916, yc-radius, xc, yc-radius)  #3rd quater, upper leftt
        self.Bezier(xc+radius*0.551916, yc - radius, xc + radius, yc-radius*0.551916, xc+radius, yc)  #2nd quater, upper right

    def Close(self):
        self.Path += ' z'

    def GenPath(self):
        if self.Label:
            line_attribs = {'style': self.Style, 'id' : self.Label, 'd': self.Path}
        else:            
            line_attribs = {'style': self.Style, 'd': self.Path}
        inkex.etree.SubElement(self.group, inkex.addNS('path', 'svg'), line_attribs)
        
class CoffinBox(inkex.Effect):
    """
    Creates a new layer with the drawings for a parametrically generaded box.
    """
    def __init__(self):
        inkex.Effect.__init__(self)
        self.knownUnits = ['in', 'pt', 'px', 'mm', 'cm', 'm', 'km', 'pc', 'yd', 'ft']

        self.OptionParser.add_option('--unit', action = 'store',
          type = 'string', dest = 'unit', default = 'mm',
          help = 'Unit, should be one of ')

        self.OptionParser.add_option('--thickness', action = 'store',
          type = 'float', dest = 'thickness', default = '3.0',
          help = 'Material thickness')

        self.OptionParser.add_option('--lid_type', action = 'store',
          type = 'string', dest = 'lid_type', default = 'IntegratedWood',
          help = 'Box lid style ')

        self.OptionParser.add_option('--z', action = 'store',
          type = 'float', dest = 'z', default = '40.0',
          help = "box height")

        self.OptionParser.add_option('--z_lid', action = 'store',
          type = 'float', dest = 'z_lid', default = '20.0',
          help = "lid height")

        self.OptionParser.add_option('--y', action = 'store',
          type = 'float', dest = 'y', default = '80.0',
          help = "box width")

        self.OptionParser.add_option('--x', action = 'store',
          type = 'float', dest = 'x', default = '120.0',
          help = "box length")

        self.OptionParser.add_option('--burn', action = 'store',
          type = 'float', dest = 'burn', default = '0.1',
          help = 'laser burn size')

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

    def drawLineHNotches(self, path, nb_notch, notch_length, notch_height, burn, startinternal):
        if notch_length > 0:
            sign = startinternal
        else:
            sign = -startinternal
        self.drawHNotch(path, notch_length, notch_height, burn, startinternal, sign*burn/2)
        for i in range(1, nb_notch):
            self.drawHNotch(path, notch_length, notch_height, burn, startinternal, 0)

    def drawLineVNotches(self, path, nb_notch, notch_length, notch_height, burn, startinternal):
        if notch_length > 0:
            sign = startinternal
        else:
            sign = -startinternal
        self.drawVNotch(path, notch_length, notch_height, burn, startinternal, sign*burn/2)
        for i in range(1, nb_notch):
            self.drawVNotch(path, notch_length, notch_height, burn, startinternal, 0)

    def drawHole(self, path, x0, y0, dx, dy, burn):
        ''' 
        Add a rectangle starting at x0,y0 and with a length dx and width dy to the current path
        burn is the burn factor, so actual coordinates are modified by burn/2
        '''
        path.MoveTo(x0+burn/2, y0+burn/2)
        path.LineToVRel(dy-burn)
        path.LineToHRel(dx-burn)
        path.LineToVRel(-dy+burn)
        path.LineToHRel(-dx+burn)

    def drawSteelHingeElement(self, idx, thickness, xOffset, yOffset, parent):
        path = inkcape_path((xOffset, yOffset), parent, 'HingeElt_'+str(idx))
        path.MoveTo(0, 0)
        #Start at upper right
        path.LineToVRel(thickness)
        path.LineToHRel(-thickness)
        path.LineToVRel(thickness)
        path.LineToHRel(thickness)
        path.LineToVRel(thickness)
        #Now draw half circle (radius is 1.5*thickness)
        #Position is now 0,3*thickness
        path.Bezier(1.5*thickness*0.551916, 3*thickness, 1.5*thickness, 3*thickness+1.5*thickness*0.551916, 1.5*thickness, 4.5*thickness) 
        path.Bezier(1.5*thickness, 4.5*thickness+1.5*thickness*0.551916, 1.5*thickness*(1-0.551916), 6*thickness, 0, 6*thickness) 
        #Second part of circle has a radius of 2*thickness
        path.Bezier(-2*thickness*0.551916, 6*thickness, -2*thickness, 6*thickness-2*thickness*0.551916, -2*thickness, 4*thickness) 
        path.LineTo(-2*thickness, thickness)
        path.Bezier(-2*thickness, thickness*(1-0.551916), thickness*-1.551916, 0, -thickness, 0)
        path.LineTo(0,0)
        #and last the circle at center for this axis, radius is RadiusSteelHingeAxis mm 
        path.drawCircle(0, 4.5*thickness, RadiusSteelHingeAxis)
        path.Close()
        path.GenPath()

        
    def gen_top_bottom(self, id_path, length, top_notch_size_x, nb_top_notch_x, width, top_notch_size_y, nb_top_notch_y, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate top or bottom element. This is a rectangle with notches on all edges
        '''
        path = inkcape_path((xOffset, yOffset), parent, id_path)
        path.MoveTo(0, 0)
        #first H line with notches
        self.drawLineHNotches(path, nb_top_notch_x, top_notch_size_x, -thickness, burn, 1)
        path.LineTo(length, 0)
        #Second line (V)
        self.drawLineVNotches(path, nb_top_notch_y, top_notch_size_y, thickness, burn, 1)
        path.LineTo(length, width)
        #Third line (H)
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, thickness, burn, 1)
        path.LineTo(0, width)
        #and last one
        self.drawLineVNotches(path, nb_top_notch_y, -top_notch_size_y, -thickness, burn, 1)
        path.LineTo(0, 0)
        path.Close()
        path.GenPath()

    def gen_front(self, id_path, length, top_notch_size_x, nb_top_notch_x, height, top_notch_size_z, nb_top_notch_z, delta_z, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate front element. This is a rectangle with notches on 3 edges, top has no notch
        '''
        path = inkcape_path((xOffset, yOffset), parent, id_path)
        path.MoveTo(-thickness, 0)      # Start at -thickness because notches are internal
        #first H line without notches
        path.LineTo(length+thickness, 0)
        #Second line (V)
        path.LineTo(length+thickness, delta_z)
        self.drawLineVNotches(path, nb_top_notch_z, top_notch_size_z, -thickness, burn, -1)
        path.LineTo(length+thickness, height+thickness)
        #Third line (H)
        path.LineTo(length, height+thickness)
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, -thickness, burn, -1)
        path.LineTo(-thickness, height+thickness)
        #and last one
        path.LineTo(-thickness, height)
        self.drawLineVNotches(path, nb_top_notch_z, -top_notch_size_z, thickness, burn, -1)
        path.LineTo(-thickness, 0)
        path.Close()
        path.GenPath()


    def gen_lid_front(self, id_path, length, top_notch_size_x, nb_top_notch_x, height, top_notch_size_z, nb_top_notch_z, delta_z, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate lid front. This is a rectangle with notches on 3 edges, bottom has no notch
        '''
        path = inkcape_path((xOffset, yOffset), parent, id_path)
        path.MoveTo(-thickness, -thickness)
        #first H line with notches
        path.LineTo(0, -thickness)
        self.drawLineHNotches(path, nb_top_notch_x, top_notch_size_x, thickness, burn, -1)
        path.LineTo(length+thickness, -thickness)
        path.LineTo(length+thickness, 0)
        #Second line (V)
        #path.LineToVRel(delta_z)
        if nb_top_notch_z > 0:
            self.drawLineVNotches(path, nb_top_notch_z, top_notch_size_z, -thickness, burn, -1)
        path.LineTo(length+thickness, height)
        #Third line (H) without notches
        path.LineTo(-thickness, height)
        #and last one
        path.LineToVRel(-delta_z)
        if nb_top_notch_z > 0:
            self.drawLineVNotches(path, nb_top_notch_z, -top_notch_size_z, thickness, burn, -1)
        path.LineTo(-thickness, -thickness)
        path.Close()
        path.GenPath()

    def gen_lid_back_IntegratedWood(self, id_path, length, top_notch_size_x, nb_top_notch_x, height, top_notch_size_z, nb_top_notch_z, delta_z, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate lid back with integrated hinge. This is a rectangle with notches on 3 edges, bottom has no notch
        There is a notch for the hinge
        '''
        path = inkcape_path((xOffset, yOffset), parent, id_path)
        path.MoveTo(-thickness, -thickness)
        #first H line with notches
        path.LineTo(0, -thickness)
        self.drawLineHNotches(path, nb_top_notch_x, top_notch_size_x, thickness, burn, -1)
        path.LineTo(length+thickness, -thickness)
        #Second line (V)
        path.LineTo(length+thickness, 0)
        if nb_top_notch_z > 0:
            self.drawLineVNotches(path, nb_top_notch_z, top_notch_size_z, -thickness, burn, -1)
        #then notch for hinge, beware no burn factor at this time
        ExtRadius = 3*thickness + 2*burn
        RectHeight = 1.5 * thickness
        path.LineTo(length+thickness, height-ExtRadius)
        path.LineTo(length, height-ExtRadius)
        path.LineTo(length, height-RectHeight)
        path.LineTo(length+thickness, height-RectHeight)
        path.LineTo(length+thickness, height)
        #Third line (H) without notches
        path.LineTo(-thickness, height)
        #and last one
        path.LineTo(-thickness, height-RectHeight)
        path.LineTo(0, height-RectHeight)
        path.LineTo(0, height-ExtRadius)
        path.LineTo(-thickness, height-ExtRadius)
        path.LineTo(-thickness, height-delta_z)
        if nb_top_notch_z > 0:
            self.drawLineVNotches(path, nb_top_notch_z, -top_notch_size_z, thickness, burn, -1)
        path.LineTo(-thickness, -thickness)
        path.Close()
        path.GenPath()

    def gen_back_IntegratedWood(self, id_path, length, top_notch_size_x, nb_top_notch_x, height, top_notch_size_z, nb_top_notch_z, delta_z, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate back with integrated hinge. This is a rectangle with notches on 3 edges, top has no notch
        There is a notch for the hinge
        '''
        ExtRadius = 3*thickness + 2*burn
        path = inkcape_path((xOffset, yOffset), parent, id_path)
        path.MoveTo(0, 0)
        #first H line without notches
        path.LineTo(length, 0)
        #Second line (V)
        path.LineTo(length, ExtRadius)       #Space for hinge
        path.LineTo(length+thickness, ExtRadius)
        path.LineTo(length+thickness, delta_z)
        if nb_top_notch_z > 0:
            self.drawLineVNotches(path, nb_top_notch_z, top_notch_size_z, -thickness, burn, -1)
        path.LineTo(length+thickness, height+thickness)
        path.LineToHRel(-thickness)
        #Third line (H) with notches
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, -thickness, burn, -1)
        path.LineTo(-thickness, height+thickness)
        #and last one
        path.LineTo(-thickness, height)
        if nb_top_notch_z > 0:
            self.drawLineVNotches(path, nb_top_notch_z, -top_notch_size_z, thickness, burn, -1)
        path.LineTo(-thickness, 4*thickness)
        path.LineTo(-thickness, ExtRadius)
        path.LineTo(0, ExtRadius)
        path.LineTo(0, 0)
        path.Close()
        path.GenPath()
      
    def gen_lid_side_IntegratedWood(self, flag_right, length, top_notch_size_x, nb_top_notch_x, height, front_notch_size_z, nb_front_notch_z, delta_z_front,  back_notch_size_z, nb_back_notch_z, delta_z_back, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate lid side with integrated hinge. This is a rectangle with a rounded cur for the hinge and notches on 3 edges
        No notch on the bottom edge
        '''
        ExtRadius = 3*thickness + 2*burn
        if flag_right > 0:
            path = inkcape_path((xOffset, yOffset), parent, 'Lid_right')
        else:
            path = inkcape_path((xOffset, yOffset), parent, 'Lid_left')
        #first H line (top) with notches, notches are inside
        path.MoveTo(0, -thickness)
        self.drawLineHNotches(path, nb_top_notch_x, top_notch_size_x, thickness, burn, -1)
        path.LineTo(length, -thickness)
        path.LineTo(length, 0)
        #second line, depend on left/right
        if flag_right > 0:
            #Draw back notches
            if nb_back_notch_z > 0:
                self.drawLineVNotches(path, nb_back_notch_z, back_notch_size_z, thickness, burn, 1)
            path.LineTo(length, height-ExtRadius*0.95)
            #Then the rounded cut, almost a quarter of circle, radius ExtRadius
            path.Bezier(length-ExtRadius*0.23, height-ExtRadius*0.90, length-ExtRadius+thickness, height-ExtRadius*0.551916, length-ExtRadius+thickness, height)
            #Third line (H) without notches
            path.LineTo(0, height)
            #draw front notches
            path.LineToVRel(-delta_z_front)
            if nb_front_notch_z > 0:
                self.drawLineVNotches(path, nb_front_notch_z, -front_notch_size_z, -thickness, burn, 1)
            path.LineTo(0, -thickness)
        else:
            #draw front notches
            if nb_front_notch_z > 0:
                self.drawLineVNotches(path, nb_front_notch_z, front_notch_size_z, thickness, burn, 1)
            path.LineTo(length, height)
            #Third line (H) without notches
            path.LineTo(ExtRadius-thickness, height)
            #Draw the rounded cut, almost a quarter of circle, radius ExtRadius
            path.Bezier(ExtRadius-thickness, height-ExtRadius*0.551916, ExtRadius*0.23, height-ExtRadius*0.90, 0, height-ExtRadius*0.95)
            #Draw back notches
            path.LineTo(0, height-delta_z_back)
            if nb_back_notch_z > 0:
                self.drawLineVNotches(path, nb_back_notch_z, -back_notch_size_z, -thickness, burn, 1)
            path.LineTo(0, -thickness)

        path.Close()
        path.GenPath()

    def gen_side_IntegratedWood_Right(self, length, top_notch_size_x, nb_top_notch_x, height, front_notch_size_z, nb_front_notch_z, delta_z_front,  back_notch_size_z, nb_back_notch_z, delta_z_back, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate lid side with integrated hinge. This is a rectangle with a circle for the hinge and notches on 3 edges
        No notch on the top edge
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'Right')
        #first H line (top) witout notches
        path.MoveTo(0, 0)
        ExtRadius = 3*thickness
        path.LineTo(length+thickness-ExtRadius, 0)
        #Then the circle for the hinge, circle radius is 3*thickness  mm
        path.Bezier(length+thickness-ExtRadius, ExtRadius*-0.551916, length+thickness-ExtRadius*0.551916, -ExtRadius, length+thickness, -ExtRadius) #first quadrant
        path.Bezier(length+thickness+ExtRadius*0.551916, -ExtRadius, length+thickness+ExtRadius, -ExtRadius*0.551916, length+thickness+ExtRadius, 0) #second quadrant
        path.Bezier(length+thickness+ExtRadius, ExtRadius*0.551916, length+thickness+ExtRadius*0.551916, ExtRadius, length+thickness, ExtRadius) #Third quadrant
        path.LineTo(length, ExtRadius)
        #Draw back notches
        path.LineTo(length, delta_z_back)
        if nb_back_notch_z > 0:
            self.drawLineVNotches(path, nb_back_notch_z, back_notch_size_z, thickness, burn, 1)
        path.LineTo(length, height+thickness)
        #Third line (H) with notches
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, -thickness, burn, -1)
        path.LineTo(0, height+thickness)
        path.LineTo(0, height)
        #draw front notches
        #if delta_z_front > 0:
        #    path.LineTo(0, delta_z_front)
        if nb_front_notch_z > 0:
            self.drawLineVNotches(path, nb_front_notch_z, -front_notch_size_z, -thickness, burn, 1)
        path.LineTo(0, 0)
        #Draw the circle internal to the hinge, radius is 2*thickness mm
        CircleRadius = 2*thickness
        path.MoveTo(length+thickness-CircleRadius, 0)
        path.Bezier(length+thickness-CircleRadius, -CircleRadius*0.551916, length+thickness-CircleRadius*0.551916, -CircleRadius, length+thickness, -CircleRadius) #first quadrant
        path.Bezier(length+thickness+CircleRadius*0.551916, -CircleRadius, length+thickness+CircleRadius, -CircleRadius*0.551916, length+thickness+CircleRadius, 0) #second quadrant
        path.Bezier(length+thickness+CircleRadius, CircleRadius*0.551916, length+thickness+CircleRadius*0.551916, CircleRadius, length+thickness, CircleRadius) #Third quadrant
        path.Bezier(length+thickness-CircleRadius*0.551916, CircleRadius, length+thickness-CircleRadius, CircleRadius*0.551916, length+thickness-CircleRadius, 0) #Fourth quadrant
        #Then the internal rectangle, rectangle height is 1.5*thickness
        RectHeight = 1.5*thickness
        path.MoveTo(length, -RectHeight)
        path.LineToHRel(thickness) 
        path.LineToVRel(RectHeight) 
        path.LineToHRel(-thickness) 
        path.LineToVRel(-RectHeight) 

        path.Close()
        path.GenPath()

    def gen_side_IntegratedWood_Left(self, length, top_notch_size_x, nb_top_notch_x, height, front_notch_size_z, nb_front_notch_z, delta_z_front,  back_notch_size_z, nb_back_notch_z, delta_z_back, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate lid side with integrated hinge. This is a rectangle with a circle for the hinge and notches on 3 edges
        No notch on the top edge
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'Left')
        #first H line (top) witout notches
        ExtRadius = 3*thickness
        InRadius = 2*thickness
        RectHeight = 1.5*thickness
        path.MoveTo(ExtRadius-thickness, 0)
        path.LineTo(length, 0)
        #draw front notches
        path.LineToVRel(delta_z_front)
        if nb_front_notch_z > 0:
            self.drawLineVNotches(path, nb_front_notch_z, front_notch_size_z, thickness, burn, 1)
        path.LineTo(length, height+thickness)
        #Third line (H) with notches
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, -thickness, burn, -1)
        path.LineTo(0, height+thickness)
        #Draw Back notches
        path.LineToVRel(-thickness)
        if nb_back_notch_z > 0:
            self.drawLineVNotches(path, nb_back_notch_z, -back_notch_size_z, -thickness, burn, 1)
        path.LineTo(0, ExtRadius)
        path.LineTo(-thickness, ExtRadius)
        #Then the circle for the hinge, circle radius is ExtRadius mm
        path.Bezier(ExtRadius*-0.551916-thickness, ExtRadius, -ExtRadius-thickness, ExtRadius*0.551916, -ExtRadius-thickness, 0) #First quadrant
        path.Bezier(-ExtRadius-thickness, ExtRadius*-0.551916, ExtRadius*-0.551916-thickness, -ExtRadius, -thickness, -ExtRadius) #Second quadrant
        path.Bezier(ExtRadius*0.551916-thickness, -ExtRadius, ExtRadius-thickness, ExtRadius*-0.551916, ExtRadius-thickness, 0) #Third quadrant

        #Draw the circle internal to the hinge, radius is InRadius mm
        path.MoveTo(InRadius-thickness, 0)
        path.Bezier(InRadius-thickness, -InRadius*0.551916, InRadius*0.551916-thickness, -InRadius, -thickness, -InRadius) #first quadrant
        path.Bezier(InRadius*-0.551916-thickness, -InRadius, -InRadius-thickness, -InRadius*0.551916, -InRadius-thickness, 0) #second quadrant
        path.Bezier(-InRadius-thickness, InRadius*0.551916, InRadius*-0.551916-thickness, InRadius, -thickness, InRadius) #Third quadrant
        path.Bezier(InRadius*0.551916-thickness, InRadius, InRadius-thickness, InRadius*0.551916, InRadius-thickness, 0) #Fourth quadrant
        #Then the internal rectangle
        path.MoveTo(-thickness, -RectHeight)
        path.LineToHRel(thickness) 
        path.LineToVRel(RectHeight) 
        path.LineToHRel(-thickness) 
        path.LineToVRel(-RectHeight) 

        path.Close()
        path.GenPath()

    def gen_lid_side_Steel(self, flag_right, length, top_notch_size_x, nb_top_notch_x, height, front_notch_size_z, nb_front_notch_z, delta_z_front,  thickness, burn, xOffset, yOffset, parent):
        '''
        Generate lid side with metal hinge. This is a rectangle with notches on 3 edges
        No notch on the bottom edge
        '''
        if flag_right > 0:
            path = inkcape_path((xOffset, yOffset), parent, 'Lid_right')
        else:
            path = inkcape_path((xOffset, yOffset), parent, 'Lid_left')
        #first H line (top) with notches, notches are inside
        path.MoveTo(0, -thickness)
        self.drawLineHNotches(path, nb_top_notch_x, top_notch_size_x, thickness, burn, -1)
        path.LineTo(length, -thickness)
        path.LineTo(length, 0)
        #Draw back notches
        if nb_front_notch_z > 0:
            self.drawLineVNotches(path, nb_front_notch_z, front_notch_size_z, thickness, burn, 1)
        path.LineTo(length, height)
        #Third line (H) without notches
        path.LineTo(0, height)
        #draw front notches
        if nb_front_notch_z > 0:
            path.LineToVRel(-delta_z_front)
            self.drawLineVNotches(path, nb_front_notch_z, -front_notch_size_z, -thickness, burn, 1)
        path.LineTo(0, -thickness)
        path.Close()
        path.GenPath()

    def gen_side_Steel(self, flag_right, length, top_notch_size_x, nb_top_notch_x, height, notch_size_z, nb_notch_z, delta_z,  thickness, burn, xOffset, yOffset, parent):
        '''
        Generate lid side with integrated hinge. This is a rectangle with notches on 3 edges
        No notch on the top edge
        '''
        if flag_right > 0:
            path = inkcape_path((xOffset, yOffset), parent, 'Right')
        else:
            path = inkcape_path((xOffset, yOffset), parent, 'Left')       
        #first H line (top) witout notches
        path.MoveTo(0, 0)
        path.LineTo(length, 0)
        #Draw vertical notches 
        path.LineTo(length, delta_z)
        if nb_notch_z > 0:
            self.drawLineVNotches(path, nb_notch_z, notch_size_z, thickness, burn, 1)
        path.LineTo(length, height+thickness)
        #Third line (H) with notches
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, -thickness, burn, -1)
        path.LineTo(0, height+thickness)
        path.LineTo(0, height)
        #draw front notches
        if nb_notch_z > 0:
            self.drawLineVNotches(path, nb_notch_z, -notch_size_z, -thickness, burn, 1)
        path.LineTo(0, 0)
        path.Close()
        path.GenPath()

    def gen_lid_back_Steel(self, length, top_notch_size_x, nb_top_notch_x, height, top_notch_size_z, nb_top_notch_z, nbHinge, FirstHingePos, SecondHingePos, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate lid back when steel apparent hinge. This is a rectangle with notches on 3 edges, bottom has no notch
        There is notches for the hinge
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'Lid_back')
        path.MoveTo(-thickness, -thickness)
        #first H line with notches
        path.LineTo(0, -thickness)
        self.drawLineHNotches(path, nb_top_notch_x, top_notch_size_x, thickness, burn, -1)
        path.LineTo(length+thickness, -thickness)
        #Second line (V)
        path.LineTo(length+thickness, 0)
        if nb_top_notch_z > 0:
            self.drawLineVNotches(path, nb_top_notch_z, top_notch_size_z, -thickness, burn, -1)
        path.LineTo(length+thickness, height)
        #Third line (H) without notches
        if nbHinge > 1:
            #First H line up to end of 2nd hinge
            path.LineTo(SecondHingePos + 5*thickness + 2.5*SteelHingeSpacing, height)
            #Then Hinge
            path.LineToVRel(-1.5*thickness - 0.5*SteelHingeSpacing)
            path.LineToHRel(-thickness - SteelHingeSpacing)
            path.LineToVRel(-thickness + 0.5*SteelHingeSpacing)
            path.LineToHRel(-thickness)
            path.LineToVRel(thickness - 0.5*SteelHingeSpacing)
            path.LineToHRel(-thickness - SteelHingeSpacing)
            path.LineToVRel(-thickness + 0.5*SteelHingeSpacing)
            path.LineToHRel(-thickness)
            path.LineToVRel(thickness - 0.5*SteelHingeSpacing)
            path.LineToHRel(-thickness - SteelHingeSpacing)
            path.LineToVRel(1.5*thickness + 0.5*SteelHingeSpacing)
        #H Line up to end of first hinge
        path.LineTo(FirstHingePos + 5*thickness + 2.5*SteelHingeSpacing, height)
        #Then Hinge
        path.LineToVRel(-1.5*thickness - 0.5*SteelHingeSpacing)
        path.LineToHRel(-thickness - SteelHingeSpacing)
        path.LineToVRel(-thickness + 0.5*SteelHingeSpacing)
        path.LineToHRel(-thickness)
        path.LineToVRel(thickness - 0.5*SteelHingeSpacing)
        path.LineToHRel(-thickness - SteelHingeSpacing)
        path.LineToVRel(-thickness + 0.5*SteelHingeSpacing)
        path.LineToHRel(-thickness)
        path.LineToVRel(thickness - 0.5*SteelHingeSpacing)
        path.LineToHRel(-thickness - SteelHingeSpacing)
        path.LineToVRel(1.5*thickness + 0.5*SteelHingeSpacing)
        path.LineTo(-thickness, height)
        #and last one
        if nb_top_notch_z > 0:
            self.drawLineVNotches(path, nb_top_notch_z, -top_notch_size_z, thickness, burn, -1)
        path.LineTo(-thickness, -thickness)
        #Now draw holes for hinge elements
        path.MoveTo(FirstHingePos + thickness + 0.5*SteelHingeSpacing, height - 3.5*thickness)
        path.LineToHRel(thickness)
        path.LineToVRel(-thickness)
        path.LineToHRel(-thickness)
        path.LineToVRel(thickness)
        path.MoveTo(FirstHingePos + 3*thickness + 1.5*SteelHingeSpacing, height - 3.5*thickness)
        path.LineToHRel(thickness)
        path.LineToVRel(-thickness)
        path.LineToHRel(-thickness)
        path.LineToVRel(thickness)
        if nbHinge > 1:
            path.MoveTo(SecondHingePos + thickness + 0.5*SteelHingeSpacing, height - 3.5*thickness)
            path.LineToHRel(thickness)
            path.LineToVRel(-thickness)
            path.LineToHRel(-thickness)
            path.LineToVRel(thickness)
            path.MoveTo(SecondHingePos + 3*thickness + 1.5*SteelHingeSpacing, height - 3.5*thickness)
            path.LineToHRel(thickness)
            path.LineToVRel(-thickness)
            path.LineToHRel(-thickness)
            path.LineToVRel(thickness)
        path.Close()
        path.GenPath()

    def gen_back_Steel(self, length, top_notch_size_x, nb_top_notch_x, height, notch_size_z, nb_notch_z, nbHinge, FirstHingePos, SecondHingePos, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate back with apparent steel hinge. This is a rectangle with notches on 3 edges, bottom has no notch
        There is notches for the hinge
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'Back')
        path.MoveTo(-thickness, 0)
        #First line is H and has notches for the hinge
        #H Line up to start of first hinge
        path.LineTo(FirstHingePos, 0)
        #Then Hinge
        path.LineToVRel(2.5*thickness)
        path.LineToHRel(thickness)
        path.LineToVRel(-thickness + 0.5*SteelHingeSpacing)
        path.LineToHRel(thickness + SteelHingeSpacing)
        path.LineToVRel(thickness - 0.5*SteelHingeSpacing)
        path.LineToHRel(thickness)
        path.LineToVRel(-thickness + 0.5*SteelHingeSpacing)
        path.LineToHRel(thickness + SteelHingeSpacing)
        path.LineToVRel(thickness - 0.5*SteelHingeSpacing)
        path.LineToHRel(thickness)
        path.LineToVRel(-2.5*thickness)
        if nbHinge > 1:
            #Then line up to start of second hinge
            path.LineTo(SecondHingePos, 0)
            #Then Hinge
            path.LineToVRel(2.5*thickness)
            path.LineToHRel(thickness)
            path.LineToVRel(-thickness + 0.5*SteelHingeSpacing)
            path.LineToHRel(thickness + SteelHingeSpacing)
            path.LineToVRel(thickness - 0.5*SteelHingeSpacing)
            path.LineToHRel(thickness)
            path.LineToVRel(-thickness + 0.5*SteelHingeSpacing)
            path.LineToHRel(thickness + SteelHingeSpacing)
            path.LineToVRel(thickness - 0.5*SteelHingeSpacing)
            path.LineToHRel(thickness)
            path.LineToVRel(-2.5*thickness)
        #Then line up to length
        path.LineTo(length+thickness, 0)
        #Second line (V)
        if nb_notch_z > 0:
            self.drawLineVNotches(path, nb_notch_z, notch_size_z, -thickness, burn, -1)
        path.LineTo(length+thickness, height+thickness)
        #Third line (H) with notches
        path.LineTo(length, height+thickness)
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, -thickness, burn, -1)
        path.LineTo(-thickness, height+thickness)
        #and last one
        path.LineTo(-thickness, height)
        if nb_notch_z > 0:
            self.drawLineVNotches(path, nb_notch_z, -notch_size_z, thickness, burn, -1)
        path.LineTo(-thickness, 0)
        #Now draw holes for hinge elements
        path.MoveTo(FirstHingePos, 4.5*thickness)
        path.LineToHRel(thickness)
        path.LineToVRel(-thickness)
        path.LineToHRel(-thickness)
        path.LineToVRel(thickness)
        path.MoveTo(FirstHingePos + 2*thickness + SteelHingeSpacing, 4.5*thickness)
        path.LineToHRel(thickness)
        path.LineToVRel(-thickness)
        path.LineToHRel(-thickness)
        path.LineToVRel(thickness)
        path.MoveTo(FirstHingePos + 4*thickness + 2*SteelHingeSpacing, 4.5*thickness)
        path.LineToHRel(thickness)
        path.LineToVRel(-thickness)
        path.LineToHRel(-thickness)
        path.LineToVRel(thickness)
        if nbHinge > 1:
            path.MoveTo(SecondHingePos, 4.5*thickness)
            path.LineToHRel(thickness)
            path.LineToVRel(-thickness)
            path.LineToHRel(-thickness)
            path.LineToVRel(thickness)
            path.MoveTo(SecondHingePos + 2*thickness + SteelHingeSpacing, 4.5*thickness)
            path.LineToHRel(thickness)
            path.LineToVRel(-thickness)
            path.LineToHRel(-thickness)
            path.LineToVRel(thickness)
            path.MoveTo(SecondHingePos + 4*thickness + 2*SteelHingeSpacing, 4.5*thickness)
            path.LineToHRel(thickness)
            path.LineToVRel(-thickness)
            path.LineToHRel(-thickness)
            path.LineToVRel(thickness)
        path.Close()
        path.GenPath()


    def gen_back_ExternalHiddenSteel(self, length, top_notch_size_x, nb_top_notch_x, height, notch_size_z, nb_notch_z, zlid, notch_size_lid_z, nb_notch_lid_z, nbHingeJoint, HingeFingerSize, HingePos, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate back and lid back with hidden steel hinge. There is only one rectangle for the 2 pieces, with a single cut betwwen back and lid
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'Back_External')
        #Internal and external parts share the same outside.
        path.MoveTo(-thickness, -thickness)
        #Lid top has notches
        path.LineTo(0, -thickness)
        self.drawLineHNotches(path, nb_top_notch_x, top_notch_size_x, thickness, burn, -1)
        path.LineTo(length+thickness, -thickness)
        #Lid vertical right 
        path.LineTo(length+thickness, -0)
        if nb_notch_lid_z > 0:
            self.drawLineVNotches(path, nb_notch_lid_z, notch_size_lid_z, -thickness, burn, -1)
        path.LineTo(length+thickness, zlid)
        #Now the right vertical for the box
        if nb_notch_z > 0:
            self.drawLineVNotches(path, nb_notch_z, notch_size_z, -thickness, burn, -1)
        path.LineTo(length+thickness, zlid+height+thickness)
        #Horizontal line for the bottom of the box
        path.LineTo(length, zlid+height+thickness)
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, -thickness, burn, -1)
        path.LineTo(-thickness, zlid+height+thickness)
        #Left vertical line for the box
        path.LineTo(-thickness, zlid+height)
        if nb_notch_z > 0:
            self.drawLineVNotches(path, nb_notch_z, -notch_size_z, thickness, burn, -1)
        path.LineTo(-thickness, zlid)
        #Left vertical line for the lid
        if nb_notch_lid_z > 0:
            self.drawLineVNotches(path, nb_notch_lid_z, -notch_size_lid_z, thickness, burn, -1)
        path.LineTo(-thickness, -thickness)
        #Draw the line between lid and box, joint height is 4*thickness
        #DeltaZ is used to take into account the fact that the axis is internal
        #DeltaZ1 is used at the start of cut, it is more important because the axis is nearer
        #I choose to not take into account the fact that the axis is shifted by HiddenSteelAxisSize/2, the difference is very small (about 0.1mm)
        DeltaZ = (2.0 - math.sqrt(3.0))*thickness
        DeltaZ1 = thickness - DeltaZ

        path.MoveTo(-thickness, zlid+DeltaZ1)
        path.LineToHRel(4*thickness)
        path.LineTo(3*thickness, zlid-2*thickness)
        path.LineTo(HingePos, zlid - 2*thickness)
        #Draw the joints
        zmove = 4*thickness
        for i in range(nbHingeJoint):
            path.LineToVRel(zmove)
            zmove = -zmove
            path.LineToHRel(HingeFingerSize)
        path.LineToVRel(zmove)
        path.LineTo(length-3*thickness, zlid - 2*thickness)
        path.LineTo(length-3*thickness, zlid+DeltaZ1)
        path.LineTo(length+thickness, zlid+DeltaZ1)
        #First the lines used to cut extra length in the box
        Zline = zlid - 2*thickness + DeltaZ
        path.MoveTo(-thickness, zlid - DeltaZ)
        path.LineTo(3*thickness, zlid - DeltaZ)
        path.MoveTo(3*thickness, Zline)
        path.LineTo(HingePos, Zline)
        for i in range(nbHingeJoint//2):
            path.MoveTo(HingePos + (2*i+1)*HingeFingerSize, Zline)
            path.LineToHRel(HingeFingerSize)
        path.MoveTo(HingePos + nbHingeJoint*HingeFingerSize, Zline)
        path.LineTo(length-3*thickness, Zline)
        path.MoveTo(length-3*thickness, zlid - DeltaZ)
        path.LineTo(length+thickness, zlid - DeltaZ)
        #Then The lines used to cut extra length in the lid
        Zline = zlid + 2*thickness - DeltaZ
        for i in range(nbHingeJoint//2 + 1):
            path.MoveTo(HingePos + (2*i)*HingeFingerSize, Zline)
            path.LineToHRel(HingeFingerSize)
        path.GenPath()
        #Then Generate a second path for the rectangle which should be engraved
        path = inkcape_path((xOffset, yOffset), parent, 'Back_engraving', objStyleEngraving)
        XStart = (HingePos + 3*thickness) / 2
        XEnd = length - XStart
        path.MoveTo( XStart, zlid - HiddenSteelAxisSize/2)
        path.LineToHRel(XEnd - XStart)
        path.LineToVRel(HiddenSteelAxisSize)
        path.LineToHRel(XStart - XEnd)
        path.LineToVRel(-HiddenSteelAxisSize)
        path.Close()
        path.GenPath()
        
    def gen_back_InternalHiddenSteel(self, length, top_notch_size_x, nb_top_notch_x, height, notch_size_z, nb_notch_z, zlid, notch_size_lid_z, nb_notch_lid_z, nbHingeJoint, HingeFingerSize, HingePos, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate back and lid back with hidden steel hinge. There is only one rectangle for the 2 pieces, with a single cut betwwen back and lid
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'Back_Internal')
        path.MoveTo(0, 0)
        #There is no notches on internal part
        path.LineTo(length, 0)
        #Lid vertical right 
        path.LineTo(length, zlid)
        path.LineTo(length, zlid+height)
        #Horizontal line for the bottom of the box
        path.LineTo(0, zlid+height)
        #Left vertical line for the box
        path.LineTo(0, zlid)
        #Left vertical line for the lid
        path.LineTo(0, 0)
        #Draw the line between lid and box, joint height is 4*thickness
        path.MoveTo(0, zlid)
        path.LineToHRel(3*thickness)
        path.LineToVRel(-2*thickness)
        path.LineTo(HingePos, zlid - 2*thickness)
        #Draw the joints
        zmove = 4*thickness
        for i in range(nbHingeJoint):
            path.LineToVRel(zmove)
            zmove = -zmove
            path.LineToHRel(HingeFingerSize)
        path.LineToVRel(zmove)
        path.LineTo(length-3*thickness, zlid - 2*thickness)
        path.LineTo(length-3*thickness, zlid)
        path.LineTo(length, zlid)
        path.GenPath()


    def effect(self):
        """
        Draws a card box box, based on provided parameters
        """


        # convert units
        unit = self.options.unit
        zbox = self.unittouu(str(self.options.z) + unit)
        zlid = self.unittouu(str(self.options.z_lid) + unit)
        xbox = self.unittouu(str(self.options.x) + unit)
        ybox = self.unittouu(str(self.options.y) + unit)
        thickness = self.unittouu(str(self.options.thickness) + unit)
        burn = self.unittouu(str(self.options.burn) + unit)
        box_lid_type = self.options.lid_type


        # Select final dimensions, using inner_size variables. If Outer_size, decrease dimensions.
        if self.options.inner_size == False:
            xbox -= 2*thickness
            ybox -= 2*thickness
            zbox -= 2*thickness
            
        if box_lid_type == 'HiddenSteel':
            ybox += thickness           #Two back plates, so add extra size in Y

        # input sanity check
        error = False
        if xbox < 30:
            inkex.errormsg('Error: min box length should be 30 mm')
            error = True

        if ybox < 30:
            inkex.errormsg('Error: min box width should be 30 mm')
            error = True

        if zbox < 20:
            inkex.errormsg('Error: min box height should be 20 mm')
            error = True

        if thickness <  1 or thickness >  10:
            inkex.errormsg('Error: thickness should be at least 1mm and less than 10mm')
            error = True

        if box_lid_type == 'IntegratedWood' and zlid < 4*thickness:
            inkex.errormsg('Error: lid height should be at least  4 times wood thickness with this hinge')
            error = True

        if box_lid_type == 'Steel' and zlid < 5*thickness:
            inkex.errormsg('Error: lid height should be at least 5 times wood thickness with this hinge')
            error = True

        if box_lid_type == 'Steel' and zbox < 5*thickness:
            inkex.errormsg('Error: box height should be at least 5 times wood thickness with this hinge')
            error = True

        if box_lid_type == 'HiddenSteel' and zlid < 3*thickness:
            inkex.errormsg('Error: lid height should be at least 3 times wood thickness for hidden hinge')
            error = True

        if box_lid_type == 'HiddenSteel' and xbox < 10*thickness:
            inkex.errormsg('Error: box length should be at least 10 times wood thickness for hidden hinge')
            error = True

        if error:
            exit()

        svg = self.document.getroot()
        docWidth = self.unittouu(svg.get('width'))
        docHeigh = self.unittouu(svg.attrib['height'])

        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'Coffin Box')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        group = inkex.etree.SubElement(layer, 'g')
        try:
            self.fDebug = open( 'DebugCoffinBox.txt', 'w')
        except IOError:
            print ('cannot open debug output file')
        self.DebugMsg("Start processing\n")

        #compute notch size for x and y
        internal_length = min(xbox, ybox)
        if internal_length < 27*thickness:
            nb_top_notch_x = int((xbox-5) / (2.8*thickness))
            top_notch_size_x = xbox/(2*nb_top_notch_x+1)
            nb_top_notch_y = int((ybox-5) / (2.8*thickness))
            top_notch_size_y = ybox/(2*nb_top_notch_y+1)
        elif internal_length < 50*thickness:
            nb_top_notch_x = int((xbox-5) / (4*thickness))
            top_notch_size_x = xbox/(2*nb_top_notch_x+1)
            nb_top_notch_y = int((ybox-5) / (4*thickness))
            top_notch_size_y = ybox/(2*nb_top_notch_y+1)
        else:
            nb_top_notch_x = int((xbox-5) / (5*thickness))
            top_notch_size_x = xbox/(2*nb_top_notch_x+1)
            nb_top_notch_y = int((ybox-5) / (5*thickness))
            top_notch_size_y = ybox/(2*nb_top_notch_y+1)
        #compute notch size for z, this is dependent of lid type
        if box_lid_type == 'IntegratedWood':
            if zbox < 27*thickness:
                nb_notch_z = int((zbox-5) / (2.8*thickness))
                size_notch_z = zbox/(2*nb_notch_z+1)
                nb_notch_z_back = int((zbox-4*thickness-5) / (2.8*thickness))
                size_notch_z_back = (zbox-4*thickness)/(2*nb_notch_z_back+1)
            elif zbox < 50*thickness:
                nb_notch_z = int((zbox-5) / (4*thickness))
                size_notch_z = zbox/(2*nb_notch_z+1)
                nb_notch_z_back = int((zbox-4*thickness-5) / (4*thickness))
                size_notch_z_back = (zbox-4*thickness)/(2*nb_notch_z_back+1)
            else:
                nb_notch_z = int((zbox-5) / (5*thickness))
                size_notch_z = zbox/(2*nb_notch_z+1)
                nb_notch_z_back = int((zbox-4*thickness-5) / (5*thickness))
                size_notch_z_back = (zbox-4*thickness)/(2*nb_notch_z_back+1)
            #Set notches size equal to have a better look
            minsizenotch = min(size_notch_z, size_notch_z_back)
            size_notch_z = minsizenotch
            size_notch_z_back = minsizenotch
            nb_notch_z = int(((zbox / size_notch_z) - 1)/2)
            nb_notch_z_back = int((((zbox-4*thickness) / size_notch_z_back) - 1)/2)
            delta_z = zbox - ((2*nb_notch_z+1)*size_notch_z)
            delta_z_back = zbox - ((2*nb_notch_z_back+1)*size_notch_z_back)         
        else:
            if zbox < 27*thickness:
                nb_notch_z = int((zbox-5) / (2.8*thickness))
                size_notch_z = zbox/(2*nb_notch_z+1)
            elif zbox < 50*thickness:
                nb_notch_z = int((zbox-5) / (4*thickness))
                size_notch_z = zbox/(2*nb_notch_z+1)
            else:
                nb_notch_z = int((zbox-5) / (5*thickness))
                size_notch_z = zbox/(2*nb_notch_z+1)
            nb_notch_z_back = 0
            size_notch_z_back = 0
            delta_z = 0
            delta_z_back = 0
        #compute z and lid notch length, height and number, this is dependent to lid type
        if box_lid_type == 'IntegratedWood':
            if zlid < 8*thickness:
                nb_notch_lid_front_z = 1
                size_notch_lid_front_z =  zlid/(2*nb_notch_lid_front_z+1)
                nb_notch_lid_back_z = 0
                size_notch_lid_back_z = 0
            elif zlid < 13*thickness:
                nb_notch_lid_front_z = int((zlid) / (2.8*thickness))
                size_notch_lid_front_z = zlid/(2*nb_notch_lid_front_z+1)
                nb_notch_lid_back_z = 0
                size_notch_lid_back_z = 0
            elif zlid < 27*thickness:
                nb_notch_lid_front_z = int((zlid) / (2.8*thickness))
                size_notch_lid_front_z = zlid/(2*nb_notch_lid_front_z+1)
                nb_notch_lid_back_z = int((zlid-4*thickness-5) / (2.8*thickness))
                size_notch_lid_back_z = (zlid - 4*thickness)/(2*nb_notch_lid_back_z+1)
            elif zlid < 50*thickness:
                nb_notch_lid_front_z = int((zlid-5) / (4*thickness))
                size_notch_lid_front_z = zlid/(2*nb_notch_lid_front_z+1)
                nb_notch_lid_back_z = int((zlid-4*thickness-5) / (5*thickness))
                size_notch_lid_back_z = (zlid - 4*thickness)/(2*nb_notch_lid_back_z+1)
            else:
                nb_notch_lid_front_z = int((zlid-5) / (4*thickness))
                size_notch_lid_front_z = zlid/(2*nb_notch_lid_front_z+1)
                nb_notch_lid_back_z = int((zlid-4*thickness-5) / (5*thickness))
                size_notch_lid_back_z = (zlid - 4*thickness)/(2*nb_notch_lid_back_z+1)
            if nb_notch_lid_back_z > 0:
                minsizenotch = min(size_notch_lid_front_z, size_notch_lid_back_z)
                size_notch_lid_front_z = minsizenotch
                size_notch_lid_back_z = minsizenotch
                nb_notch_lid_front_z = int(((zlid / size_notch_lid_front_z) - 1)/2)
                nb_notch_lid_back_z = int((((zlid-4*thickness) / size_notch_lid_back_z) - 1)/2)
                delta_lid_front_z = zlid - ((2*nb_notch_lid_front_z+1)*size_notch_lid_front_z)
                delta_lid_back_z = zlid - ((2*nb_notch_lid_back_z+1)*size_notch_lid_back_z)   
            else:
                delta_lid_front_z = 0
                delta_lid_back_z = 4*thickness
        else:
            if zlid < 6*thickness:
                nb_notch_lid_front_z = 1
                size_notch_lid_front_z = zlid/(2*nb_notch_lid_front_z+1)
            elif zlid < 27*thickness:
                nb_notch_lid_front_z = int((zlid-5) / (2.8*thickness))
                size_notch_lid_front_z = zlid/(2*nb_notch_lid_front_z+1)
            elif zlid < 50*thickness:
                nb_notch_lid_front_z = int((zlid-5) / (4*thickness))
                size_notch_lid_front_z = zlid/(2*nb_notch_lid_front_z+1)
            else:
                nb_notch_lid_front_z = int((zlid-5) / (5*thickness))
                size_notch_lid_front_z = zlid/(2*nb_notch_lid_front_z+1)
            nb_notch_lid_back_z = nb_notch_lid_front_z
            size_notch_lid_back_z = size_notch_lid_front_z
            delta_lid_front_z = 0
            delta_lid_back_z = 0
        self.DebugMsg("xbox="+str(xbox)+" nb_top_notch_x="+str(nb_top_notch_x)+"  top_notch_size_x="+str(top_notch_size_x)+"\n")
        self.DebugMsg("ybox="+str(ybox)+" nb_top_notch_y="+str(nb_top_notch_y)+"  top_notch_size_y="+str(top_notch_size_y)+"\n")
        self.DebugMsg("zbox="+str(zbox)+" nb_notch_z="+str(nb_notch_z)+"  size_notch_z="+str(size_notch_z)+" nb_notch_z_back="+str(nb_notch_z_back)+"  size_notch_z_back="+str(size_notch_z_back)+"\n")
        self.DebugMsg("zlid="+str(zlid)+" nb_notch_lid_front_z="+str(nb_notch_lid_front_z)+"  size_notch_lid_front_z="+str(size_notch_lid_front_z)+" nb_notch_lid_back_z="+str(nb_notch_lid_back_z)+"  size_notch_lid_back_z="+str(size_notch_lid_back_z)+"\n")
        self.DebugMsg("delta_z="+str(delta_z)+" delta_z_back="+str(delta_z_back)+"\n")
        self.DebugMsg("delta_lid_front_z="+str(delta_lid_front_z)+" delta_lid_back_z="+str(delta_lid_back_z)+"\n")

        #generate top and bottom
        self.gen_top_bottom('Top', xbox, top_notch_size_x, nb_top_notch_x, ybox, top_notch_size_y, nb_top_notch_y, thickness, burn, 0, 0, group)
        self.gen_top_bottom('Bottom', xbox, top_notch_size_x, nb_top_notch_x, ybox, top_notch_size_y, nb_top_notch_y, thickness, burn, -xbox - 2*thickness - 2, 0, group)
        #Gen lid front
        self.gen_lid_front('Lid_Front', xbox, top_notch_size_x, nb_top_notch_x, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, delta_lid_front_z, thickness, burn, 0 , -ybox - 2*thickness - 2, group)
        #Gen front
        self.gen_front('Front', xbox, top_notch_size_x, nb_top_notch_x, zbox, size_notch_z, nb_notch_z, delta_z, thickness, burn, 0 , -ybox - zlid - 2*thickness - 4, group)

        #Other sides are dependent on the lid type.
        
        if box_lid_type == 'IntegratedWood':
            #Generate lid back
            self.gen_lid_back_IntegratedWood('Lid_Back', xbox, top_notch_size_x, nb_top_notch_x, zlid, size_notch_lid_back_z, nb_notch_lid_back_z, delta_lid_back_z, thickness, burn, -xbox - 2*thickness - 2 , -ybox - 2*thickness - 2, group)
            #Gen back
            self.gen_back_IntegratedWood('Back', xbox, top_notch_size_x, nb_top_notch_x, zbox, size_notch_z_back, nb_notch_z_back, delta_z_back, thickness, burn, -xbox - 2*thickness - 2 , -ybox - zlid - 2*thickness - 4, group)
            # Now generate sides, Right lid first
            self.gen_lid_side_IntegratedWood(1, ybox, top_notch_size_y, nb_top_notch_y, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, delta_lid_front_z, size_notch_lid_back_z, nb_notch_lid_back_z, delta_lid_back_z, thickness, burn, 0 , -ybox - zbox -zlid - 4*thickness - 6, group)
            # Then right lid
            self.gen_lid_side_IntegratedWood(0, ybox, top_notch_size_y, nb_top_notch_y, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, delta_lid_front_z, size_notch_lid_back_z, nb_notch_lid_back_z, delta_lid_back_z, thickness, burn, -ybox - 8*thickness - 3 , -ybox - zbox -zlid - 4*thickness - 6, group)
            # and last, left side and right side
            self.gen_side_IntegratedWood_Right(ybox, top_notch_size_y, nb_top_notch_y, zbox, size_notch_z, nb_notch_z, delta_z, size_notch_z_back, nb_notch_z_back, delta_z_back, thickness, burn, -1 , -ybox - zbox -2*zlid - 5*thickness - 5, group)
            self.gen_side_IntegratedWood_Left(ybox, top_notch_size_y, nb_top_notch_y, zbox, size_notch_z, nb_notch_z, delta_z, size_notch_z_back, nb_notch_z_back, delta_z_back, thickness, burn, -ybox - 8*thickness - 3 , -ybox - zbox -2*zlid - 5*thickness - 5, group)
        elif box_lid_type == 'Steel':
            #Compute placement of hinge
            hingeWidth = 5*thickness + 3*SteelHingeSpacing
            if ( hingeWidth > xbox - 10 ):
                inkex.errormsg('Error: min box length should be at least '+str(hingeWidth+10)+'mm')
                exit(1)
            if xbox > 2*hingeWidth + 30:
                nbHinge = 2         #2 hinge if box is sufficiently wide
                HingeSpacing = (xbox - 2*hingeWidth) * 0.75
                FirstHingePos = max(10, (xbox - 2*hingeWidth - HingeSpacing)*0.5)
                FirstHingePos = min(30, (xbox - 2*hingeWidth - HingeSpacing)*0.5)
                SecondHingePos = FirstHingePos + hingeWidth + HingeSpacing
            else:
                nbHinge = 1     #Only one hinge for small boxes
                FirstHingePos = (xbox - hingeWidth)/2.0
                SecondHingePos = 0
            #Generate lid back
            self.gen_lid_back_Steel(xbox, top_notch_size_x, nb_top_notch_x, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, nbHinge, FirstHingePos, SecondHingePos, thickness, burn, -xbox - 2*thickness - 2 , -ybox - 2*thickness - 2, group)
            #Gen back
            self.gen_back_Steel(xbox, top_notch_size_x, nb_top_notch_x, zbox, size_notch_z, nb_notch_z, nbHinge, FirstHingePos, SecondHingePos, thickness, burn, -xbox - 2*thickness - 2 , -ybox - zlid - 2*thickness - 4, group)
            # Now generate sides, Right lid first
            self.gen_lid_side_Steel(1, ybox, top_notch_size_y, nb_top_notch_y, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, delta_lid_front_z, thickness, burn, 0 , -ybox - zbox -zlid - 4*thickness - 6, group)
            # Then right lid
            self.gen_lid_side_Steel(0, ybox, top_notch_size_y, nb_top_notch_y, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, delta_lid_front_z, thickness, burn, -ybox - 2*thickness -2 , -ybox - zbox -zlid - 4*thickness - 6, group)
            # left side and right side
            self.gen_side_Steel(1, ybox, top_notch_size_y, nb_top_notch_y, zbox, size_notch_z, nb_notch_z, delta_z, thickness, burn, 0 , -ybox - zbox -2*zlid - 4*thickness - 8, group)
            self.gen_side_Steel(0, ybox, top_notch_size_y, nb_top_notch_y, zbox, size_notch_z, nb_notch_z, delta_z, thickness, burn, -ybox - 2*thickness -2 , -ybox - zbox -2*zlid - 4*thickness - 8, group)
            #and last the elements of the hinge
            for i in range(1,5*nbHinge+1):
                self.drawSteelHingeElement(i, thickness, i*(-3.5*thickness - 2) + 2*thickness, -ybox - 2*zbox -2*zlid - 5*thickness - 10, group)
        else:       #Hidden Steel
            #Compute placement of hinge
            hingeWidth = max(xbox * 0.8 - 6*thickness, xbox - 20 - 6*thickness)
            #now compute number of joints
            if hingeWidth <= 10*thickness:
                nbHingeJoint = int(hingeWidth/(1.5*thickness))
                nbHingeJoint |= 1           #Should be odd
                HingeJointSize = hingeWidth / nbHingeJoint
            elif hingeWidth <= 20*thickness:
                nbHingeJoint = int(hingeWidth/(2*thickness))
                nbHingeJoint |= 1           #Should be odd
                HingeJointSize = hingeWidth / nbHingeJoint
            elif hingeWidth <= 30*thickness:
                nbHingeJoint = int(hingeWidth/(3*thickness))
                nbHingeJoint |= 1           #Should be odd
                HingeJointSize = hingeWidth / nbHingeJoint
            elif hingeWidth <= 40*thickness:
                nbHingeJoint = int(hingeWidth/(4*thickness))
                nbHingeJoint |= 1           #Should be odd
                HingeJointSize = hingeWidth / nbHingeJoint
            else:
                nbHingeJoint = int(hingeWidth/(5*thickness))
                nbHingeJoint |= 1           #Should be odd
                HingeJointSize = hingeWidth / nbHingeJoint
            HingePos = (xbox - 6*thickness - hingeWidth) / 2 + 3*thickness
            self.DebugMsg("hingeWidth ="+str(hingeWidth)+", nbHingeJoint="+str(nbHingeJoint)+" HingeJointSize="+str(HingeJointSize)+" HingePos="+str(HingePos)+"\n")
            #Generate back  + Lid (Internal)
            self.gen_back_InternalHiddenSteel(xbox, top_notch_size_x, nb_top_notch_x, zbox, size_notch_z, nb_notch_z, zlid, size_notch_lid_back_z, nb_notch_lid_back_z, nbHingeJoint, HingeJointSize, HingePos, thickness, burn, -xbox - 2*thickness - 2 , -ybox - 2*thickness - 2, group)
            #Gen back + Lid (External)
            self.gen_back_ExternalHiddenSteel(xbox, top_notch_size_x, nb_top_notch_x, zbox, size_notch_z, nb_notch_z, zlid, size_notch_lid_back_z, nb_notch_lid_back_z, nbHingeJoint, HingeJointSize, HingePos, thickness, burn, -xbox - 2*thickness - 2 , -ybox -zbox - zlid - 4*thickness - 4, group)
            if xbox > ybox:
                # Now generate sides, Right lid first
                self.gen_lid_side_Steel(1, ybox, top_notch_size_y, nb_top_notch_y, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, delta_lid_front_z, thickness, burn, 0 , -ybox - zbox - zlid - 4*thickness - 6, group)
                # Right side and right side
                self.gen_side_Steel(1, ybox, top_notch_size_y, nb_top_notch_y, zbox, size_notch_z, nb_notch_z, delta_z, thickness, burn, 0 , -ybox - zbox -2*zlid - 4*thickness - 8, group)
                # Then left lid
                self.gen_lid_side_Steel(0, ybox, top_notch_size_y, nb_top_notch_y, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, delta_lid_front_z, thickness, burn, 0 , -ybox - 2*zbox -2*zlid - 6*thickness - 10, group)
                self.gen_side_Steel(0, ybox, top_notch_size_y, nb_top_notch_y, zbox, size_notch_z, nb_notch_z, delta_z, thickness, burn, 0 , -ybox - 2*zbox -3*zlid - 6*thickness - 12, group)
            else:
                # Now generate sides, Right lid first
                self.gen_lid_side_Steel(1, ybox, top_notch_size_y, nb_top_notch_y, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, delta_lid_front_z, thickness, burn, 0 , -ybox - 2*zbox - 2*zlid - 6*thickness - 6, group)
                # Right side
                self.gen_side_Steel(1, ybox, top_notch_size_y, nb_top_notch_y, zbox, size_notch_z, nb_notch_z, delta_z, thickness, burn, 0 , -ybox - 2*zbox -3*zlid - 6*thickness - 8, group)
                # Then left lid
                self.gen_lid_side_Steel(0, ybox, top_notch_size_y, nb_top_notch_y, zlid, size_notch_lid_front_z, nb_notch_lid_front_z, delta_lid_front_z, thickness, burn, -ybox - 2*thickness - 2 , -ybox - 2*zbox - 2*zlid - 6*thickness - 6, group)
                self.gen_side_Steel(0, ybox, top_notch_size_y, nb_top_notch_y, zbox, size_notch_z, nb_notch_z, delta_z, thickness, burn, -ybox - 2*thickness - 2 ,  -ybox - 2*zbox -3*zlid - 6*thickness - 8, group)

            
        #Close Debug file if open
        if self.fDebug:
            self.fDebug.close()


# Create effect instance and apply it.
effect = CoffinBox()
effect.affect()
