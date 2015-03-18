from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter
from kivy.animation import Animation
from kivy.properties import ListProperty,BooleanProperty
from kivy.core.window import Window
from random import randint

class Valid(Scatter):
    color = ListProperty([0,0,1,0.9])
    valid=BooleanProperty()
    def __init__(self,**kwargs):
        super(Valid,self).__init__(**kwargs)
        self.children_pos={"0":[2,2],"1":[self.width/2,2],"2":[2,self.width/2],"3":[self.width/2,self.width/2],}
        
    def on_touch_down(self,touch):
    	super(Valid,self).on_touch_down(touch)
    	if self.collide_point(*touch.pos):
            anim = Animation(opacity=1,d=0.1)
            anim.start(self.ids['btn_close'])
            anim.start(self.ids['btn_valid'])
            return True
    def on_touch_up(self,touch):
    	super(Valid,self).on_touch_up(touch)
    	if self.collide_point(*touch.pos):
            anim = Animation(opacity=0,d=0.1)
            anim.start(self.ids['btn_close'])
            anim.start(self.ids['btn_valid'])
            return True
    def validation(self,selector):
        item_list = self.ids['my_layout'].children
        if len(item_list) > 1:
            field={}
            for i in item_list:
                if i.item[selector] not in field :
                    field[i.item[selector]]=[i]
                else :
                    field[i.item[selector]].append(i)
            if len(field)==1:
                return True
            else :
                return False
        else :
            return None

    def anim_valid(self,valid):
        if valid == None :
            return
        else :
            if valid == True :
                self.valid=True
                color = (0,1,0,0.9)
            else :
                color = (1,0,0,0.9)
                self.valid=False
            Animation(color=color,d=0.3).start(self)

    def close(self):
        item_list = list(self.ids['my_layout'].children)
        if item_list == []and self.parent != None:
            self.parent.exists=False
            self.parent.remove_widget(self)
            return
        color = (0,0,1,0.9)
        anim = Animation(color=color,d=0.3)
        anim.start(self)
        for i in item_list:
            temp = i
            temp.do_scale=True
            temp.do_translation = True
            temp.do_rotation=True
            temp.pos=self.pos
            self.ids['my_layout'].remove_widget(i)
            for wid in self.parent.children :
                if isinstance(wid,FloatLayout):
                    wid.add_widget(temp,0)
                    break
            anim=Animation(pos=(randint(int(0.5*Window.width-300),int(0.5*Window.width+100)),randint(int(0.5*Window.height-300),int(0.5*Window.height+100))),rotation=randint(0,360),d=0.2,scale=0.5)
            anim.start(temp)
            

