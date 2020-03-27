from kivy.animation import Animation


def animate_size(width, height, duration=.3, use_hint=False):
    if not use_hint:
        animation = Animation(size=(width, height),
                              duration=.3, t='out_quad')
    else:
        animation = Animation(size_hint=(width, height),
                              duration=.3, t='out_quad')
    return animation


def animate_pos(x, y, duration=2, use_hint=False):
    if not use_hint:
        animation = Animation(pos=(x, y),
                              duration=duration, t='in_out_quad')
    else:
        animation = Animation(pos_hint={'x': x, 'y': y},
                              duration=duration, t='in_out_quad')
    return animation


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
