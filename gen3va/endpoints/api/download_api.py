"""Manages downloads.
"""

import os
import zipfile
import StringIO

from flask import Blueprint, Response

from substrate import Tag
from gen3va import database
from gen3va.config import Config


download_api = Blueprint('download_api',
                         __name__,
                         url_prefix='%s/download' % Config.BASE_URL)

DOWNLOAD_DIR = '%s/static/downloads' % Config.SERVER_FILE_ROOT


@download_api.route('/<tag_name>', methods=['GET'])
def test(tag_name):
    """Returns a zipped directory with one plain text file for each signature.
    """
    tag = database.get(Tag, tag_name, 'name')

    # Write the contents of the signatures to file and get the filenames.
    filenames = _get_signature_files(tag)

    # Folder name in ZIP archive which contains the above files
    zip_subdir = tag.name
    zip_filename = '%s.zip' % zip_subdir

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()
    # The zip compressor
    zf = zipfile.ZipFile(s, 'w')

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        # Add file, at correct path
        zf.write(fpath, zip_path)

    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = Response(s.getvalue(), mimetype='application/x-zip-compressed')
    resp.headers['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    # Remove files from disc
    for f in filenames:
        os.remove(f)

    return resp


def _get_signature_files(tag):
    """Returns a list of filenames where each file has the contents of a gene
    signature.
    """
    filenames = []
    for idx, sig in enumerate(tag.report.gene_signatures):
        fname = _write_signature_to_file(idx, sig)
        filenames.append(fname)
    return filenames


def _write_signature_to_file(idx, gene_signature):
    """Returns the name of a file with the contents of a gene signature.
    """
    name = gene_signature.name.replace('/', '')
    path = '%s/%s_%s.txt' % (DOWNLOAD_DIR, idx, name)
    with open(path, 'w+') as f:

        rm = gene_signature.required_metadata
        _write_metadata(f, 'diff_exp_method', rm.diff_exp_method)
        _write_metadata(f, 'ttest_correction_method', rm.ttest_correction_method)
        _write_metadata(f, 'cutoff', rm.cutoff)
        _write_metadata(f, 'threshold', rm.threshold)

        for om in gene_signature.filtered_optional_metadata:
            _write_metadata(f, om.name, om.value)

        f.write('!end_metadata\n\n')

        for rg in gene_signature.combined_genes:
            line = '%s\t%s\n' % (rg.gene.name, rg.value)
            f.write(line)
    return path


def _write_metadata(f, key, value):
    """Writes metadata key-value pair to file, encoding to UTF-8.
    """
    try:
        line = '!%s\t%s\n' % (key, value)
        line = line.encode('utf-8')
        f.write(line)
    except UnicodeEncodeError as e:
        print(e)
