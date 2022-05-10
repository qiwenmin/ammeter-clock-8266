import cairo
import math
import platform

DEBUG = False
DRAW_HAND = False

# Face
FACE_W = 59.4
FACE_H = 29.6
CENTER_D = 9.2
HAND_R = 33.2
HOUR_R = 32.0
HOUR_RULER_DR = 2.0
HOUR_NUM_DR = 2.4
MINUTE_R = 31.2
MINUTE_RULER_DR = -1.8
MINUTE_NUM_DR = -3.7
POINT_FROM = math.pi * 5 / 4
POINT_TO = math.pi * 7 / 4
POINT_RANGE = POINT_TO - POINT_FROM

NAME_DY = -16.0
CALLSIGN_AND_DATE_DY = -14.0

# A4
PAGE_WIDTH = 210
PAGE_HEIGHT = 297

PAGE_MARGIN = 7.5
FACE_MARGIN = 2.5

NUM_FONT_NAME = "Luminari"
HOUR_NUM_FONT_SIZE = 8
MINUTE_NUM_FONT_SIZE = 7

TEXT_FONT_NAME = "Cochin"

if platform.system() == "Darwin":
    LOGO_FONT_NAME = "LiSong Pro"
else:
    LOGO_FONT_NAME = "SimHei"

LOGO_FONT_SIZE = 7
NAME_FONT_SIZE = 7
CALLSIGN_AND_DATE_FONT_SIZE = 5
POWERED_BY_FONT_SIZE = 5

CALLSIGN_AND_DATE = "BG1REN, 2022-05-09"


def mm2px(mm):
    return mm / 25.4 * 72.0


def debug_cross(ctx, x, y, w = 2):
    if not DEBUG:
        return

    ctx.set_source_rgba(0, 0, 0, 0.2)
    ctx.set_line_width(0.5)
    ctx.move_to(mm2px(x - w / 2), mm2px(y))
    ctx.line_to(mm2px(x + w / 2), mm2px(y))
    ctx.move_to(mm2px(x), mm2px(y - w / 2))
    ctx.line_to(mm2px(x), mm2px(y + w / 2))
    ctx.stroke()


def debug_grids(ctx):
    for x in range(0, PAGE_WIDTH + 1, 10):
        for y in range(0, PAGE_HEIGHT + 1, 10):
                debug_cross(ctx, x, y)


def debug_hand(ctx, v):
    if not DRAW_HAND:
        return

    ctx.set_source_rgba(1, 0, 0, 1)
    ctx.set_line_width(0.5)
    hand_r = mm2px(HAND_R)
    a = POINT_FROM + POINT_RANGE / 100 * v
    ctx.move_to(0, 0)
    ctx.line_to(hand_r * math.cos(a), hand_r * math.sin(a))
    ctx.stroke()


def draw_face(ctx):
    # border
    border_x = - mm2px(FACE_W) / 2
    border_y = - mm2px(FACE_H + CENTER_D)
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_line_width(mm2px(0.1))
    ctx.rectangle(border_x, border_y, mm2px(FACE_W), mm2px(FACE_H))
    ctx.stroke()

    # hours ruler
    ctx.set_line_cap(cairo.LINE_CAP_SQUARE)
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_line_width(mm2px(0.25))
    r = mm2px(HOUR_R)
    dr = mm2px(HOUR_RULER_DR)
    ctx.arc(0, 0, r, POINT_FROM, POINT_TO)
    ctx.stroke()

    for i in range(12 * 4 + 1):
        a = POINT_FROM + POINT_RANGE / 12 / 4 * i
        x1, y1 = math.cos(a) * r, math.sin(a) * r
        r2 = r + dr * 0.6
        ctx.set_line_width(mm2px(0.1))
        if i % 8 == 0:
            r2 = r + dr
            ctx.set_line_width(mm2px(0.25))
        elif i % 4 == 0:
            r2 = r + dr * 0.8
            ctx.set_line_width(mm2px(0.25))

        x2, y2 = math.cos(a) * r2, math.sin(a) * r2
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()

    ctx.select_font_face(NUM_FONT_NAME, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(HOUR_NUM_FONT_SIZE)
    dr = mm2px(HOUR_NUM_DR)
    for i in range(7):
        a = POINT_FROM + POINT_RANGE / 6 * i
        x, y = math.cos(a) * (r + dr), math.sin(a) * (r + dr)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(POINT_FROM + POINT_RANGE / 6 * i + math.pi / 2)

        s = f'{i * 2}'
        _, _, w, _, _, _ = ctx.text_extents(s)
        ctx.move_to(- w / 2, 0)
        ctx.show_text(s)
        ctx.stroke()

        ctx.restore()

    # minutes ruler
    ctx.set_line_cap(cairo.LINE_CAP_SQUARE)
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.set_line_width(mm2px(0.25))
    r = mm2px(MINUTE_R)
    dr = mm2px(MINUTE_RULER_DR)
    ctx.arc(0, 0, r, POINT_FROM, POINT_TO)
    ctx.stroke()

    for i in range(60 + 1):
        a = POINT_FROM + POINT_RANGE / 60 * i
        x1, y1 = math.cos(a) * r, math.sin(a) * r
        r2 = r + dr * 0.6
        ctx.set_line_width(mm2px(0.1))
        if i % 10 == 0:
            r2 = r + dr
            ctx.set_line_width(mm2px(0.25))
        elif i % 5 == 0:
            r2 = r + dr * 0.8
            ctx.set_line_width(mm2px(0.25))

        x2, y2 = math.cos(a) * r2, math.sin(a) * r2
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()

    ctx.select_font_face(NUM_FONT_NAME, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(MINUTE_NUM_FONT_SIZE)
    dr = mm2px(MINUTE_NUM_DR)
    for i in range(7):
        a = POINT_FROM + POINT_RANGE / 6 * i
        x, y = math.cos(a) * (r + dr), math.sin(a) * (r + dr)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(POINT_FROM + POINT_RANGE / 6 * i + math.pi / 2)

        s = f'{i * 10}'
        _, _, w, _, _, _ = ctx.text_extents(s)
        ctx.move_to(- w / 2, 0)
        ctx.show_text(s)
        ctx.stroke()

        ctx.restore()

    # Logo
    ctx.select_font_face(LOGO_FONT_NAME, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(LOGO_FONT_SIZE)

    s = "拾壹工坊"
    padding = mm2px(0.5)
    _, _, w, h, _, _ = ctx.text_extents(s)
    rect_x = border_x + padding
    rect_y = border_y + padding
    rect_w = w + padding * 2
    rect_h = h + padding * 2

    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.rectangle(rect_x, rect_y, rect_w, rect_h)
    ctx.fill()

    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.move_to(rect_x + padding, rect_y + padding * 0.5 + h)
    ctx.show_text(s)
    ctx.stroke()

    # Name
    ctx.select_font_face(TEXT_FONT_NAME, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(NAME_FONT_SIZE)

    s = "AMMETER CLOCK"
    _, _, w, _, _, _ = ctx.text_extents(s)
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.move_to(- w / 2, mm2px(NAME_DY))
    ctx.show_text(s)
    ctx.stroke()

    # Callsign and date
    ctx.select_font_face(TEXT_FONT_NAME, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(CALLSIGN_AND_DATE_FONT_SIZE)

    _, _, w, _, _, _ = ctx.text_extents(CALLSIGN_AND_DATE)
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.move_to(- w / 2, mm2px(CALLSIGN_AND_DATE_DY))
    ctx.show_text(CALLSIGN_AND_DATE)
    ctx.stroke()

    # Powered by
    ctx.select_font_face(TEXT_FONT_NAME, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(POWERED_BY_FONT_SIZE)

    s = "Powered by ESP8266"
    _, _, w, h, _, _ = ctx.text_extents(s)
    ctx.set_source_rgba(0, 0, 0, 1)
    ctx.move_to(border_x + mm2px(FACE_W) - w - mm2px(1.0), border_y + h + mm2px(1.0))
    ctx.show_text(s)
    ctx.stroke()

    # hand
    debug_hand(ctx, 40)


def main():
    with cairo.PDFSurface("85c1.pdf", mm2px(PAGE_WIDTH), mm2px(PAGE_HEIGHT))as surface:
        ctx = cairo.Context(surface)
        debug_grids(ctx);

        y = PAGE_MARGIN
        while y < PAGE_HEIGHT - PAGE_MARGIN - FACE_MARGIN * 2 - FACE_H:
            center_y = mm2px(y + FACE_H + CENTER_D)
            y += FACE_MARGIN * 2 + FACE_H

            x = PAGE_MARGIN
            while x < PAGE_WIDTH - PAGE_MARGIN - FACE_MARGIN * 2 - FACE_W:
                center_x = mm2px(x + FACE_MARGIN + FACE_W / 2)
                x += FACE_MARGIN * 2 + FACE_W

                ctx.save()
                ctx.translate(center_x, center_y)
                draw_face(ctx)
                ctx.restore()


if __name__ == '__main__':
    main()
