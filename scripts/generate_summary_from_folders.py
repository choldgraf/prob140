import os


def files_to_markdown(files, indentation='  '):
    md = []
    for title, link, level in files:
        md.append(level*indentation + '* [{}]({})'.format(title, link))
    md = [ii+'\n' for ii in md]
    return md


def notebooks_folder_to_files(notebooks_folder):
    last_folder = ''
    all_files = []
    for ii, (dirpath, dirnames, filenames) in enumerate(os.walk(notebooks_folder)):
        if '.ipynb_checkpoints' in dirpath:
            continue
        rel_folder = dirpath.split(notebooks_folder)[-1].strip('/')
        split_subfolders = rel_folder.split('/')
        level = len(split_subfolders) if split_subfolders[0] != '' else 0
        if last_folder != rel_folder:
            subfolder_title = ' '.join(ii.capitalize() for ii in split_subfolders[-1].split('_'))
            all_files.append((subfolder_title, '', level-1))

        for filename in filenames:
            if not filename.endswith('.ipynb'):
                continue
            filename_parts = filename.split('_')
            try:
                # If first part of the filename is a number for ordering, remove it
                int(filename_parts[0])
                filename_parts = filename_parts[1:]
            except Exception:
                pass
            title = ' '.join(ii.capitalize() for ii in filename_parts)
            title = title.replace('.ipynb', '')
            url = os.path.join(notebooks_folder, rel_folder, filename)
            last_folder = rel_folder
            all_files.append((title, url, level))
    return all_files


if __name__ == '__main__':
    files = notebooks_folder_to_files('./notebooks')
    md = files_to_markdown(files)
    with open('./SUMMARY.md', 'w') as ff:
        ff.writelines(md)
