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
    def __init__(self, Offset, group, Label=None):
        self.offsetX = Offset[0]
        self.offsetY = Offset[1]
        self.Path = ''
        self.group = group
        self.Label = Label
    
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
        if self.Label:
            line_attribs = {'style': objStyle, 'id' : self.Label, 'd': self.Path}
        else:            
            line_attribs = {'style': objStyle, 'd': self.Path}
        inkex.etree.SubElement(self.group, inkex.addNS('path', 'svg'), line_attribs)
        
class CardBox(inkex.Effect):
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

        self.OptionParser.add_option('--n_slot', action = 'store',
          type = 'int', dest = 'n_slot', default = '2',
          help = 'Number of slots for cards')

        self.OptionParser.add_option('--z', action = 'store',
          type = 'float', dest = 'z', default = '40.0',
          help = "inner height")

        self.OptionParser.add_option('--y_card', action = 'store',
          type = 'float', dest = 'y_card', default = '89.0',
          help = "Cards' height")

        self.OptionParser.add_option('--x_card', action = 'store',
          type = 'float', dest = 'x_card', default = '58.0',
          help = "Cards' width")

        self.OptionParser.add_option('--burn', action = 'store',
          type = 'float', dest = 'burn', default = '0.1',
          help = 'laser burn size')

       
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

        
    def gen_top(self, length, top_notch_size, nb_top_notch, width, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate top element. This is a rectangle with notches on one x edge
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'TOP')
        path.MoveTo(0,-thickness)
        #first line with notches
        self.drawLineHNotches(path, nb_top_notch, top_notch_size, thickness, burn, -1)
        path.LineTo(length, -thickness)
        #then the three others edges of the rectangle
        path.LineTo(length, width)
        path.LineToHRel(-length)
        path.LineTo(0, -thickness)
            
        path.Close()
        path.GenPath()

    def gen_bottom(self, n_slots, x_card, length, top_notch_size_x, nb_top_notch_x, width, top_notch_size_y, nb_top_notch_y, thickness, burn, xOffset, yOffset, parent):
        '''
        Generate bottom element. This is a rectangle with notches on all edges
        We also need to draw holes in this element to accept the "walls" between card slots
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'BOTTOM')
        path.MoveTo(0,0)
        #first H line with notches
        self.drawLineHNotches(path, nb_top_notch_x, top_notch_size_x, -thickness, burn, 1)
        path.LineTo(length, 0)
        
        #then the second edge of the rectangle
        self.drawLineVNotches(path, nb_top_notch_y, top_notch_size_y, thickness, burn, 1)
        path.LineTo(length, width)

        #then third edge
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, thickness, burn, 1)
        path.LineTo(0, width)

        #and the last one
        self.drawLineVNotches(path, nb_top_notch_y, -top_notch_size_y, -thickness, burn, 1)
        path.LineTo(0, 0)

        #now the holes used to fix the walls
        for i in range(1, n_slots):
            #For each wall, draw holes corresponding at each notch_y
            for j in range(nb_top_notch_y):
                self.drawHole(path, i*(x_card+thickness), j*2*top_notch_size_y + top_notch_size_y, thickness, top_notch_size_y, burn)
            
        path.Close()
        path.GenPath()

    def gen_front(self, n_slots, x_card, length, top_notch_size_x, nb_top_notch_x, zbox, edge_notch_size, nb_edge_notch, thickness, burn, xOffset, yOffset, parent):
        '''
        box front, this is is a rectangle with notches on 3 edges (not on top) and with holes for the walls
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'FRONT')
        path.MoveTo(-thickness,0)
        #first H line without notches
        path.LineTo(length+thickness, 0)
        #Second line (V)
        path.LineTo(length+thickness, 3*thickness)
        self.drawLineVNotches(path, nb_edge_notch, edge_notch_size, -thickness, burn, -1)
        path.LineTo(length+thickness, zbox+2*thickness)
        #Third line (H) with notches
        path.LineTo(length, zbox+2*thickness)
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, -thickness, burn, -1)
        path.LineTo(-thickness, zbox+2*thickness)
        #and last one
        path.LineTo(-thickness, zbox-thickness)
        self.drawLineVNotches(path, nb_edge_notch, -edge_notch_size, thickness, burn, -1)
        path.LineTo(-thickness, 0)

        #now the holes used to fix the walls
        for i in range(1, n_slots):
            #For each wall, draw holes corresponding at each edge_notch
            for j in range(nb_edge_notch):
                self.drawHole(path, i*(x_card+thickness), j*2*edge_notch_size + edge_notch_size+2*thickness, thickness, edge_notch_size, burn)

        path.Close()
        path.GenPath()
        
    def gen_back(self, n_slots, x_card, length, top_notch_size_x, nb_top_notch_x, zbox, edge_notch_size, nb_edge_notch, thickness, burn, xOffset, yOffset, parent):
        '''
        box back, this is is a rectangle with notches on 3 edges (not on top) and with holes for the walls
        Last edge has a cut able to accept top side
        '''
        path = inkcape_path((xOffset, yOffset), parent, 'BACK')
        path.MoveTo(-thickness, thickness)
        #first H line without notches
        path.LineToHRel(thickness)
        path.LineToVRel(thickness)
        path.LineToHRel(length)
        path.LineToVRel(-thickness)
        path.LineTo(length+thickness, thickness)
        #Second line (V)
        path.LineTo(length+thickness, 3*thickness)
        self.drawLineVNotches(path, nb_edge_notch, edge_notch_size, -thickness, burn, -1)
        path.LineTo(length+thickness, zbox+2*thickness)
        #Third line (H) with notches
        path.LineTo(length, zbox+2*thickness)
        self.drawLineHNotches(path, nb_top_notch_x, -top_notch_size_x, -thickness, burn, -1)
        path.LineTo(-thickness, zbox+2*thickness)
        #and last one
        path.LineTo(-thickness, zbox-thickness)
        self.drawLineVNotches(path, nb_edge_notch, -edge_notch_size, thickness, burn, -1)
        path.LineTo(-thickness, thickness)

        #now the holes used to fix the walls
        for i in range(1, n_slots):
            #For each wall, draw holes corresponding at each edge_notch
            for j in range(nb_edge_notch):
                self.drawHole(path, i*(x_card+thickness), j*2*edge_notch_size + edge_notch_size+2*thickness, thickness, edge_notch_size, burn)

        path.Close()
        path.GenPath()

    def gen_side(self, id_path, y_card, top_notch_size_y, nb_top_notch_y, zbox, edge_notch_size, nb_edge_notch, thickness, burn, xOffset, yOffset, parent):
        '''
        box side, this is is a rectangle with notches on all edges
        '''
        path = inkcape_path((xOffset, yOffset), parent, id_path)
        path.MoveTo(0,-thickness)
        #first H line with notches
        self.drawLineHNotches(path, nb_top_notch_y, top_notch_size_y, thickness, burn, -1)
        path.LineTo(y_card, -thickness)
        #Second line (V)
        path.LineTo(y_card, 2*thickness)
        self.drawLineVNotches(path, nb_edge_notch, edge_notch_size, thickness, burn, 1)
        path.LineTo(y_card, zbox+thickness)
        #Third line (H)
        self.drawLineHNotches(path, nb_top_notch_y, -top_notch_size_y, -thickness, burn, -1)
        path.LineTo(0, zbox+thickness)
        #and last one
        path.LineTo(0, zbox-2*thickness)
        self.drawLineVNotches(path, nb_edge_notch, -edge_notch_size, -thickness, burn, 1)
        path.LineTo(0, 0)

        
        path.Close()
        path.GenPath()

    def gen_internal_wall(self, index, y_card, top_notch_size_y, nb_top_notch_y, zbox, edge_notch_size, nb_edge_notch, thickness, burn, xOffset, yOffset, parent):
        '''
        box internal wall, this is is a rectangle with notches on 3 edges and an opening
        '''
        opening_size = 20
        if y_card < 30:
            opening_size = y_card * 0.7
        elif y_card > 100:
            opening_size = y_card * 0.2
        z_opening = opening_size / 2
        if z_opening > (zbox - thickness)*0.75:
            z_opening = (zbox - thickness)*0.75
        path = inkcape_path((xOffset, yOffset), parent, 'WALL_'+str(index+1))
        path.MoveTo(0,0)
        #first H line up to opening
        path.LineToHRel((y_card - opening_size)/2)
        #Then draw opening
        path.LineToVRel(zbox-z_opening-thickness)
        #Then the curve
        path.Bezier((y_card - opening_size)/2, zbox-z_opening-thickness+z_opening*0.551916, y_card/2-opening_size*0.275958, zbox-thickness, y_card/2, zbox-thickness)
        path.Bezier( y_card/2+opening_size*0.275958, zbox-thickness, (y_card+opening_size)/2,  zbox-z_opening*(1-0.551916)-thickness, (y_card+opening_size)/2, zbox-z_opening-thickness)
        path.LineTo((y_card+opening_size)/2, 0)
        path.LineTo(y_card, 0)
        #Second line (V)
        self.drawLineVNotches(path, nb_edge_notch, edge_notch_size, thickness, burn, 1)
        path.LineTo(y_card, zbox)
        #Third line (H)
        self.drawLineHNotches(path, nb_top_notch_y, -top_notch_size_y, thickness, burn, 1)
        path.LineTo(0, zbox)
        #and last one
        path.LineTo(0, zbox-3*thickness)
        self.drawLineVNotches(path, nb_edge_notch, -edge_notch_size, -thickness, burn, 1)
        path.LineTo(0, 0)

        
        path.Close()
        path.GenPath()


    def gen_internal_side(self, id_path, y_card, zbox, thickness, xOffset, yOffset, parent):
        '''
        internal box side, this is is a rectangle with no notches but an opening in the top center
        '''
        opening_size = 20
        if y_card < 30:
            opening_size = y_card * 0.7
        elif y_card > 100:
            opening_size = y_card * 0.2
        z_opening = opening_size / 2
        if z_opening > (zbox - thickness)*0.75:
            z_opening = (zbox - thickness)*0.75
        path = inkcape_path((xOffset, yOffset), parent, id_path)
        path.MoveTo(0,0)
        #first H line up to opening
        path.LineToHRel((y_card - opening_size)/2)
        #Then draw opening
        path.LineToVRel(zbox-z_opening-thickness)
        #Then the curve
        path.Bezier((y_card - opening_size)/2, zbox-z_opening-thickness+z_opening*0.551916, y_card/2-opening_size*0.275958, zbox-thickness, y_card/2, zbox-thickness)
        path.Bezier( y_card/2+opening_size*0.275958, zbox-thickness, (y_card+opening_size)/2,  zbox-z_opening*(1-0.551916)-thickness, (y_card+opening_size)/2, zbox-z_opening-thickness)
        path.LineTo((y_card+opening_size)/2, 0)
        path.LineTo(y_card, 0)
        #Second line (V)
        path.LineTo(y_card, zbox)
        #Third line (H)
        path.LineTo(0, zbox)
        #and last one
        path.LineTo(0, 0)
        
        path.Close()
        path.GenPath()

    def gen_hinge(self, id_path, delta_l, size, top_notch_size, nb_top_notch, thickness, burn, xOffset, yOffset, parent):
        '''
        side hinge, this is is a line of notches
        '''
        path = inkcape_path((xOffset, yOffset), parent, id_path)
        path.MoveTo(-delta_l,0)
        #first H line without notches
        path.LineTo(size+delta_l, 0)
        #Second line (V)
        path.LineTo(size+delta_l, thickness)
        if delta_l > 0:
            path.LineToHRel(-delta_l)
        #Third line (H)
        self.drawLineHNotches(path, nb_top_notch, -top_notch_size, thickness, burn, 1)
        path.LineTo(-delta_l, thickness)
        #and last one
        path.LineTo(-delta_l, 0)
        
        path.Close()
        path.GenPath()
 
    def effect(self):
        """
        Draws a card box box, based on provided parameters
        """

        # input sanity check
        error = False
        if self.options.x_card < 20:
            inkex.errormsg('Error: card size should be at least 20 x 20 mm')
            error = True

        if self.options.y_card < 20:
            inkex.errormsg('Error: card size should be at least 20 x 20 mm')
            error = True

        if self.options.thickness <  1 or self.options.thickness >  10:
            inkex.errormsg('Error: thickness should be at least 1mm and less than 10mm')
            error = True

        if error:
            exit()


        # convert units
        unit = self.options.unit
        n_slots = self.options.n_slot
        zbox = self.unittouu(str(self.options.z) + unit)
        x_card = self.unittouu(str(self.options.x_card) + unit)
        y_card = self.unittouu(str(self.options.y_card) + unit)
        thickness = self.unittouu(str(self.options.thickness) + unit)
        burn = self.unittouu(str(self.options.burn) + unit)

         
        svg = self.document.getroot()
        docWidth = self.unittouu(svg.get('width'))
        docHeigh = self.unittouu(svg.attrib['height'])

        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'Card Box')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        group = inkex.etree.SubElement(layer, 'g')
        try:
            self.fDebug = open( 'DebugCardBox.txt', 'w')
        except IOError:
            pass
        self.DebugMsg("Start processing\n")
        #compute total internal length
        internal_length = x_card * n_slots + (n_slots-1)*thickness + 2*thickness
        #compute top notch size_x
        if internal_length < 10:
            inkex.errormsg('Error: each edge should be at least 10mm long')
        elif internal_length < 20:      #  Only one notch
            nb_top_notch_x = 1
            top_notch_size_x = internal_length / 3
        elif internal_length < 80:
            nb_top_notch_x = int((internal_length-5) / 8)
            top_notch_size_x = internal_length/(2*nb_top_notch_x+1)
        elif internal_length < 150:
            nb_top_notch_x = int((internal_length-5) / 12)
            top_notch_size_x = internal_length/(2*nb_top_notch_x+1)
        else:
            nb_top_notch_x = int((internal_length-5) / 15)
            top_notch_size_x = internal_length/(2*nb_top_notch_x+1)
        #compute top notch size_y
        if y_card < 10:
            inkex.errormsg('Error: each edge should be at least 10mm long')
        elif y_card < 20:      #  Only one notch
            nb_top_notch_y = 1
            top_notch_size_y = y_card / 3
        elif y_card < 80:
            nb_top_notch_y = int((y_card-5) / 8)
            top_notch_size_y = y_card/(2*nb_top_notch_y+1)
        elif y_card < 150:
            nb_top_notch_y = int((y_card-5) / 12)
            top_notch_size_y = y_card/(2*nb_top_notch_y+1)
        else:
            nb_top_notch_y = int((y_card-5) / 15)
            top_notch_size_y = y_card/(2*nb_top_notch_y+1)

        #compute edge notch length, height and number
        if zbox < 10+4*thickness:
            inkex.errormsg('Error: box height too small, should be at least 4*thickness+10')
        elif zbox-4*thickness < 20:      #  Only one notch
            nb_edge_notch = 1
            edge_notch_size = (zbox-4*thickness) / 3
        elif zbox-4*thickness < 40:
            nb_edge_notch = int((zbox-4*thickness-5) / 8)
            edge_notch_size = (zbox-4*thickness)/(2*nb_edge_notch+1)
        elif zbox-4*thickness < 80:
            nb_edge_notch = int((zbox-4*thickness-5) / 12)
            edge_notch_size = (zbox-4*thickness)/(2*nb_edge_notch+1)
        else:
            nb_edge_notch = int((zbox-4*thickness-5) / 15)
            edge_notch_size = (zbox-4*thickness)/(2*nb_edge_notch+1)
        #generate top
        self.gen_top(internal_length, top_notch_size_x, nb_top_notch_x, y_card, thickness, burn, 0, 0, group)
        #generate bottom, drawingis right from previous one with 2 mm interval 
        self.gen_bottom(n_slots, x_card, internal_length, top_notch_size_x, nb_top_notch_x, y_card, top_notch_size_y, nb_top_notch_y, thickness, burn, -internal_length -thickness - 2, 0, group)
        #Generate front side, drawing is below the top
        self.gen_front(n_slots, x_card, internal_length, top_notch_size_x, nb_top_notch_x, zbox, edge_notch_size, nb_edge_notch, thickness, burn, 0, -y_card - 2, group)
        #Generate back side
        self.gen_back(n_slots, x_card, internal_length, top_notch_size_x, nb_top_notch_x, zbox, edge_notch_size, nb_edge_notch, thickness, burn, -internal_length - 2*thickness - 5, -y_card-thickness - 5, group)
        #generate left and right side
        self.gen_side('LEFT',  y_card, top_notch_size_y, nb_top_notch_y, zbox, edge_notch_size, nb_edge_notch, thickness, burn, 0, - zbox -y_card-4*thickness - 7, group)     
        self.gen_side('RIGHT',  y_card, top_notch_size_y, nb_top_notch_y, zbox, edge_notch_size, nb_edge_notch, thickness, burn, -y_card-2*thickness - 5, -zbox-y_card-4*thickness - 7, group)     
        #Then internal LEFT and internal RIGHT, which are close to left and right edges
        self.gen_internal_side('LEFT_INTERNAL', y_card, zbox-thickness, thickness, 0, - 2*zbox - y_card-5*thickness - 9, group)  
        self.gen_internal_side('RIGHT_INTERNAL', y_card, zbox-thickness, thickness, -y_card-2*thickness - 5, - 2*zbox - y_card-5*thickness - 9, group)  
        #Then internal walls
        for i in range(n_slots-1):
            self.gen_internal_wall(i, y_card, top_notch_size_y, nb_top_notch_y, zbox-thickness, edge_notch_size, nb_edge_notch, thickness, burn, i*(-y_card-2*thickness-5), - 3*zbox -y_card-4*thickness - 11, group) 
        #then Side hinges
        self.gen_hinge('LEFT_HINGE', 0, y_card, top_notch_size_y, nb_top_notch_y, thickness, burn, 0, - 4*zbox -y_card-4*thickness - 13, group)
        self.gen_hinge('RIGHT_HINGE', 0, y_card, top_notch_size_y, nb_top_notch_y, thickness, burn, -y_card-2*thickness - 5, - 4*zbox -y_card-4*thickness - 13, group)
        #and at last back_hinge
        self.gen_hinge('BACK_HINGE', thickness, internal_length, top_notch_size_x, nb_top_notch_x, thickness, burn, -internal_length - 2*thickness - 5, -y_card-thickness - 2, group)
        #Close Debug file if open
        if self.fDebug:
            self.fDebug.close()


# Create effect instance and apply it.
effect = CardBox()
effect.affect()
