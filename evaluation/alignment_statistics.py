import matching.utilities as utl
import os
from matching.defaultvalues import *
import json

""" Prints the number of aligned sentences
"""

website_hashes = utl.get_website_hashes()
counter = {}
sentences = 0
for website in website_hashes:
    counter[website] = 0
    for hash in website_hashes[website]:
        path = f"results/alignment/{hash}.normal"
        if os.path.exists(path):
            with open(path) as fp:
                lines = fp.readlines()
                counter[website] += len(lines)
                sentences += len(lines)
        # else:
        #     print(f"Not found {hash}")
    print(f"{website} = {counter[website]} sentences")

print(f"Overall sentences: {sentences}")