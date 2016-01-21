#
# Cookbook Name:: vt-sailbot
# Recipe:: default
#

# Installs the core SailBOT packages / dependencies
package [
  'build-essential',
  'python3-dev',
  'python-dev',
  'python-setuptools',
  'python-smbus',
  'python-pip'
  ]  do
  action :install
end

# Update the system clock
bash 'Update system clock' do
  code <<-EOH
    /usr/bin/ntpdate -b -s -u pool.ntp.org;
    EOH
end

# Installs optional, depencency packages
if node.chef_environment == "dev"
  package ['telnet', 'tree', 'vim']  do
    action :install
  end

  bash 'Install IPython' do
    code <<-SCRIPT
      sudo pip3 install ipython;
      SCRIPT
  end
end

# Installs the web server
bash 'Install Tornado Web Server' do
  code <<-SCRIPT
    sudo pip3 install tornado;
    SCRIPT
end

# Installs Adafruit Servo packages
bash 'Install Adafruit Servo packages' do
  code <<-SCRIPT
    sudo pip3 install Adafruit_BBIO;
    sudo pip install Adafruit_BBIO;
    SCRIPT
end
