#!/usr/bin/env python

'''


Author: Bipin Bachhao (bipinbachhao@gmail.com)

Copyright 2017 Bipin Bachhao (bipinbachhao@gmail.com)

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

'''

import argparse
import os
import shutil
import sys
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


image_dir_path = os.getcwd()
image_file_name = 'image_input'
templates_dir = os.path.join(os.getcwd(), 'templates')
ks_template_name = 'kickstart.template'


time_now = datetime.now()
timestamp = '.%s' % (time_now.strftime('%Y%m%d_%H%M%S'),)


def main():
    print 'Hello there this is the first line of this code'


def write_input_file(server_specs):
    for s in server_specs.servers:
        server_image_dir = os.path.join(image_dir_path, '%s.%s' % (s, server_specs.domain))
        inputfile = os.path.join(server_image_dir, image_file_name)
        if os.path.isdir(server_image_dir):
            if os.path.lexists(inputfile):
                print 'found existing image_ksinput, backing up! '
                os.rename(inputfile, inputfile + timestamp)
        else:
            os.mkdir(server_image_dir)
        with open(inputfile, 'a') as myinputfile:
            myinputfile.write('''
IMAGETYPE=%(imagetype)s
OS=%(os)s

# Partition information
BOOT=%(boot)s
ROOT=%(root)s
VAR_PART=%(var)s
TMP=%(tmp)s
SWAP=%(swap)skickstart jinja2 python templatecd g

# Host information
HOST=%(host)s
DOMAIN=%(domain)s
IP=%(ip)s
NM=%(netmask)s
GW=%(gateway)s
            '''%{
                'imagetype': server_specs.image,
                'os': server_specs.release,
                'boot': server_specs.boot_part,
                'root': server_specs.root_part,
                'var': server_specs.var_part,
                'tmp': server_specs.tmp_part,
                'swap': server_specs.swap_part,
                'host': s,
                'domain': server_specs.domain,
                'ip': server_specs.ipaddr,
                'netmask': server_specs.netmask,
                'gateway': server_specs.gateway,
            }
                              )

def keypair_convert(file_loc):
    myvars = {}
    with open(file_loc) as myfile:
        for line in myfile:
            tmp_line = line.rstrip()
            if not tmp_line.startswith("#"):
                name, var = line.partition("=")[::2]
                myvars[name.strip()] = var.strip()
    return myvars


def write_kickstart_file(server_specs):
    print "Printing fist line inside write_kickstart_file function"
    for s in server_specs.servers:
        server_image_dir = os.path.join(image_dir_path, '%s.%s' % (s, server_specs.domain))
        ksfile = os.path.join(server_image_dir, image_file_name)
        ks_environment = Environment(loader=FileSystemLoader(templates_dir))
        ks_template = ks_environment.get_template(ks_template_name)
    if os.path.exists(server_image_dir):
        if os.path.exists(post_install_scripts_path):
            if os.path.lexists(os.path.join(post_install_scripts_path, 'chef-client-installer.sh')):
                shutil.copy2(os.path.join(post_install_scripts_path, 'chef-client-installer.sh'), server_image_dir)
    else:
        print 'Server image Dir does not exists. Exiting: %s' % server_image_dir
        sys.exit()


# Standard boilerplate to call the main() function to begin
# the program

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pass the arguments to pass the information to create kickstart file')
    parser.add_argument('-r', '--release', required=True, help='OS Release version, rhel 6.7')
    parser.add_argument('-i','--image', default='physical', help='Image type either VM, physical, Box. Default=physical')
    parser.add_argument('-s', '--servers', nargs='+', required=True)
    parser.add_argument('-c', '--create', action='store_true', help='Create a kickstart file, boot image or box image')
    parser.add_argument('-d', '--domain', default='example.com', help='Domain of the server. Default: example.com')
    parser.add_argument('-ip', '--ipaddr', default='10.10.0.99')
    parser.add_argument('-nm', '--netmask', default='255.255.255.0', help='Netmask for the server. Default: 255.255.255.0')
    parser.add_argument('-gw', '--gateway', default='10.10.0.1', help='Gateway for the server')
    parser.add_argument('-rp', '--root-part', default='20480', help='Custom root partition size. Default: 20480')
    parser.add_argument('-bp', '--boot-part', default='300', help='Custom boot partition size. Default: 300')
    parser.add_argument('-vp', '--var-part', default='20480', help='Custom var partition size. Default: 20480')
    parser.add_argument('-sp', '--swap-part', default='2048', help='Custom swap partition size. Default: 2048')
    parser.add_argument('-tp', '--tmp-part', default='20480', help='Custom tmp parition size. Default:20480')

    args = parser.parse_args()

    print 'Servers to Build:'
    for ser in args.servers:
        print '  %s.%s' % (ser, args.domain)
    print 'OS Release: %s' % args.release
    print 'Image Type: %s' % args.image
    print 'Create kickstart Files: %s' % args.create
    print 'Domain For the Server: %s' % args.domain
    print 'IP Address of the Server: %s' % args.ipaddr
    print 'Netmask for the Server: %s' % args.netmask
    print 'Gateway for the Server: %s' % args.gateway
    print 'Root partition size: %s' % args.root_part
    print 'Boot partution size: %s' % args.boot_part
    print 'Var partition size: %s' % args.var_part
    print 'SWAP partition size: %s' % args.swap_part
    print 'TMP partition size: %s' % args.tmp_part
    main()
    write_input_file(args)
