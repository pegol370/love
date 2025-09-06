# main.py
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.animation import Animation
from random import randint, choice
from kivy.core.window import Window

KV = '''
#:import rgba kivy.utils.get_color_from_hex

<HeartParticle@Widget>:
    size_hint: None, None
    size: dp(36), dp(36)
    angle: 0
    color: 1, 0.2, 0.6, 1
    canvas:
        PushMatrix
        Rotate:
            angle: self.angle
            origin: self.center
        Color:
            rgba: self.color
        Ellipse:
            size: self.size
            pos: self.pos
        PopMatrix

<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: 0.06, 0.02, 0.12, 1
            Rectangle:
                size: self.size
                pos: self.pos
        Label:
            text: "Welcome to Pegol"
            font_size: '28sp'
            size_hint_y: None
            height: self.texture_size[1] + dp(6)
            bold: True
            color: 1,0.75,0.85,1
        Label:
            text: "Enter password:"
            size_hint_y: None
            height: self.texture_size[1] + dp(4)
            color: 1,1,1,0.9
        TextInput:
            id: pwd
            password: True
            multiline: False
            hint_text: "Type password..."
            size_hint_y: None
            height: dp(46)
            on_text_validate: root.verify(pwd.text)
        Button:
            text: "Enter"
            size_hint_y: None
            height: dp(48)
            on_release: root.verify(pwd.text)
        Label:
            id: info
            text: root.info_text
            color: 1,0.6,0.7,1
            size_hint_y: None
            height: self.texture_size[1] + dp(6)

<AnimationScreen>:
    FloatLayout:
        id: stage
        canvas.before:
            Color:
                rgba: 0.05, 0.0, 0.06, 1
            Rectangle:
                pos: self.pos
                size: self.size

        # Center pulsing message
        Label:
            id: center_msg
            text: root.center_text
            font_size: '30sp'
            markup: True
            size_hint: None, None
            size: self.texture_size
            pos_hint: {"center_x":0.5, "center_y":0.55}
            color: 1, 0.85, 0.9, 1

        Label:
            text: root.from_text
            font_size: '18sp'
            pos_hint: {"center_x":0.5, "center_y":0.45}
            color: 0.9, 0.7, 1, 1

        Button:
            text: "Exit"
            size_hint: None, None
            size: dp(80), dp(40)
            pos_hint: {"right":0.98, "y":0.02}
            on_release: app.stop()
'''

# --- Screens ---
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

class LoginScreen(Screen):
    info_text = StringProperty("")
    def verify(self, text):
        if text.strip() == "seham":
            self.manager.current = "anim"
            self.manager.get_screen('anim').start_animation()
        else:
            self.info_text = "Wrong password. Try again."

class HeartParticle(Widget):
    vx = NumericProperty(0)
    vy = NumericProperty(0)
    life = NumericProperty(1)
    color = ListProperty([1, 0.2, 0.6, 1])

class AnimationScreen(Screen):
    center_text = StringProperty("[b]Love you, Mum ♥[/b]")
    from_text = StringProperty("From Pegol")
    _spawn_ev = None
    particles = []

    def on_pre_enter(self):
        Window.clearcolor = (0.05, 0.0, 0.06, 1)

    def start_animation(self):
        # center pulsing animation
        lbl = self.ids.center_msg
        anim = Animation(font_size=42, duration=0.6, t='out_quad') + Animation(font_size=30, duration=0.6, t='in_quad')
        anim.repeat = True
        anim.start(lbl)

        # spawn floating hearts periodically
        if self._spawn_ev:
            self._spawn_ev.cancel()
        self._spawn_ev = Clock.schedule_interval(self._spawn_heart, 0.16)

        # continuous rotation / tweak for existing particles
        Clock.schedule_interval(self._update_particles, 1/30.)

    def _spawn_heart(self, dt):
        # create a heart particle (simple colored ellipse — looks like heart-ish on small sizes)
        p = HeartParticle()
        width = self.ids.stage.width
        height = self.ids.stage.height
        # random start X near bottom center
        p.size = (36, 36)
        p.pos = (randint(int(width*0.15), int(width*0.85)), -40)
        p.vx = randint(-20, 20) / 10.0
        p.vy = randint(40, 90) / 10.0
        # pick color
        colors = [
            (1.0, 0.4, 0.6, 1),
            (1.0, 0.7, 0.9, 1),
            (1.0, 0.6, 0.3, 1),
            (0.9, 0.5, 1.0, 1)
        ]
        p.color = choice(colors)
        self.ids.stage.add_widget(p)
        self.particles.append(p)

        # animate size / rotation / fade out using Animation
        anim = Animation(y=height + 80, x=p.x + randint(-60, 60), duration=3 + randint(0,2), t='out_quad') & \
               Animation(opacity=0, duration=3 + randint(0,2))
        # also pulse scale
        anim &= Animation(size=(p.width*1.5, p.height*1.5), duration=1.2) + Animation(size=(p.width, p.height), duration=1.2)
        anim.bind(on_complete=lambda inst, wid: self._kill_particle(p))
        anim.start(p)

        # small continuous rotation:
        def rot(dt):
            if p.parent:
                p.angle += randint(-6,6)
        Clock.schedule_interval(rot, 0.12)

    def _kill_particle(self, p):
        try:
            if p in self.particles:
                self.particles.remove(p)
            if p.parent:
                self.ids.stage.remove_widget(p)
        except Exception:
            pass

    def _update_particles(self, dt):
        # gentle sway for particles (to make motion more organic)
        for p in list(self.particles):
            # slight horizontal wobble
            p.x += (p.vx * dt * 20)
            # gravity effect reduced (we animated y already but keep slight offset)
            p.y += (p.vy * dt * 10)

class PegolApp(App):
    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AnimationScreen(name='anim'))
        return sm

if __name__ == "__main__":
    PegolApp().run()
