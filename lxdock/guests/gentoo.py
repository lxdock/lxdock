from .base import Guest


class GentooGuest(Guest):
    """ This guest can provision Gentoo containers. """

    name = 'gentoo'

    def install_packages(self, packages):
        # Ensure that we have this Gentoo helper toolkit.
        # It contains "equery" that can check which package has been installed.
        self.run(['emerge', 'app-portage/gentoolkit'])
        for p in packages:
            retcode = self.run(['equery', 'list', p])
            if retcode != 0:  # Not installed yet
                self.run(['emerge', p])
