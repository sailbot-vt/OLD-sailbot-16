#
# Cookbook Name:: vt-sailbot
# Recipe:: default
#

include_recipe 'apt'

# Installs the core SailBOT packages / dependencies
package [
  'build-essential',
  'python3-dev',
  'gpsd',
  'gpsd-clients',
  'python-gps',
  'i2c-tools',
  'python-smbus',
  'python3-pip',
  'libgps-dev'
  ]  do
  action :install
end

# Installs optional, depencency packages
if node.chef_environment == "dev"
  package ['telnet']  do
    action :install
  end

  bash 'Install IPython' do
    code <<-EOH
      sudo pip3 install ipython
      EOH
  end
end

# Installs the web server
bash 'Install Tornado Web Server' do
  code <<-EOH
    sudo pip3 install tornado
    EOH
end
