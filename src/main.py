# Public Opinion
# A top-down social dymanics simulator.

import argparse
import cProfile
import math
import random

import pygame

import actor
import colours
import controls
import menu
import meter
import states
import world


def main(resolution, fullscreen):
    # Initialise screen
    pygame.init()

    flags = 0
    if fullscreen:
        flags |= pygame.FULLSCREEN
    screen = pygame.display.set_mode(resolution, flags)
    screenRect = screen.get_rect()
    pygame.display.set_caption('Public Opinion')

    font = pygame.font.SysFont("sans,arial", 30)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))

    col = colours.Colours()

    sprites = pygame.sprite.Group()
    stage = world.World(screen.get_size())
    players = []

    hud = pygame.sprite.Group()
    meter_rect = screenRect.copy()
    meter_rect.width /= 4
    meter_rect.height = 40
    meter_rect.midtop = screenRect.midtop
    meter_rect.top += 20
    opinion_meter = meter.Meter(meter_rect, font, col)
    hud.add(opinion_meter)

    def start_1_player(menu):
        sprites.empty()
        stage.empty()
        del players[:]

        players.append(actor.Actor(stage, col, (-0.5, 0.5), True, -1.0))
        sprites.add(players)

        citizens = [actor.Citizen(stage, col, position=random.uniform(0.0, 1.0))
                    for i in xrange(40)]
        for c in citizens:
            c.connection = {actor: random.uniform(0.0, 1.0)
                            for actor in sprites}
            for a in c.connection:
                a.connection[c] = c.connection[a]
            sprites.add(c)

        opinion_meter.update(0, 0)

        state.change(states.GAME)

    def start_2_player(menu):
        sprites.empty()
        stage.empty()
        del players[:]

        players.append(actor.Actor(stage, col, (-0.5, 0.5), True, -1.0))
        players.append(actor.Actor(stage, col, (0.5, -0.5), True, 1.0))
        sprites.add(players)

        citizens = [actor.Citizen(stage, col, position=random.uniform(-0.2, 0.2))
                    for i in xrange(40)]
        for c in citizens:
            c.connection = {actor: random.uniform(0.0, 1.0)
                            for actor in sprites}
            for a in c.connection:
                a.connection[c] = c.connection[a]
            sprites.add(c)

        opinion_meter.update(0, 0)

        state.change(states.GAME)

    def resume(menu):
        state.change(states.GAME)

    def main(menu):
        state.change(states.MAIN_MENU)

    def quit(menu):
        state.change(states.QUITTING)

    enable_cb = ["Enable Colour Blind Mode", None]
    disable_cb = ["Disable Colour Blind Mode", None]

    def enable_cb_mode(menu):
        menu.options[menu.selected] = disable_cb
        col.cb_mode = True

    def disable_cb_mode(menu):
        menu.options[menu.selected] = enable_cb
        col.cb_mode = False

    enable_cb[1] = enable_cb_mode
    disable_cb[1] = disable_cb_mode

    main_menu = menu.Menu(font, [
            ("New 1 Player Game", start_1_player),
            ("New 2 Player Game", start_2_player),
            enable_cb,
            ("Quit Game", quit),
        ])
    pause_menu = menu.Menu(font, [
            ("Resume", resume),
            ("Main Menu", main),
            ("Quit Game", quit),
        ])

    clock = pygame.time.Clock()
    time = 0.0
    frames = 0

    ctrl = controls.Controls()
    state = states.State(states.MAIN_MENU)

    while True:
        dt = clock.tick(200) / 1000.0
        frames += 1
        time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state.change(states.QUITTING)
            elif event.type == pygame.KEYDOWN:
                ctrl.keydown(event.key)
            elif event.type == pygame.JOYBUTTONDOWN:
                ctrl.keydown((event.joy, event.button))

        if state == states.QUITTING:
            return
        elif state == states.MAIN_MENU:
            if state.on_enter():
                main_menu.reset()
            ctrl.update_menu(main_menu, state, dt)

            screen.blit(background, (0, 0))
            main_menu.draw(screen)
        elif state == states.PAUSE_MENU:
            if state.on_enter():
                pause_menu.reset()
            ctrl.update_menu(pause_menu, state, dt)

            screen.blit(background, (0, 0))
            hud.draw(screen)
            pause_menu.draw(screen)
        elif state == states.GAME:
            ctrl.update_game(players, state, dt)

            sprites.update(frames, dt)

            red = 0
            blue = 0
            for a in sprites:
                if a.position > 0.0:
                    red += 1
                else:
                    blue += 1
            if red != opinion_meter.red or blue != opinion_meter.blue:
                opinion_meter.update(blue, red)

            # if red > 0.9 * (red + blue):
            #     print("Well done. You took " + str(time) + " seconds.")
            #     quit = True

            if time > 60.0:
                quit = True

            screen.blit(background, (0, 0))
            sprites.draw(screen)

            time_remaining = font.render("{:.1f} s".format(abs(60.0 - time)), True, (0, 0, 0))
            fontrect = time_remaining.get_rect()
            fontrect.midtop = screenRect.midtop
            fontrect.top += 70
            screen.blit(time_remaining, fontrect.topleft)

            hud.draw(screen)

        pygame.display.flip()

    # print("Rendered " + str(frames) + " frames in " + str(time)
    #       + " seconds (" + str(frames / time) + " FPS)")

    r = opinion_meter.red_perc()
    b = opinion_meter.blue_perc()
    format_str = "{:.1f}% to {:.1f}%"
    if blue > red:
        print("Blue wins!")
        print(format_str.format(b, r))
    else:
        print("Red wins!")
        print(format_str.format(r, b))


def resolution(raw):
    a = raw.split("x")
    if len(a) != 2:
        raise ValueError()
    return (int(a[0]), int(a[1]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A top-down social dynamics simulator.')
    parser.add_argument('--profile-file', action='store',
                        help="File to store profiling output in")
    parser.add_argument('-p', '--profile', action='store_true',
                        help="Enable profiling using cProfile")
    parser.add_argument('-r', '--resolution', action='store',
                        type=resolution, default=(0, 0),
                        help="Target screen resolution (e.g. 1920x1080)")
    parser.add_argument('-f', '--fullscreen', action='store_true',
                        dest="fullscreen", default=True,
                        help="Run in full screen.")
    parser.add_argument('-w', '--windowed', action='store_false',
                        dest="fullscreen",
                        help="Run in window.")
    args = parser.parse_args()
    if args.profile:
        cProfile.run(
            "main(args.resolution, args.fullscreen)",
            filename=args.profile_file)
    else:
        main(args.resolution, args.fullscreen)
