import os
import logging
import tempfile


def setup(parser=None, callback=None, **args):
    # add an option to the diag command line interface
    # currently three options are supported [simple, all]
    # simple -- just collect the currently used checkpoint files
    # all -- collect the hot and backup checkpoint files
    parser.add_option("--checkpoint", dest="checkpoint")


def collect_diag_info(diag, options=None, global_options=None, app_dir=None, **args):
    logging.info("start to collect DB Connect checkpoint files")

    checkpoint_src_dir = os.path.join(os.environ['SPLUNK_HOME'], 'var', 'lib', 'splunk', 'modinputs', 'server',
                                      'splunk_app_db_connect')
    dirpath = tempfile.mkdtemp()
    try:
        checkpoint_dest_dir = 'checkpoint_files'
        diag.add_dir(dirpath, checkpoint_dest_dir)
        if options.checkpoint is None:
            simple_collect(diag, checkpoint_src_dir, checkpoint_dest_dir)
        elif options.checkpoint.lower() == 'simple':
            simple_collect(diag, checkpoint_src_dir, checkpoint_dest_dir)
        elif options.checkpoint.lower() == 'all':
            all_collect(diag, checkpoint_src_dir, checkpoint_dest_dir)
        else:
            simple_collect(diag, checkpoint_src_dir, checkpoint_dest_dir)
    finally:
        os.removedirs(dirpath)


def simple_collect(diag, checkpoint_src_dir, checkpoint_dest_dir):
    logging.info("collect checkpoint files in mode simple!")
    logging.info('collect hot checkpoint files')
    files = os.listdir(checkpoint_src_dir)
    for f in files:
        if not os.path.isdir(f) and not f.endswith("bak"):
            diag.add_file(os.path.join(checkpoint_src_dir, f), os.path.join(checkpoint_dest_dir, f))


def all_collect(diag, checkpoint_src_dir, checkpoint_dest_dir):
    logging.info("collect checkpoint files in mode all!")
    logging.info('collect hot and cold checkpoint files')
    files = os.listdir(checkpoint_src_dir)
    for f in files:
        if not os.path.isdir(f):
            diag.add_file(os.path.join(checkpoint_src_dir, f), os.path.join(checkpoint_dest_dir, f))


