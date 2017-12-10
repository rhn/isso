#!/home/.rhn_slow/play/marginalia/isso_install/bin/python3

# -*- coding: utf-8 -*-
import re
import sys

from isso import main
import isso
print(isso)

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
