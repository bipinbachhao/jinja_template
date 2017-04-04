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
post_install_scripts_path = os.path.join(os.getcwd(), 'post_install_scripts')


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
                print 'found existing image_input, backing up! '
                os.rename(inputfile, inputfile + timestamp)
        else:
            os.mkdir(server_image_dir)
        with open(inputfile, 'a') as myinputfile:
            myinputfile.write('''
OS=%(os)s
RELEASE=%(release)s
MAJOR_RELEASE=%(major_release)s
MIN_RELEASE=%(min_release)s
SELINUX=%(selinux)s
WORKSTATION=%(workstation)s
# Partition information
BOOT=%(boot)s
ROOT=%(root)s
VAR_PART=%(var)s
TMP=%(tmp)s
SWAP=%(swap)s
# Host information
HOST=%(host)s.%(domain)s
DOMAIN=%(domain)s
IP=%(ip)s
NM=%(netmask)s
GW=%(gateway)s
DHCP=%(dhcp)s
ROOTPASSWD=%(rootpasswd)s
TIMEZONE=%(timezone)s
            '''%{
                'release': server_specs.release,
                'os': server_specs.os_name,
                'major_release': str(server_specs.release).split('.')[0],
                'min_release': str(server_specs.release).split('.')[1],
                'selinux': server_specs.enable_selinux,
                'workstation': server_specs.workstation,
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
                'dhcp': server_specs.dhcp,
                'rootpasswd': server_specs.root_passwd,
                'timezone': server_specs.timezone,
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
        inputfile = os.path.join(server_image_dir, image_file_name)
        kscfg_file = os.path.join(server_image_dir, 'ks.cfg')
        ks_environment = Environment(loader=FileSystemLoader(templates_dir))
        ks_template = ks_environment.get_template(ks_template_name)
        if os.path.exists(server_image_dir):
            if os.path.exists(post_install_scripts_path):
                if os.path.lexists(os.path.join(post_install_scripts_path, 'chef-client-installer.sh')):
                    shutil.copy2(os.path.join(post_install_scripts_path, 'chef-client-installer.sh'), server_image_dir)
            else:
                print 'Post install scripts directory does not exists Exiting: %s' % post_install_scripts_path
                sys.exit()
        else:
            print 'Server image Dir does not exists. Exiting: %s' % server_image_dir
            sys.exit()
        server_input = keypair_convert(inputfile)
        with open(kscfg_file, 'w') as kscfg_output:
            kscfg_output.write(ks_template.render(**server_input))


# Standard boilerplate to call the main() function to begin
# the program

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pass the arguments to pass the information to create kickstart file')
    parser.add_argument('-r', '--release', required=True, type=float, help='OS Release version, rhel 6.7')
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
    parser.add_argument('-os', '--os-name', default='centos', help='OS name Default: centos')
    parser.add_argument('--dhcp', action='store_true', default=False, help='Use DHCP')
    parser.add_argument('--timezone', default='America/Indiana/Indianapolis',
                        help='Default: America/Indiana/Indianapolis')
    parser.add_argument('--enable-selinux', action='store_true', default=False, help='Enable SELinux, Default: False')
    parser.add_argument('--root-passwd', default='$5$CurWicWfoFibljY$r4SwMWFh.Fd7Z7HEA2xncS2dQ3XaqR.T.VyCFaF/Vv0', help='Root Password Hash- Reset@12345')
    parser.add_argument('--workstation', action='store_true', default=False,
                        help='If its a Workstation. Default: False, This will be server')

    args = parser.parse_args()

    print 'Servers to Build:'
    for ser in args.servers:
        print '  %s.%s' % (ser, args.domain)
    print 'OS Release: %s' % args.release
    print 'Create kickstart Files: %s' % args.create
    print 'Domain For the Server: %s' % args.domain
    print 'IP Address of the Server: %s' % args.ipaddr
    print 'NetMask for the Server: %s' % args.netmask
    print 'Gateway for the Server: %s' % args.gateway
    print 'Root partition size: %s' % args.root_part
    print 'Boot partition size: %s' % args.boot_part
    print 'Var partition size: %s' % args.var_part
    print 'SWAP partition size: %s' % args.swap_part
    print 'TMP partition size: %s' % args.tmp_part
    print 'OS Name: %s' % args.os_name
    print 'DHCP: %s' % args.dhcp
    print 'TimeZone: %s' % args.timezone
    print 'Enable SELinux: %s' % args.enable_selinux
    print 'WorkStation: %s' % args.workstation
    main()
    write_input_file(args)
