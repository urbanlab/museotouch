#!/usr/bin/env python
# -*- coding: utf-8 -*-
import kivy
#kivy.require('1.0.8-dev')
kivy.require('1.1.1')

from kivy.config import Config
Config.set('kivy', 'log_level', 'debug')
Config.set('graphics','fullscreen','auto')
from random import random, randint
from os.path import join, dirname, exists, basename,isfile
from os import makedirs, remove, walk, listdir
from zipfile import ZipFile
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.resources import resource_add_path, resource_remove_path
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.utils import format_bytes_to_human, platform
from kivy.core.window import Window
from kivy.properties import BooleanProperty, NumericProperty
from kivy.cache import Cache

from kivy.loader import Loader

import museolib
from museolib.utils import format_date, no_url
from museolib.widgets.imageitem import ImageItem
from museolib.widgets.scrollviewitem import ScrollViewItem
from museolib.widgets.exposelector import ExpoSelector
from museolib.backend.backendjson import BackendJSON
from museolib.backend.backendweb import BackendWeb
from museolib.widgets.quitbutton import QuitButton
from museolib.widgets.menu import Menu
from json import dump, dumps
from imp import load_source
from math import ceil
from functools import partial

from pdb import set_trace as rrr
import time
import unicodedata

# from kivy.support import install_twisted_reactor
# install_twisted_reactor()

# from twisted.internet import reactor
# from twisted.internet import protocol
# from twisted.protocols.basic import NetstringReceiver
# from socket import gethostname

# class EchoProtocol(NetstringReceiver):
#     def dataReceived(self, data):
#         response = self.factory.app.handle_message(data)
#         if response:
#             if self.factory.app.content_type == "expos":
#                 for expo in response:
#                     self.sendString(self.factory.app.content_type+"|"+dumps(expo))
#             if self.factory.app.content_type in ["get_config","get_widgets"]:
#                 self.sendString(self.factory.app.content_type+"|"+dumps(response))
#             if self.factory.app.content_type in ["name"]:
#                 self.sendString(self.factory.app.content_type+"|"+response)


# class EchoFactory(protocol.Factory):
#     protocol = EchoProtocol

#     def __init__(self, app):
#         self.app = app

class MuseotouchApp(App):

    # def handle_message(self, msg):
    #     if msg == 'get_expos' :
    #         print "Incoming connexion"
    #         msg = self.selector.get_offline_expos()
    #         self.content_type='expos'
    #         return msg
    #     if msg == "get_name":
    #         self.content_type='name'
    #         return gethostname()
    #     if msg in ["more_info","physics"]:
    #         boolean = self.config.getboolean('museotouch',msg)
    #         if boolean == 0 :
    #             self.config.set('museotouch',msg,1)
    #         else:
    #             self.config.set('museotouch',msg,0)       
    #     if msg == 'get_config':
    #         config={}
    #         for boolean in ["more_info","physics"]:
    #             config[boolean] = self.config.getboolean('museotouch',boolean)
    #         self.content_type=msg
    #         return config
    #     if msg.isdigit()==True:
    #         self.reset(go_to_menu=False)
    #         self.show_expo(msg)
    #     if msg == "get_widgets":
    #         self.content_type=msg
    #         return self.widget_list()
    #     if msg in ["circularslider","sizeslider","imagemap","keywords","dropdown"]:
    #         self.toggle_widget(self.widgets[msg])
    #     return None

    def delayed_work(self, func, items, delay=0):
        if not items:
            return
        def _delayed_work(*l):
            item = items.pop()
            self.items_to_add = len(items)
            if func(item) is False or not len(items):
                return False
            Clock.schedule_once(_delayed_work, delay)
        Clock.schedule_once(_delayed_work, delay)
    @property
    def mode(self):
        if platform() in ('android', 'ios'):
            return 'mobile'
        return 'table'
    
    def do_reset_item_position(self, *largs):
        self.images_pos = {}
        root = self.root_images     
        for i, item in enumerate(reversed(root.children)):
            x = randint(root.x + 200, root.right - 500)
            y = randint(root.y + 300, root.top - 200)
            rotation = randint(0, 360)
            item.flip_front = True
            (Animation(d=0.1 + i / 30.) + Animation(scale=item.scale_min, center=(x, y),
                    rotation=rotation, t='out_quad', d=.25)).start(item)

    def do_ordering_origin(self, *largs):
        children = self.root_images.children
        origs = list(set([x.item.origin_key for x in children]))
        def index_for_child(groups, child):
            return groups.index(child.item.origin_key)
        self._display_ordering_as_group(children, origs, index_for_child)

    def do_ordering_keywords(self, *largs):
        # ordering only on the current selected group
        if not self.keywords:
            return
        # get current active group
        children = self.root_images.children
        active = [x for x in self.keywords.children if not x.collapse]
        groups = [uid for g, uid in self.keywords.selected_keywords if g.accitem
                in active]
        if not groups:
            return
        def index_for_child(groups, child):
            for index, key in enumerate(groups):
                if key in child.item.keywords:
                    return index
            return -1
        self._display_ordering_as_group(children, groups, index_for_child)

    def do_ordering_size(self, *largs):
        children = self.root_images.children[:]
        children.sort(key=lambda x: x.item.taille)
        self._display_ordering_as_table(children)

    def do_ordering_datation(self, *largs):
        children = self.root_images.children[:]
        children.sort(key=lambda x: x.item.date)
        self._display_ordering_as_table(children)

    def _display_ordering_as_group(self, children, groups, index_for_child):
        # size of image
        imgs = int(512 * .7)

        # size of area for work
        width = self.root_images.width - 800
        height = self.root_images.height - 400

        # images per size
        mx = max(1, width // imgs)
        my = max(1, height // imgs)

        # max
        mmx = min(len(groups), mx)
        mmy = int(min(ceil(len(groups) / float(mx)), my))

        x = self.root_images.center_x - (mmx * imgs) / 2
        y = self.root_images.center_y - (mmy * imgs) / 2 + imgs
        m = imgs

        # direction
        dx = 1
        dy = -1

        for i, item in enumerate(reversed(children)):
            mi = index_for_child(groups, item)
            ix = x + (mi % mx) * m * dx
            iy = y + (mi // mx) * m * dy
            '''
            ix = x + groups.index(keyfn(item)) * m
            iy = y
            '''
            item.flip_front=True
            (Animation(d=0.05 + i / 30.) + Animation(scale=item.scale_min, pos=(ix, iy),
                    rotation=0 + random() * 20 - 10, t='out_quad',
                    d=.20)).start(item)

    def _display_ordering_as_table(self, children):
        # remove and readd all children
        self.root_images.clear_widgets()
        for item in reversed(children):
            self.root_images.add_widget(item)

        cx, cy = self.root_images.center

        # size of image
        imgs = int(512 * .5)

        # size of area for work
        width = self.root_images.width - 600
        height = self.root_images.height - 400

        # images per size
        mx = 1 + width // imgs
        my = 1 + height // imgs

        # initial position
        x = self.root_images.center_x - (mx * imgs) / 2
        y = self.root_images.center_y + (my * imgs) / 2 - imgs

        # XXX make it configurable, this is to prevent overlap with map widget
        y += 80

        # direction
        dx = 1
        dy = -1

        for i, item in enumerate(children):
            mi = i % (mx * my)
            ix = x + (mi % mx) * imgs * dx
            iy = y + (mi // mx) * imgs * dy
            item.flip_front=True
            (Animation(d=0.1 + i / 30.) + Animation(scale=item.scale_min, pos=(ix, iy),
                    rotation=0., t='out_quad',
                    d=.25)).start(item)

    def show_object(self, defs):
        #rrr()
        if self.root.type_expo == 'normal':
            source = defs['source']
            if source not in self.images_displayed:
                return
            current_images = [x.source for x in self.root_images.children]
            if source in current_images:
                return

            images_pos = self.images_pos
            if source in images_pos:
                p = images_pos[source]
                defs.pop('center', None)
                defs['center'] = p['center']
                defs['rotation'] = p['rotation']
    
            if self.root.square_items == True:
                defs['square'] = True

            center = defs.pop('center')
            rotation = defs.pop('rotation')
            item = ImageItem(**defs)
            self.root_images.add_widget(item, -1)
            item.rotation = rotation
            item.center = center
            images_pos[source] = {
                'center': item.center,
                'rotation': item.rotation}
    def toggle_widget(self,widget):
        if widget.disabled == True:
            widget.disabled= False
            Animation(opacity=1,d=0.5).start(widget)
        else:
            widget.disabled=True
            Animation(opacity=0,d=0.5).start(widget)
    def show_objects(self, objects):
        root = self.root
        if isinstance(self.root_images.x, (int, long)):
            if root.type_expo == 'normal':
                images = [x.source for x in self.root_images.children]

                images_to_add = []
                images_displayed = []
                for item in objects:
                    # is the current filename is already showed ?
                    filename = item.filename
                    if filename in images:
                        images.remove(filename)
                        continue
                    try:
                        x = randint(self.root_images.x + 200, self.root_images.right - 200)
                        y = randint(root.y + 300, root.top - 100)
                    except:
                        x = randint(Window.width*0.2,Window.width*0.8)
                        y = randint(Window.height*0.2,Window.height*0.8)
                    angle = randint(0, 360)

                    image = dict(source=filename, rotation=angle + 90,
                            center=(x, y), item=item, app=self)
                    images_to_add.append(image)
                    images_displayed.append(filename)

                self.images_displayed = images_displayed
                self.delayed_work(self.show_object, images_to_add)

                # remove all the previous images
                for child in self.root_images.children[:]:
                    for filename in images:
                        if filename == child.source:
                            self.images_pos[filename] = {
                                'center': child.center,
                                'rotation': child.rotation }
                            self.root_images.remove_widget(child)
            elif root.type_expo == 'ns':
                #rrr()
                images = [x.source for x in root.scroller.layout.children]

                images_to_add = []
                images_displayed = []
                for item in objects:
                    # is the current filename already showed ?
                    filename = item.filename
                    if filename in images:
                        images.remove(filename)
                        continue

                    image = dict(source=filename, item=item, app=self)
                    images_to_add.append(image)
                    images_displayed.append(filename)

                self.images_displayed = images_displayed
                #delayed_work(self.show_object, images_to_add)

                # remove all the previous images
                for child in root.scroller.layout.children[:]:
                    for filename in images:
                        if filename == child.source:
                            root.scroller.layout.remove_widget(child)
                            if child.imgItem is not None:
                                if hasattr(child.imgItem, 'sound'):
                                    child.imgItem.sound.stop()
                                    child.imgItem.sound.unload()
                                child.imgItem.parent.remove_widget(child.imgItem)

                # show_object is not called because we make the display process here
                winWidth = Window.width
                totalHeight = Window.height * 0.8
                try:
                    itemWidth = winWidth / len(objects)
                except ZeroDivisionError:
                    itemWidth = winWidth
                
                if itemWidth < 200:
                    itemWidth = 200

                root.scroller.layout.col_default_width = itemWidth
                root.scroller.layout.bind(minimum_width=root.scroller.layout.setter('width'))
                
                for img in images_to_add:
                    item = ScrollViewItem(source = img['source'], itemWidth = itemWidth, totalHeight = totalHeight, app=self)
                    item.db_item = img['item']
                    root.scroller.layout.add_widget(item)
                root.scroller.updateItemSize()

    def update_objects_from_filter(self, *largs):
        '''Update the objects displayed from filters (date range, origin...)
        '''
        # start from all items
        items = self.db.items
        result = []
        # print self.valid_list
        # avoid bad interactions with validation widget
        for item in items[:] :
            if item.id in self.valid_list :
                items.remove(item)
        # update date range from slider value
        if self.date_slider:
            ma, mb = self.date_slider.value_range
            count = len(items)
            item_min = int(ma * count)
            item_max = max(item_min + 1, int(mb * count))

            # adjust item selection
            items = result = items[item_min:item_max]
            if len(items) == 0:
                self.show_objects(items)
                return
            item1 = items[0]
            item2 = items[-1]

            # set the text inside the slider
            if item1.date and item2.date:
                self.date_slider.text_min = format_date(item1.date)
                self.date_slider.text_max = format_date(item2.date)
        
        # filter on size
        if self.size_slider:
            # reorder item by taille
            items.sort(key=lambda x: x.taille)
            # added another drawing system
            # more precise and reliable 
            # but certainly slower
            try:
                self.taille_max = float(items[-1]['taille'])
                borne_max = self.taille_max*self.size_slider.value_max
                borne_min = self.taille_max*self.size_slider.value_min
                items = [x for x in items if (float(x['taille']) <= borne_max) and (float(x['taille']) >= borne_min)]
            # fallback to the old system
            # in case 'taille' field has been filled up with a non digit string in the backoffice
            except:
                ma, mb = self.size_slider.value_range
                count = len(items)
                item_min = int(ma * count)
                item_max = max(item_min + 1, int(mb * count))
                # adjust item selection
                items = result = items[item_min:item_max]
            if len(items) == 0:
                self.show_objects(items)
                return

        # # filter from size but with dropdown menu
        if self.dropdown:
            if self.dropdown.ids.mainbutton.text.lower() != 'valider un lot' and self.dropdown.ids.mainbutton.text.lower() !='tous les lots':
                items = [x for x in items if x['taille'].lower()==self.dropdown.ids.mainbutton.text.lower()]
            

        # filter from origin
        if self.imagemap:
            origin_ids = self.imagemap.active_ids

            # special case. If we got some keywords, but no origin, don't use
            # it.
            if self.keywords and self.keywords.selected_keywords and not origin_ids:
                pass
            else:
                items = result = [x for x in items if x.origin_key in origin_ids or x.origin_key==""]

        # filter from keywords but with image buttons, only if there is group of keyword with 'filtre' in the group's name
        if self.imageButtons:
            keywords_names = self.imageButtons.active_ids
            keywords_ids = []
            groups = self.db.keywords
            items_result = []  
            keywords_all = []

            for group in groups:
                groupname = group['group'].lower()
                if groupname.find('filtre') != -1:
                    keywords_all = group['children']

            def remove_accents(input_str):
                nkfd_form = unicodedata.normalize('NFKD', input_str)
                return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

            if (keywords_all):
                for name in keywords_names:
                    for keyword in keywords_all:
                        # Preprocess keyname in order to avoid accents and convert from unicode to string for comparison
                        keyname = remove_accents(keyword['name'])
                        keyname = keyname.encode('utf8')
                        if name == keyname:
                            keywords_ids.append(keyword['id'])

                for item in items:
                    for key in keywords_ids:
                        if key in item.keywords:
                            items_result.append(item)

                if self.imageButtons.show_objects_when_empty == True:
                    if not keywords_names and not items_result: #si aucune image activee et aucun resultat
                      items_result = items # on affiche tout

                items = result = items_result

            # for group in groups:
            #     if group.title.find('filtre'):
            #         print('filtre image trouvé')

            #         if self.keywords and self.keywords.selected_keywords and not keywords_ids:
            #             pass
            #         else:
            #             #items = [x for x in items if x.origin_ex in keywords_ids]
            #           items_result = []
            #           items = self.db.items       
            #           for item in items:
            #               #print item.keywords
            #               for key in keywords_ids:
            #               if key in item.keywords:
            #                   if not item in items_result:
            #                   items_result.append(item)                           
            #           items = items_result        
        #print "image buttons filter"       
        # items

        # filter with keywords
        # AND between group
        # OR inside group
        if self.keywords and self.keywords.selected_keywords:
            selected_keywords = self.keywords.selected_keywords
            
            groups = list(set([x[0] for x in selected_keywords]))
            groups_result = {}
            items_result = []

            # check every group
            for group in groups:
                # check keywords for current group
                keywords = [x[1] for x in selected_keywords if x[0] == group]
                result = []
                # check every items if we got at least one keyword of that group
                for item in items:
                    #print 'item : ', item.origin_ex
                    is_in = True
                    if self.keywords.or_and == True :
                        # OR
                        for key in keywords:
                            # found one group keyword in the 
                            if key in item.keywords:
                                result.append(item)
                                if not item in items_result:
                                    items_result.append(item)
                                break
                    else:
                        # AND
                        for key in keywords:
                            if key not in item.keywords:
                                is_in = False
                        if is_in == True:
                            result.append(item)
                            if not item in items_result:
                                items_result.append(item)

                # add the result to the group result
                groups_result[group] = result




            # on all the avialable item, ensure they are all in the selected
            # group
            if not hasattr(self.keywords, 'multiple_groups'):
                # if multiple_groups:
                for item in items_result[:]:
                    valid = all([item in x for x in groups_result.itervalues()])
                    if not valid:
                        items_result.remove(item)

            # now set the result as the new set of items
            items = result = items_result



        if self.calendar:
            calfield = 'cal'
            if len(items) > 0:
                if 'calannee' in items[0]:
                    calfield = 'calannee'
                items = result = [x for x in items if self.calendar.accepts(x[calfield])]


        # show only the first 10 objects
        if not self.should_display_images_by_default:
            items = result


        self.show_objects(items)


    def build_config(self, config):
        config.setdefaults('museotouch', {
            'url': 'http://www.crdp-lyon.fr/educatouch/',
            'url_api': 'http://www.crdp-lyon.fr/educatouch/api/',
            'url_data': 'http://www.crdp-lyon.fr/educatouch/uploads/',
            'expo': '0',
            'demo':'1',
            'more_info':'1',
            'splashscreen':'0',
            'splashscreen_interval':'60',
            'fast':'1',
            'validation':'1',
            'physics':'1',
            'email_send' : 'True',
            'url_send_url' : 'http://urltest.lapin.be',
            'url_send' : 'True',
            'url_send_detailed_item' : 'True'
        })
        if platform() not in ('ios', 'android'):
            config.setdefaults('rfid', {
                'uid_restart': '',
                'uid_mainscreen': '',
                'uid_settings': '',
            })

    def build_settings(self, settings):
        jsondata = '''[
            {
                "type": "numeric",
                "title": "Exposition",
                "desc": "Identifiant de l'exposition par defaut",
                "section": "museotouch",
                "key": "expo"
            }, {
                "type": "string",
                "title": "URL API",
                "desc": "Url vers l'API du backend web",
                "section": "museotouch",
                "key": "url_api"
            }, {
                "type": "string",
                "title": "URL Data",
                "desc": "Url vers les datas (scenarios et objets)",
                "section": "museotouch",
                "key": "url_data"
            }, {
                "type": "bool",
                "title": "Physics",
                "desc": "Activer ou désactiver l'inertie des fiches",
                "section": "museotouch",
                "key": "physics"
            }, {
                "type": "bool",
                "title": "Connexion au back-office",
                "desc": "Activer ou désactiver la synchronisation avec le backoffice",
                "section": "museotouch",
                "key": "fast"
            }, {
                "type": "bool",
                "title": "Widget validation",
                "desc": "Activer ou désactiver le widget de validation (si disponible pour ce scénario)",
                "section": "museotouch",
                "key": "validation"
            }, {
                "type": "bool",
                "title": "Activer ou désactiver le retournement des fiches",
                "desc": "Permet d'empêcher ou d'autoriser les utilisateurs à retourner les fiches (flèche en haut à droite de chaque fiche)",
                "section": "museotouch",
                "key": "more_info"
            }, {
                "type": "options",
                "title": "Ecran de veille",
                "desc": "Permet de régler le temps (en secondes) de déclenchement de l'écran de veille (0 pour désactiver)",
                "section": "museotouch",
                "options":["0","15","30","60","90","120"],
                "key": "splashscreen"
            }, {
                "type": "options",
                "title": "Intervalle de l'écran de veille",
                "desc": "Permet de régler l'intervalle de temps (en secondes) entre les images de l'écran de veille (0 pour désactiver)",
                "section": "museotouch",
                "options":["0","5","15","30","60","90","120"],
                "key": "splashscreen_interval"
            }]'''
        settings.add_json_panel('Museotouch', self.config, data=jsondata)
        if platform() not in ('ios', 'android'):
            jsondata = '''[
                {
                    "type": "string",
                    "title": "Redémarrage",
                    "desc": "RFID pour le redémarrage de l'application",
                    "section": "rfid",
                    "key": "uid_restart"
                }, {
                    "type": "string",
                    "title": "Ecran principal",
                    "desc": "Retour vers l'écran principal",
                    "section": "rfid",
                    "key": "uid_mainscreen"
                }, {
                    "type": "string",
                    "title": "Configuration",
                    "desc": "Affichage de l'écran de configuration",
                    "section": "rfid",
                    "key": "uid_settings"
                }]'''
            settings.add_json_panel('Rfid', self.config, data=jsondata)

    def build(self):

        config = self.config

        self.init_widgets()

        # set the image type from mode
        # TODO : get values from museotouch.ini
        # self.imgtype = 'dds'
        # self.imgdir = 'dds'
        self.imgtype = 'jpg'
        self.imgdir = 'raw'

        # display images when nothing is selected ?
        self.should_display_images_by_default = BooleanProperty(True)

        # list of removed objects
        self.images_displayed = []
        self.images_pos = {}

        self.items_to_add = NumericProperty(0)  #Number of items waiting for display

        # add data directory as a resource path
        self.data_dir = data_dir = join(dirname(museolib.__file__), 'data')
        resource_add_path(data_dir)

        # list of imageitems currently inside validation widgets
        # avoids those items to be impacted by sorting function
        self.valid_list = []

        # timer for splashscreen
        self.timer=False

        # Boolean to check if a media is already playing
        self.media_playing = False

        self.offline=BooleanProperty(False)
        # add kv file
        Builder.load_file(join(data_dir, 'global.kv'))

        loading_png_fn = join(data_dir, 'loading.gif')

        Loader.loading_image = Image(source=loading_png_fn)

        # create trigger for updating objects
        self.trigger_objects_filtering = Clock.create_trigger(
            self.update_objects_from_filter, 0)
        self.menu = Menu()
        # web backend
        self.disconnected = not self.config.getboolean('museotouch','fast')
        if self.disconnected == False :
            self.backend = BackendWeb(
                    url=config.get('museotouch', 'url_api'),
                    interfaces_url=config.get('museotouch', 'client_api'))
        else :
            self.backend=BackendWeb(
                    url='',
                    data_url='')

        # rfid daemon
        self.rfid_daemon = None
        if platform() not in ('ios', 'android'):
            try:
                from museolib.rfid import RfidDaemon
                self.rfid_daemon = RfidDaemon()
                self.rfid_daemon.bind(on_uid=self.on_rfid_uid)
                self.rfid_daemon.start()
            except Exception:
                Logger.critical('Unable to import RfidDaemon, pynfc missing ?')
                Logger.exception('')

        # if we are on android, always start on selector
        # otherwise, check configuration
        if self.mode == 'table':
            self.build_for_table()
        else:
            self.build_selector()
        # Local server
        # print "STARTING SERVER"
        # server = EchoFactory(self)
        # reactor.listenTCP(8000, server)
        # print "SERVER STARTED"

    def on_stop(self):
        if self.rfid_daemon:
            self.rfid_daemon.stop()
        super(MuseotouchApp, self).on_stop()


    def init_widgets(self):
        #: imagemap widget. If set, it will be used to filter items from
        #: origin_key
        self.imagemap = None

        #: date_slider widget. If set, it will be used to filter items from
        #: a the date range.
        self.date_slider = None

        #: keywords widget. If set, it will be used to show keywords
        self.keywords = None

        #: size slider. If set, it will be used to show all sizes
        self.size_slider = None
        
        #: drop down menu. If set, it will be used to show all sizes
        self.dropdown = None

        #:Image buttons. 
        self.imageButtons = None

        #: Calendar 
        self.calendar = None

    def on_rfid_uid(self, instance, uid):
        Logger.debug('App: Got RFID %r' % uid)
        token = self.config.get
        if uid in token('rfid', 'uid_restart').lower().split(','):
            Logger.info('App: Rfid ask to restart the app !')
            self.stop()
        elif uid in token('rfid', 'uid_mainscreen').lower().split(','):
            Logger.info('App: Rfid ask to return on main screen')
            self.close_settings()
        elif uid in token('rfid', 'uid_settings').lower().split(','):
            Logger.info('App: Rfid ask to open settings')
            self.open_settings()
        else:
            # TODO: check on webserver if some scenario need to be done
            pass

    def build_for_table(self):
        # check which exposition we must use from the configuration
        expo = str(self.config.getint('museotouch', 'expo'))
        if expo is None or int(expo) <= 0:
            # no exposition set in the configuration file.
            # show the selector
            return self.build_selector()        
        self.show_expo(expo)
        return FloatLayout()

    def build_selector(self, *l):        
        client = str(self.config.getint('museotouch', 'client_id'))
        self.selector = ExpoSelector(app=self, client_id=client)
        return self.selector

    def build_app(self,offline=None):
        if '__expo__'+self.expo_id not in sys.modules:
            modexpo = load_source('__expo__'+self.expo_id, join(
                self.expo_data_dir, '__init__.py'))
        else:
            modexpo = sys.modules['__expo__'+self.expo_id]


        # link with the db. later, we need to change it to real one.
        Builder.load_file(join(self.expo_data_dir, 'museotouch.kv'))
        self.db = db = BackendJSON(filename=join(
            self.expo_dir, 'expo.json'))
        Logger.info('Museotouch: loaded %d items' % len(db.items))
        # resolving filename for all item
        items = db.items[:]
        imgtype = self.imgtype
        for item in items[:]:
            if imgtype == 'raw':
                directory, ext = 'raw', 'png'
            if imgtype == 'jpg':
                directory, ext = 'raw', 'jpg'
            else:
                directory, ext = self.imgdir, imgtype
            filename = join(self.expo_img_dir,  directory, '%d.%s' % (item.id, ext))
            # if not exists(filename):
            #     Logger.error('Museolib: Unable to found image %s' % filename)
            #     items.remove(item)
            #     continue
            #rrr()
            filename, ext = self._sync_convert_filename(item['mainMedia'])
            item.filename = self._sync_get_local_filename(filename)
            

        print ">>>>>>>>>>>>>>>>>>>>>>>> n items", len(items)
        db.items = items
        Logger.info('Museotouch: %d items usable' % len(db.items))

        # construct the app.
        self.root = root = modexpo.build(self)
        if self.offline == True :
            self.root.add_widget(Label(text="Pas de connexion au serveur.\nMode offline activé.\nLes fiches ne sont pas mises à jour.",color=(1,0,0,1)))
        try:
            self.root.add_widget(self.menu)
        except:
            pass
        # type_expo introduced for nuits sonores ("ns")
        if not hasattr(root, 'type_expo'):
            root.type_expo = 'normal'

        #resize dds file in items for an item without black margins
        if not hasattr(root, 'square_items'):
            root.square_items = False

        # add root layer for putting image
        self.root_images = FloatLayout()
        root.add_widget(self.root_images)

        # update keywords
        if self.keywords:
            self.keywords.keywords = db.keywords
            self.keywords.bind(selected_keywords=self.trigger_objects_filtering)

        # update size slider
        if self.size_slider:
            self.size_slider.bind(value_range=self.trigger_objects_filtering)

        # update the initial slider values to show date.
        if self.date_slider:
            self.date_slider.bind(value_range=self.trigger_objects_filtering)

        if self.imagemap:
            self.imagemap.bind(active_ids=self.trigger_objects_filtering)
        
        if self.imageButtons:
            self.imageButtons.bind(active_ids=self.trigger_objects_filtering)

        if self.calendar:
            self.calendar.bind(update=self.trigger_objects_filtering)

        if self.dropdown:
            batch_list=[]
            for i in items:
                if i['taille'].capitalize() not in batch_list:
                    batch_list.append(i['taille'].capitalize())
            self.dropdown.populate_drop_down(batch_list)
            self.dropdown.bind(button_text=self.trigger_objects_filtering)
        
        if not hasattr(root, 'hide_items'):
            self.trigger_objects_filtering()


        parent = self.root.parent
        if parent:
            parent.remove_widget(self.root)
        else:
            from kivy.core.window import Window
            parent = Window
        self.root = root
        parent.add_widget(self.root)
        demo = self.config.getboolean('museotouch', 'demo')
        self.update_error_log()
        if demo==True: 
            # button_inst = QuitButton()
            # from kivy.uix.scatter import Scatter
            # scat = Scatter(size=(1200,1200),pos_hint={'right': 1, 'top': 1}, size_hint=(None, None), scale=.05,do_translation=False,do_rotation=False,do_scale=False)
            # scat.add_widget(button_inst)
            # parent.add_widget(scat)
            def restart():
                self.reset(go_to_menu=True)
            # button_inst.do_action = restart
        return root
    def widget_list(self):
        self.widgets = {}
        widgets = []
        if self.root :
            for widget in self.root.children:
                try:
                    widgets.append(widget.name)
                    self.widgets[widget.name]=widget.proxy_ref
                except :
                    for child in widget.children:
                        try :
                            widgets.append(child.name)
                            self.widgets[child.name]=widget.proxy_ref
                        except:
                            pass
            return widgets

    def update_error_log(self):
        # errors = self.backend.get_errors()
        # logpath = join(self.expo_dir,'error.log')
        # logfile = open(logpath,'w')
        # if errors == []:
        #     remove(logpath)
        # else:
        #     Logger.error("Some fields aren't filled properly in the back-office. See %s for more information"%logpath)
        #     for error in errors:
        #         logfile.write('Au moins un champ mal rempli pour la fiche "%s"\n'%(error))
        # logfile.close()
        pass



    def change_expo(self, expo_id):
        self.reset(go_to_menu=False)
        # check if expo is available on the disk
        self.expo_dir = self.get_expo_dir(expo_id)
        self.expo_data_dir = join(self.expo_dir, 'data')
        self.expo_img_dir = join(self.expo_dir, 'images')
        resource_add_path(self.expo_data_dir)
        self.expo_id = expo_id
        
        force_sync = True
        popup=None
        
        if force_sync:
            # create popup
            if popup is None:
                popup = Popup(title='Chargement...', size_hint=(None, None), opacity=0,
                        size=(300, 300), auto_dismiss=False)
                popup.open()

            # synchronize it !
            self.sync_expo(expo_id, popup)

        else:
            self.build_app()

    def show_expo(self, expo_id, popup=None):
        # check if expo is available on the disk
        self.expo_dir = self.get_expo_dir(expo_id)
        self.expo_data_dir = join(self.expo_dir, 'data')
        self.expo_img_dir = join(self.expo_dir, 'images')
        resource_add_path(self.expo_data_dir)
        self.expo_id = expo_id
        # be able to run offline too.
        force_sync = True
        if force_sync:
            # create popup
            if popup is None:
                popup = Popup(title='Chargement...', size_hint=(None, None),
                        size=(300, 300), auto_dismiss=False)
                popup.open()
            # synchronize it !
            self.sync_expo(expo_id, popup)
        else:
            self.build_app()

    #
    # Synchronisation of an exhibition
    # this part is seperated in multiple step:
    # 1. create directory layout for an exhibition if not exists
    # 2. update the objects list of an exhibition
    # 3. fetch missing objects
    #

    def get_expo_dir(self, expo_id=None):
        if self.mode == 'mobile':
            root_expo = '/sdcard/museotouch/expos'
        else:
            root_expo = join(dirname(__file__), 'expos')
        try:
            makedirs(root_expo)
        except OSError, e:            
            print 'Le dossier expos existe déjà ', e
        if expo_id is None:
            return root_expo
        return join(root_expo, expo_id)

    def sync_expo(self, expo_id, popup=None):
        # adjust the popup 
        popup.title = 'Synchronisation en cours...'
        popup.content = Image(source='loader.gif', anim_delay=.1)
        Animation(size=(300, 200), d=.2, t='out_quad').start(popup)
        self._sync_popup = popup

        # prepare popup for synchronisation
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(halign='center'))
        layout.add_widget(Label(halign='center'))
        layout.add_widget(ProgressBar())
        self._sync_popup.content = layout

        self._sync_popup_text(u'Téléchargement de la description')

        # create layout for exhibition
        for directory in (
                self.expo_dir,
                self.expo_data_dir,
                self.expo_img_dir,
                join(self.expo_img_dir, self.imgdir)):
            try:
                makedirs(directory)
            except OSError:
                pass
        # get the initial json
        self.backend.set_expo(expo_id)

        if self.disconnected == True:
            print 'building fast'
            self._sync_popup.dismiss()
            self.build_app(offline=True)
        else:
            # get the initial zipfile
            Logger.info('Museotouch: Synchronization starting')
            self.backend.get_objects(
                    on_success=self._sync_expo_1,
                    on_error=self._sync_error_but_continue,
                    on_progress=self._sync_progress)

    def _sync_popup_text(self, text):
        self._sync_popup.content.children[-1].text = text

    def _sync_expo_1(self, req, result):
        Logger.info('Museotouch: Synchronization part 1')
        # check result files to found a zip files
        
        # self._expo_files = files = [x['fichier'] for x in result['data']]
        # zipfiles = [x for x in files if x.rsplit('.', 1)[-1] == 'zip']
        # if len(zipfiles) != 1:
        #     self.error(u'Aucun fichier de données attaché '
        #             u'à cette exposition (zip not found)')
        #     return

        self._expo_files = result

        zipfile = result['zipContent']
        if (zipfile == ''):
            self.error(u'Aucun fichier de données attaché '
                    u'à cette exposition (zip not found)')
            return
        # write the part of the json corresponding to that expo in the dir
        expojson = join(self.expo_dir, 'expo.json')
        with open(expojson, 'w') as fd:
            dump([result], fd)

        # if we already downloaded the data, we might have a checksum if
        # everything is ok.
        zipchecksum = join(self.expo_dir, 'data.checksum')
        checksum = ''
        if exists(zipchecksum):
            with open(zipchecksum, 'r') as fd:
                checksum = fd.read()

        if checksum == zipfile:
            Logger.info('Museolib: expo data dir already downloaded, continue.')
            # avoid downloading the zip, already got it.
            self._sync_expo_3()
            return


        # download the zip
        print ' &&&& the zip is', zipfile
        self._sync_popup_text(u'Téléchargement des données')
        self.backend.get_file(
            zipfile,
            on_success=self._sync_expo_2,
            on_error=self._sync_error_but_continue,
            on_progress=self._sync_progress)

    def _sync_expo_2(self, req, result):
        Logger.info('Museotouch: Synchronization part 2')
        # write result to data.zip
        zipfilename = join(self.expo_dir, 'data.zip')
        with open(zipfilename, 'wb') as fd:
            fd.write(result)
        pa = join(self.expo_dir, 'data/widgets/')
        for root, dirs, files in walk(pa):
            for name in files:
                remove(join(root, name))

        # uncompress in current directory
        zp = ZipFile(zipfilename)
        zp.extractall(self.expo_data_dir)

        # all ok, write original filename
        zipchecksum = join(self.expo_dir, 'data.checksum')
        with open(zipchecksum, 'w') as fd:
            fd.write(req.url)

        self._sync_expo_3()

    def _sync_expo_3(self):
        Logger.info('Museotouch: Synchronization part 3')
        # try to found at least one image
        # images = [x for x in self._expo_files if \
        #     x.rsplit('.', 1)[-1].lower() in ('png', 'jpg')]

        image = self._expo_files['mainMedia']
        if not image:
            self._sync_expo_5()
            return

        # if we already downloaded the data, we might have a checksum if
        # everything is ok.
        thumbchecksum = join(self.expo_dir, 'thumbnail.checksum')
        checksum = ''
        if exists(thumbchecksum):
            with open(thumbchecksum, 'r') as fd:
                checksum = fd.read()

        if checksum == image:
            Logger.info('Museolib: expo thumbnail already downloaded, continue.')
            # avoid downloading the zip, already got it.
            self._sync_expo_5()
            return

        # download the first one as a thumbnail
        self._sync_popup_text(u'Téléchargement de la miniature')
        self.backend.get_file(
            image,
            on_success=self._sync_expo_4,
            on_error=self._sync_error_but_continue,
            on_progress=self._sync_progress)

    def _sync_expo_4(self, req, result):
        Logger.info('Museotouch: Synchronization part 4')
        ext = req.url.rsplit('.', 1)[-1]
        thumbnailfn = join(self.expo_dir, 'thumbnail.%s' % ext)
        with open(thumbnailfn, 'wb') as fd:
            fd.write(result)

        # all ok, write original filename
        thumbchecksum = join(self.expo_dir, 'thumbnail.checksum')
        with open(thumbchecksum, 'w') as fd:
            fd.write(req.url)

        self._sync_expo_5()

    def _sync_expo_5(self):
        Logger.info('Museotouch: Synchronization part 5')
        # get objects now.
        self._sync_popup_text(u'Téléchargement des objets')
        # self.backend.get_objects(
                # on_success=self._sync_expo_6,
                # on_error=self._sync_error_but_continue,
                # on_progress=self._sync_progress)
        self._sync_expo_6(None, None)

    def aft(self, req, result):
        ''' fonction appelee quand un fichier secondaire a fini son telechargement '''
        if not exists(join(self.expo_dir, 'otherfiles')):
            makedirs(join(self.expo_dir, 'otherfiles'))
        # filepath = join(self.expo_dir, 'otherfiles', no_url(req.url))
        filepath = join(self.expo_dir, 'otherfiles', basename(req.url))
        
        try:
            output = open(filepath, 'wb')
            output.write(result) # fichier sauvegarde
            output.close()
        except TypeError, e:
            print e
            if isfile(filepath):
                    remove(filepath)
            else:    ## Show an error ##
                    print("Error: %s file not found while removing" % filepath)

        self.url_requests.remove(req)
        if not self.url_requests: # si c'etait le dernier fichier
            if hasattr(self, 'root'):
                if hasattr(self.root, 'gif'):
                    self.root.remove_widget(self.root.gif) # on supprime le gif de chargement
        print " ###", req.url, '--> download finished !'

    def _sync_expo_6(self, req, result):
        Logger.info('Museotouch: Synchronization part 6')
        self._sync_popup_text(u'Téléchargement des ...')
        self.url_requests = []

        # filename = join(self.expo_dir, u'objects.json')
        # with open(filename, 'wb') as fd:
        #     s = dumps(result)
        #     fd.write(s)
        result = self._expo_files
        # on the result, remove all the object already synced
        items = result['items'][:]
        for item in result['items']:
            # fichiers = item['fields']['data']
            if not item['mainMedia']:
                print '===> remove item %r, no data attached' % item['itemId']
                items.remove(item)
                continue
            need_sync = True





            # print 'check', item['id']
            # for fichier in fichiers:                
            #     if not self._sync_is_filename_of_item(item, fichier):
            #         # print ' ### The file <{0}> is not downloaded - yet.'.format(fichier)
            #         from museolib.utils import no_url
            #         filepath = join(self.expo_dir, 'otherfiles', no_url(fichier))
            #         # print ' ### It could be downloaded in', filepath
                    

            #         filename = basename(fichier)
            #         filepath = join(self.expo_dir, 'otherfiles', filename)

            #         # if not isfile(join(self.expo_dir, 'otherfiles', no_url(fichier))):
            #         # TEMPORARY Next lines commented out : was preventing "otherfiles" to update if a file with the same name was already here
            #         # UPDATE : uncommented : was causing other (big) problems
            #         if not isfile(filepath):
            #             from kivy.network.urlrequest import UrlRequest
            #             req = UrlRequest(fichier, on_success=self.aft, on_error=self.aft)
            #             self.url_requests.append(req)
            #         continue
            item['__item_filename__'] = item['mainMedia']
            filename, ext = self._sync_convert_filename(item['mainMedia'])
            local_filename = self._sync_get_local_filename(filename)

            if exists(local_filename):                
                need_sync = False

                # # now, ensure the md5 is the same
                # md5_local_filename = '%s.md5sum' % local_filename
                # md5 = item['fichier_md5'].strip()

                # # if we don't have md5 sum attached, forget about it.
                # if not exists(md5_local_filename):
                #     if not md5:
                #         need_sync = False
                #     print '3', need_sync, repr(md5)
                #     continue
                # # ok, is the md5 is the same ?
                # with open(md5_local_filename, 'r') as fd:
                #     md5_local = fd.read()
                # # different md5, redownload.
                # if md5 != md5_local:
                #     print '4', repr(md5)
                #     continue
                
            if not need_sync:
                items.remove(item)

        Logger.info('Museotouch: %d need to be synced' % len(items))

        self._sync_result = items
        self._sync_index = 0
        self._sync_missing = []

        if len(items):
            self._sync_download()
        else:
            # no item to synchronize, all done !
            self._sync_popup.dismiss()
            self.build_app()

    def _sync_get_local_filename(self, fn):
        if type(fn) in (list, tuple):
            fn = fn[0]
        return join(self.expo_img_dir, self.imgdir, fn)

    def _sync_is_filename_of_item(self, item, fichier):
        uid = fichier.split('/')[-1].rsplit('.', 1)[0]
        return str(uid) == str(item['itemId'])

    def _sync_convert_filename(self, filename):
        # from the original filename given by json
        # convert to the filename we want.
        filename = basename(filename)
        if self.imgtype != 'raw':
            filename = filename.rsplit('.', 1)[0] + '.' + self.imgtype
        # get ext
        ext = filename.rsplit('.', 1)[-1]
        return filename, ext

    def _sync_download(self):
        uri = self._sync_result[self._sync_index]['mainMedia']   
        if '__item_filename__' in self._sync_result[self._sync_index]:
            filename, ext = self._sync_convert_filename(
                self._sync_result[self._sync_index]['__item_filename__'])

            text = 'Synchronisation de %d/%d' % (
                    self._sync_index + 1, len(self._sync_result))
            if len(self._sync_missing):
                text += '\n(%d non disponible)' % len(self._sync_missing)
            self._sync_popup.content.children[-1].text = text

            # check if the file already exist on the disk
            filename = self._sync_get_local_filename(filename)
            '''
            if exists(filename):
                # speedup a little bit. but we can't use always -1.
                Clock.schedule_once(self._sync_download_next,
                        -1 if self._sync_index % 10 < 8 else 0)
            else:
            '''

        self.backend.download_object(uri, self.imgdir, self.imgtype,
                self._sync_download_ok, self._sync_error, self._sync_progress)

    def _sync_download_ok(self, req, result):
        if req.resp_status < 200 or req.resp_status >= 300:
            # look like invalid ? ok.
            self._sync_missing.append(self._sync_index)
        else:
            # save on disk
            filename, ext = self._sync_convert_filename(req.url)
            filename = self._sync_get_local_filename(filename)
            with open(filename, 'wb') as fd:
                fd.write(result)

            # write md5 attached to item if exist
            # item_md5 = self._sync_result[self._sync_index]['fichier_md5'].strip()
            # if item_md5:
            #     md5_filename = '%s.md5sum' % filename
            #     with open(md5_filename, 'wb') as fd:
            #         fd.write(item_md5)

        Clock.schedule_once(self._sync_download_next)

    def _sync_download_next(self, *largs):
        self._sync_index += 1
        if self._sync_index >= len(self._sync_result):
            self._sync_end()
            return
        self._sync_download()

    def _sync_end(self):
        self._sync_popup.dismiss()
        self.build_app()

    def _sync_progress(self, req, current, total):
        if total == -1:
            total = req.chunk_size * 10
            current %= req.chunk_size * 10
            total_str = None
        else:
            total_str = format_bytes_to_human(total)

        self._sync_popup.content.children[0].max = total
        self._sync_popup.content.children[0].value = current
        text = self._sync_popup.content.children[-2].text
        
        if text is not None:
            text = ''
            text = '%s' % format_bytes_to_human(current)
            if total_str is not None:
                text += '/%s' % total_str
            self._sync_popup.content.children[-2].text = text

    def _sync_error(self, req, result):
        if req.resp_status == 404: 
            Clock.schedule_once(self._sync_download_next)
        else:
            self.error('Erreur lors de la synchro : '+ str(result))

    def _sync_error_but_continue(self, req, result):
        self._sync_popup.dismiss()
        self.build_app()

    def error(self, error):
        if type(error) not in (str, unicode):
            error = str(error)
        content = BoxLayout(orientation='vertical')
        label = Label(text=error, valign='middle')
        label.bind(size=label.setter('text_size'))
        content.add_widget(label)
        btn = Button(text='Fermer', size_hint_y=None, height=50)
        content.add_widget(btn)
        btn.bind(on_release=self.reset)
        popup = Popup(title='Erreur', content=content, auto_dismiss=False,
                size_hint=(.5, .5))
        popup.open()

    def reset(self, go_to_menu=True, *l ):
        # reset the whole app, restart from scratch.
        for child in Window.children[:]:
            Window.remove_widget(child)
        self.init_widgets()
        self.menu = Menu()
        Cache.remove('kv.texture')
        # remove everything from the current expo
        if hasattr(self, 'expo_data_dir'):
            resource_remove_path(self.expo_data_dir)
            Builder.unload_file(join(self.expo_data_dir, 'museotouch.kv'))

        if go_to_menu == True:
            print 'reset'
            # restart with selector.
            Window.add_widget(self.build_selector())


import sys, traceback
if __name__ in ('__main__', '__android__'):    
    try:
        MuseotouchApp().run()
    except:
        print "Trigger Exception, traceback info forward to log file."
        traceback.print_exc(file=sys.stdout)
        # Désactive le besoin de taper une touche pour fermer museotouch ce qui bloquait le relancement automatique.
        # TODO : Placer la trace dans un fichier à chaque crash.
        sys.exit(1)