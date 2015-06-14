<?php

/* Server Side Adapter pattern presenting Mysql data matching Museotouch client side API */

//VARIABLES DE CONFIGURATION
    $config = array();
    $config['scenario_fichier'] = 'http://ns318835.ip-91-121-122.eu/museotouch/uploads/expos/4/raw/145999c43e00d700eefcb113ddf72c58.zip';
    $config['scenario_logo'] = 'http://ns318835.ip-91-121-122.eu/museotouch/uploads/expos/4/raw/3b22edd9b30af3c6cdec582e4d80bc05.jpg';
    $config['default_file'] = 'http://omeka.reciproque.com/museotouch/data/noir.jpg';  // fichier par défault
    $config['nb_kw'] = 1;  // nb de groupes de mots clefs
    include 'connect.php';


//CONNEXION A LA BASE DE DONNEES
    $bdd = @mysql_connect($config['bdd_host'], $config['bdd_user'], $config['bdd_pass']) or die('Erreur de connexion au serveur de base de données ! Merci de repasser plus tard !');
    // selection de la base
    if (!$bdd || !@mysql_select_db($config['bdd_name'], $bdd)) {
      die ('Erreur de connexion à la base de données ! Merci de repasser plus tard.');
    }
    // forçage de l'utf-8 pour la bdd
    @mysql_set_charset('utf8', $bdd);


//GENERATION DE LA SORTIE

    // Données générales exposition
      $don = array('id' => 1000, 'name' => 'Museotouch', 'private' => '0');
      $up = array();
      $up[] = array('fichier' => urlencode($config["scenario_fichier"]));
      $up[] = array('fichier' => urlencode($config["scenario_logo"]));

    //Mots clefs de l'exposition
      $kw = array();
      $id=0;
      //Cas1 : Pour la récupération de mots clefs uniques dans une colone Catx
        /*
        for ($i=1; $i <=$config['nb_kw']; $i++) { 
          $sqkw = @mysql_query("SELECT DISTINCT Cat".$i." FROM `UP8_dispositifs`");
          $children = array();
          while ($don = @mysql_fetch_assoc($sqkw)) {
            $children[] = array('id' => "$id", 'name' => urlencode($don["Cat".$i]));
            $id++;
            }
        $kw[] = array('group' => "KW".$i, 'children' => $children);
        }
        */
      // Cas 2 : Création d'une sous-arborescence spécifique Cat 1 > Cat2
        $sqkw1 = @mysql_query("SELECT DISTINCT Cat1 FROM `UP8_dispositifs` LIMIT 4");
        while ($don1 = @mysql_fetch_assoc($sqkw1)) {
          $sqkw2 = @mysql_query("SELECT Cat2, Cat1 FROM `UP8_dispositifs` WHERE Cat1 = '".$don1['Cat1']."' GROUP BY Cat2");
          $children = array();
          while ($don2 = @mysql_fetch_assoc($sqkw2)) {
            $children[] = array('id' => "$id", 'name' => urlencode($don2["Cat2"]));
            $id++;
            }
          $kw[] = array('group' => urlencode($don1['Cat1']), 'children' => $children);
        }

    // Liste des objets de l'exposition
      $item = array();
      $sql = @mysql_query("SELECT * FROM `UP8_dispositifs` WHERE ID NOT IN (500) LIMIT 200 OFFSET 0");

      while ($it = @mysql_fetch_assoc($sql)) {
        //Fichiers
          //Fichier principal
            $main_file = $config['default_file'];
            $md5_main_file = @md5_file($main_file);
            $url = $it['Fichier'];

            if ($url != '') {
              if(@fopen(rawurlencode($url),'r')) {
                  $main_file = rawurlencode($url);
                  $md5_main_file = @md5_file($main_file);
                }
              else
                {
                  $url = "http://omeka.reciproque.com/uploads/".rawurlencode($url);
                  if(@fopen($url,'r')) {
                    $main_file = $url;
                    $md5_main_file = @md5_file($main_file);
                  }
                }
            }

          //Fichiers secondaires
            $data = array();

            /*if (@is_dir('../uploads/objets/'.@$it['id'].'/raw/')) {
              if ($dir = @opendir('../uploads/objets/'.$it['id'].'/raw/')) {
                while (($file = @readdir($dir)) !== false) {
                  if ($file !== '.' && $file !== '..' && is_file('../uploads/objets/'.$it['id'].'/raw/'.$file)) {
                    $data[] = array('fichier' => urlencode($config['site_http'].'/uploads/objets/'.$it['id'].'/raw/'.$file));
                      if (strpos($file, $it['id'].'.') === 0) {
                        $main_file = 'uploads/objets/'.$it['id'].'/raw/'.$file;
                        $md5_main_file = @md5_file('../'.$main_file);
                      }
                  }
                }
                @closedir($dir);
              }
            }
            */

        //Carte
          $orig_geo = urlencode(@$it['Tags_demo']);
        
        //Mots Clefs objet
          $kw1 = array();
          //Cas 1
            /*
            for ($i=1; $i <=$config['nb_kw']; $i++) { 
              foreach ($kw as $key1 => $value1) {
                foreach ($value1['children'] as $key => $value) {
                  if (urlencode(@$it["Cat".$i]) == $value['name']) {
                    $kw1[] = urlencode($value['id']);
                    if ($i==1) $orig_geo="c".$value['id'];
                    }
                }
              } 
            }*/
          //Cas 2
            foreach ($kw as $key1 => $value1) {
              foreach ($value1['children'] as $key => $value) {
                if ((urlencode(@$it["Cat2"]) == $value['name'])&&(urlencode(@$it["Cat1"]) == $value1['group'])) {
                  $kw1[] = urlencode($value['id']);
                  }
              }
            }

        //Champs principaux
          if (@$it['Tags_demo'] != '0')
            $item[] = array(
              'nom' => urlencode(@$it['NOM_dispositif']), 
              'date_acqui' => (urlencode(@$it['Date_deb']) != '' ? urlencode(@$it['Date_deb']) : '1900'),
              'date_crea' => (urlencode(@$it['Date_deb']) != '' ? urlencode(@$it['Date_deb']) : '1900'), 
              'datation' => urlencode(@$it['Date_deb'] != '' ? urlencode(@$it['Date_deb']) : '1900' ), 
              'orig_geo' => urlencode($orig_geo != '' ? $orig_geo : 'autres'), 
              'orig_geo_prec' => urlencode(@$it['Intention']), 
              'taille' => (urlencode(@$it['IND_COL']) != '' ? urlencode(@$it['IND_COL']) : '0'), 
              'description' => urlencode(str_replace("\n", "", substr(@$it['Descriptif'],0,1000))), 
              'private' => '',
              'freefield' => urlencode(@$it['Motivation']),
              'english' => [],
              'spanish' => [],
              'id' => urlencode($it['ID']), 
              'fichier' => urlencode($main_file),
              'fichier_md5' => urlencode($md5_main_file),
              'timestamp_file' => '0',
              'data' => $data, 
              'keywords' => $kw1,              
              'children' => [],
              'organisation' => urlencode(@$it['NOM_organisation']),
              'intention' => urlencode(@$it['Intention']),
              'motivation' => urlencode(@$it['Motivation']),
              'url' => urlencode(@$it['URL']),
              'cat1' => urlencode(@$it['Cat1']),
              'cat2' => urlencode(@$it['Cat2']),
              'cat3' => urlencode(@$it['Cat3'])
          );

      }

    //Outside
      header('Content-Type: application/json');
      $out = array('id' => urlencode($don['id']), 'name' => urlencode($don['name']), 'private' => urlencode(empty($don['private'])?0:1), 'data' => $up, 'keywords' => $kw, 'items' => $item, 'nodes' => []);
      echo json_encode($out);
    
?>