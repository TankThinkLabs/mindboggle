#!/usr/bin/python
"""
Use FreeSurfer to register a subject's brain surfaces to a template.

Command: python <this file name>
                <FreeSurfer subject directory>
                <template directory> <template name>

Example: python surfaces_to_template.py
                /Applications/freesurfer/subjects/bert
                ./templates_freesurfer/  KKI
         ("KKI" above refers to, for example, "lh.KKI.tif")

This program uses FreeSurfer's mris_register:
mris_register [options] <surface> <target template/surface> <output surface>

Authors:  Arno Klein  .  arno@mindboggle.info  .  www.binarybottle.com

(c) 2011  Mindbogglers (www.mindboggle.info), under Apache License Version 2.0

"""

import sys
import os

# Check inputs
if len(sys.argv) == 4:
    subject_path = sys.argv[1] + '/'
    average_template_path = sys.argv[2] + '/'
    average_template_name = sys.argv[3]
else:
    print("Please check your command-line arguments.")
    sys.exit()

output_path = subject_path 
if os.path.exists(subject_path) and os.path.exists(average_template_path):
    pass
else:
    print(subject_path + ', ' + output_path + ', or ' + \
          average_template_path + " doesn't exist.")
    sys.exit()

for h in ['lh','rh']:
    average_template_file = average_template_path + h + '.' + \
                            average_template_name + '.tif'
    if not os.path.exists(average_template_file):
        print(average_template_file + " doesn't exist.")
        sys.exit()
    else:
        args = ['mris_register -curv',
                subject_path + '/surf/' + h + '.sphere',
                average_template_file,
                subject_path + '/surf/' + h + '.sphere_to_template.reg']
        print(' '.join(args)); os.system(' '.join(args)); # p = Popen(args);