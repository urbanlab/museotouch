#!/usr/bin/python
'''
Basket : A widget where to drag some objects in order to be sent the url by email, where to retrieve the objects online
'''

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.animation import Animation

import urllib2#, urllib
 

#from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, \
    BooleanProperty, DictProperty, ListProperty 
from kivy.logger import Logger
from kivy.graphics import Color, Line, Rectangle#, LineWidth
#from kivy.clock import Clock
from kivy.core.image import Image

from os.path import join, split, abspath, splitext#, dirname, exists
from os import listdir 
from json import loads
from random import random


class EmailForm(Widget):
    app = ObjectProperty(None)
    email = StringProperty('')

    def __init__(self, **kwargs):
        super(EmailForm,self).__init__(**kwargs)
        
        self.ti = ti = TextInput( text = 'Entrez votre email')#,size_hint =(None,None),size = (215,30), pos_hint =(None,None), pos = (0,50) )
        self.add_widget(ti)
        self.val_button = val_button = Button( text = 'ok')#, size_hint =(None,None),size = (40,40), pos_hint =(None,None), pos = (185,0) )
        self.val_button.bind(on_press = self.app.basket.validate_keyboard_input)
        self.add_widget(val_button)
        self.label = label = Label(text = 'Entrez votre email')#, size_hint =(None,None), size = (180,30), pos_hint =(None,None), pos = (0,0) )
        self.add_widget(label)


class Basket(Button):
    active = BooleanProperty( False )
    email_send = BooleanProperty( False )
    url_send = BooleanProperty( False )
    url_send_url = StringProperty( '' )
    objects = ListProperty( [] )
    app = ObjectProperty(None)
    url = StringProperty( 'http://museotouch.erasme.org/prive/' )
    api_url = StringProperty( 'api/index.php' )
    retrieve_basket_url = StringProperty( 'cart.php' ) 
    api_url_commands = {'new_basket' : '?act=cart', 'add_object': ['?act=acart&item=','&cart='], 'delete_object':['?act=dcart&item=','&cart='], 'retrieve_basket_online': ['?id=','&code='], 'send_basket': ['?act=scart&id=','&mail='] }
    smtp_server = StringProperty( '' )    
    counter = NumericProperty(0)
    enlarged = BooleanProperty(False)
    email = StringProperty( '' )  

    def __init__(self, **kwargs):
        super(Basket,self).__init__(**kwargs)
        self.opener = urllib2.build_opener()
        #counter label
        self.text = '       '+str(self.counter)+'\n  '
        #link action on press
        self.bind(on_press = self.validate_basket)
        
    def update_counter_label(self):
        self.text = '      '+str(self.counter)+'\n    '

    def reset(self):
        #self.layout.clear_widgets()
        self.objects = []
        self.counter = 0
        #clear text input
        self.update_counter_label()

    def already_in(self, id):
        if id in self.objects :
            return True
        else : 
            return False 

    def add_item(self,id):
        if not self.active : return
        self.counter +=1
        self.objects.append(id)
        self.update_counter_label()
        print 'basket : add item '+str(id)

    def get_url(self,url):
        page = self.opener.open(url)
        return page.read()

    def enlarge(self):
        self.enlarged = True 
        #bring to front
        parent = self.parent
        parent.remove_widget(self)
        parent.add_widget(self)
        #open/enlarge basket
        anim = Animation(size = (self.width * 2, self.height * 2), duration = .25, t='out_quad' )
        anim.start(self)

    def get_email(self):
        self.ti = ti = TextInput( text = 'Entrez votre email',size_hint =(None,None),size = (215,30), pos_hint = {'top':1,'right':1} )
        self.parent.add_widget(ti)
        win = self.get_parent_window()     
        #win.request_keyboard(callback = self.keyboard_callback, target = ti)
        self.val_button = val_button = Button( text = 'ok', size_hint =(None,None),size = (40,40), pos_hint = {'top':1,'right':1} )
        self.val_button.bind(on_press = self.validate_keyboard_input)
        self.parent.add_widget(val_button)

    def validate_keyboard_input(self,a) :
        email = self.ti.text
        if not self.email_integrity_ok(email): 
            self.ti.text = 'Email errone'
            return
        self.email = email
        parent = self.parent
        parent.remove_widget(self.ti) 
        parent.remove_widget(self.val_button)
        self.get_parent_window().release_keyboard()
        #reduce size
        anim = Animation(size = (self.width / 2, self.height / 2), duration = .25, t='out_quad' )
        anim.start(self)
        self.enlarged = False

    def email_integrity_ok(self,email):
        #control email integrity
        a,b,c = email.partition('@')  
        if email == a : return False # '@' is missing
        elif (len(a) == 0 or len(c) == 0): return False # no char before or after '@'
        else : 
            d,e,f = c.partition('.')
            if d == c : return False # '.' is missing
            elif (len(d) <= 1 or len(f) <= 1): return False # no char before or after '.'
        return True  
               
    def validate_basket(self,a):
        objects = self.objects
        if not (self.active and len(objects)>0) : 
            return

        if self.enlarged : return
        if self.email_send :
            self.enlarge()
            self.get_email()

        #in a specific thread in order to not block the app while waiting for an http answer?
        id_basket,url_code = self.api_create_basket()
        self.api_add_objects(objects, id_basket)
        self.api_email_send(id_basket)
        self.api_url_send(id_basket,url_code)
        #reset basket
        self.reset()

    def api_create_basket(self):
        #send to api
        url = self.url+self.api_url
        #create a new basket into the backend, get its id in return
        urla = url + self.api_url_commands['new_basket']
        answera = self.get_url(urla)
        try :
            answera = loads(answera)#decode json
        except TypeError :
            print '[ERROR  ] Basket : Backend URL is unreachable: check either url configuration or connectivity' 
            return
        #print answera
        id_basket = answera['id']
        url_code = answera['code_url']#url param to retrieve the basket online
        
        return (id_basket,url_code)

    def api_add_objects(self, objects, id_basket):
            #add objects to the basket into the backend
            idb =''
            for i in objects :
                #add object to the basket
                if idb == '' : idb = idb + str(i)
                else : idb = idb + ',' + str(i)
            suffix = self.api_url_commands['add_object'] 
            urlb = self.url + suffix[0] + idb + suffix[1] + id_basket
            #send to api
            answerb = self.get_url(urlb)
            #answerb = wget(urlb)
            if not answerb == "OK" : 
                #print log
                pass

    def api_email_send(self,id_basket):
        #ask the backend to send the basket by email
        if self.email_send :
                email_add = self.email
                
                suffix = self.api_url_commands['send_basket']
                urlc = self.url + suffix[0] + id_basket + suffix[1] + email_add 
                #send to api
                answerc = self.get_url(urlc)
                print 'basket : email sent to '+ email_add

    def api_url_send(self,id_basket,url_code):
        #ask the backend to send the basket to the specidied url
        if self.url_send :
                suffix = self.api_url_commands['retrieve_basket_online']
                urld = self.url + self.retrieve_basket_url + suffix[0] + id_basket + suffix[1] + url_code
                urle = self.url_send_url + urld
                try :
                    answere = self.get_url(urle)
                    print 'basket : url '+ urle
                except :
                    print '[ERROR  ] Basket : Url defined as url_send_url in __init__.py file is unreachable: check either url or connectivity' 
                    return
    
   

class TestApp(App):

    def build(self):
        self.g = Basket(app=self)
        return self.g 

if __name__ in ('__android__', '__main__'):
    TestApp().run()
