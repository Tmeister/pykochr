import os
from google.appengine.api import mail

class Notification:
	def send(self, to, title, content):
		template = self.get_template()
		domain   = self.get_domain()
		template = template.replace( "%_url_%", domain )
		template = template.replace( "%_title_mail_%", title )
		template = template.replace( "%_content_%", content )

		mail = mail.EmailMessage(sender="Kochster <contact@kochster.com>",subject=title)
		mail.to = to
		mail.body = content
		mail.html = template
		mail.send()


	def get_template(self):
		path = '%s/templates/email.html' % ( os.getcwd() )
		f = open(path, 'r')
		return f.read()

	def get_domain(self):
		port = ':8080' if os.environ['SERVER_NAME'] == 'localhost' else ''
		return 'http://%s%s' % ( os.environ['SERVER_NAME'], port )