#!/usr/bin/env python

# tile-generator
#
# Copyright (c) 2015-Present Pivotal Software, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function
import click
import sys
import yaml
import os
import types
from . import build
from . import template
from . import config
from .config import Config

@click.group()
def cli():
	pass

@cli.command('init')
@click.argument('name', nargs=1, required=False)
def init_cmd(name):
	dir = '.'
	if name is not None:
		dir = name
		os.mkdir(name)
		os.chdir(name)
	if os.path.isfile(config.CONFIG_FILE):
		print('Already initialized.', file=sys.stderr)
		sys.exit(0)
	name = os.path.basename(os.getcwd())
	template.render(config.CONFIG_FILE, config.CONFIG_FILE, { 'name': name })
	template.render('.gitignore', 'gitignore', {})
	print('Generated initial tile files; begin by customizing "{}/tile.yml"'.format(dir))

@cli.command('build')
@click.argument('version', 'patch', required=False)
@click.option('--verbose', is_flag=True)
@click.option('--sha2', is_flag=True)
@click.option('--docker-cache', '--cache', type=str, default=None)
def build_cmd(version, verbose,sha2, cache):
	cfg = Config().read()

	if type(sha2) is not types.BooleanType:
		if sha2 == 'false':
			sha2 = False
		else:
			sha2 = True
	cfg.set_version(version)
	cfg.set_verbose(verbose)
	cfg.set_sha2(sha2)
	cfg.set_cache(cache)
	print('name:', cfg.get('name', '<unspecified>'))
	print('icon:', cfg.get('icon_file', '<unspecified>'))
	print('label:', cfg.get('label', '<unspecified>'))
	print('description:', cfg.get('description', '<unspecified>'))
	print('version:', cfg.get('version', '<unspecified>'))
	print('sha2:', cfg.get('sha2', '<unspecified>'))
	stemcell = cfg.get('stemcell_criteria', {})
	print('stemcell:', stemcell.get('os', '<unspecified>'), stemcell.get('version', '<unspecified>'))
	print()
	build.build(cfg)
	cfg.save_history()

@cli.command('expand')
@click.argument('version', 'patch', required=False)
def expand_cmd(version):
	cfg = Config().read()
	cfg.set_version(version)
	config.write_yaml(sys.stdout, dict(cfg))

if __name__ == "__main__":
	cli()
