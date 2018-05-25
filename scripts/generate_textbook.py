from subprocess import check_call
import os
import shutil as sh
from glob import glob
import nbformat as nbf
from nbclean import NotebookCleaner
from tqdm import tqdm
import numpy as np

SITE_ROOT = os.path.expanduser('~/github/forks/python/teaching/dsep/jupyterhub-for-education-template')
SITE_NAVIGATION = os.path.join(SITE_ROOT, '_data', 'navigation.yml')
TEMPLATE_PATH = os.path.expanduser('~/github/forks/python/teaching/dsep/jupyterhub-for-education-template/assets/templates/jekyllmd.tpl')
TEXTBOOK_FOLDER_NAME = 'textbook'
NOTEBOOKS_FOLDER_NAME = 'notebooks'
TEXTBOOK_FOLDER = os.path.join(SITE_ROOT, TEXTBOOK_FOLDER_NAME)
NOTEBOOKS_FOLDER = os.path.join(SITE_ROOT, NOTEBOOKS_FOLDER_NAME)
IMAGES_FOLDER = os.path.join(SITE_ROOT, 'images')
MARKDOWN_FILE = os.path.join(SITE_ROOT, 'SUMMARY.md')


def _markdown_to_files(path_markdown, indent=2):
    """Takes a markdown file containing chapters/sub-headings and
    converts it to a file structure we can use to build a side bar."""

    with open(path_markdown, 'r') as ff:
        lines = ff.readlines()

    files = []
    for line in lines:
        if line.strip().startswith('* '):
            title = _between_symbols(line, '[', ']')
            link = _between_symbols(line, '(', ')')
            spaces = len(line) - len(line.lstrip(' '))
            level = spaces / indent
            files.append((title, link, level))
    return files


def _between_symbols(string, c1, c2):
    """Will return empty string if nothing is between c1 and c2."""
    for char in [c1, c2]:
        if char not in string:
            raise ValueError("Couldn't find charachter {} in string {}".format(
                char, string))
    return string[string.index(c1)+1:string.index(c2)]


def _clean_notebook(notebook):
    cleaner = NotebookCleaner(notebook)
    cleaner.remove_cells(empty=True)
    cleaner.remove_cells(search_text="# HIDDEN")
    cleaner.clear('stderr')
    cleaner.save(notebook)
    return notebook

if __name__ == '__main__':
    # --- Collect the files we'll convert over ---
    files = _markdown_to_files(MARKDOWN_FILE)
    for ix_file, (title, link, level) in tqdm(list(enumerate(files))):
        if len(link) == 0:
            continue
        if not os.path.exists(link):
            raise ValueError("Could not find file {}".format(link))

        # Collecting and renaming files/folders
        filename = os.path.basename(link)
        new_folder = os.path.dirname(link).replace(NOTEBOOKS_FOLDER_NAME, TEXTBOOK_FOLDER_NAME)
        new_file_path = os.path.join(new_folder, filename.replace('.ipynb', '.md'))

        # Collect previous/next md file for pagination
        if ix_file == 0:
            prev_file_link = ''
            prev_file_title = ''
        else:
            prev_file_title, prev_file_link, _ = files[ix_file-1]
            prev_file_link = prev_file_link.replace(NOTEBOOKS_FOLDER_NAME, TEXTBOOK_FOLDER_NAME).replace('.ipynb', '')

        if ix_file == len(files) - 1:
            next_file_link = ''
            next_file_title = ''
        else:
            next_file_title, next_file_link, _ = files[ix_file+1]
            next_file_link = next_file_link.replace(NOTEBOOKS_FOLDER_NAME, TEXTBOOK_FOLDER_NAME).replace('.ipynb', '')

        if not os.path.isdir(new_folder):
            os.makedirs(new_folder)

        # Create a temporary version of the notebook we can modify
        tmp_notebook = link + '_TMP'
        sh.copy2(link, tmp_notebook)

        # Clean up the file before converting
        _clean_notebook(tmp_notebook)

        # Run nbconvert moving it to the output folder
        build_call = '--FilesWriter.build_directory={}'.format(new_folder)
        images_call = '--NbConvertApp.output_files_dir={}'.format(
            os.path.join(IMAGES_FOLDER, new_folder))
        check_call(['jupyter', 'nbconvert', '--log-level="CRITICAL"',
                    '--to', 'markdown', '--template', TEMPLATE_PATH,
                    images_call, build_call, tmp_notebook])

        # Images: replace relative image paths to baseurl paths
        IMG_STRINGS = [ii*'../' + IMAGES_FOLDER for ii in range(4)]
        with open(new_file_path, 'r') as ff:
            lines = ff.readlines()
        for ii, line in enumerate(lines):
            for IMG_STRING in IMG_STRINGS:
                line = line.replace(IMG_STRING, '{{ site.baseurl }}/images')
            lines[ii] = line

        # Front-matter YAML
        yaml = []
        yaml += ['---']
        yaml += ['layout: textbook']
        yaml += ['interact_link: {}'.format(link.lstrip('./'))]
        yaml += ['previous:']
        yaml += ['  url: {}'.format(prev_file_link.lstrip('.'))]
        yaml += ['  title: {}'.format(prev_file_title)]
        yaml += ['next:']
        yaml += ['  url: {}'.format(next_file_link.lstrip('.'))]
        yaml += ['  title: {}'.format(next_file_title)]
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
        with open(new_file_path, 'w') as ff:
            ff.writelines(lines)

        os.remove(tmp_notebook)

    # Generate sidebar
    sidebar_text = ['sidebar-textbook:']
    sp = '  '
    chapter_ix = 1
    for ix_file, (title, link, level) in tqdm(list(enumerate(files))):
        if level > 0 and len(link) == 0:
            continue
        if level == 0:
            title = '{}. {}'.format(chapter_ix, title)
            chapter_ix += 1
        new_link = link.replace(NOTEBOOKS_FOLDER_NAME, TEXTBOOK_FOLDER_NAME).replace('.ipynb', '').strip('.')
        space = '  ' if level == 0 else '    '
        level = int(level)
        sidebar_text.append(space + '- title: {}'.format(title))
        sidebar_text.append(space + '  class: level_{}'.format(level))
        if len(link) > 0:
            sidebar_text.append(space + '  url: {}'.format(new_link))
        if ix_file != (len(files) - 1) and level < files[ix_file + 1][-1]:
            sidebar_text.append(space + '  children:')
    sidebar_text = [ii + '\n' for ii in sidebar_text]

    with open(SITE_NAVIGATION, 'r') as ff:
        lines = ff.readlines()

    text_start = np.where(['# --- Textbook sidebar ---' in line for line in lines])[0][0]
    lines = lines[:text_start+1]
    lines += sidebar_text

    with open(SITE_NAVIGATION, 'w') as ff:
        ff.writelines(lines)
    print('Done!')
