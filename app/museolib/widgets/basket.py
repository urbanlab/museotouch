#!/usr/bin/python
'''
Basket : A widget where to drag some objects in order to be sent the url by email, where to retrieve the objects online
'''

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
#from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, \
    BooleanProperty, DictProperty, ListProperty 
from kivy.logger import Logger
from kivy.graphics import Color, Line, Rectangle#, LineWidth
#from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.network.urlrequest import UrlRequest

from os.path import join, split, abspath, splitext#, dirname, exists
from os import listdir 
from json import loads
from random import random
import urllib.request, urllib.error, urllib.parse, urllib.request, urllib.parse, urllib.error

from kivy.uix.gridlayout import GridLayout

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
    #send by email the url of the basket content in html format
    email_send = BooleanProperty( False )
    #send item detailed to url_send_url when an item is added to the basket (get method)
    url_send_detailed_item = BooleanProperty( False )
    #send to url_send_url the url that contains the basket content in json (get method) 
    url_send = BooleanProperty( False ) 
    url_send_url = StringProperty( '' )
    objects = ListProperty( [] )
    objects_detailed = DictProperty( {} )
    app = ObjectProperty(None)
    url = StringProperty( '' ) 
    api_url = StringProperty( 'api/index.php' )
    retrieve_basket_url = StringProperty( 'cart.php' ) 
    api_url_commands = {'new_basket' : '?act=cart', 'add_object': ['?act=acart&item=','&cart='], 'delete_object':['?act=dcart&item=','&cart='], 'retrieve_basket_online': ['?id=','&code='], 'send_basket': ['?act=scart&id=','&mail='], 'retrieve_basket_as_json': ['?act=lcart&id=', '&code='] }
    smtp_server = StringProperty( '' )    
    counter = NumericProperty(0)
    enlarged = BooleanProperty(False)
    email = StringProperty( '' )
    id_basket = StringProperty( '' ) 
    url_code = StringProperty( '' ) 

    def __init__(self, **kwargs):
        super(Basket,self).__init__(**kwargs)
        self.opener = urllib.request.build_opener()
        #counter label
        self.text = '       '+str(self.counter)+'\n  '
        #link action on press
#        self.bind(on_press = self.validate_basket)
        self.url = self.app.config.get('museotouch', 'url')
        self.url_send_url = self.app.config.get('museotouch', 'url_send_url')
        self.email_send = ( self.app.config.get('museotouch', 'email_send') == 'True')
        self.url_send_detailed_item = ( self.app.config.get('museotouch', 'url_send_detailed_item') == 'True')
        self.url_send = ( self.app.config.get('museotouch', 'url_send') == 'True')
    
        # Add a layout to display added items
        self.itemsLayout = GridLayout(cols=4, rows = 6, row_default_height=100, col_default_width = 100, spacing = 20, size_hint=(None,None))
    
    def update_counter_label(self):
        self.text = '      '+str(self.counter)+'\n    '

    def reset(self):
        #self.layout.clear_widgets()
        self.objects = []
        self.objects_detailed = {}
        self.counter = 0
        #clear text input
        self.update_counter_label()

    def already_in(self, id):
        if id in self.objects :
            return True
        else : 
            return False 

    def add_item(self,id, item, imgItem = None):
        if not self.active : return
        self.counter +=1
        self.objects.append(id)
        self.objects_detailed[str(id)] = item
        self.update_counter_label()
        self.url_send_item(id, item)
        print(('basket : add item '+str(id), imgItem.source))
        # Add image from imgItem.source in self.itemsLayout + item.title
        img = Image(source = imgItem.source, size = (100,100))
        self.itemsLayout.add_widget(img)
        

    def get_url(self,url):
        page = self.opener.open(url)
        return page.read()

    def enlarge(self):
        if self.enlarged : return 
        self.enlarged = True 
        #bring to front
        parent = self.parent
        parent.remove_widget(self)
        parent.add_widget(self)
        #open/enlarge basket
        anim = Animation(size = (self.width * 2, self.height * 2), duration = .25, t='out_quad' )
        anim.start(self)

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
        if not (self.active and len(self.objects)>0) : 
            return
        if self.enlarged : return
        #each process is in a specific thread in order to not block the app while waiting for an http answer
        #start with that first process
        self.api_create_basket()

    def api_create_basket(self):
        #send to api
        url = self.url+self.api_url
        #create a new basket into the backend, get its id in return
        urla = url + self.api_url_commands['new_basket']
        answera = UrlRequest(urla, self.api_create_basket2, self.api_create_basket_error)
        
    def api_create_basket2(self, req, answera):
        self.id_basket = id_basket = answera['id']
        self.url_code = answera['code_url']#url param to retrieve the basket online

        #next step
        self.api_add_objects(self.objects, id_basket)

    def api_create_basket_error(self, req):
        print('[ERROR  ] Basket : Backend URL is unreachable: check either url configuration or connectivity')

    def api_add_objects(self, objects, id_basket):
        #add objects to the basket into the backend
        idb =''
        for i in objects :
                #add object to the basket
                if idb == '' : idb = idb + str(i)
                else : idb = idb + ',' + str(i)
        suffix = self.api_url_commands['add_object']
        url = self.url+self.api_url 
        urlb = url + suffix[0] + idb + suffix[1] + id_basket
        #send to api
        answerb = UrlRequest(urlb, self.api_add_objects2, self.api_add_objects_error)
        
    def api_add_objects2(self, req, answerb):
        id_basket = self.id_basket
        #next stepS in parallel
        self.api_url_send(id_basket,self.url_code)
        self.api_email_send(id_basket)

    def api_add_objects_error(self, req):
        pass

    def api_email_send(self,id_basket):
        #ask the backend to send the basket by email
        if self.email_send == True:
                if self.enlarged : return
                self.enlarge()
                self.api_email_send2(id_basket)

    def api_email_send2(self, id_basket):
        font_size = 12
        self.ti = ti = TextInput( text = 'Entrez votre email',size_hint =(None,None),size = (315,45), font_size = font_size, pos_hint = {'top':1,'right':1} )
        self.parent.add_widget(ti)
        win = self.get_parent_window()     
        #win.request_keyboard(callback = self.keyboard_callback, target = ti)
        self.val_button = val_button = Button( text = 'ok', size_hint =(None,None),size = (60,47), font_size = font_size, pos_hint = {'top':1,'right':1} )
        self.val_button.bind(on_press = self.validate_keyboard_input)
        self.parent.add_widget(val_button)
        self.cancel_button = cancel_button = Button( text = 'annul', font_size = font_size, size_hint =(None,None),size = (60,45), pos_hint = {'top':0.875,'right':1} )
        self.cancel_button.bind(on_press = self.cancel_keyboard_input)
        self.parent.add_widget(cancel_button)
        self.delete_button = delete_button = Button( text = 'suppr', font_size = font_size, size_hint =(None,None),size = (60,45), pos_hint = {'top':0.935,'right':1} )
        self.delete_button.bind(on_press = self.delete_basket)
        self.parent.add_widget(delete_button)
        #self.id_basket = id_basket

    def validate_keyboard_input(self,a) :
        email = self.ti.text
        if not self.email_integrity_ok(email): 
            self.ti.text = 'Email errone'
            return
        self.email = email
        #reduce size
        self.reduce_size()
        #continue email_send
        self.api_email_send3()

    def reduce_size(self):
        if not self.enlarged : return
        parent = self.parent
        parent.remove_widget(self.ti) 
        parent.remove_widget(self.val_button)
        parent.remove_widget(self.cancel_button)
        parent.remove_widget(self.delete_button)
        self.get_parent_window().release_keyboard()
        anim = Animation(size = (self.width / 2, self.height / 2), duration = .25, t='out_quad' )
        anim.start(self)
        self.enlarged = False

    def cancel_keyboard_input(self,a) :
        self.reduce_size()

    def delete_basket(self,a) :
        self.reduce_size()
        self.reset()

    def api_delete_basket(self):
        return
        id_basket = self.id_basket
        suffix = self.api_url_commands['delete_basket']
        url = self.url+self.api_url
        urlc2 = url + suffix[0] + id_basket + suffix[1] + email_add
        answerc = UrlRequest(urlc2)
        print(('basket : basket number '+ id_basket+' deleted from backend'))

    def api_email_send3(self):
        email_add = self.email 
        id_basket = self.id_basket                

        suffix = self.api_url_commands['send_basket']
        url = self.url+self.api_url
        urlc = url + suffix[0] + id_basket + suffix[1] + email_add 
        #send to api
        answerc = UrlRequest(urlc)
        print(('basket : email sent to '+ email_add))
        self.reset()
        print('basket : reset')

    def url_send_item(self,id_item, item):
        #send the detailed content of the item to the specidied url
        if self.url_send_detailed_item == True:
            item = self.objects_detailed[str(id_item)]
            #build url suffix
            item_urlencoded = {}
            for key,detail in item.items():
                key = key.encode("utf-8")
                if key not in ['keywords','data'] :
                    detail = detail.encode("utf-8")
                    item_urlencoded[key] = detail
            item_urlencoded = urllib.parse.urlencode(item_urlencoded)
            urle = self.url_send_url + '?%s' % item_urlencoded
            print(('basket : added item '+ urle))
            #send
            answere = UrlRequest(urle, self.url_send_item2, self.url_send_item_error)
            
    def url_send_item2(self,req, answere):
        pass

    def url_send_item_error(self, req, err):
        print(err)
        print('[ERROR  ] Basket : Url defined as url_send_url in __init__.py file is unreachable: check either url or connectivity')

    def api_url_send(self,id_basket,url_code):
        #ask the backend to send the basket to the specidied url
        if self.url_send == True:
            suffix = self.api_url_commands['retrieve_basket_as_json']
            urld = suffix[0] + str(id_basket) + suffix[1] + str(url_code)
            urle = self.url_send_url + '?json='+self.url+self.api_url+urld
            print(('basket : json '+ urle))
            answere = UrlRequest(urle, self.url_send_item2, self.url_send_item_error)
            
            if not self.email_send :
                self.reset()
   

class TestApp(App):

    def build(self):
        self.g = Basket(app=self)
        return self.g 

if __name__ in ('__main__'):
    TestApp().run()
