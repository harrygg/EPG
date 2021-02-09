# -*- coding: utf-8 -*-
import os
import sys
import git
import epg
from helper import *

log("Script execution started")
log("Bin dir: " + bindir)
log("Git dir: " + gitdir)
log("Logs dir: " + logdir)
log("Config dir: " + configdir)
log("Chaning dir to " + bindir)
os.chdir(bindir)
log("Current working dir: %s" % os.getcwd())


log("Generating platform specific version of wgmulti.exe.config")
content = ''
with open(wgexeconfig + '.tmpl', 'r') as f:
  content = f.read()

content = content.replace('$ConfigDir', configdir)
content = content.replace('$GrabbingTempFolder', temp)
content = content.replace('$ReportFolder', gitdir)
maxAsyncProcesses = '4' if os.name == 'nt' else '2'
content = content.replace('$MaxAsyncProcesses', maxAsyncProcesses)

with open(wgexeconfig, 'w') as w:
  w.write(content)

log("Generating wgmulti.exe.config finished!")

if len(sys.argv) > 1:
  if "-n" in sys.argv:
    commitEnabled = False
    log("Running with option -n: commit disabled")

  if "-d" in sys.argv:
    grabbingEnabled = False
    log("Running with option -d: demo mode, grabbing disabled")

### Pull online changes
if commitEnabled:
  log("Updating files in folder %s" % gitdir)
  repo = git.cmd.Git(gitdir)
  repo.pull()
  log("Updating files finished")

### Generate EPG
if grabbingEnabled:
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

else:
  log("Grabbing disabled. Skipping it.")

if commitEnabled:
  commit(gitdir, "Updating EPG")

  try:
    from shutil import copyfile
    harrygg_dir = os.path.join(gitdir, '../harrygg.github.io/')
    log("Copying report to %s and commiting" % harrygg_dir)
    copyfile(report_file, harrygg_dir + "index.html")
    log(report_file + " copied to " + harrygg_dir)    
    log("Updating files in folder %s" % harrygg_dir)
    repo = git.cmd.Git(harrygg_dir)
    repo.pull()
    log("Updating files finished")
    commit(harrygg_dir)
    
  except Exception as er:
    log("Error: %s" % er)

log("Finished!")
