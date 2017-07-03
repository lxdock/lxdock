import logging
import shlex
from pathlib import Path, PurePosixPath

from voluptuous import All, IsDir, IsFile

from ..exceptions import ProvisionFailed
from .base import Provisioner


__all__ = ('PuppetProvisioner', )

logger = logging.getLogger(__name__)


def finalize_options(options):
    # Refs Vagrant code:
    # https://github.com/mitchellh/vagrant/blob/9c299a2a357fcf87f356bb9d56e18a037a53d138/
    #         plugins/provisioners/puppet/config/puppet.rb#L58
    if options.get('environment_path') is None and options.get('manifests_path') is None:
        logger.warn("environment_path and manifests_path are both unset, "
                    "assuming manifests mode and manifests_path as 'manifests'...")
        options['manifests_path'] = 'manifests'

    if options.get('environment_path') is None:
        if options.get('manifest_file') is None:
            logger.warn("manifest_file is not set. Assuming 'default.pp'...")
            options['manifest_file'] = 'default.pp'
    else:
        if options.get('environment') is None:
            logger.warn("environment is not set. Assuming 'production'...")
            options['environment'] = 'production'

    return options


def validate_paths(options):
    # Refs Vagrant code:
    # https://github.com/mitchellh/vagrant/blob/9c299a2a357fcf87f356bb9d56e18a037a53d138/
    #         plugins/provisioners/puppet/config/puppet.rb#L112
    if options.get('manifests_path') is not None:
        host_manifest_file = str(
            Path(options['manifests_path']) / options['manifest_file'])
        IsFile(msg="File {} does not exist".format(host_manifest_file))(host_manifest_file)
    elif options.get('environment_path') is not None:
        host_selected_environment_path = str(
            Path(options['environment_path']) / options['environment'])
        IsDir(msg="Directory {} does not exist".format(host_selected_environment_path))(
            host_selected_environment_path)
    return options


class PuppetProvisioner(Provisioner):
    """ Allows to perform provisioning operations using Puppet. """

    name = 'puppet'

    guest_required_packages_arch = ['puppet']
    guest_required_packages_debian = ['puppet']
    guest_required_packages_fedora = ['puppet']
    guest_required_packages_ubuntu = ['puppet']

    # Refs Vagrant docs:
    # https://www.vagrantup.com/docs/provisioning/puppet_apply.html#options
    schema = All({
        'binary_path': str,
        'facter': dict,
        'hiera_config_path': IsFile(),
        'manifest_file': str,
        'manifests_path': IsDir(),
        'module_path': IsDir(),
        'environment': str,
        'environment_path': IsDir(),
        'environment_variables': dict,
        'options': str,
    }, finalize_options, validate_paths)

    _guest_manifests_path = '/.lxdock.d/puppet/manifests'
    _guest_module_path = '/.lxdock.d/puppet/modules'
    _guest_default_module_path = '/etc/puppet/modules'
    _guest_environment_path = '/.lxdock.d/puppet/environments'
    _guest_hiera_file = '/.lxdock.d/puppet/hiera.yaml'

    def provision_single(self, guest):
        """ Performs the provisioning operations using puppet. """
        # Verify if `puppet` has been installed.
        binary_path = self.options.get('binary_path')
        if binary_path is not None:
            puppet_bin = str(PurePosixPath(binary_path) / 'puppet')
            retcode = guest.run(['test', '-x', puppet_bin])
            fail_msg = (
                "puppet executable is not found in the specified path {} in the "
                "guest container. ".format(binary_path)
            )
        else:
            retcode = guest.run(['which', 'puppet'])
            fail_msg = (
                "puppet was not automatically installed for this guest. "
                "Please specify the command to install it in LXDock file using "
                "a shell provisioner and try `lxdock provision` again. You may "
                "also specify `binary_path` that contains the puppet executable "
                "in LXDock file.")
        if retcode != 0:
            raise ProvisionFailed(fail_msg)

        # Copy manifests dir
        manifests_path = self.options.get('manifests_path')
        if manifests_path is not None:
            guest.copy_directory(
                Path(manifests_path), PurePosixPath(self._guest_manifests_path))

        # Copy module dir
        module_path = self.options.get('module_path')
        if module_path is not None:
            guest.copy_directory(Path(module_path), PurePosixPath(self._guest_module_path))

        # Copy environment dir
        environment_path = self.options.get('environment_path')
        if environment_path is not None:
            guest.copy_directory(
                Path(environment_path), PurePosixPath(self._guest_environment_path))

        # Copy hiera file
        hiera_file = self.options.get('hiera_config_path')
        if hiera_file is not None:
            guest.copy_file(Path(hiera_file), PurePosixPath(self._guest_hiera_file))

        # Run puppet.
        command = self._build_puppet_command()

        if environment_path:
            logger.info("Running Puppet with environment {}...".format(self.options['environment']))
        else:
            logger.info("Running Puppet with {}...".format(self.options['manifest_file']))

        guest.run(['sh', '-c', ' '.join(command)])

    ##################################
    # PRIVATE METHODS AND PROPERTIES #
    ##################################

    def _build_puppet_command(self):
        """
        Refs:
        https://github.com/mitchellh/vagrant/blob/9c299a2a357fcf87f356bb9d56e18a037a53d138/
                plugins/provisioners/puppet/provisioner/puppet.rb#L173
        """

        options = self.options.get('options', '')
        options = list(map(shlex.quote, shlex.split(options)))

        module_path = self.options.get('module_path')
        if module_path is not None:
            options += ['--modulepath',
                        '{}:{}'.format(self._guest_module_path,
                                       self._guest_default_module_path)]

        hiera_path = self.options.get('hiera_config_path')
        if hiera_path is not None:
            options += ['--hiera_config={}'.format(self._guest_hiera_file)]

        # TODO: we are not detecting console color support now, but please contribute if you need!

        options += ['--detailed-exitcodes']

        environment_path = self.options.get('environment_path')
        if environment_path is not None:
            options += ['--environmentpath', str(self._guest_environment_path),
                        '--environment', self.options['environment']]
        else:
            options += ['--manifestdir', str(self._guest_manifests_path)]

        manifest_file = self.options.get('manifest_file')
        if manifest_file is not None:
            options += [str(
                PurePosixPath(self._guest_manifests_path) / manifest_file)]

        # Build up the custom facts if we have any
        facter = []
        facter_dict = self.options.get('facter')
        if facter_dict is not None:
            for key, value in sorted(facter_dict.items()):
                facter.append("FACTER_{}={}".format(key, shlex.quote(value)))

        binary_path = self.options.get('binary_path')
        if binary_path is not None:
            puppet_bin = str(PurePosixPath(binary_path) / 'puppet')
        else:
            puppet_bin = 'puppet'

        # TODO: working_directory for hiera. Please contribute!

        env = []
        env_variables = self.options.get('environment_variables')
        if env_variables is not None:
            for key, value in sorted(env_variables.items()):
                env.append("{}={}".format(key, shlex.quote(value)))

        command = env + facter + [puppet_bin, 'apply'] + options

        return command
