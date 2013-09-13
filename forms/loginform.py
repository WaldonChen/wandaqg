import pygtk
pygtk.require('2.0')
import gtk

class LoginForm:
	def __init__(self, verifyimg):
		label = gtk.Label("Input the verify code for login:")
		hbox1 = gtk.HBox(False, 3)
		img_holder = gtk.Image()
		img_holder.set_from_file(verifyimg)
		self.verifycode_entry = gtk.Entry(4)
		hbox1.pack_start(img_holder)
		hbox1.pack_start(self.verifycode_entry)

		vbox1 = gtk.VBox(False, 10)
		vbox1.pack_start(label)
		vbox1.pack_start(hbox1)

		self.dialog = gtk.Dialog("Input Verify Code:",
					None,
					gtk.DIALOG_MODAL,
					(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		self.dialog.vbox.pack_start(vbox1)
		vbox1.show_all()
		self.dialog.resize(120, 160)
		self.verifycode_entry.connect('key_press_event',
				self.on_verifycode_entry_keypress)

	def on_verifycode_entry_keypress(self, widget, event):
		if gtk.gdk.keyval_name(event.keyval) == 'Return':
			self.dialog.response(gtk.RESPONSE_ACCEPT)

	def run(self):
		self.response = self.dialog.run()

	def get_verifycode(self):
		ret = self.verifycode_entry.get_text()
		self.dialog.destroy()
		return ret

def GetVerifycode(verifyimg):
	login_form = LoginForm(verifyimg)
	login_form.run()
	ret = login_form.get_verifycode()
	return ret
