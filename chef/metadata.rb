name 'vt-sailbot'
license 'MIT'
description 'Installs/Configures resources on the Raspberry Pi to run SailBOT code'
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version '0.1.0'

%w(ubuntu debian).each do |os|
  supports os
end

depends 'apt'
