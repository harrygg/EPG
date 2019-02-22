# -*- coding: utf-8 -*-
import json
import gzip
import shutil
import codecs
import hashlib
import requests
import subprocess
from operator import attrgetter
from random import randint
from helper import *
import xml.etree.ElementTree as et

config_file = os.path.join(configdir, "wgmulti.config.json")

def get_map():
  log("Getting channels map")
  try:
    r = requests.get("https://raw.githubusercontent.com/harrygg/EPG/master/maps/channels-tvbg.json")
    with open("mapping.json", "w") as w:
     w.write(r.text.encode("utf-8"))
  except:
    log("WARNING Downloading map failed. Loading local mapping file.")

  streams_map = json.load(codecs.open("mapping.json", 'r'))["streams"]
  log("mapping.json loaded successfully")
  return streams_map

def get_ids():

  channels = []
  ids = []

  try:
    r = requests.get("http://megaepg.kodibg.org/bedroom/channels.json?cachebuster=%s" % randint(0, 10000))
    channels = r.json()
    with open("channels.json", "w") as w:
      w.write(r.text.encode("utf-8"))
    log("Successfully saved remote channels.json")
  except Exception as er:
    log("Error during getting the ids")
    log(er)
  try:
    channels = json.load(codecs.open("channels.json", 'r'))
  except:
    log("No channels.json file loaded")

  for c in channels:
    if c["id"] not in ids:
      ids.append(c["id"])

  log("Got %s ids" % len(ids))
  #with open("ids.json", "w") as w:
  #  w.write(json.dumps(ids, indent=2, separators=(',', ': ')).decode('unicode-escape').encode('utf8'))

  return ids

def generate_config():
  config = json.load(codecs.open(config_file))
  channels = config["channels"]
  new_channels = {}

  log("Loaded %s channels in %s" % (len(channels), config_file))
  log( "Getting ids ...")
  ids = get_ids()
  if (len(ids)) > 0:
    log( "Got %s channel ids" % len(ids))

    ### Loop through all channels in the config
    ### If channel is not in current playlist ids disable it
    ### Else enable it and remove from the ids list
    for channel in channels:
      if channel["name"] not in ids: #if channel is not in playlist, disable it
        channel["enabled"] = False
      else:
        channel["enabled"] = True
        ids.remove(channel["name"])

      #if there are timeshifts channels, check
      ### whether they are in the current playlist ids list
      if channel.get("timeshifts"):
        for timeshifted in channel["timeshifts"]:
          if timeshifted["name"] in ids:
            timeshifted["enabled"] = True
            ids.remove(timeshifted["name"])
          else:
            timeshifted["enabled"] = False

      #if len(channel["siteinis"]) == 0:
      #  channel["enabled"] = False

    ### All ids that are left are new, that is new channels
    ### Add them to the config as new channels without siteini and site_id
    new_channels = len(ids)

    for id in ids:
      ### Find out if this is an offset channel
      offset = 0
      try: offset = int(re.compile("\+\d+").findall(id)[0].replace("+", ""))
      except: pass
      if offset > 0:
        ### This is a timeshifted channel, try finding the parent channel
        name = id.replace("+%s" % offset, "").rstrip()
        log( "Found timeshifted channel in current ids list: '%s' offset: %s, searching for parent" % (name, offset))
        found = False
        for c in channels:
          if c["name"] == name:
            log("Found parent '%s'" % c["name"])
            if not c.get("timeshifts"):
              c["timeshifts"] = []
            log( "Adding new channel %s as parent of '%s'" % (name, c["name"]))
            c["timeshifts"].append({"name": name, "xmltv_id":name, "offset": offset})
            found = True
            break
        if found:
          continue

      ### If channel was no offset channel or parent was not found, add it as a new channel
      log( "Adding new channel %s " % id)
      channels.append({"name": id, "xmltv_id":id, "siteinis":[], "enabled": True, "update": "i"})

    channels = sorted(channels, key=lambda channel: channel["name"], reverse=False)
    config["channels"] = channels

    with open(config_file, "w") as w:
      #w.write(pretty_json(config))
      w.write(json.dumps(config, indent=2, separators=(',', ': ')).decode('unicode-escape').encode('utf8'))

  n = 0
  log( "Channels with no siteini:")
  for c in channels:
    if not c.get("siteinis") or len(c["siteinis"]) == 0:
      #log( c["name"])
      n += 1

  log( "----------------------------")
  log( "Total channels in config %s" % len(channels))
  log( "Total newly added channels %s" % new_channels)
  log( "Total channels without siteini %s" % n)

def grab():
    #try:
    ### Find webgrab path:
    if not os.path.isfile(wgmulti):
      log("ERROR wgmulti.exe not found. %s" % wgmulti)
      log("Grabbing stopped!!!")
      return

    log("Using wgmulti: %s" % wgmulti)
    log("Using config dir %s" % configdir)
    log("Using wglogfile %s" % wglogfile)
    # cmd = "\"%s\" %s > %s" % (wgmulti, configdir, wglogfile)
    cmd = "\"%s\" %s" % (wgmulti, configdir)
    log("Executing command '%s'" % cmd)
    retval = subprocess.call(cmd, shell=True)
    log("Returned code: %s" % retval)
    log("Grabbing finished.")
    #except Exception as er:
    log("Error while grabbing data.")
    #log(er)

def queryimdb():
  try:
    log("Quering for IMDB data")
    xmltv_mdb_processor = "xmltv_mdb_processor.exe"
    imdb_file = os.path.join(configdir, "imdb.xml")
    cmd = "\"%s\" \"%s\" \"%s\" \"%s\"" % (xmltv_mdb_processor, imdb_file, epg_file, final_epg_file)
    log("Running command: %s " % cmd)
    subprocess.call(cmd)
    log("Quering for IMDB data finished.")
  except Exception as er:
    log("Error while quering for IMDB data.")
    log(er)

def remove_tags():
  try:
    log("Removing selected tags")
    lines = []
    with open(final_epg_file) as f:
      for line in f:
        if "<url>" not in line:
          lines.append(line)
    
    with open(final_epg_file, "w") as w:
      for line in lines:
        w.write(line)
    
    log("Removing selected tags finished")
  except Exception as er:
    log("Error while removing tags.")
    log(er)
    
    
def hash():
  try:
    ## Generate md5
    log("Calculating MD5 hash for file %s" % final_epg_file)
    hash_md5 = md5(final_epg_file)
    log("MD5 hash is %s" % hash_md5)
    
    ## Save md5 hash to a file
    with open(os.path.join(gitdir, "checksum.txt"), "w") as w:
      w.write(hash_md5)
    
    statinfo = os.stat(epg_file)
    log("epg.xml size %s " % convert_bytes(statinfo.st_size))
  except Exception as er:
    log("Error while generating EPG hash.")
    log(er)

def zip(epg_file):
  try:
    log("Zipping EPG")
    ## Zip EPG
    gzfile = epg_file + ".gz"
    with open(epg_file, 'rb') as f_in, gzip.open(gzfile, 'wb') as f_out:
      shutil.copyfileobj(f_in, f_out)
    statinfo = os.stat(gzfile)
    log("Zip file saved to %s" % gzfile)
    log("Epg zip size %s " % convert_bytes(statinfo.st_size))
  except Exception as er:
    log("Error while zipping the EPG file.")
    log(er)
    
def convert_bytes(num):
  """
  this function will convert bytes to MB.... GB... etc
  """
  for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
      if num < 1024.0:
          return "%3.1f %s" % (num, x)
      num /= 1024.0  

def md5(fname):
  hash_md5 = hashlib.md5()
  with open(fname, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
          hash_md5.update(chunk)
  return hash_md5.hexdigest()

def sortchildrenby(parent, attr):
  parent[:] = sorted(parent, key=lambda child: child.get(attr))


def export_other_epgs():
  #try:
  files = []
  export_config_file = os.path.join(configdir, "exports.json")
  export_configs = json.load(codecs.open(export_config_file))
  for conf in export_configs:
    tv = et.Element('tv')
    epg_file = os.path.join(gitdir, conf["filename"])
    files.append(epg_file)
    log("Exporting EPG file: %s" % epg_file)
    #with open(epg_file, 'w') as w_out:
    tree = et.parse(final_epg_file)
    root = tree.getroot()
    channel_ids = []
    
    for elem in root:  
      for subelem in elem:
        if elem.tag == "channel":
          channel_name = elem.find('display-name').text
          if channel_name in conf["channels"]:
            channel_ids.append(elem.get("id"))
            tv.append(elem)
        elif elem.tag == "programme":
          channel_id = elem.get("channel")
          if channel_id in channel_ids:
            tv.append(elem)

    tree = et.ElementTree()   
    tree._setroot(tv)
    tree.write(epg_file, encoding="utf-8", xml_declaration=True)
    
    return files

    
    
