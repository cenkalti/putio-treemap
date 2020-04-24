import os
from typing import Dict

import putiopy
import plotly.graph_objects as go

client = putiopy.Client(os.environ['PUTIO_TOKEN'])


class File:
    def __init__(self, putio_file):
        self.id = putio_file.id
        self.parent_id = putio_file.parent_id
        self.name = putio_file.name
        self.size = putio_file.size


files: Dict[int, File] = {}


def append_file(putio_file):
    global processed
    print("appending file id:", putio_file.id)
    f = File(putio_file)
    files[f.id] = f
    if putio_file.content_type != 'application/x-directory':
        processed += putio_file.size
        print("processed %d of %d gb" % (processed // 2**30, total_size // 2**30))


processed = 0
root = client.File.get(int(os.getenv('PUTIO_FILE_ID', '0')))
total_size = root.size


def get_folder_recursive(putio_file):
    if putio_file.folder_type == 'SHARED_ROOT':
        return

    append_file(putio_file)
    if putio_file.content_type == 'application/x-directory':
        children = putio_file.dir()
        for child in children:
            get_folder_recursive(child)


get_folder_recursive(root)


def human_size(num):
    """Convert file size to human readable format"""
    if num is None:
        return '0'
    return "%3.1f %s" % _divide_bytes(num)


def _divide_bytes(num):
    num = float(num)
    for x in ['B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']:
        if num < 1024:
            return num, x
        num /= 1024
    return '∞'


ids = []
labels = []
parents = []
values = []
hovertext = []

for id, file in files.items():
    ids.append(file.id)
    labels.append(file.name)
    values.append(file.size)
    hovertext.append(human_size(file.size))
    try:
        parents.append(files[file.parent_id].id)
    except KeyError:
        parents.append('')


fig = go.Figure(go.Treemap(
    ids=ids,
    labels=labels,
    parents=parents,
    values=values,
    # hovertext=hovertext,
    marker_colorscale='Reds',
    branchvalues='total',
    # textinfo='text',
    # textinfo = "label+value+percent parent+percent entry",
    texttemplate='%{label}',
    hovertemplate='%{label}<br>%{value:.2s}<extra></extra>',
))

# TODO to_html
# TODO thread pool
# TODO combine many items
# TODO flask
# TODO zeit
# TODO github
# TODO deploy on push
# TODO auth
# TODO favorite tools
# TODO filter small items
# TODO api method children count
# TODO show sizes in human
fig.show()
