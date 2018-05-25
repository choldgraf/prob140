from glob import glob
from collections import OrderedDict
import os
import numpy as np

SITE_ROOT = os.path.expanduser('~/github/forks/python/teaching/dsep/jupyterhub-for-education-template')
TEXTBOOK_FOLDER = 'textbook'
SITE_TEXTBOOK = os.path.join(SITE_ROOT, 'textbook')
SITE_NAVIGATION = os.path.join(SITE_ROOT, '_data', 'navigation.yml')

for ii, (dirpath, dirnames, filenames) in enumerate(os.walk(SITE_TEXTBOOK)):
    if ii == 0:
        sidebar_roots = OrderedDict((idir, []) for idir in dirnames)
    rel_folder = dirpath.split(TEXTBOOK_FOLDER)[-1].strip('/')
    split_subfolders = rel_folder.split('/')
    base_folder = split_subfolders[0]
    level = len(split_subfolders) if split_subfolders[0] != '' else 0
    this_class = 'level_{}'.format(level)

    for filename in filenames:
        filename_noext = filename.replace('.md', '')
        title = ' '.join(filename_noext.split('_')[1:])
        url = os.path.join(TEXTBOOK_FOLDER, rel_folder, filename.replace('.md', ''))
        sidebar_roots[base_folder].append((title, url, this_class))

sidebar_text = ['sidebar-textbook:']
sp = '  '
for key, vals in sidebar_roots.items():
    chapter_title = key.replace('_', ' ')
    sidebar_text.append(sp*1 + '- title: {}'.format(chapter_title))
    sidebar_text.append(sp*1 + '  children:')
    for ititle, iurl, iclass in vals:
        sidebar_text.append(sp*2 + '- title: {}'.format(ititle))
        sidebar_text.append(sp*2 + '  url: {}'.format(iurl))
        sidebar_text.append(sp*2 + '  class: {}'.format(iclass))
sidebar_text = [ii + '\n' for ii in sidebar_text]

with open(SITE_NAVIGATION, 'r') as ff:
    lines = ff.readlines()

text_start = np.where(['# --- Textbook sidebar ---' in line for line in lines])[0][0]
lines = lines[:text_start+1]
lines += sidebar_text

with open(SITE_NAVIGATION, 'w') as ff:
    ff.writelines(lines)
