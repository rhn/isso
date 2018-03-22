import qrcode
import sys

from gensite import *

def generate(srcpath, dstpath):
    config = yaml.load(open(os.path.join(srcpath, 'config.yaml')).read())
    with open_db(config["db_path"]) as session:
        for access in session.query(Access):
            qr = qrcode.QRCode(version=3,
                               error_correction=qrcode.constants.ERROR_CORRECT_M,
                               box_size=1, border=0)
            text = '{site_url}/{post_path}/{key}'.format(key=access.key, **config)
            print(text)
            qr.add_data(text)
            qr.make()
            img = qr.make_image()
            img.save(os.path.join(dstpath, access.uri + '.png'))
            open(os.path.join(dstpath, access.uri + '.txt'), 'w').write(access.key)
            # TODO: generate whole SVG
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("sourcepath")
    parser.add_argument("destpath")
    args = parser.parse_args()
    generate(args.sourcepath, args.destpath)
