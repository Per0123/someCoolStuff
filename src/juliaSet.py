# ASCII Julia Set Renderer
# z[n+1] = z[n]^2 + c

WIDTH = 120
HEIGHT = 40

XMIN, XMAX = -1.5, 1.5
YMIN, YMAX = -1.0, 1.0

C_REAL = -0.8
C_IMAG = 0.156

MAX_ITER = 80

# your requested character set
CHARS = " .:-=+*#%@"

for y in range(HEIGHT):
    for x in range(WIDTH):
        zr = XMIN + (x / WIDTH) * (XMAX - XMIN)
        zi = YMIN + (y / HEIGHT) * (YMAX - YMIN)

        i = 0
        while zr*zr + zi*zi <= 4 and i < MAX_ITER:
            zr, zi = (
                zr*zr - zi*zi + C_REAL,
                2*zr*zi + C_IMAG
            )
            i += 1

        # map iterations → ASCII
        index = i * (len(CHARS) - 1) // MAX_ITER
        print(CHARS[index], end="")

    print()
