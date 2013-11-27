"""
############################################################
Cosmo Conquerors - A multiplayer invasion battle
############################################################

:Author: *Carlo E. T. Oliveira*
:Contact: carlo@nce.ufrj.br
:Date: 2013/11/20
:Status: This is a "work in progress"
:Home: `Labase <http://labase.selfip.org/>`__
:Copyright: 2013, `GPL <http://is.gd/3Udt>`__.

Cosmo Conquerors are a divided race conquering anothers race planet.
"""
ATACK_PATH = "M-1000 %d L550 %d"
WIDTH = 40
__version__ = '0.1.0'

from random import randint, shuffle, random
COSMO = "https://dl.dropboxusercontent.com/u/1751704/labase/pggames/space-planets.jpg"
PIECESTR = "https://dl.dropboxusercontent.com/u/1751704/labase/pggames/type%%20%d/type%d%%20%s.png"
PIECE = [[PIECESTR % (i, i, name) for i in [1, 2, 4]] for name in "blue green red yellow silver".split()]
FACE = [face for kind in PIECE[:-1] for face in kind]
FACES = FACE + FACE
LEFT = TOP = 10
HEIGHT = 700
ORBIT = HEIGHT * 0.9
STEP = int(ORBIT // 5)
DEPLOY = range(WIDTH, ORBIT, STEP)
SHIPS = [(x+2*WIDTH, y+WIDTH) for x in DEPLOY for y in DEPLOY]
ROUTES = ['alt%d' % r for r in range(10)]
ATACKS = ['atk%d' % r for r in range(12)]
MYID, MYPASS, START = 'private-cosmo-conquerors', 'c5c9p7', 'S_T_A_R_T__'


class Cosmo:
    """A section of the cosmos being invaded. :ref:`cosmo`
    """
    def __init__(self, gui):
        """Init cosmos. """
        def nop(**kwargs):
            pass

        def envia(channel='move', **kwargs):
            data = dict(to=MYID, CHANNEL_=channel, **kwargs)
            print('envia', data)
            self.pusher.send(gui.JSON.dumps(data))

        def conecta():
            self.pusher.send('{"setID":"' + MYID + '","passwd":"' + MYPASS + '"}')
            self.send = envia
            #self.pusher.send('{"to":"' + MYID + '","' + START + '":"' + START + '"}')

        def recebe(ev):
            data = gui.JSON.loads(ev.data)
            if 'SID' in data:
                self.sid = str(data['SID'])
                self.create_assets()
            if 'CHANNEL_' in data and data['sID'] != str(self.sid):
                print('CHANNEL_ in data', self.sid, data)
                self.event[data['CHANNEL_']](**data)
            print('ev.data', ev.data)

        self.event = self.assets = {}
        self.actor = self
        self.sid = ''
        self.color = 0
        self.defenders = self.defender = [self] * 12
        self.send = nop
        self.pusher = self.space = None
        #self.event = dict(move=self.move_heroi, cria=self.cria_heroi, pega=self.pega_item)
        self.doc = gui.DOC
        self.html = gui.HTML
        self.vg = gui.SVG
        self.br_gui = gui
        self.win = gui.WIN
        self.timer = gui.TIME
        self.gamepad = {}
        #self.pusher = gui.WSK('ws://achex.ca:4010')
        #self.pusher.on_open = conecta
        #self.pusher.on_message = recebe

        self.div = self.doc['main']
        self.svg = gui.SVG.svg(width=1000, height=HEIGHT)
        #self.div <= self.svg

        self.shell = [face for kind in PIECE[:-1] for face in kind]
        self.atacks = ATACKS*2
        self.create_assets()

    def create_assets(self):
        """Assemble alien armies."""
        self.space = Space(self.html, self)
        self.space.div <= self.svg
        #Defender(self.html, self, PIECE[0][0])
        ships = SHIPS[:]
        shuffle(ships)
        routes = ROUTES*4
        shuffle(routes)
        debris = zip(PIECE[-1]*8, routes)
        shuffle(self.atacks)
        shuffle(self.shell)
        flak = zip(self.shell, self.atacks)
        [Attacker(self.vg, self, face, FACES.index(face), route)
         for color, (face, route) in enumerate(flak[:2])]
        #return
        self.defenders = [Defender(
            self.html, self, face, FACES.index(face), place[0], place[1])
            for color, (face, place) in enumerate(zip(FACES, ships))]
        Gamepad(self, self.win, self.timer, self.defenders)
        print("Assemble alien armies.", PIECE)
        [Lander(self.html, self, face[color % 3], HEIGHT + 2*WIDTH*color)
         for color, face in enumerate(PIECE[:-1])]
        [Debris(self.vg, self, face, color, route, kind) for kind in (20, 25, 30)
         for color, (face, route) in enumerate(debris)]

        return self

    def try_me(self, color, flak):
        self.defender[color].intercept(flak)

    def acquire(self, color, defender):
        self.space.bind_drag(defender.move)
        self.defender[self.color] = self
        self.actor = defender
        self.defender[color % 12] = defender
        self.color = color
        print("acquire", color)

    def flak_intercept(self, color, defender, Id):
        pass

    def move_asset(self, x, y):
        self.actor.move(x, y)

    def move(self, ev):
        pass

    def intercept(self, flak):
        pass

    def defend_planet(self, color, flak):
        self.trigger_flak(color, flak)

    def trigger_flak(self, color, flak):
        shuffle(self.atacks)
        shuffle(self.shell)
        flak.trigger_flak(self.shell[0], self.atacks[0])

    def move_heroi(self, camara='Camara0', nome='heroi', sID=None, **kwargs):
        """Move um heroi em uma sala da caverna."""
        if sID == self.sid:
            self.send(channel='move', camara=camara, nome=nome)

    def pega_item(self, item=None, nome=None, sID=None, **kwargs):
        print('pega_item', item, nome, sID)
        if sID == self.sid:
            self.send(channel='pega', item=item, nome=nome)

STEP = 100
DEAD = 0.265
NOP = lambda: None


class Gamepad:
    """Controls Gamepad. :ref:`gamepad`
    """

    class Button:
        """Controls Gamepad Button. :ref:`button`
        """
        def __init__(self, click=NOP, up=NOP, down=NOP):
            """Inicializa Gamepad. """
            self.action = self.dodown
            self.subscribers = dict()
            self._buttonclick = self._buttonup = self._buttondown = lambda: None
            self._down = self._dodown
            self._click = lambda: None

        def onbuttondown(self, listener):
            self._buttondown = listener

        def onbuttonup(self, listener):
            self._buttonup = listener

        def onbuttonclick(self, listener):
            self._buttonclick = listener

        def nop(self, e=0):
            pass

        def _doclick(self, e=0):
            #print('_doclick')
            self._click = lambda: None
            self._buttonclick()
            self._buttonup()

        def _dodown(self, e=0):
            #print('_dodown')
            self._down = lambda: None
            self._buttondown()

        def dodown(self, e=0):
            self._click = self._doclick
            self._down()

        def doup(self, e=0):
            self._down = self._dodown
            self._click()

    def __init__(self, cosmo, win, timer, defenders):
        """Inicializa Gamepad. """
        def choose(e=0):
            gx, gy, defend = self.clientX, self.clientY, self.defenders
            ranges = [(gx - int(a.div.left)) ** 2 + (gy - int(a.div.top)) ** 2
                      for a in defend]
            #print("Inicializa updateStatus", [pad1x, pad1y, pad2x, pad2y], self.gridx, self.gridy, ranges)
            #self.cosmo.space.div.text = [self.gridx, self.gridy]
            self.div.x, self.div.y = self.clientX, self.clientY
            defender_range = min(ranges)
            self.defender.div.style.opacity = 0.6
            #self.defender.mover(self)
            self.defender = self.defenders[ranges.index(defender_range)]
            self.defender.div.style.opacity = 1

        def mover(e=0):
            self.div.style.display = 'none'
            self.defender.move(self)

        def nop(e=0):
            self.go()
            self.go = lambda e=0: None
            pass

        def action(e=0):
            self.action = release
            self.move = mover
            self.defender.action()

        def release(e=0):
            self.action = action
            self.div.style.display = 'block'
            self.move = choose
            self.defender.release()

        def con_gamepad(e):
            self.gamepad[e.gamepad.index] = e.gamepad
            self.pad1x, self.pad1y, self.pad2x,  self.pad2y = (0, 0, 0, 0)
            a = (
                self.gamepad[0].axes[0]*STEP, self.gamepad[0].axes[1]*STEP,
                self.gamepad[0].axes[3]*STEP, self.gamepad[0].axes[4]*STEP)
            #self.win.mozRequestAnimationFrame(updateStatus)
            timer.set_interval(updateStatus, 100)
            print("Inicializa con_gamepad", self.gamepad.keys())

        def updateStatus(e=0):
            pad1x, pad1y, pad2x, pad2y = (
                self.gamepad[0].axes[0]*STEP - self.pad1x, self.gamepad[0].axes[1]*STEP - self.pad1y,
                self.gamepad[0].axes[3]*STEP - self.pad2x, self.gamepad[0].axes[4]*STEP - self.pad2y)
            gamebutton, gamepadbuttons = self.gamebutton, self.gamepad[0].buttons
            [gamebutton[i][button]() for i, button in enumerate(gamepadbuttons)]
            self.clientX = (self.clientX + int(pad1x * DEAD) + int(pad2x * DEAD)) % HEIGHT
            self.clientY = (self.clientY + int(pad1y * DEAD) + int(pad2y * DEAD)) % HEIGHT
            self.move()
        self.cosmo, self.win, self.defenders = cosmo, win, defenders
        self.go = lambda e=0: None
        self.move = choose
        self.action = action
        button_mapper = {'0': nop, '1': self.action, '2': release}
        self.gamepad = {}
        self.clientX = self.clientY = 0

        def mapper(mapping):
            button = Gamepad.Button()
            button.onbuttonclick(button_mapper[mapping])
            return {0: button.doup, 1: button.dodown}
        self.gamebutton = [mapper(mapping) for mapping in '11221100022000']
        self.defender = self.defenders[0]
        self.clientX = self.clientY = 0
        self.div = self.cosmo.vg.image(
            id="highlight", href=PIECESTR % (1, 1, "gold"), x=0,
            y=0, width=WIDTH, height=WIDTH, opacity=0.2)
        self.cosmo.svg <= self.div
        print(self.cosmo, self.win, [a.div.left for a in self.defenders])
        self.win.addEventListener("gamepadconnected", con_gamepad)


class Defender:
    """Repel atacks from orbital flak. :ref:`defender`
    """
    def __init__(self, gui, cosmo, face, color, px, py):
        """Inicializa Heroi. """
        def go(place):
            return randint(place - WIDTH, place + WIDTH)

        def unclick(ev):
            self.cosmo.acquire(self.color, self.cosmo)
            self.div.onclick = click

        def click(ev):
            self.cosmo.acquire(self.color, self)
            self.div.onclick = unclick
        self.html, self.cosmo, self.face, self.color = gui, cosmo, face, color
        self.mover = lambda ev=0: None
        self.action = self.doaction
        #print("Inicializa Heroi. ", face)
        self.kind, self.l, self.t = self.__class__.__name__, go(px), go(py)
        self._id = "%s%d_%d" % (self.kind, self.l, self.t)
        estilo = dict(width=WIDTH, height=WIDTH, background='url(%s) 100%% 100%% / cover' % face,
                      Float="left", position="absolute", left=self.l, top=self.t, opacity=0.6)
        self.div = self.html.DIV(Id=self._id, style=estilo)
        self.cosmo.div <= self.div
        self.div.onclick = click

    def doaction(self, ev=0):
        self.mover = self.move
        self.action = self.release

    def release(self, ev=0):
        self.action = self.doaction
        self.mover = lambda ev=0: None

    def no_move(self, x, y):
        """Move Heroi. """
        self.div.style.left = x
        self.div.style.top = y

    def move(self, ev):
        """Move Heroi. """
        self.div.style.left = ev.clientX
        self.div.style.top = ev.clientY

    def intercept(self, flak):
        """Localiza Heroi. """
        flak.intercept(self)
        self.div.style.display = 'none'
        return self.cosmo.flak_intercept(self.color, self, self._id)

    def local(self):
        """Localiza Heroi. """
        return self.cosmo.camara.Id


class Lander:
    """Lands and conquer planet terrain. :ref:`lander`
    """
    def __init__(self, gui, cosmo, face, left):
        """Init Lander. """
        self.html, self.cosmo, self.face = gui, cosmo, face
        print("Inicializa Lander. ", face)
        self.kind, self.l, self.t = self.__class__.__name__, left, TOP
        estilo = dict(width=WIDTH+10, height=WIDTH+10, background='url(%s) 100%% 100%% / cover' % face,
                      Float="left", position="absolute", left=self.l, top=self.t, opacity=0.6)
        self.div = self.html.DIV(Id="%s%d_%d" % (self.kind, self.l, self.t), style=estilo)
        self.cosmo.div <= self.div


class DivDebris:
    """Remains of wasted atackers. :ref:`debris`
    """
    def __init__(self, gui, cosmo, face, color, route, kind):
        """Init Debris. """
        self.html, self.cosmo, self.face = gui, cosmo, face
        #print("Inicializa Debris. ", face, color, route)
        self.kind, self.l, self.t = self.__class__.__name__, ORBIT, ORBIT
        animate = '%s %fs linear %fs infinite alternate' % (route, random()*5+5, random()*2)
        estilo = dict(
            width=kind, height=kind, background='url(%s) 100%% 100%% / cover' % face,
            Float="left", position="absolute", left=self.l, top=self.t, opacity=0.6,
            WebkitAnimation=animate, animation=animate)
            #animation='%s 5s linear %ds infinite alternate %s 5s linear %ds infinite alternate' % (
            #    route[0], randint(1, 6), route[1], randint(1, 6)
            #))
        self.div = self.html.DIV(Id="%s_%d" % (self.kind, color), style=estilo)
        self.cosmo.div <= self.div


class Debris:
    """Remains of wasted atackers. :ref:`debris`
    """
    def __init__(self, gui, cosmo, face, color, route, kind):
        """Init Debris. """
        self.vg, self.cosmo, self.face = gui, cosmo, face
        #print("Inicializa Debris. ", face, color, route)
        self.kind, self.l, self.t = self.__class__.__name__, ORBIT, ORBIT
        animatex = self.vg.animateTransform(
            attributeType="xml", attributeName="transform", begin="%dms" % randint(0, 3000),
            type="translate", to="350, %d" % (randint(-150, -380)),
            dur="%dms" % randint(6000, 12000), repeatCount="indefinite")
        animatex.setAttribute("from", "%d, 50" % (randint(-100, -450)))
        self.div = self.vg.image(
            Id="%s_%d" % (self.kind, color), href=face, x=self.l,
            y=self.t, width=kind, height=kind, opacity=0.6)
        self.div <= animatex
        self.cosmo.svg <= self.div


class DivAttacker:
    """Flak defenses from invaded planet orbit. :ref:`atacker`
    """
    def __init__(self, gui, cosmo, face, color, route):
        """Init Atacker. """
        self.html, self.cosmo, self.face, self.color = gui, cosmo, face, color
        #print("Inicializa Debris. ", face, color, route)
        self.kind, self.l, self.t = self.__class__.__name__, -100, 0
        animate = '%s %fs linear %fs 1 normal' % (route, random()*2+16, random()*2+2)
        estilo = dict(
            width=WIDTH, height=WIDTH, background='url(%s) 100%% 100%% / cover' % face,
            Float="left", position="absolute", left=self.l, top=self.t, opacity=0.6,
            _webkit_animation=animate, animation=animate)
        self._id = "%s_%d" % (self.kind, color)
        self.div = self.html.DIV(Id=self._id, style=estilo)
        self.div.onmouseover = self.over
        self.div.onanimationend = self.hit
        self.cosmo.div <= self.div


class Attacker:
    """Flak defenses from invaded planet orbit. :ref:`atacker`
    """
    def __init__(self, gui, cosmo, face, color, route):
        """Init Atacker. """
        self.vg, self.cosmo, self.face, self.color = gui, cosmo, face, color
        #print("Inicializa Debris. ", face, color, route)
        self.kind, self.l, self.t = self.__class__.__name__, -1000, 0
        self.transform = self.vg.animateMotion(
            begin="%dms" % randint(2000, 4000), rotation="auto", dur="%dms" % randint(8000, 16000),
            path=ATACK_PATH % (randint(0, HEIGHT), randint(0, 400)),
            repeatCount="indefinite")
        self._id = "%s_%d" % (self.kind, color)
        self.div = self.vg.image(
            id=self._id, href=face, x=self.l,
            y=self.t, width=WIDTH, height=WIDTH, opacity=0.6)
        self.div <= self.transform
        self.cosmo.svg <= self.div
        self.div.onmouseover = self.over
        #self.transform.onend = self.hit
        self.div.onrepeat = self.hit

    def over(self, ev):
        #print("Init Atacker over. ", self, ev.target.Id, self.color, self._id)
        self.cosmo.try_me(self.color, self)

    def hit(self, ev):
        self.cosmo.defend_planet(self._id, self)
        #print("Init Atacker hit. ", self, ev.target.Id, self._id)

    def fail(self, ev):
        #print("Init Atacker fail. ", self, ev.target.Id)
        self.cosmo.trigger_flak(self._id, self)
        self.div.style.display = 'none'
        #self.div.onanimationend = self.hit
        self.div.onend = self.hit

    def trigger_flak(self, face, route):
        """Localiza Heroi. """
        self.color = FACES.index(face)
        self.div.x, self.div.y = str(self.l), str(self.t)
        self.div.setAttribute('x', 100)  # self.l)
        self.div.setAttribute('y', self.t)
        self.div.href = face
        self.transform.path = ATACK_PATH % (randint(0, HEIGHT), randint(0, 400))
        #self.transform.dur = "%dms" % randint(6000, 12000)
        self.div.style.display = 'block'

        #print("trigger_flak. ", self, self.color, self._id)
        '''
        #self.transform.to = "800, %d" % (randint(0, 400))
        #self.transform.setAttribute("from", "20, %d" % (randint(0, 700)))
        self.transform.begin = "%dms" % randint(2000, 4000)
        #self.transform.onend = self.hit
        self.div.onend = self.hit
        #self.div.beginElement()
        self.div <= self.transform
        self.div.removeChild(self.transform)
        self.transform = self.vg.animateMotion(
            begin="%dms" % randint(2000, 4000), rotation="auto", dur="%dms" % randint(6000, 12000),
            path="M-100 %d L800 %d" % (randint(0, 700), randint(0, 400)),
            repeatCount="1")
        #self.cosmo.svg <= self.div
        self.div <= self.transform
        '''

    def div_trigger_flak(self, face, route):
        """Localiza Heroi. """
        self.color = FACES.index(face)
        estilo = dict(
            width=WIDTH, height=WIDTH, background='url(%s) 100%% 100%% / cover' % face,
            Float="left", position="absolute", left=self.l, top=self.t, opacity=0.6, display='block',
            animation='%s %fs ease-out %fs 1 normal' % (
                route, random()*2+4, random()*2+2
            ))
        self.div.onanimationend = self.hit
        self.div.style = estilo

    def intercept(self, flak):
        """Localiza Heroi. """
        self.div.animationend = self.fail
        self.div.style.display = 'none'


class Space:
    """The last frontier, scenary wher battles are fought. :ref:`space`
    """

    def __init__(self, html, cosmo, nome='Space'):
        """Inicializa Camara. """
        def click(ev):
            self.cosmo.acquire(0, self.cosmo)
        self.html, self.cosmo, self.nome = html, cosmo, nome
        estilo = dict(width=1000, height=HEIGHT, background='url(%s) 100%% 100%% / cover' % COSMO)
        estilo = dict(width=1000, height=HEIGHT)
        self.div = self.html.DIV(id=nome, style=estilo)

        cosmo.div <= self.div
        self.div.onmousemove = self.drag
        self.div.onclick = click

    def drag(self, ev):
        pass
        #self.cosmo.move_asset(ev.clientX, ev.clientY)

    def bind_drag(self, bond):
        #print(ev.clientX, ev.clientY)
        self.div.unbind("mousemove")
        self.div.onmousemove = bond


class Shuttle(Defender):
    """Uma camara da caverna. :ref:`camara`
    """
    pass


class Planet(Space):
    """Um tunel ligando duas camaras da caverna. :ref:`tunel`
    """
    pass


def main(gui):
    print('Cosmogonic Invaders %s' % __version__)
    Cosmo(gui)
