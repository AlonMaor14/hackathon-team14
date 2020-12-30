import colorama


def colorize(text, color='blue'):
    if text == '':
        return ''
    if color is None:
        return text
    color = getattr(colorama.Fore, color.upper())
    reset_color = colorama.Fore.RESET
    return f'{color}{text}{reset_color}'


class Colors(object):
    server = 'green'
    error = 'cyan'
    fatal = 'red'
    title = 'yellow'
