# -*- coding: utf-8 -*-
"""Recipe apachevhosts"""

from datetime import datetime
import logging
import os


default_template = """
#
#
# DO NOT MODIFY THIS BY HAND
# AUTOMATICALLY GENERATED DURING BUILDOUT
# YOUR CHANGES *WILL* BE LOST
#
# Buildout dir: %(buildout)s
# Buildout part: %(part)s
# Last update:  %(timestamp)s
#
#  listenaddress= * 
#  serveradmin  = webmaster@yourdomain.com 
#  absdir       = /http/sites/sitename
#  url          = mysite.com  
#  reldir       = /http/sites/sitename 
#  urlaliases   = www.mysite.com other.sitename.com www.other.sitename.com 
#      
#  ProxyRequets = Off  
#  ProxyPath    = http://%(httpaddress)s/VirtualHostBase/http/%(url)s:80%(path)s/VirtualHostRoot/
#  ProxyPathRev = http://%(httpaddress)s/VirtualHostBase/http/%(url)s:80%(path)s/VirtualHostRoot/ 
# 
#  script-alias
#               /cgi-bin   %(absdir)s/cgi-bin 
#               /cgibin    %(absdir)s/cgibin 
#               /cgitools  %(absdir)s/cgitools 
  

Listen %(listenaddress)s:80

<VirtualHost %(listenaddress)s>
ServerAdmin %(serveradmin)s
DocumentRoot %(absdir}%/htdocs
ServerName %(url)s 

ProxyRequests Off
<Proxy *>
  Order deny,allow
  Allow from all
</Proxy>


ProxyPass / %(proxypath)s
ProxyPassReverse / %(ProxyPathRev)s 



ErrorLog %(reldir)s/logs/error_log
CustomLog %(reldir)s/logs/access_log custom
ScriptAlias /cgi-bin %(absdir)s/cgi-bin
ScriptAlias /cgibin %(absdir)s/cgibin
ScriptAlias /cgibin/12 %(absdir)s/cgibin/12
ErrorDocument 404 http://%(servername)s

<Directory %(reldir)s/htdocs>
AddType application/x-httpd-php .php3
Options +Includes
</Directory>

    <Directory />
        Options FollowSymLinks
        AllowOverride None
    </Directory>


</VirtualHost>



<VirtualHost *:80>
    ServerName %(url)s
    %(urlalias)s

    ProxyRequests Off
    <Proxy *>
        Order deny,allow
        Allow from all
    </Proxy>

    ProxyPass / http://%(httpaddress)s/VirtualHostBase/http/%(url)s:80%(path)s/VirtualHostRoot/
    ProxyPassReverse / http://%(httpaddress)s/VirtualHostBase/http/%(url)s:80%(path)s/VirtualHostRoot/

    <Directory />
        Options FollowSymLinks
        AllowOverride None
    </Directory>

</VirtualHost>

"""

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(name)

    def install(self):
        """Installer"""
        return self.writeVhosts()

    def update(self):
        """Updater"""
        return self.writeVhosts()
        
    def writeVhosts(self):
        files = []
        vhosts = self.options['vhosts']
        httpaddress =  self.options['http-address']
        outputdir = self.options['outputdir']
        prefix = self.options.get('prefix')
        postfix = self.options.get('postfix')
        template = self.options.get('template')
        scriptalias = self.options.get('script-alias') 
        absdir = self.options.get('absdir') 

        listenaddress= self.options.get('listenaddress') 
        serveradmin  = self.options.get('serveradmin') 
        url          = self.options.get('url') 
        reldir       = self.options.get('reldir') 
        ProxyRequests= self.options.get('ProxyRequests') 
        ProxyPath    = self.options.get('ProxyPath')
        ProxyPathRev = self.options.get('ProxyPathRev') 

#
#  script-alias
#               /cgi-bin   %(absdir)s/cgi-bin
#               /cgibin    %(absdir)s/cgibin
#               /cgitools  %(absdir)s/cgitools



        localscriptalias = '' 

        for line in scriptalias.split('\n'): 
            if len(line.split()):
               publicpath, localpath = line.split() 
               localscriptalias = localscriptalias + 'ScriptAlias /%s %s/%s' % ( publicpath, absdir, localpath ) 
                

        for line in vhosts.split('\n'):
            if len(line.split()):
        	site, path, url = line.split()
        	if prefix is not None:
        	    url = "%s.%s" % (prefix, url)
        	if postfix is not None:
        	    url = "%s.%s" % (site, postfix)
        	    
        	values = dict()
        	values['buildout'] = self.buildout['buildout']['directory']
        	values['httpaddress'] = httpaddress
        	values['site'] = site
        	values['path'] = path
        	values['url'] = url
        	values['part'] = self.name
        	values['timestamp'] = str(datetime.now())[0:16]
        	
        	# Provide non-'www.' alias directive
        	if url[0:4] == 'www.':
        	    values['urlalias'] = 'ServerAlias %s' % url[4:]
        	else:
        	    values['urlalias'] = ""
        	
        	# Use provided template or default
        	if template is None:
        	    template = default_template
        	filename = os.path.join(outputdir, "%s.conf" % site)
        	files.append(filename)
        	out = open(filename, "w")
        	out.write(template % values)
        	out.close()

        return files

