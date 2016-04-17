# Public Opinion
# A top-down social dymanics simulator.

import argparse
import cProfile
import math
import random

import pygame

import actor
import world


def main(resolution, fullscreen):
    # Initialise screen
    pygame.init()

    flags = 0
    if fullscreen:
        flags |= pygame.FULLSCREEN
    screen = pygame.display.set_mode(resolution, flags)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))

    sprites = pygame.sprite.Group()
    stage = world.World(screen.get_size())
    player = actor.Actor(stage, (0.0, 0.0), True, 1.0)
    sprites.add(player)

    citizens = [actor.Citizen(stage, position=-1.0) for i in xrange(20)]

    for c in citizens:
        sprites.add(c)
        c.connection = {actor: random.uniform(0.0, 1.0)
                        for actor in stage.actors}

    quit = False

    clock = pygame.time.Clock()
    time = 0.0
    frames = 0

    while not quit:
        dt = clock.tick(200) / 1000.0
        frames += 1
        time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit = True

        move = [0.0, 0.0]
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP] or pressed[pygame.K_w]:
            move[1] -= 1.0
        if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            move[1] += 1.0
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            move[0] -= 1.0
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            move[0] += 1.0
        norm2 = move[0]**2 + move[1]**2
        if norm2 > 1:
            norm = math.sqrt(norm2)
            move[0] /= norm
            move[1] /= norm

        player.direction = move
        sprites.update(frames, dt)

        screen.blit(background, (0, 0))
        sprites.draw(screen)
        pygame.display.flip()

    print("Rendered " + str(frames) + " frames in " + str(time)
          + " seconds (" + str(frames / time) + " FPS)")


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
