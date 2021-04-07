import random

import pygame

import textrect
# textrect is a module written by someone else to enable rendering of "\n"
# (since pygame's text rendering can't render newlines)

pygame.mixer.pre_init(44100, -16, 1, 1024)  # to take out delay in playing sound
pygame.init()

screen = pygame.display.set_mode((800, 600))  # y should be 3/4 of x for correct aspect ratio
xMulti = screen.get_width() / 40  # the screen works in tiles, 40 tiles by 30 tiles
yMulti = screen.get_height() / 30
fps = 40


class Aarak:
    """ 3x3 tiles, position is defined by bottom middle """

    def __init__(self, level):
        self.loadImages(level)
        self.DELAY = fps / 10  # animation, delay between frames
        self.reset(level)
        self.updateImage()

    def reset(self, level):
        self.position = [2.0, 14.0]  # pp
        self.frame = 0
        self.pause = 0
        self.frameD = 1  # direction moving through frames
        self.holdFrame1 = False  # frame 1 is jumping frame
        self.facing = 1  # 1 facing right, -1 facing left
        if level == 6:
            self.position = [37, 12]
            self.facing = -1
        if level < 5 or level == 11:
            self.hp = 3  # a1
        else:
            self.hp = 5
        self.weight = 0.0
        self.shootx = 55.0
        self.shooty = 55.0  # greater than 50 = nonexistent

    def fall(self, terrain, leftDown, rightDown):
        if self.weight > 0:
            self.position[1] += self.weight
        elif self.weight < 0:
            if terrain[(int(self.position[0]) * 100 + round(self.position[1])) - 3] != 176 and \
               terrain[(int(self.position[0]) * 100 + round(self.position[1])) - 3] != 64 and \
               terrain[(round(self.position[0]) * 100 + round(self.position[1])) - 3] != 176 and \
               terrain[(round(self.position[0]) * 100 + round(self.position[1])) - 3] != 64 and \
               terrain[(int(self.position[0]) * 100 + round(self.position[1])) - 103] != 176 and \
               terrain[(int(self.position[0]) * 100 + round(self.position[1])) - 103] != 64 and \
               terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 97] != 176 and \
               terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 97] != 64 and \
               self.position[1] > 2:
                self.position[1] += self.weight
        if self.weight <= 2 - (5 / fps):  # so I don't fall through the ground at low fps
            self.weight += 36 / (fps * fps)

        # if there's anything to stand on under me, put me on ground and no down movement
        if terrain[(int(self.position[0]) * 100 + round(self.position[1])) + 1] == 176 or \
           terrain[(int(self.position[0]) * 100 + round(self.position[1])) + 1] == 64 or \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 1] == 176 or \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 1] == 64 or \
           terrain[(int(self.position[0]) * 100 + round(self.position[1])) - 99] == 176 or \
           terrain[(int(self.position[0]) * 100 + round(self.position[1])) - 99] == 64 or \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 101] == 176 or \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 101] == 64:
            if self.weight >= 0:
                self.position[1] = round(self.position[1])  # if I'm in ground, put me on top of it
            if self.weight > 0:
                self.weight = 0
                self.holdFrame1 = False
                if not leftDown and not rightDown:
                    self.frame = 0
                    self.frameD = 1
                self.updateImage()
        else:  # nothing under me
            self.frame = 1
            self.updateImage()

        if self.position[1] > 15:  # fallen in hole
            self.hp = 0

    def get1up(self, lives, terrain):
        """detect collision with 1up (line 640)
        :param lives: to modify it
        :param terrain: to see where the 1up is
        :return: new lives
        """

        if terrain[(int(self.position[0]) * 100 + int(self.position[1]))] == 35:
            lives += 1
            terrain[(int(self.position[0]) * 100 + int(self.position[1]))] = 32
        if terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 1] == 35:
            lives += 1
            terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 1] = 32
        if terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 2] == 35:
            lives += 1
            terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 2] = 32
        if terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 100] == 35:
            lives += 1
            terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 100] = 32
        if terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 101] == 35:
            lives += 1
            terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 101] = 32
        if terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 102] == 35:
            lives += 1
            terrain[(int(self.position[0]) * 100 + int(self.position[1])) - 102] = 32
        if terrain[(int(self.position[0]) * 100 + int(self.position[1])) + 100] == 35:
            lives += 1
            terrain[(int(self.position[0]) * 100 + int(self.position[1])) + 100] = 32
        if terrain[(int(self.position[0]) * 100 + int(self.position[1])) + 99] == 35:
            lives += 1
            terrain[(int(self.position[0]) * 100 + int(self.position[1])) + 99] = 32
        if terrain[(int(self.position[0]) * 100 + int(self.position[1])) + 98] == 35:
            lives += 1
            terrain[(int(self.position[0]) * 100 + int(self.position[1])) + 98] = 32
        return lives

    def shoot(self):
        self.shootx = self.position[0] + self.facing
        self.shooty = self.position[1] - 1
        self.shootv = self.facing * (10 / fps)

    def jump(self, terrain):
        if terrain[(int(self.position[0]) * 100 + round(self.position[1])) + 1] == 176 or \
           terrain[(int(self.position[0]) * 100 + round(self.position[1])) + 1] == 64 or \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 1] == 176 or \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 1] == 64 or \
           terrain[(int(self.position[0]) * 100 + round(self.position[1])) - 99] == 176 or \
           terrain[(int(self.position[0]) * 100 + round(self.position[1])) - 99] == 64 or \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 101] == 176 or \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) + 101] == 64:
            self.weight = -20 / fps
            self.holdFrame1 = True
            self.frame = 1
            self.updateImage()
            # boing sound?

    def moveLeft(self, terrain, leftWentDown, rightWentDown):
        if terrain[(round(self.position[0]) * 100 + round(self.position[1])) - 200] != 176 and \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) - 200] != 64 and \
           terrain[(round(self.position[0]) * 100 + int(self.position[1])) - 201] != 176 and \
           terrain[(round(self.position[0]) * 100 + int(self.position[1])) - 201] != 64 and \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) - 201] != 176 and \
           terrain[(round(self.position[0]) * 100 + round(self.position[1])) - 201] != 64 and \
           terrain[(round(self.position[0]) * 100 + int(self.position[1])) - 202] != 176 and \
           terrain[(round(self.position[0]) * 100 + int(self.position[1])) - 202] != 64 and \
           self.position[0] > 1:
            self.position[0] -= 8 / fps
            leftWentDown = False
            rightWentDown = False
            if not self.holdFrame1:  # if not jumping
                self.pause += 1
                if self.pause >= self.DELAY:
                    self.pause = 0
                    self.frame += self.frameD
                    if self.frame == 0:
                        self.frameD = 1
                    elif self.frame == 2:
                        self.frameD = -1
                    self.updateImage()
        return leftWentDown, rightWentDown

    def moveRight(self, terrain, leftWentDown, rightWentDown):
        if terrain[(round(self.position[0] - .5) * 100 + round(self.position[1])) + 200] != 176 and \
           terrain[(round(self.position[0] - .5) * 100 + round(self.position[1])) + 200] != 64 and \
           terrain[(round(self.position[0] - .5) * 100 + int(self.position[1])) + 199] != 176 and \
           terrain[(round(self.position[0] - .5) * 100 + int(self.position[1])) + 199] != 64 and \
           terrain[(round(self.position[0] - .5) * 100 + round(self.position[1])) + 199] != 176 and \
           terrain[(round(self.position[0] - .5) * 100 + round(self.position[1])) + 199] != 64 and \
           terrain[(round(self.position[0] - .5) * 100 + int(self.position[1])) + 198] != 176 and \
           terrain[(round(self.position[0] - .5) * 100 + int(self.position[1])) + 198] != 64:
            self.position[0] += 8 / fps
            leftWentDown = False
            rightWentDown = False
            if not self.holdFrame1:  # if not jumping
                self.pause += 1
                if self.pause >= self.DELAY:
                    self.pause = 0
                    self.frame += self.frameD
                    if self.frame == 0:
                        self.frameD = 1
                    elif self.frame == 2:
                        self.frameD = -1
                    self.updateImage()
        return leftWentDown, rightWentDown

    def blit(self):
        screen.blit(self.image, ((self.position[0] * xMulti) - xMulti, (self.position[1] * yMulti) - (yMulti * 2)))

    def loadImages(self, level):
        self.r = []
        self.l = []
        if level < 5 or level == 11:
            for i in range(3):
                imgName = "resources/aarakr%d.png" % i
                tmpImage = pygame.image.load(imgName)
                tmpImage = pygame.transform.scale(tmpImage, (int(xMulti * 3), int(yMulti * 3)))
                transcolor = tmpImage.get_at((1, 1))
                tmpImage.set_colorkey(transcolor)
                tmpImage = tmpImage.convert()
                self.r.append(tmpImage)
            for i in range(3):
                imgName = "resources/aarakl%d.png" % i
                tmpImage = pygame.image.load(imgName)
                tmpImage = pygame.transform.scale(tmpImage, (int(xMulti * 3), int(yMulti * 3)))
                transcolor = tmpImage.get_at((1, 1))
                tmpImage.set_colorkey(transcolor)
                tmpImage = tmpImage.convert()
                self.l.append(tmpImage)
        else:
            for i in range(3):
                imgName = "resources/aaraker%d.png" % i
                tmpImage = pygame.image.load(imgName)
                tmpImage = pygame.transform.scale(tmpImage, (int(xMulti * 3), int(yMulti * 3)))
                transcolor = tmpImage.get_at((1, 1))
                tmpImage.set_colorkey(transcolor)
                tmpImage = tmpImage.convert()
                self.r.append(tmpImage)
            for i in range(3):
                imgName = "resources/aarakel%d.png" % i
                tmpImage = pygame.image.load(imgName)
                tmpImage = pygame.transform.scale(tmpImage, (int(xMulti * 3), int(yMulti * 3)))
                transcolor = tmpImage.get_at((1, 1))
                tmpImage.set_colorkey(transcolor)
                tmpImage = tmpImage.convert()
                self.l.append(tmpImage)

    def updateImage(self):
        if self.facing == 1:
            self.image = self.r[self.frame]
        else:
            self.image = self.l[self.frame]


class Enemy:
    """ 3x2 tiles, position is bottom middle tile """

    IMAGE = pygame.image.load("resources/enemy.png")
    IMAGE = pygame.transform.scale(IMAGE, (int(xMulti * 3), int(yMulti * 2)))
    transColor = IMAGE.get_at((1, 1))
    IMAGE.set_colorkey(transColor)
    IMAGE = IMAGE.convert()

    def __init__(self):
        self.reset()

    def reset(self):
        self.dx = -2.5 / fps
        self.position = [50.0, 50.0]

    def move(self, terrain):
        if self.position[0] < 50:  # only if it's one of the enemies on screen
            if self.dx > 0:
                if terrain[int(self.position[0]) * 100 + 200 + self.position[1]] != 176 and \
                   terrain[int(self.position[0]) * 100 + 200 + self.position[1]] != 64 and \
                   terrain[int(self.position[0]) * 100 + 199 + self.position[1]] != 176 and \
                   terrain[int(self.position[0]) * 100 + 199 + self.position[1]] != 64 and \
                   self.position[0] < 38 and (terrain[int(self.position[0]) * 100 + 201 + self.position[1]] == 176 or
                                              terrain[int(self.position[0]) * 100 + 201 + self.position[1]] == 64):
                    self.position[0] += self.dx
                else:
                    self.dx = -2.5 / fps
            elif self.dx < 0:
                if terrain[round(self.position[0]) * 100 - 200 + self.position[1]] != 176 and \
                   terrain[round(self.position[0]) * 100 - 200 + self.position[1]] != 64 and \
                   terrain[round(self.position[0]) * 100 - 201 + self.position[1]] != 176 and \
                   terrain[round(self.position[0]) * 100 - 201 + self.position[1]] != 64 and \
                   self.position[0] > 1 and (terrain[round(self.position[0]) * 100 - 199 + self.position[1]] == 176 or
                                             terrain[round(self.position[0]) * 100 - 199 + self.position[1]] == 64):
                    self.position[0] += self.dx
                else:
                    self.dx = 2.5 / fps

    def blit(self):
        if self.position[0] < 50:
            screen.blit(Enemy.IMAGE, ((self.position[0] * xMulti) - xMulti, (self.position[1] * yMulti) - yMulti))


def title():  # return what level the player is on (1, or 11 for secret level, -1 if quit)

    song = pygame.mixer.Sound("resources/title.ogg")

    titleScreen = pygame.surface.Surface((320, 240))
    titleScreen.fill((0, 0, 0))
    titlePoints = ((46, 22, 37, 83), (46, 22, 67, 24), (66, 24, 64, 44), (64, 44, 46, 53), (46, 53, 69, 78),
                   (86, 22, 86, 83), (85, 53, 97, 56), (97, 22, 96, 78), (114, 72, 131, 24), (131, 24, 139, 83),
                   (126, 53, 135, 57), (161, 28, 161, 79), (161, 28, 173, 29), (173, 28, 175, 47), (175, 47, 161, 53),
                   (161, 53, 176, 81), (200, 78, 208, 23), (208, 23, 219, 57),
                   (219, 57, 240, 33), (240, 33, 237, 82), (256, 78, 274, 31), (274, 31, 286, 81), (266, 57, 280, 56),
                   (0, 139, 27, 101), (27, 101, 64, 141), (61, 150, 88, 120), (88, 120, 111, 139), (109, 150, 139, 107),
                   (139, 107, 171, 142), (155, 117, 187, 94), (187, 94, 233, 132), (227, 144, 256, 111),
                   (256, 111, 299, 148), (290, 133, 311, 110),
                   (311, 110, 319, 117), (319, 118, 319, 174), (319, 174, 0, 174), (0, 140, 0, 174))
    for x1, y1, x2, y2 in titlePoints:
        pygame.draw.line(titleScreen, (255, 255, 255), (x1, y1), (x2, y2), 1)
    titleScreen = pygame.transform.scale(titleScreen, (screen.get_size()))
    titleScreen = titleScreen.convert()

    myFont = pygame.font.SysFont("default", int(yMulti * 2))
    welcome = myFont.render("   WELCOME...", False, (255, 255, 255))
    pressAnyKey = myFont.render(" PRESS ANY KEY.", False, (255, 255, 255))

    playedSong = False
    shiftDown = False
    clock = pygame.time.Clock()
    time = 0.0
    done = False

    while not done:

        clock.tick(fps)
        time += 1 / fps

        if time > .5 and not playedSong:
            song.play()
            playedSong = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                keyName = pygame.key.name(event.key)
                if "shift" in keyName:
                    shiftDown = True
                elif keyName == "`" and shiftDown:
                    return 11
                elif time > 2.5:
                    # return 5 # for testing
                    return 1
            elif event.type == pygame.KEYUP:
                if "shift" in pygame.key.name(event.key):
                    shiftDown = False

        screen.blit(titleScreen, (0, 0))
        screen.blit(welcome, (0, yMulti * 25))
        if time > 2.5:
            screen.blit(pressAnyKey, (0, yMulti * 27))
        pygame.display.flip()
    return -1


def scene(level):
    song = pygame.mixer.Sound("resources/scene" + str(level) + ".ogg")
    song2 = pygame.mixer.Sound("resources/scene72.ogg")

    background = pygame.surface.Surface(screen.get_size())
    background.fill((0, 0, 0))
    background = background.convert()

    wood = pygame.image.load("resources/wood.png")
    wood = pygame.transform.scale(wood, (int(xMulti) + 1, int(yMulti) + 1))
    wood = wood.convert()

    stone = pygame.image.load("resources/stone.png")
    stone = pygame.transform.scale(stone, (int(xMulti) + 1, int(yMulti) + 1))
    stone = stone.convert()

    oneUp = pygame.image.load("resources/heart1p.png")
    oneUp = pygame.transform.scale(oneUp, (int(xMulti), int(yMulti)))
    oneUp = oneUp.convert()

    aarak = Aarak(1)
    if level != 1:
        aarak.facing = -1
        aarak.updateImage()

    aarakAura = pygame.image.load("resources/aarakel0aura.png")
    aarakAura = pygame.transform.scale(aarakAura, (int(xMulti * 3), int(yMulti * 3)))
    transColor = aarakAura.get_at((1, 1))
    aarakAura.set_colorkey(transColor)
    aarakAura = aarakAura.convert()

    aarakEnhanced = pygame.image.load("resources/aarakel0.png")
    aarakEnhanced = pygame.transform.scale(aarakEnhanced, (int(xMulti * 3), int(yMulti * 3)))
    transColor = aarakEnhanced.get_at((1, 1))
    aarakEnhanced.set_colorkey(transColor)
    aarakEnhanced = aarakEnhanced.convert()

    aarakBroken = pygame.image.load("resources/aarakBroken.png")
    aarakBroken = pygame.transform.scale(aarakBroken, (int(xMulti * 4), int(yMulti * 3)))
    transColor = aarakBroken.get_at((1, 1))
    aarakBroken.set_colorkey(transColor)
    aarakBroken = aarakBroken.convert()

    enemy = Enemy.IMAGE

    messenger = pygame.image.load("resources/green stick black bg 24 24.png")
    messenger = pygame.transform.scale(messenger, (int(xMulti * 3), int(yMulti * 3)))
    transColor = messenger.get_at((1, 1))
    messenger.set_colorkey(transColor)
    messenger = messenger.convert()

    sanou = pygame.image.load("resources/sanou.png")
    sanou = pygame.transform.scale(sanou, (int(xMulti * 4), int(yMulti * 4)))
    transColor = sanou.get_at((1, 1))
    sanou.set_colorkey(transColor)
    sanou = sanou.convert()

    king = pygame.image.load("resources/king.png")
    king = pygame.transform.scale(king, (int(xMulti * 5), int(yMulti * 5)))
    transColor = king.get_at((1, 1))
    king.set_colorkey(transColor)
    king = king.convert()

    lafta = pygame.image.load("resources/dark purple stick black bg 24 24.png")
    lafta = pygame.transform.scale(lafta, (int(xMulti * 3), int(yMulti * 3)))
    transColor = lafta.get_at((1, 1))
    lafta.set_colorkey(transColor)
    lafta = lafta.convert()

    laftaBroken = pygame.image.load("resources/laftaBroken.png")
    laftaBroken = pygame.transform.scale(laftaBroken, (int(xMulti * 4), int(yMulti * 3)))
    transColor = laftaBroken.get_at((1, 1))
    laftaBroken.set_colorkey(transColor)
    laftaBroken = laftaBroken.convert()

    # text
    myFont = pygame.font.SysFont("default", int(yMulti * 2))
    scene9Font = pygame.font.SysFont("Lucida Console", int(yMulti * 1.5))
    s1l1 = textrect.render_textrect("MESSENGER: AARAK! DEMONS ARE TAKING\nOVER THE KINGDOM!!", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s1l2 = textrect.render_textrect("AARAK: ALL OF RHARMA?", myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)),
                                    (255, 255, 255), (0, 0, 0))
    s1l3 = textrect.render_textrect(
        "MESSENGER: YES, THERE ARE HUNDREDS OF\nTHEM. THE BARONE SANOU IN THE CITY OF\nANADA WANTS YOU TO REPORT TO HIM RIGHT\nAWAY.",
        myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s1l4 = textrect.render_textrect("AARAK: HOW DO I GET THERE IF THERE\nARE HUNDREDS OF DEMONS?", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s1l5 = textrect.render_textrect(
        "MESSENGER: JUST DON'T LET THEM TOUCH\nYOU. TAKE THESE RESURRECTION STONES\nJUST IN CASE. GOOD LUCK!", myFont,
        pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s1l6 = textrect.render_textrect(
        "USE LEFT AND RIGHT TO MOVE.\nUSE DOWN TO GO IN A DOOR.\nUSE UP TO JUMP.\nUSE THE SPACEBAR TO USE A WEAPON.",
        myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s1l7 = textrect.render_textrect("- WOOD\n- RESURRECTION STONE\n- ROCK OR GROUND", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))

    s2l1 = textrect.render_textrect(
        "SANOU: AARAK, WE NEED YOUR HELP! WE\nCANNOT FIGHT THE DEMONS WITH THE POWER\nWE HAVE. GO TO THE CASTLE IN WANAK AND\nGET PRINCE GHANERA. WE CAN USE HIS\nPOWERS TO DEFEAT THE DEMONS.",
        myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s2l2 = textrect.render_textrect("AARAK: I CAN'T GET THERE WITH WHAT\nI HAVE. I NEED SOME OTHER HELP.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s2l3 = textrect.render_textrect(
        "SANOU: TAKE THIS TORCH THROWER. THE\nDEMONS CAN BE BURNED, AND YOU CAN ALSO\nUSE IT TO BURN WALLS IN YOUR WAY. HURRY,\nWE MUST DEFEAT THE DEMONS BEFORE THEY\nTAKE OVER THE WHOLE KINGDOM.",
        myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))

    s3l1 = textrect.render_textrect(
        "AARAK: ARE YOU THE KING? I NEED TO\nTALK TO PRINCE GHANERA. I THINK HE CAN\nHELP US DEFEAT THE DEMONS.",
        myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s3l2 = textrect.render_textrect("KING: IS THIS A JOKE? I DON'T HAVE\nTIME FOR THIS.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s3l3 = textrect.render_textrect("AARAK: THE BARONE SANOU TOLD ME\nTHAT HE CAN HELP US.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s3l4 = textrect.render_textrect("KING: THE PRINCE IS DEAD, I DON'T\nHAVE TIME FOR THIS NONSENSE.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s3l5 = textrect.render_textrect("AARAK: WHAT HAPPENED?!! HE WAS THE\nONLY ONE WHO COULD HELP US.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s3l6 = textrect.render_textrect("KING: I'M TOO BUSY. THESE DEMONS\nARE MAD! GO FIND LAFTA, IN THE FOREST.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))

    s4l1 = textrect.render_textrect("LAFTA: WHAT DO YOU WANT?", myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)),
                                    (255, 255, 255), (0, 0, 0))
    s4l2 = textrect.render_textrect(
        "AARAK: DO YOU KNOW WHAT HAPPENED\nTO PRINCE GHANERA? I WENT TO THE CASTLE\nTO FIND HIM BUT THE KING SAID HE IS\nDEAD.",
        myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s4l3 = textrect.render_textrect("LAFTA: YES, HE DIED MANY YEARS AGO.\nI WAS THE KINGS SERVANT THEN.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s4l4 = textrect.render_textrect("AARAK: BUT WE NEEDED HIM TO DEFEAT\nTHE DEMONS.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s4l5 = textrect.render_textrect(
        "LAFTA: THIS WAS THE RING THAT GAVE\nHIM THE POWER HE HAD, BUT HE IS THE ONLY\nONE WHO CAN WEAR IT.", myFont,
        pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s4l6 = textrect.render_textrect(
        "[THERE IS A LOUD CRASH AND DEMONS COME\nTHROUGH THE WALL. LAFTA IS INJURED AND\nBOTH ARE THROWN THROUGH THE OPPOSITE\nWALL.]",
        myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s4l7 = textrect.render_textrect(
        "LAFTA: YOU HAVE TO GET BACK IN\nTHERE... THE RING IS IN THERE....  GO TO\nTHE BACK DOOR.", myFont,
        pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))

    s5l1 = textrect.render_textrect("AARAK: THEY'RE GONE. ARE YOU HURT\nBADLY?", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s5l2 = textrect.render_textrect("LAFTA: UH... I THINK MY ARM IS\nBROKEN... AND I CAN'T MOVE MY... BACK.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s5l3 = textrect.render_textrect("  ...THE RING...", myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)),
                                    (255, 255, 255), (0, 0, 0))
    s5l4 = textrect.render_textrect("[HE LOOKS AT IT FOR A FEW SECONDS,\nTHEN SLIPS IT ON WITHOUT THINKING]", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s5l5 = textrect.render_textrect("LAFTA: I KNEW IT!! I KNEW IT SINCE\nYOU CAME TO MY DOOR!", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s5l6 = textrect.render_textrect("AARAK: WHAT?!", myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)),
                                    (255, 255, 255), (0, 0, 0))
    s5l7 = textrect.render_textrect("LAFTA: YOU ARE THE PRINCE!!", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s5l8 = textrect.render_textrect("AARAK: I THOUGHT YOU SAID THE\nPRINCE WAS DEAD.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s5l9 = textrect.render_textrect(
        "LAFTA: WE THOUGHT HE WAS DEAD. THE\nCASTLE WAS RAIDED WHEN YOU WERE YOUNG.\nAFTER EVERYTHING WAS SORTED OUT... THE\nPRINCE TURNED UP MISSING. WE THOUGHT...\n...HE WAS DEAD...",
        myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s5l10 = textrect.render_textrect("AARAK: WHAT'S WRONG? HERE, I'LL\nGIVE YOU ONE OF MY RESURRECTION STONES.", myFont,
                                     pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s5l11 = textrect.render_textrect(
        "LAFTA: NO, THEY CAN'T HELP ME...\n..MY BODY IS DAMAGED...    NOW YOU MUST\nDEFEAT... THE DE... MON...", myFont,
        pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s5l12 = textrect.render_textrect("GO...", myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255),
                                     (0, 0, 0))
    s5l13 = textrect.render_textrect("SAVE..", myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255),
                                     (0, 0, 0))
    s5l14 = textrect.render_textrect("OUR KINGDOM.", myFont, pygame.Rect((40, 40, xMulti * 40, yMulti * 10)),
                                     (255, 255, 255), (0, 0, 0))
    s5l15 = textrect.render_textrect("[LAFTA THEN FALLS INTO AN ETERNAL\nSLEEP]", myFont,
                                     pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))

    s7l1 = textrect.render_textrect("KING: I SEE YOU ARE WEARING YOUR\nRING, PRINCE GHANERA. WELCOME BACK.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))
    s7l2 = textrect.render_textrect("CONGRADULATIONS, YOU HAVE SAVED\nOUR KINGDOM.", myFont,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 10)), (255, 255, 255), (0, 0, 0))

    s9l1 = textrect.render_textrect(" GG   AA  M  M EEEE   OO  V  V EEEE RRR\n" +
                                    "G  G A  A MMMM E     O  O V  V E    R  R\n" +
                                    "G    A  A MMMM E     O  O V  V E    R  R\n" +
                                    "G    AAAA M  M EEE   O  O V  V EEE  RRR\n" +
                                    "G GG A  A M  M E     O  O V  V E    R R\n" +
                                    "G  G A  A M  M E     O  O  VV  E    R  R\n" +
                                    " GG  A  A M  M EEEE   OO   VV  EEEE R  R", scene9Font,
                                    pygame.Rect((40, 40, xMulti * 40, yMulti * 16)), (255, 255, 255), (0, 0, 0))

    f = open("resources/scene" + str(level) + ".dat", 'r')
    file = f.read()
    f.close()
    lines = file.split("\n")

    playedSong = False
    playedSong2 = False
    clock = pygame.time.Clock()
    time = 0.0
    SeeD = random.randint(0, 100)
    done = False

    while not done:

        random.seed(
            SeeD)  # I need it to pick the same random numbers every time it goes through this loop (for scene 4)
        clock.tick(fps)
        time += 1 / fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                level = -1
            if event.type == pygame.KEYDOWN:  # for testing
                done = True

        screen.blit(background, (0, 0))
        for line in lines:
            data = line.split()
            if data[2] == "blit" or data[2] == "text":
                if float(data[0]) < time < float(data[1]):
                    # all there is to blit
                    if data[3] == "stone":
                        screen.blit(stone, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "wood":
                        screen.blit(wood, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "random":
                        if random.randint(0, 1):
                            screen.blit(wood, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                        else:
                            screen.blit(stone, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "oneUp":
                        screen.blit(oneUp, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "aarak":
                        screen.blit(aarak.image, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "messenger":
                        screen.blit(messenger, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "sanou":
                        screen.blit(sanou, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "king":
                        screen.blit(king, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "lafta":
                        screen.blit(lafta, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "laftaBroken":
                        screen.blit(laftaBroken, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "aarakEnhanced":
                        screen.blit(aarakEnhanced, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "aarakAura":
                        screen.blit(aarakAura, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "aarakBroken":
                        screen.blit(aarakBroken, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "enemy":
                        screen.blit(enemy, (float(data[4]) * xMulti, float(data[5]) * yMulti))

                    elif data[3] == "s1l1":
                        screen.blit(s1l1, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s1l2":
                        screen.blit(s1l2, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s1l3":
                        screen.blit(s1l3, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s1l4":
                        screen.blit(s1l4, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s1l5":
                        screen.blit(s1l5, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s1l6":
                        screen.blit(s1l6, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s1l7":
                        screen.blit(s1l7, (float(data[4]) * xMulti, float(data[5]) * yMulti))

                    elif data[3] == "s2l1":
                        screen.blit(s2l1, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s2l2":
                        screen.blit(s2l2, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s2l3":
                        screen.blit(s2l3, (float(data[4]) * xMulti, float(data[5]) * yMulti))

                    elif data[3] == "s3l1":
                        screen.blit(s3l1, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s3l2":
                        screen.blit(s3l2, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s3l3":
                        screen.blit(s3l3, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s3l4":
                        screen.blit(s3l4, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s3l5":
                        screen.blit(s3l5, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s3l6":
                        screen.blit(s3l6, (float(data[4]) * xMulti, float(data[5]) * yMulti))

                    elif data[3] == "s4l1":
                        screen.blit(s4l1, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s4l2":
                        screen.blit(s4l2, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s4l3":
                        screen.blit(s4l3, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s4l4":
                        screen.blit(s4l4, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s4l5":
                        screen.blit(s4l5, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s4l6":
                        screen.blit(s4l6, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s4l7":
                        screen.blit(s4l7, (float(data[4]) * xMulti, float(data[5]) * yMulti))

                    elif data[3] == "s5l1":
                        screen.blit(s5l1, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l2":
                        screen.blit(s5l2, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l3":
                        screen.blit(s5l3, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l4":
                        screen.blit(s5l4, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l5":
                        screen.blit(s5l5, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l6":
                        screen.blit(s5l6, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l7":
                        screen.blit(s5l7, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l8":
                        screen.blit(s5l8, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l9":
                        screen.blit(s5l9, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l10":
                        screen.blit(s5l10, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l11":
                        screen.blit(s5l11, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l12":
                        screen.blit(s5l12, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l13":
                        screen.blit(s5l13, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l14":
                        screen.blit(s5l14, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s5l15":
                        screen.blit(s5l15, (float(data[4]) * xMulti, float(data[5]) * yMulti))

                    elif data[3] == "s7l1":
                        screen.blit(s7l1, (float(data[4]) * xMulti, float(data[5]) * yMulti))
                    elif data[3] == "s7l2":
                        screen.blit(s7l2, (float(data[4]) * xMulti, float(data[5]) * yMulti))

                    elif data[3] == "s9l1":
                        screen.blit(s9l1, (float(data[4]) * xMulti, float(data[5]) * yMulti))

            elif data[2] == "play" and float(data[0]) < time and not playedSong:
                song.play()
                playedSong = True
            elif data[2] == "play2" and float(data[0]) < time and not playedSong2:
                song2.play()
                playedSong2 = True
            elif data[2] == "end" and float(data[0]) < time:
                done = True

        pygame.display.flip()
    if level == 7:
        level = 0
    return level


def play(level, lives):  # return level, lives

    song = pygame.mixer.Sound("resources/door.ogg")

    background = pygame.surface.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    wood = pygame.image.load("resources/wood.png")
    wood = pygame.transform.scale(wood, (int(xMulti) + 1, int(yMulti) + 1))
    wood = wood.convert()

    stone = pygame.image.load("resources/stone.png")
    stone = pygame.transform.scale(stone, (int(xMulti) + 1, int(yMulti) + 1))
    stone = stone.convert()

    door = pygame.surface.Surface((int(xMulti) + 1, int(yMulti) + 1))
    door = door.convert()
    door.fill((0x99, 0x55, 0x55))

    aarak = Aarak(level)

    enemies = []
    numberOfEnemies = 4  # maximum
    for count in range(numberOfEnemies):
        enemies.append(Enemy())

    oneUp = pygame.image.load("resources/heart1p.png")
    oneUp = pygame.transform.scale(oneUp, (int(xMulti), int(yMulti)))
    oneUp = oneUp.convert()

    fire = pygame.image.load("resources/fireball.png")
    fire = pygame.transform.scale(fire, (int(xMulti), int(yMulti)))
    transColor = fire.get_at((1, 1))
    fire.set_colorkey(transColor)
    fire = fire.convert()

    myFont = pygame.font.SysFont("default", int(yMulti * 2))
    livesText = myFont.render("LIVES:", False, (255, 255, 255))
    energyText = myFont.render("ENERGY:", False, (255, 255, 255))
    zero = myFont.render("0", False, (255, 255, 255))
    one = myFont.render("1", False, (255, 255, 255))
    two = myFont.render("2", False, (255, 255, 255))
    three = myFont.render("3", False, (255, 255, 255))
    four = myFont.render("4", False, (255, 255, 255))
    five = myFont.render("5", False, (255, 255, 255))
    six = myFont.render("6", False, (255, 255, 255))
    seven = myFont.render("7", False, (255, 255, 255))
    eight = myFont.render("8", False, (255, 255, 255))
    nine = myFont.render("9", False, (255, 255, 255))

    leftDown = False
    leftWentDown = False
    rightDown = False
    rightWentDown = False

    finishedLevel = False
    if not level == 11:
        file = open("resources/level" + str(level) + ".dat", 'r')

    while not finishedLevel:
        for enemy in enemies:
            enemy.reset()
        enemyN = 0
        terrain = []  # ip
        for fill in range(4200):
            terrain.append(0)
        for terx in range(0, 4000, 100):
            if level != 11:  # normal level
                tery = 0
                line = file.readline()
                elements = line.split(',')
                for element in elements:
                    terrain[terx + tery] = int(element.strip())
                    if terrain[terx + tery] == 46:
                        enemies[enemyN].position[0] = int(terx / 100)
                        enemies[enemyN].position[1] = tery
                        terrain[terx + tery] = 32
                        enemyN += 1
                    tery += 1
            else:  # secret level
                for tery in range(16):
                    z7 = random.randint(0, 480)
                    terrain[terx + tery] = 32
                    if z7 > 460:
                        terrain[terx + tery] = 176
                    elif z7 == 253:
                        terrain[terx + tery] = 35
                    elif z7 == 157:
                        terrain[terx + tery] = 61
                    elif z7 == 391 and 400 < terx < 3600 and tery != 0:
                        terrain[terx + tery] = 46
                    if terrain[terx + tery] == 46 and enemyN < 4:
                        enemies[enemyN].position[0] = int(terx / 100)
                        enemies[enemyN].position[1] = tery
                        terrain[terx + tery] = 32
                        enemyN += 1
                    if 0 < terx < 400 and tery == 15:
                        terrain[terx + tery] = 176

        clock = pygame.time.Clock()
        timeSinceEnemyHurt = 0.0
        finishedRoom = False

        while not finishedRoom:

            clock.tick(fps)

            aarak.fall(terrain, leftDown, rightDown)

            for enemy in enemies:
                enemy.move(terrain)

            for count in range(2):
                # fireball hits

                if aarak.shooty < 50:
                    if terrain[int(aarak.shootx) * 100 + round(aarak.shooty)] == 176:
                        aarak.shooty = 55
                    elif terrain[int(aarak.shootx) * 100 + round(aarak.shooty)] == 64:
                        terrain[int(aarak.shootx) * 100 + round(aarak.shooty)] = 32
                        aarak.shooty = 55
                    for enemy in enemies:
                        if abs(aarak.shootx - enemy.position[0]) < 2 and round(aarak.shooty) == enemy.position[1] - 1:
                            enemy.position[0] = 50  # off screen, dead
                            enemy.position[1] = 50
                            aarak.shooty = 55  # and bullet off screen

                # move fireball

                if aarak.shooty < 50:
                    aarak.shootx += aarak.shootv
                    # a sound could go with this?
                    if aarak.shootx > 40 or aarak.shootx < -1:
                        aarak.shooty = 55

            lives = aarak.get1up(lives, terrain)

            # detect collision with enemy (line FOR before 690)

            timeSinceEnemyHurt += 1 / fps
            if timeSinceEnemyHurt >= .8:  # can't get hurt more than once per .8 seconds
                for enemy in enemies:
                    if abs(aarak.position[0] - enemy.position[0]) < 2.5:  # if they collide on x
                        if 3 > aarak.position[1] - enemy.position[1] > -2:
                            aarak.hp -= 1
                            timeSinceEnemyHurt = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1, lives
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # shoot
                        if level > 1:
                            aarak.shoot()
                    elif event.key == pygame.K_RIGHT:
                        aarak.facing = 1
                        rightDown = True
                        rightWentDown = True
                    elif event.key == pygame.K_LEFT:
                        aarak.facing = -1
                        leftDown = True
                        leftWentDown = True
                    elif event.key == pygame.K_UP:
                        leftWentDown = False
                        rightWentDown = False
                        aarak.jump(terrain)
                    elif event.key == pygame.K_DOWN and terrain[round(aarak.position[0]) * 100 +
                                                                int(aarak.position[1])] == 61 and level != 11:
                        song.play()
                        finishedRoom = True
                        finishedLevel = True
                        level += 1
                    elif event.key == pygame.K_DOWN and terrain[round(aarak.position[0]) * 100 +
                                                                int(aarak.position[1])] == 61 and level == 11:
                        # in secret level, push down in a door moves you to the next room
                        finishedRoom = True
                        aarak.position = [2, 14]
                        aarak.weight = 0
                        aarak.shootx = 55
                        aarak.shooty = 55
                    elif event.key == pygame.K_DOWN and level == 11:
                        aarak.hp = 0  # in secret level, push down when not in a door is suicide
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        rightDown = False
                    elif event.key == pygame.K_LEFT:
                        leftDown = False

            # if left/right is down or went down, move and then change WentDown to False
            if leftDown or leftWentDown:
                leftWentDown, rightWentDown = aarak.moveLeft(terrain, leftWentDown, rightWentDown)
            if rightDown or rightWentDown:
                leftWentDown, rightWentDown = aarak.moveRight(terrain, leftWentDown, rightWentDown)

            if aarak.position[0] > 38:
                aarak.position[0] -= 38
                finishedRoom = True

            # die
            if aarak.hp < 1:
                lives -= 1
                finishedRoom = True
                finishedLevel = False
                aarak.position = [47, 47]  # pp
                aarak.weight = 0
                aarak.shootx = 55
                aarak.shooty = 55
                if level != 11:
                    file.close()
                    file = open("resources/level" + str(level) + ".dat", 'r')
                else:
                    aarak.reset(level)
            if lives < 1:
                finishedLevel = True
                if level != 11:
                    file.close()

            screen.blit(background, (0, 0))
            screen.blit(livesText, (xMulti * 2, yMulti * 18))
            if lives == 0:
                screen.blit(zero, (xMulti * 8, yMulti * 18))
            elif lives == 1:
                screen.blit(one, (xMulti * 8, yMulti * 18))
            elif lives == 2:
                screen.blit(two, (xMulti * 8, yMulti * 18))
            elif lives == 3:
                screen.blit(three, (xMulti * 8, yMulti * 18))
            elif lives == 4:
                screen.blit(four, (xMulti * 8, yMulti * 18))
            elif lives == 5:
                screen.blit(five, (xMulti * 8, yMulti * 18))
            elif lives == 6:
                screen.blit(six, (xMulti * 8, yMulti * 18))
            elif lives == 7:
                screen.blit(seven, (xMulti * 8, yMulti * 18))
            elif lives == 8:
                screen.blit(eight, (xMulti * 8, yMulti * 18))
            elif lives == 9:
                screen.blit(nine, (xMulti * 8, yMulti * 18))
            screen.blit(energyText, (xMulti * 12, yMulti * 18))
            if aarak.hp == 0:
                screen.blit(zero, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 1:
                screen.blit(one, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 2:
                screen.blit(two, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 3:
                screen.blit(three, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 4:
                screen.blit(four, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 5:
                screen.blit(five, (xMulti * 20, yMulti * 18))
            for terx in range(0, 40):
                for tery in range(0, 16):
                    if terrain[terx * 100 + tery] == 176:
                        screen.blit(stone, (terx * xMulti, tery * yMulti))
                    elif terrain[terx * 100 + tery] == 64:
                        screen.blit(wood, (terx * xMulti, tery * yMulti))
                    elif terrain[terx * 100 + tery] == 61:
                        screen.blit(door, (terx * xMulti, tery * yMulti))
                    elif terrain[terx * 100 + tery] == 35:
                        screen.blit(oneUp, (terx * xMulti, tery * yMulti))
            if not finishedRoom:
                aarak.blit()
            for enemy in enemies:
                enemy.blit()
            if aarak.shooty < 50:
                screen.blit(fire, (aarak.shootx * xMulti, aarak.shooty * yMulti))
            pygame.display.flip()

            if aarak.hp < 1:
                aarak.reset(level)
                for timePass in range(0, fps):
                    clock.tick(fps)

    for timePass in range(0, 2 * fps):
        clock.tick(fps)
    return level, lives


def lastroom(level, lives):  # return level, lives

    background = pygame.surface.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    stone = pygame.image.load("resources/stone.png")
    stone = pygame.transform.scale(stone, (int(xMulti) + 1, int(yMulti) + 1))
    stone = stone.convert()

    aarak = Aarak(level)

    enemy = pygame.image.load("resources/boss.png")
    enemy = pygame.transform.scale(enemy, (int(xMulti * 5), int(yMulti * 3)))
    transColor = enemy.get_at((1, 1))
    enemy.set_colorkey(transColor)
    enemy = enemy.convert()

    fire = pygame.image.load("resources/fireball.png")
    fire = pygame.transform.scale(fire, (int(xMulti), int(yMulti)))
    transColor = fire.get_at((1, 1))
    fire.set_colorkey(transColor)
    fire = fire.convert()

    myFont = pygame.font.SysFont("default", int(yMulti * 2))
    livesText = myFont.render("LIVES:", False, (255, 255, 255))
    energyText = myFont.render("ENERGY:", False, (255, 255, 255))
    zero = myFont.render("0", False, (255, 255, 255))
    one = myFont.render("1", False, (255, 255, 255))
    two = myFont.render("2", False, (255, 255, 255))
    three = myFont.render("3", False, (255, 255, 255))
    four = myFont.render("4", False, (255, 255, 255))
    five = myFont.render("5", False, (255, 255, 255))
    six = myFont.render("6", False, (255, 255, 255))
    seven = myFont.render("7", False, (255, 255, 255))
    eight = myFont.render("8", False, (255, 255, 255))
    nine = myFont.render("9", False, (255, 255, 255))

    music = pygame.mixer.Sound("resources/lastroom peak-12.ogg")

    enemyHp = 10

    leftDown = False
    leftWentDown = False
    rightDown = False
    rightWentDown = False

    finishedLevel = False
    file = open("resources/lastroom.dat", 'r')
    music.play(-1)

    while not finishedLevel:
        enemyMove = [-2.5 / fps]  # de
        enemyWeight = 0.0

        enemyN = 0
        enemyPosition = [[4.0, 14.0]]  # pe
        terrain = []  # ip
        for fill in range(4200):
            terrain.append(0)
        for terx in range(0, 4000, 100):
            tery = 0
            line = file.readline()
            elements = line.split(',')
            for element in elements:
                terrain[terx + tery] = int(element.strip())
                tery += 1

        clock = pygame.time.Clock()
        timeSinceEnemyHurt = 0.0
        finishedRoom = False

        while not finishedRoom:

            clock.tick(fps)

            aarak.fall(terrain, leftDown, rightDown)

            # evemy gravity

            if enemyWeight > 0:
                enemyPosition[0][1] += enemyWeight
            elif enemyWeight < 0:
                if terrain[(int(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) - 3] != 176 and \
                   terrain[(round(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) - 3] != 176 and \
                   terrain[(int(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) - 103] != 176 and \
                   terrain[(round(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) + 97] != 176 and \
                   terrain[(int(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) - 203] != 176 and \
                   terrain[(round(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) + 197] != 176 and \
                   enemyPosition[0][1] > 2:
                    enemyPosition[0][1] += enemyWeight
            if enemyWeight <= 2 - (36 / (fps * fps)):  # so he don't fall through the ground at low fps
                enemyWeight += 36 / (fps * fps)

            # if there's anything to stand on under him, put him on ground and no down movement
            if terrain[(int(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) + 1] == 176 or \
               terrain[(round(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) + 1] == 176 or \
               terrain[(int(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) - 99] == 176 or \
               terrain[(round(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) + 101] == 176:
                if enemyWeight >= 0:
                    enemyPosition[0][1] = round(enemyPosition[0][1])  # if I'm in ground, put me on top of it
                if enemyWeight > 0:
                    enemyWeight = 0

            # move enemy
            enemyMove[0] = 0
            if enemyPosition[0][0] > aarak.position[0] and \
               terrain[round(enemyPosition[enemyN][0]) * 100 - 300 + round(enemyPosition[enemyN][1])] != 176 and \
               terrain[round(enemyPosition[enemyN][0]) * 100 - 301 + round(enemyPosition[enemyN][1])] != 176 and \
               terrain[round(enemyPosition[enemyN][0]) * 100 - 302 + round(enemyPosition[enemyN][1])] != 176 and \
               enemyPosition[0][0] > 2:
                enemyMove[0] = -4 / fps
            if enemyPosition[0][0] < aarak.position[0] and \
               terrain[int(enemyPosition[enemyN][0]) * 100 + 300 + round(enemyPosition[enemyN][1])] != 176 and \
               terrain[int(enemyPosition[enemyN][0]) * 100 + 299 + round(enemyPosition[enemyN][1])] != 176 and \
               terrain[int(enemyPosition[enemyN][0]) * 100 + 298 + round(enemyPosition[enemyN][1])] != 176 and \
               enemyPosition[0][0] < 37:
                enemyMove[0] = 4 / fps
            enemyPosition[enemyN][0] += enemyMove[enemyN]

            # enemy jump
            if terrain[(int(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) + 1] == 176 or \
               terrain[(round(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) + 1] == 176 or \
               terrain[(int(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) - 99] == 176 or \
               terrain[(round(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) + 101] == 176 or \
               terrain[(int(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) - 199] == 176 or \
               terrain[(round(enemyPosition[0][0]) * 100 + round(enemyPosition[0][1])) + 201] == 176:
                enemyWeight = -15 / fps
                # enemy boing sound? (probably not)

            for count in range(2):
                # fireball hits

                if aarak.shooty < 50:
                    if terrain[int(aarak.shootx) * 100 + round(aarak.shooty)] == 176:
                        aarak.shooty = 55
                    if abs(aarak.shootx - enemyPosition[enemyN][0]) < 2:
                        if int(aarak.shooty) == int(enemyPosition[enemyN][1]) - 1 or int(aarak.shooty) == int(
                                enemyPosition[enemyN][1]) - 2:
                            enemyHp -= 1
                            aarak.shooty = 55

                # move fireball

                if aarak.shooty < 50:
                    aarak.shootx += aarak.shootv
                    # a sound could go with this?
                    if aarak.shootx > 40 or aarak.shootx < -1:
                        aarak.shooty = 55

            # detect collision with enemy (line FOR before 690)
            timeSinceEnemyHurt += 1 / fps
            if timeSinceEnemyHurt >= .8:  # can't get hurt more than once per .8 seconds
                if abs(aarak.position[0] - enemyPosition[enemyN][0]) < 3.5:  # if they collide on x
                    if 3 > aarak.position[1] - enemyPosition[enemyN][1] > -3:
                        aarak.hp -= 1
                        timeSinceEnemyHurt = 0

        # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1, lives
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # shoot
                        if level > 1:
                            aarak.shoot()
                    elif event.key == pygame.K_RIGHT:
                        aarak.facing = 1
                        rightDown = True
                        rightWentDown = True
                    elif event.key == pygame.K_LEFT:
                        aarak.facing = -1
                        leftDown = True
                        leftWentDown = True
                    elif event.key == pygame.K_UP:
                        leftWentDown = False
                        rightWentDown = False
                        aarak.jump(terrain)
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        rightDown = False
                    elif event.key == pygame.K_LEFT:
                        leftDown = False

            # if left/right is down or went down, move and then change WentDown to False
            if leftDown or leftWentDown:
                leftWentDown, rightWentDown = aarak.moveLeft(terrain, leftWentDown, rightWentDown)
            if (rightDown or rightWentDown) and aarak.position[0] < 40:  # in last room, keep him from going off screen
                leftWentDown, rightWentDown = aarak.moveRight(terrain, leftWentDown, rightWentDown)

            if enemyHp < 1:
                music.stop()
                finishedRoom = True
                finishedLevel = True
                level += 1

            # die
            if aarak.hp < 1:
                lives -= 1
                file.close()
                finishedRoom = True
                enemyHp = 10
                aarak.position = [47, 47]  # pp
                aarak.weight = 0
                aarak.shootx = 55
                aarak.shooty = 55

                leftDown = False
                leftWentDown = False
                rightDown = False
                rightWentDown = False

                finishedLevel = False
                file = open("resources/lastroom.dat", 'r')
            if lives < 1:
                file.close()
                music.stop()
                finishedLevel = True

            screen.blit(background, (0, 0))
            screen.blit(livesText, (xMulti * 2, yMulti * 18))
            if lives == 0:
                screen.blit(zero, (xMulti * 8, yMulti * 18))
            elif lives == 1:
                screen.blit(one, (xMulti * 8, yMulti * 18))
            elif lives == 2:
                screen.blit(two, (xMulti * 8, yMulti * 18))
            elif lives == 3:
                screen.blit(three, (xMulti * 8, yMulti * 18))
            elif lives == 4:
                screen.blit(four, (xMulti * 8, yMulti * 18))
            elif lives == 5:
                screen.blit(five, (xMulti * 8, yMulti * 18))
            elif lives == 6:
                screen.blit(six, (xMulti * 8, yMulti * 18))
            elif lives == 7:
                screen.blit(seven, (xMulti * 8, yMulti * 18))
            elif lives == 8:
                screen.blit(eight, (xMulti * 8, yMulti * 18))
            elif lives == 9:
                screen.blit(nine, (xMulti * 8, yMulti * 18))
            screen.blit(energyText, (xMulti * 12, yMulti * 18))
            if aarak.hp == 0:
                screen.blit(zero, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 1:
                screen.blit(one, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 2:
                screen.blit(two, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 3:
                screen.blit(three, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 4:
                screen.blit(four, (xMulti * 20, yMulti * 18))
            elif aarak.hp == 5:
                screen.blit(five, (xMulti * 20, yMulti * 18))
            for terx in range(0, 40):
                for tery in range(0, 16):
                    if terrain[terx * 100 + tery] == 176:
                        screen.blit(stone, (terx * xMulti, tery * yMulti))
            if not finishedRoom:
                aarak.blit()
            screen.blit(enemy, (
                (enemyPosition[enemyN][0] * xMulti) - (xMulti * 2), (enemyPosition[enemyN][1] * yMulti) - (yMulti * 2)))
            if aarak.shooty < 50:
                screen.blit(fire, (aarak.shootx * xMulti, aarak.shooty * yMulti))
            pygame.display.flip()

            if aarak.hp < 1:
                aarak.reset(level)
                for timePass in range(0, fps):
                    clock.tick(fps)

    return level, lives


def main():
    pygame.display.set_caption("Rharma")

    # level: 0 title screen -1 quit 11 secret level 6 last room 7 win 9 game over
    end = False
    while not end:
        level = title()
        lives = 3
        while level > 0:
            if level != 6 and level != 11:
                level = scene(level)
            if (0 < level < 6) or level == 11:
                level, lives = play(level, lives)
            elif level == 6:
                level, lives = lastroom(level, lives)
            if lives < 1:
                scene(9)
                level = 0
        if level == -1:
            end = True
    pygame.quit()


if __name__ == "__main__":
    main()
