# TEMPLATES
# --

INIT_LXDOCK_FILE_CONTENT = """# This is a basic configuration file for LXDock.
# All configuration is done through this YML file that should be placed at the root of your project.
# The file define a basic LXDock project containing a single container with highlights regarding
# some other useful options.
name: {project_name}
image: {image}

# By default LXDock creates a single "default" container if you don't specify a "containers" option.
# But you need the "containers" option if you have more than one container.

# containers:
#   - name: {project_name}01
#   - name: {project_name}02
#   - name: {project_name}02
#     Most of the options can be redefined for each container definition, eg. the "image" option:
#     image: archlinux

# You can use the "provisioning" option to define provisioning tools that should be used to
# provision your containers. For example, you could use Ansible as follows:
# provisioning:
#   - type: ansible
#     playbook: deploy/site.yml

# A common need is to access your project folder in your containers. To do this you can use the
# "shares" option:
# shares:
#   - source: .
#     dest: /myshare
"""
