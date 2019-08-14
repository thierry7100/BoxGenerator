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

class PolygonBox(inkex.Effect):
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

        self.OptionParser.add_option('--n_vertices', action = 'store',
          type = 'int', dest = 'n_vertices', default = '6',
          help = 'number of vertices of base polygon')

        self.OptionParser.add_option('--z', action = 'store',
          type = 'float', dest = 'z', default = '100.0',
          help = 'Height')

        self.OptionParser.add_option('--radius', action = 'store',
          type = 'float', dest = 'radius', default = '100.0',
          help = 'radius of circle in polygon')

        self.OptionParser.add_option('--burn', action = 'store',
          type = 'float', dest = 'burn', default = '50.0',
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

    def drawNotch(self, path, notch_length, notch_height, theta, burn, delta_first=0):
        ''' 
        Draw a single notch with size notch_length and height notch_height, notch is drawed with an angle theta
        '''
        path.LineToRel((delta_first+notch_length + burn)*math.cos(theta), (notch_length + burn)*math.sin(theta))
        path.LineToRel(notch_height*math.cos(theta+math.pi/2), notch_height*math.sin(theta+math.pi/2))
        path.LineToRel((notch_length - burn)*math.cos(theta), (notch_length - burn)*math.sin(theta))
        path.LineToRel(notch_height*math.cos(theta-math.pi/2), notch_height*math.sin(theta-math.pi/2))

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



    def gen_top_bottom(self, id, external_radius, n_vertices, top_notch_size, nb_top_notch, thickness, burn, has_hole, xOffset, yOffset, parent):
        '''
        Generate bottom or top element. When the box is closed, these elements are identical.
        When the box is open or with a lid, the top has a hole cut.
        '''
        path = inkcape_path((xOffset - external_radius, yOffset - external_radius), parent, id)
        self.DebugMsg("Enter gen_top_bottom: external_radius="+str(external_radius)+", n_vertices="+str(n_vertices)+", top_notch_size="+str(top_notch_size)+", nb_top_notch="+str(nb_top_notch)+"\n")
        for i in range(n_vertices):
            if i == 0:
                path.MoveTo(external_radius, 0)
            else:
                path.LineTo(external_radius*math.cos(i*2.0*math.pi/n_vertices), external_radius*math.sin(i*2.0*math.pi/n_vertices))
            deltaX = math.cos((i+1)*2.0*math.pi/n_vertices) - math.cos(i*2.0*math.pi/n_vertices)
            deltaY = math.sin((i+1)*2.0*math.pi/n_vertices) - math.sin(i*2.0*math.pi/n_vertices)
            theta = math.atan2(deltaY, deltaX)
            self.drawNotch(path, top_notch_size, thickness, theta, burn, -burn/2)
            for j in range(1, nb_top_notch):
                self.drawNotch(path, top_notch_size, thickness, theta, burn)
        path.LineTo(external_radius, 0)
            
        if has_hole:
            Internal_radius1 = external_radius * math.cos(math.pi/n_vertices)
            Internal_radius1 -= thickness
            Internal_radius = Internal_radius1 * 0.92
            Internal_radius = min(Internal_radius1-2.0,  Internal_radius)
            Internal_radius = max(Internal_radius1-15, Internal_radius)

            path.MoveTo(Internal_radius, 0)
            #In order to draw a circle, draw 4 bezier segments
            path.Bezier(Internal_radius, Internal_radius*0.551916, Internal_radius*0.551916, Internal_radius, 0, Internal_radius)
            path.Bezier(Internal_radius*-0.551916, Internal_radius, -Internal_radius, Internal_radius*0.551916, -Internal_radius, 0)
            path.Bezier(-Internal_radius, -Internal_radius*0.551916, Internal_radius*-0.551916, -Internal_radius, 0, -Internal_radius)
            path.Bezier(Internal_radius*0.551916, -Internal_radius, Internal_radius, Internal_radius*-0.551916, Internal_radius, 0)
                
        path.Close()
        path.GenPath()

    def gen_lid(self, external_radius, n_vertices, has_circle_top, xOffset, yOffset, parent):
        '''
        Generate lid, it is either a circle or a polygon
        '''
        path = inkcape_path((xOffset - external_radius, yOffset - external_radius), parent, 'Lid')
        if has_circle_top:
            radius = external_radius * math.cos(math.pi/n_vertices)
            path.MoveTo(radius, 0)
            #In order to draw a circle, draw 4 bezier segments
            path.Bezier(radius, radius*0.551916, radius*0.551916, radius, 0, radius)
            path.Bezier(radius*-0.551916, radius, -radius, radius*0.551916, -radius, 0)
            path.Bezier(-radius, -radius*0.551916, radius*-0.551916, -radius, 0, -radius)
            path.Bezier(radius*0.551916, -radius, radius, radius*-0.551916, radius, 0)
        else:
            for i in range(n_vertices):
                if i == 0:
                    path.MoveTo(external_radius, 0)
                else:
                    path.LineTo(external_radius*math.cos(i*2.0*math.pi/n_vertices), external_radius*math.sin(i*2.0*math.pi/n_vertices))
            path.LineTo(external_radius, 0)
        path.Close()
        path.GenPath()
        
    def gen_vertical(self, index, edge_length, zbox, top_notch_size, nb_top_notch, edge_notch_size, edge_notch_height, nb_edge_notch, thickness, burn, xOffset, yOffset, parent):
        self.DebugMsg("Entering gen_vertical, edge_length="+str(edge_length)+", zbox="+str(zbox)+", nb_edge_notch="+str(nb_edge_notch)+", edge_notch_size="+str(edge_notch_size)+", edge_notch_height="+str(edge_notch_height)+"\n") 
        path = inkcape_path((xOffset, yOffset), parent, 'Side_'+str(index))
        #Left side has 
        path.MoveTo(0,0)
        #Draw first horizontal line with notches inside, so begin in x=0
        self.drawLineHNotches(path, nb_top_notch, top_notch_size, -thickness, burn, 1)
        path.LineTo(edge_length-edge_notch_height, 0)       #right side has outside notches so stop a little bit short of edge_length
        #Now draw vertical notches
        self.drawLineVNotches(path, nb_edge_notch//2, edge_notch_size, edge_notch_height, burn, 1)
        path.LineTo(edge_length-edge_notch_height, zbox)
        #Then the return horizontal line, first notch is shifted by edge_notch_height
        self.drawHNotch(path, -top_notch_size, thickness, burn, 1, edge_notch_height-burn/2)
        for i in range(1, nb_top_notch):
            self.drawHNotch(path, -top_notch_size, thickness, burn, 1, 0)
        path.LineTo(0, zbox)       #right side has outside notches so stop a little bit short of edge_length
        #and at last (left) vertical line
        self.drawLineVNotches(path, nb_edge_notch//2, -edge_notch_size, edge_notch_height, burn, -1)

        path.LineTo(0, 0)
        path.Close()
        path.GenPath()

    
    def effect(self):
        """
        Draws a polygonal box, based on provided parameters
        """

        # input sanity check
        error = False
        if self.options.radius < 20:
            inkex.errormsg('Error: radius should be at least 10mm')
            error = True

        if self.options.thickness <  1 or self.options.thickness >  10:
            inkex.errormsg('Error: thickness should be at least 1mm and less than 10mm')
            error = True

        if error:
            exit()


        # convert units
        unit = self.options.unit
        radius = self.unittouu(str(self.options.radius) + unit)
        n_vertices = self.options.n_vertices
        zbox = self.unittouu(str(self.options.z) + unit)
        thickness = self.unittouu(str(self.options.thickness) + unit)
        burn = self.unittouu(str(self.options.burn) + unit)
        box_top_type = self.options.top_type

        # Select final dimensions, using inner_size variables. If Outer_size, decrease dimensions.
        if self.options.inner_size == False:
            radius -= thickness
            zbox -= 2*thickness
            
        # Decide if the top should have a hole, and a lid is needed
        
        has_hole = box_top_type != 'Closed'
        has_lid = box_top_type == 'Lid_poly' or box_top_type == 'Lid_circle'
        has_circle_top = box_top_type == 'Lid_circle'
            
        svg = self.document.getroot()
        docWidth = self.unittouu(svg.get('width'))
        docHeigh = self.unittouu(svg.attrib['height'])

        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'Polygonal Box')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        group = inkex.etree.SubElement(layer, 'g')
        try:
            self.fDebug = open( 'DebugPolygonBox.txt', 'w')
        except IOError:
            pass
        self.DebugMsg("Start processing\n")
        #compute length of each edge
        edge_length = 2*radius * math.tan(math.pi / n_vertices)
        #compute external radius 
        external_radius = radius / math.cos(math.pi/n_vertices)
        #compute top notch size
        if edge_length < 10:
            inkex.errormsg('Error: too many edges for this radius, each edge should be at least 10mm long')
        elif edge_length < 20:      #  Only one notch
            nb_top_notch = 1
            top_notch_size = edge_length / 3
        elif edge_length < 40:
            nb_top_notch = int((edge_length-5) / 10)
            top_notch_size = edge_length/(2*nb_top_notch+1)
        elif edge_length < 80:
            nb_top_notch = int((edge_length-5) / 15)
            top_notch_size = edge_length/(2*nb_top_notch+1)
        else:
            nb_top_notch = int((edge_length-5) / 20)
            top_notch_size = edge_length/(2*nb_top_notch+1)
        #compute edge notch length, height and number
        if zbox < 10:
            inkex.errormsg('Error: too many edges for this radius, each edge should be at least 10mm long')
        elif zbox < 20:      #  Only one notch
            nb_edge_notch = 3
            edge_notch_size = zbox / 3
        elif zbox < 40:
            nb_edge_notch = int((zbox-5) / 5)
            nb_edge_notch = nb_edge_notch | 1       #Ensure odd 
            edge_notch_size = zbox/(nb_edge_notch)
        elif zbox < 80:
            nb_edge_notch = int((zbox-5) / 7.5)
            nb_edge_notch = nb_edge_notch | 1       #Ensure odd 
            edge_notch_size = zbox/(nb_edge_notch)
        else:
            nb_edge_notch = int((zbox-5) / 10)
            nb_edge_notch = nb_edge_notch | 1       #Ensure odd 
            edge_notch_size = zbox/(nb_edge_notch)
        if n_vertices == 3:
            #Specific case
            edge_notch_height = thickness / math.cos(math.pi/3)
        else:
            edge_notch_height = thickness * math.sin(2*math.pi/n_vertices)
        #generate top
        self.gen_top_bottom('Top', external_radius, n_vertices, top_notch_size, nb_top_notch, thickness, burn, has_hole, 0, 0, group)
        #generate bottom
        self.gen_top_bottom('Bottom', external_radius, n_vertices, top_notch_size, nb_top_notch, thickness, burn, 0, -2*external_radius-2*thickness-2, 0, group)
        #Then lid if needed
        if has_lid:
            self.gen_lid(external_radius, n_vertices, has_circle_top, -4*external_radius-4*thickness-4, 0, group)
        #And vertical plates, one for each edge of the polygon
        for i in range(n_vertices):
            self.gen_vertical(i, edge_length, zbox, top_notch_size, nb_top_notch, edge_notch_size, edge_notch_height, nb_edge_notch, thickness, burn, -1*i*(edge_length+2*edge_notch_height+2), -2*external_radius-2*thickness-2, group)
        #Close Debug file if open
        if self.fDebug:
            self.fDebug.close()


# Create effect instance and apply it.
effect = PolygonBox()
effect.affect()
