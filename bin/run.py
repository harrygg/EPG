# -*- coding: utf-8 -*-
import os
import sys
try:
  import git
except ImportError:
  print ("Python git module not found. Try 'pip install gitpython'")
  sys.exit()
  
import epg
from helper import *

if len(sys.argv) > 1 and sys.argv[1] == "-n":
  commitEnabled = False
  log("Running with option -n --commit-disabled")


### Pull online changes
if commitEnabled:
  log("Updating files folder %s" % gitdir)
  repo = git.cmd.Git(gitdir)
  repo.pull()
  log("Updating files finished")

### Generate EPG
log("Generating EPG started")
#epg.generate_config()
epg.grab()
epg.queryimdb()
epg.remove_tags()
epg.hash()
epg.zip(final_epg_file)
exported_files = epg.export_other_epgs()
for file in exported_files:
  log("zipping file %s" % file)
  epg.zip(file)
log("Generating EPG endeded")

if commitEnabled:
  ### Push local changes
  log("Pushing local changes")
  files = repo.diff(None, name_only=True).split('\n')
  l = len(files)
  if l == 0:
    log("No files were modified")
  elif l == 1:
    log("1 file was modified")
  else:
    log("%s files were modified" % l)

  if l > 0:
    for f in files:
      log("Executing 'git add %s'" % f)
      repo.add(f)

    commitmsg = "Updating EPG"
    log("Executing 'git commit -m '%s'" % commitmsg)
    log("Pushing local files")
    ## add log file last
    repo.commit('-m', commitmsg)
    repo.push()

log("Exiting!")