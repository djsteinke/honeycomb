import math

# Print
nozzle = 0.4
layer_h = 0.2
fillament_d = 1.75
e_mm = (nozzle * layer_h)/(math.pi * math.pow((fillament_d/2), 2))

# Size
sZ = 1.8
sX = 180.0
sY = 180.0
cell_w = 4.0

start_x = 70.0
start_y = 15.0

aY = cell_w/2.0
degR = 30.0/360.0*2.0*math.pi
aX = round(aY*math.tan(degR), 2)
print(aX)

w = math.sqrt(math.pow(aX, 2) + math.pow(aY, 2))
eW = round(w * e_mm, 5)

cX = int(sX/((aX + w) * 2))
if cX % 2 != 0:
    cX += 1
sX = cX * (aX + w) * 2
cY = int(sY/(aY * 2))
cZ = int(sZ/layer_h) + 1

sM = 5000
sH = 300
sP = 1200

x = start_x
y = start_y
z = layer_h
e = 0

gcode = ';PYTHON CODE \n'

gcode_h = ';LAYER HORIZONTAL \n'
gcode_v = ';LAYER VERTICAL \n'

c_line_y = sX + start_x - (1.5*25.4)
c_line_x = sY + start_y - (3.75*25.4)


def write_text(t):
    global gcode
    gcode += t + "\n"


def write_line(g, f, in_x, in_y, in_z, in_e):
    new_line = "G" + str(g)

    in_x = round(in_x, 3)
    in_y = round(in_y, 3)
    if f >= 0:
        new_line += " F" + str(f)
    if in_x >= 0:
        new_line += " X" + str(in_x)
    if in_y >= 0:
        new_line += " Y" + str(in_y)
    if in_z >= 0:
        new_line += " Z" + str(in_z)
    if in_e >= 0:
        new_line += " E" + str(in_e)

    new_line += ' \n'
    return new_line


def horizontal():
    global x, y, z, e, gcode_h
    gcode_h = '\n;LAYER HORIZONTAL \n'
    for c_y in range(cY):
        for c_x in range(cX):
            for line in range(4):
                write = True
                if line == 0:
                    x += aX
                    y -= aY
                    e += eW
                elif line == 1:
                    x += w
                    e += eW
                elif line == 2:
                    x += aX
                    y += aY
                    e += eW
                else:
                    if c_x == cX-1:
                        write = False
                    else:
                        e += eW
                        x += w

                if write:
                    gcode_h += write_line(1, -1, x, y, -1, e)
        for c_x in range(cX):
            for line in range(4):
                write = True
                if line == 0:
                    if c_x > 0:
                        x -= w
                        if c_y == cY - 1:
                            e += eW
                        else:
                            write = False
                            gcode_h += write_line(0, -1, x, y, -1, -1)
                elif line == 1:
                    x -= aX
                    y += aY
                    e += eW
                elif line == 2:
                    x -= w
                    if c_y == cY - 1:
                        e += eW
                    else:
                        write = False
                        gcode_h += write_line(0, -1, x, y, -1, -1)
                else:
                    x -= aX
                    y -= aY
                    e += eW

                if write:
                    gcode_h += write_line(1, -1, x, y, -1, e)
        y += aY
        x += aX
        gcode_h += write_line(0, -1, x, y, -1, -1)
        y += aY
        x -= aX
        gcode_h += write_line(0, -1, x, y, -1, -1)


def vertical():
    global x, y, z, e, gcode_v
    gcode_v = '\n;LAYER VERTICAL \n'

    # Draw vertical zigzag
    for c_x in range(cX):
        if c_x == 0:  # First row/column, move down to start
            x += aX
            y -= aY
            gcode_v += write_line(0, 1200, x, y, -1, -1)
            gcode_v += write_line(1, 1200, -1, -1, -1, e)
        else:  # After end of first row, move over to next column
            x += aX
            y += aY
            gcode_v += write_line(0, 1200, x, y, -1, -1)
            x += w
            gcode_v += write_line(1, 1200, x, y, -1, -1)
            x += aX
            y -= aY
            gcode_v += write_line(0, 1200, x, y, -1, -1)
        for c_y in range(cY):  # Draw vertical zigzag up
            for line in range(2):
                if line == 0:
                    x -= aX
                    y += aY
                    e += eW
                else:
                    x += aX
                    y += aY
                    e += eW
                gcode_v += write_line(1, -1, x, y, -1, e)
        x += w
        gcode_v += write_line(0, 1200, x, -1, -1, -1)
        for c_y in range(cY):  # Draw vertical zigzag down
            for line in range(2):
                if line == 0:
                    x += aX
                    y -= aY
                    e += eW
                else:
                    x -= aX
                    y -= aY
                    e += eW
                gcode_v += write_line(1, -1, x, y, -1, e)

    # Draw horizontal connector
    for c_y in range(cY+1):
        for c_x in range(cX):
            x -= w
            e += eW
            gcode_v += write_line(1, 1200, x, y, -1, e)  # Draw lower horizontal connector moving left
            if c_x < cX - 1:
                x -= aX
                y = y + aY if c_y < cY else y - aY
                gcode_v += write_line(0, 1200, x, y, -1, -1)  # Up
                x -= w
                gcode_v += write_line(0, 1200, x, y, -1, -1)  # Left
                x -= aX
                y = y - aY if c_y < cY else y + aY
                gcode_v += write_line(0, 1200, x, y, -1, -1)  # Down

        if c_y < cY:   # Draw mid horizontal connector
            x += w
            gcode_v += write_line(0, 1200, x, y, -1, -1)  # Right
            y += aY
            x += aX
            gcode_v += write_line(0, 1200, x, y, -1, -1)  # Up
            for c_x in range(cX - 1):
                x += w
                e += eW
                gcode_v += write_line(1, 1200, x, y, -1, e)  # Draw mid horizontal connector moving right
                if c_x < cX - 1:
                    x += aX
                    y -= aY
                    gcode_v += write_line(0, 1200, x, y, -1, -1)  # Down
                    x += w
                    gcode_v += write_line(0, 1200, x, y, -1, -1)  # Right
                    x += aX
                    y += aY
                    gcode_v += write_line(0, 1200, x, y, -1, -1)  # Up

        if c_y < cY:
            y += aY
            x -= aX
            gcode_v += write_line(0, 1200, x, y, -1, -1)


def run_steps():
    global x, y, z, gcode
    gcode += write_line(0, 1200, x, y, -1, -1)
    gcode += write_line(0, 300, x, y, z, -1)
    gcode += write_line(1, 1200, x, y, -1, e)
    draw_c_lines()
    for step_z in range(cZ):
        print('layer ' + str(step_z+1))
        if step_z % 2 == 0:
            vertical()
            gcode += gcode_v
        else:
            horizontal()
            gcode += gcode_h
        gcode += write_line(1, -1, -1, -1, -1, e - 5)
        z += layer_h
        gcode += write_line(0, 300, x, y, z, -1)
        x = start_x
        y = start_y
        gcode += write_line(0, 5000, x, y, -1, -1)
        gcode += write_line(1, 1200, -1, -1, -1, e)
    write_text("M140 S0 ;Turn off bed")
    write_text("M104 S0 ;Turn off hotend")
    write_text("M106 S0 ;Turn off fan")
    write_text("G91 ;Relative positioning")
    gcode += write_line(1, 2000, -1, -1, 5, -5)
    gcode += write_line(1, 2000, 5, 5, -1, -1)
    gcode += write_line(1, 2000, -1, -1, 10, -1)
    write_text("G90 ;Relative positioning")
    gcode += write_line(1, 2000, 0, 220, -1, -1)
    write_text("M84 X Y E ;Disable all steppers except Z")
    write_text("M82 ;Absolute extrusion mode")
    write_text(";End of GCODE")


def draw_c_lines():
    global gcode, x, y, e
    gcode += write_line(1, 1200, -1, -1, -1, e-5)
    gcode += write_line(0, 2000, start_x, c_line_y, -1, -1)
    gcode += write_line(1, 1200, -1, -1, -1, e)
    x += sX - w
    e += sX * e_mm
    gcode += write_line(1, 1200, x, c_line_y, -1, e)
    new_y = c_line_y-nozzle
    e += nozzle*e_mm
    gcode += write_line(1, 1200, start_x, new_y, -1, e)
    x -= sX - w
    e += sX * e_mm
    gcode += write_line(1, 1200, x, new_y, -1, e)
    gcode += write_line(1, 1200, start_x, new_y, -1, e-5)
    gcode += write_line(0, 2000, c_line_x, start_y-aY, -1, -1)
    y += sY - aY*2
    e += sY * e_mm
    gcode += write_line(1, 1200, c_line_x, y, -1, e)
    new_x = c_line_x-nozzle
    e += nozzle*e_mm
    gcode += write_line(1, 1200, new_x, y, -1, e)
    y -= sY - aY
    e += sY * e_mm
    gcode += write_line(1, 1200, new_x, y, -1, e)
    gcode += write_line(1, 1200, -1, -1, -1, e-5)
    x = start_x
    y = start_y
    gcode += write_line(0, 2000, x, y, -1, -1)
    gcode += write_line(1, 1200, -1, -1, -1, e)


def header():
    global gcode
    write_text(";FLAVOR:Marlin")
    write_text("M140 S40 ;Set bed temp")
    write_text("M105")
    write_text("M190 S40 ;Wait for bed to heat")
    write_text("M104 S215 ;Set hotend temp")
    write_text("M105")
    write_text("M109 S215 ;Wait for hotend to heat")
    write_text("M82 ;Absolute extrusion mode")
    write_text("G92 E0 ;Reset extruder")
    write_text("G28 ;Home all axes")
    write_text("G1 Z2.0 F3000 ;Move Z Axis up little to prevent scratching of Heat Bed")
    write_text("G1 X0.1 Y20 Z0.3 F5000.0 ;Move to start position")
    write_text("G1 X0.1 Y200.0 Z0.3 F1500.0 E15 ;Draw the first line")
    write_text("G1 X0.4 Y200.0 Z0.3 F5000.0 ;Move to side a little")
    write_text("G1 X0.4 Y20 Z0.3 F1500.0 E30 ;Draw the second line")
    write_text("G92 E0 ;Reset Extruder")
    write_text("G1 Z2.0 F3000 ;Move Z Axis up little to prevent scratching of Heat Bed")
    write_text("G1 X5 Y20 Z0.3 F5000.0 ;Move over to prevent blob squish")
    write_text("G92 E0")
    write_text("G92 E0")
    gcode += write_line(1, 1200, -1, -1, -1, -5)
    gcode += write_line(0, 1200, start_x, start_y, layer_h, 0)
    gcode += write_line(1, 1200, -1, -1, -1, 0)
    write_text("M107 ;Fan off")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    header()
    run_steps()
    f = open("honeycomb.gcode", "w")
    f.write(gcode)
    f.close()
