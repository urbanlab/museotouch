from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter
from kivy.animation import Animation
from kivy.properties import ListProperty,BooleanProperty,ObjectProperty
from kivy.core.window import Window
from random import randint

class Valid(Scatter):
    color = ListProperty([0,0,1,0.9])
    valid=BooleanProperty()
    last_valid=ListProperty([])
    def __init__(self,**kwargs):
        super(Valid,self).__init__(**kwargs)
        self.children_pos={"2":{'pos':[2,2],'available':True},"3":{'pos':[self.width/2,2],'available':True},\
        "0":{'pos':[2,self.width/2],'available':True},"1":{'pos':[self.width/2,self.width/2],'available':True}}
        self.app = App.get_running_app()
    def on_touch_down(self,touch):
    	super(Valid,self).on_touch_down(touch)
    	if self.collide_point(*touch.pos):
            if touch.is_triple_tap :
                for child in self.ids['my_layout'].children:
                    if child.collide_point(*self.to_widget(*touch.pos)):
                        self.remove_item(child)
                        self.children_pos[self.touched_item(self.to_widget(*touch.pos))]['available']=True
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
    def validation(self,selector,use_keywords=False):
        item_list = self.ids['my_layout'].children
        if len(item_list) > 1:
            field={}
            keys={}
            for i in item_list:
                if i.item['fields'][selector]!= u'':
                    if i.item['fields'][selector] not in field :
                        field[i.item['fields'][selector]]=[i]
                    else :
                        field[i.item['fields'][selector]].append(i)
                if use_keywords==True:
                    if str(i.item["keywords"][0]) not in keys :
                        keys[str(i.item["keywords"][0])]="exists"
                else:
                    keys={'void':True}
            if len(field)==1 and len(keys)==1:
                self.last_valid.append(field.keys()[0])
                self.last_valid.sort()
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
            self.remove_item(i)
        for pos in self.children_pos:
            self.children_pos[pos]['available']=True

    def remove_item(self,i):
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
        try :
            self.app.db.items.append(i.item)
            self.app.valid_list.remove(i.item.id)
        except:
            pass

    def touched_item(self,pos):
        x,y=int(pos[0]),int(pos[1])
        if x in range (0,int(self.width/2)):
            if y in range (0,int(self.height/2)):
                return '2'
            if y in range (int(self.height/2),int(self.height)):
                return '0'
        if x in range (int(self.width/2),int(self.width)):
            if y in range (0,int(self.height/2)):
                return '3'
            if y in range (int(self.height/2),int(self.height)):
                return '1'

            

