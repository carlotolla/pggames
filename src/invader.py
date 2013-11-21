"""
############################################################
Cosmogonic Invaders - A multiplayer invasion battle
############################################################

:Author: *Carlo E. T. Oliveira*
:Contact: carlo@nce.ufrj.br
:Date: 2013/11/20
:Status: This is a "work in progress"
:Home: `Labase <http://labase.selfip.org/>`__
:Copyright: 2013, `GPL <http://is.gd/3Udt>`__.

Cosmogonic invaders are a divided race conquering anothers race planet.
"""
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
                self.cria_caverna()
            if 'CHANNEL_' in data and data['sID'] != str(self.sid):
                print('CHANNEL_ in data', self.sid, data)
                self.event[data['CHANNEL_']](**data)
            print('ev.data', ev.data)
        self.assets = {}
        self.actor = self
        self.sid = ''
        self.color = 0
        self.defender = [self] * 12
        self.send = nop
        self.space = None
        self.event = dict(move=self.move_heroi, cria=self.cria_heroi, pega=self.pega_item)
        self.doc = gui.DOC
        self.html = gui.HTML
        self.gui = gui
        #self.pusher = gui.WSK('ws://achex.ca:4010')
        #self.pusher.on_open = conecta
        #self.pusher.on_message = recebe

        self.div = self.doc['main']
        self.shell = [face for kind in PIECE[:-1] for face in kind]
        self.atacks = ATACKS*2
        self.create_assets()

    def create_assets(self):
        """Assemble alien armies."""
        self.space = Space(self.html, self)
        #Defender(self.html, self, PIECE[0][0])
        ships = SHIPS[:]
        shuffle(ships)
        routes = ROUTES*4
        shuffle(routes)
        debris = zip(PIECE[-1]*8, routes)
        shuffle(self.atacks)
        shuffle(self.shell)
        flak = zip(self.shell, self.atacks)
        print("Assemble alien armies.", flak)
        [Atacker(self.html, self, face, FACES.index(face), route)
         for color, (face, route) in enumerate(flak[:2])]
        [Defender(self.html, self, face, FACES.index(face), place[0], place[1])
         for color, (face, place) in enumerate(zip(FACES, ships))]
        [Lander(self.html, self, face[color % 3], HEIGHT + 2*WIDTH*color)
         for color, face in enumerate(PIECE[-1])]
        [Debris(self.html, self, face, color, route, kind) for kind in (20, 30, 40)
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

    def cria_heroi(self, camara='Camara0', nome=None, sID=None, tipo=True, **kwargs):
        """Cria um heroi em uma sala da caverna."""
        nome = nome or 'h' + self.sid
        if nome not in self.herois:
            heroi = self.habitante[tipo](self.html, self.sala[camara], nome)
            self.herois[nome] = heroi
            if sID == self.sid:
                #self.heroi = heroi
                self.send(channel='cria', camara=camara, nome=nome, tipo=tipo)
            else:
                if tipo:
                    print('cria_heroi, tipo, self.heroi, self.sid, sID', tipo, self.heroi, self.sid, sID)
                    self.send(channel='cria', camara=self.heroi.local(), nome=self.heroi.nome, tipo=tipo)
                else:
                    print('cria_heroi, tipo, self.heroi, self.sid, sID', tipo, self.heroi, self.sid, sID)
                    self.send(channel='cria', camara=self.monster.local(), nome=self.monster.nome, tipo=tipo)
            return heroi

    def move_heroi(self, camara='Camara0', nome='heroi', sID=None, **kwargs):
        """Move um heroi em uma sala da caverna."""
        self.herois[nome].move(self.sala[camara])
        if sID == self.sid:
            self.send(channel='move', camara=camara, nome=nome)

    def entra(self, destino):
        """Entra em uma sala da caverna."""
        self.caverna <= self.local.camara
        #self.local.camara <= self.heroi.heroi
        self.move_heroi(camara=self.local.camara.Id, nome=self.heroi.nome, sID=self.sid)
        self.ambiente <= self.local.camara

    def pega_item(self, item=None, nome=None, sID=None, **kwargs):
        print('pega_item', item, nome, sID)
        self.herois[nome].pega(self.doc[item])
        if sID == self.sid:
            self.send(channel='pega', item=item, nome=nome)

    def pega(self, item):
        heroi, sid, it = self.heroi.nome, self.sid, item
        print('pega', it, heroi, sid)
        self.pega_item(item=it, nome=heroi, sID=sid)
        #self.pega_item(item, self.heroi.nome, self.sid)


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
        #print("Inicializa Heroi. ", face)
        self.kind, self.l, self.t = self.__class__.__name__, go(px), go(py)
        self._id = "%s%d_%d" % (self.kind, self.l, self.t)
        estilo = dict(width=WIDTH, height=WIDTH, background='url(%s) 100%% 100%% / cover' % face,
                      Float="left", position="absolute", left=self.l, top=self.t, opacity=0.6)
        self.div = self.html.DIV(Id=self._id, style=estilo)
        self.cosmo.div <= self.div
        self.div.onclick = click

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

    def no_move(self, camara):
        """Movimenta Heroi. """
        self.cosmo = camara
        self.cosmo.camara <= self.div

    def pega(self, item):
        """Localiza Heroi. """
        self.mochila <= item


class Lander:
    """Lands and conquer planet terrain. :ref:`lander`
    """
    def __init__(self, gui, cosmo, face, left):
        """Init Lander. """
        self.html, self.cosmo, self.face = gui, cosmo, face
        #print("Inicializa Lander. ", face)
        self.kind, self.l, self.t = self.__class__.__name__, left, TOP
        estilo = dict(width=WIDTH+10, height=WIDTH+10, background='url(%s) 100%% 100%% / cover' % face,
                      Float="left", position="absolute", left=self.l, top=self.t, opacity=0.6)
        self.div = self.html.DIV(Id="%s%d_%d" % (self.kind, self.l, self.t), style=estilo)
        self.cosmo.div <= self.div


class Debris:
    """Remains of wasted atackers. :ref:`debris`
    """
    def __init__(self, gui, cosmo, face, color, route, kind):
        """Init Debris. """
        self.html, self.cosmo, self.face = gui, cosmo, face
        #print("Inicializa Debris. ", face, color, route)
        self.kind, self.l, self.t = self.__class__.__name__, ORBIT, ORBIT
        estilo = dict(
            width=kind, height=kind, background='url(%s) 100%% 100%% / cover' % face,
            Float="left", position="absolute", left=self.l, top=self.t, opacity=0.6,
            animation='%s %fs linear %fs infinite alternate' % (
                route, random()*5+5, random()*2
            ))
            #animation='%s 5s linear %ds infinite alternate %s 5s linear %ds infinite alternate' % (
            #    route[0], randint(1, 6), route[1], randint(1, 6)
            #))
        self.div = self.html.DIV(Id="%s_%d" % (self.kind, color), style=estilo)
        self.cosmo.div <= self.div


class Atacker:
    """Flak defenses from invaded planet orbit. :ref:`atacker`
    """
    def __init__(self, gui, cosmo, face, color, route):
        """Init Atacker. """
        def over(ev):
            print("Init Atacker over. ", self, ev.target.Id, color, self._id)
            self.cosmo.try_me(color, self)
        self.html, self.cosmo, self.face, self.color = gui, cosmo, face, color
        #print("Inicializa Debris. ", face, color, route)
        self.kind, self.l, self.t = self.__class__.__name__, -100, 0
        estilo = dict(
            width=WIDTH, height=WIDTH, background='url(%s) 100%% 100%% / cover' % face,
            Float="left", position="absolute", left=self.l, top=self.t, opacity=0.6,
            animation='%s %fs ease-out %fs 1 normal' % (
                route, random()*2+16, random()*2+2*color
            ))
        self._id = "%s_%d" % (self.kind, color)
        self.div = self.html.DIV(Id=self._id, style=estilo)
        self.div.onmouseover = over
        self.div.onanimationend = self.hit
        self.cosmo.div <= self.div

    def hit(self, ev):
        self.cosmo.defend_planet(self._id, self)
        #print("Init Atacker hit. ", self, ev.target.Id)

    def fail(self, ev):
        #print("Init Atacker fail. ", self, ev.target.Id)
        self.cosmo.trigger_flak(self._id, self)
        self.div.style.display = 'none'
        self.div.onanimationend = self.hit

    def trigger_flak(self, face, route):
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


class NoAtacker:
    """Um monstro que assombra a caverna. :ref:`monstro`
    """
    def __init__(self, gui, camara, face, top):
        """Inicializa Heroi. """

        self.html, self.camara, self.nome = gui, camara, nome
        estilo = dict(width=50, height=50, background='url(%s) 100%% 100%% / cover' % face,
                      Float="left", position="absolute", left=LEFT, top=top, opacity=0.6)
        self.div = self.html.DIV(Id=nome, style=estilo)
        self.camara.camara <= self.div

    def local(self):
        """Localiza Heroi. """
        return self.camara.camara.Id

    def no_move(self, camara):
        """Movimenta Heroi. """
        self.camara = camara
        self.camara.camara <= self.div

    def pega(self, item):
        """Localiza Heroi. """
        self.mochila <= item


class Space:
    """The last frontier, scenary wher battles are fought. :ref:`space`
    """

    def __init__(self, gui, cosmo, nome='Space'):
        """Inicializa Camara. """
        def click(ev):
            self.cosmo.acquire(0, self.cosmo)
        self.html, self.cosmo, self.nome = gui, cosmo, nome
        estilo = dict(width=1000, height=HEIGHT, background='url(%s) 100%% 100%% / cover' % COSMO)
        self.div = self.html.DIV(nome, Id=nome, style=estilo)

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
