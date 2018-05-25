from subprocess import check_call
import os
import shutil as sh
from glob import glob
import nbformat as nbf
from nbclean import NotebookCleaner
from tqdm import tqdm
import numpy as np

SITE_ROOT = os.path.expanduser('~/github/forks/python/teaching/dsep/jupyterhub-for-education-template')
TEMPLATE_PATH = os.path.expanduser('~/github/forks/python/teaching/dsep/jupyterhub-for-education-template/assets/templates/jekyllmd.tpl')
TEXTBOOK_FOLDER = os.path.join(SITE_ROOT, 'textbook')
NOTEBOOKS_FOLDER = os.path.join(SITE_ROOT, 'notebooks')
IMAGES_FOLDER = os.path.join(SITE_ROOT, 'images')

ipynb_files = glob(os.path.join(NOTEBOOKS_FOLDER, '**/*.ipynb'), recursive=True)
markdown_files = glob(os.path.join(NOTEBOOKS_FOLDER, '/*/*.md'), recursive=True)
notebooks_folders = glob(os.path.join(NOTEBOOKS_FOLDER, '*'))
notebooks_folders = {ii: [] for ii in notebooks_folders if os.path.isdir(ii)}
notebooks_folder_name = NOTEBOOKS_FOLDER.split('/')[-1]

previous_md_file = None
for ix_file, ifile in tqdm(list(enumerate(ipynb_files))):
    filename = os.path.basename(ifile)
    i_folders = os.path.dirname(ifile.split(notebooks_folder_name)[-1]).strip('/')
    new_folder = os.path.join(TEXTBOOK_FOLDER, i_folders)
    level = len(i_folders.split('/'))

    if not os.path.isdir(new_folder):
        os.makedirs(new_folder)

    # Create a temporary version of the notebook we can modify
    tmp_notebook = ifile + '_TMP'
    sh.copy2(ifile, tmp_notebook)

    # Clean up the file before converting
    cleaner = NotebookCleaner(tmp_notebook)
    cleaner.remove_cells(empty=True)
    cleaner.remove_cells(search_text="# HIDDEN")
    cleaner.clear('stderr')
    cleaner.save(tmp_notebook)

    # Run nbconvert moving it to the output folder
    build_call = '--FilesWriter.build_directory={}'.format(new_folder)
    images_call = '--NbConvertApp.output_files_dir={}'.format(os.path.join(IMAGES_FOLDER, i_folders))
    check_call(['jupyter', 'nbconvert', '--log-level="CRITICAL"',
                '--to', 'markdown', '--template', TEMPLATE_PATH,
                images_call, build_call, tmp_notebook])

    # Read in the markdown and replace each image file with the site URL
    IMG_STRINGS = ['../../../images', '../../images', IMAGES_FOLDER]
    path_md = os.path.join(new_folder, os.path.basename(ifile).replace('.ipynb', '.md'))
    with open(path_md, 'r') as ff:
        lines = ff.readlines()
    for ii, line in enumerate(lines):
        for IMG_STRING in IMG_STRINGS:
            line = line.replace(IMG_STRING, '{{ site.baseurl }}/images')
        lines[ii] = line

    # Collect previous/next md file for pagination
    if ix_file == 0:
        prev_file = ''
        prev_file_name = ''
    else:
        prev_file = ipynb_files[ix_file-1]
        prev_file = prev_file.split('notebooks')[-1].strip('/')
        prev_file = '/'+os.path.join('textbook', prev_file.replace('.ipynb', ''))
        prev_file_name = os.path.basename(prev_file).replace('_', ' ')
    if ix_file == len(ipynb_files) - 1:
        next_file = ''
        next_file_name = ''
    else:
        next_file = ipynb_files[ix_file+1]
        next_file = next_file.split('notebooks')[-1].strip('/')
        next_file = '/'+os.path.join('textbook', next_file.replace('.ipynb', ''))
        next_file_name = os.path.basename(next_file).replace('_', ' ')

    # Add front-matter YAML
    interact_link = os.path.join(i_folders, filename)
    yaml = []
    yaml += ['---']
    yaml += ['layout: textbook']
    yaml += ['interact_link: {}'.format(interact_link)]
    yaml += ['previous:']
    yaml += ['  url: {}'.format(prev_file)]
    yaml += ['  title: {}'.format(prev_file_name)]
    yaml += ['next:']
    yaml += ['  url: {}'.format(next_file)]
    yaml += ['  title: {}'.format(next_file_name)]
    yaml += ['sidebar:']
    yaml += ['  nav: sidebar-textbook']
    yaml += ['---']
    yaml = [ii + '\n' for ii in yaml]
    lines = yaml + lines

    # Add an extra slash to the inline math before `#` since Jekyll strips it
    inline_replace_chars = ['#']
    for ii, line in enumerate(lines):
        dollars = np.where(['$' == char for char in line])[0]
        # Make sure we have at least two dollar signs and they
        # Aren't right next to each other
        if len(dollars) > 2 and all(ii > 1 for ii in (dollars[1:] - dollars[:1])):
            for char in inline_replace_chars:
                lines[ii] = line.replace('\\#', '\\\\#')

    # Write the result
    with open(path_md, 'w') as ff:
        ff.writelines(lines)

    os.remove(tmp_notebook)

# Copy the markdown files
print('Copying {} markdown files'.format(len(markdown_files)))
for ifile in markdown_files:
    file_name = os.path.basename(ifile)
    sh.copy2(ifile, os.path.join(TEXTBOOK_FOLDER, file_name))
