from kivy.animation import Animation


def animate_size(width, height, duration=.3):
    return Animation(size=(width, height),
                     duration=.3, t='out_quad')


def animate_pos(x, y, duration=2):
    return Animation(pos=(x, y),
                     duration=duration, t='in_out_quad')


def move_left(widget_frame, anim_obj, gui):
    if gui.is_busy():
        width = widget_frame.width / (2 * 1.618)
        left = widget_frame.x
        anim = animate_size(width, anim_obj.size[1])
        anim &= animate_pos(left, anim_obj.pos[1])
        anim.bind(on_complete=lambda *_: move_right(widget_frame, anim_obj, gui))
        anim.bind(on_complete=lambda *_: stop(widget_frame, anim_obj, gui))
        anim.start(anim_obj)
        return anim


def move_right(widget_frame, anim_obj, gui):
    if gui.is_busy():
        width = widget_frame.width / (2 * 1.618)
        right = widget_frame.x + widget_frame.width - width
        anim = animate_size(width, anim_obj.size[1])
        anim &= animate_pos(right, anim_obj.pos[1])
        anim.bind(on_complete=lambda *_: move_left(widget_frame, anim_obj, gui))
        anim.bind(on_complete=lambda *_: stop(widget_frame, anim_obj, gui))
        anim.start(anim_obj)
        return anim


def stop(widget_frame, anim_obj, gui):
    if not gui.is_busy():
        width = widget_frame.width
        left = widget_frame.x
        anim = animate_size(width, anim_obj.size[1], .3)
        anim &= animate_pos(left, anim_obj.pos[1], .3)
        anim.start(anim_obj)
        return anim
