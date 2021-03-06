from flask import Flask, render_template, send_file
import os
import os.path
import requests
import urllib2

DEBUG = os.environ.get('DEBUG', 'True') == 'True'
DOCVERTER_URL =   'http://c.docverter.com/convert'
FILES_FOLDER = 'files'
if not os.path.exists(FILES_FOLDER):
    os.mkdir(FILES_FOLDER)
DEFAULT_TEXT = u"# Example\nThis is an example of a markdown document!".encode('utf8')

app = Flask(__name__)
app.config.from_object(__name__)  
if app.debug:
	print " * Running in debug mode"

def docverter(filename, from_format="markdown", to_fromat="pdf"):
    print 'Sending request to Docverter for file', filename
    r = requests.post(app.config['DOCVERTER_URL'], data={'to':to_fromat,'from':from_format},files={'input_files[]':open(filename,'rb')})
    if r.ok:
        outname = '.'.join(filename.split('.')[:-1] + [to_fromat] ) 
        fout = open(outname, 'wb')
        fout.write(r.content)
        fout.close()
        return outname
    else:
        print 'Request failed:', r.status_code
        return ''

def path_to_file(filename):
    return FILES_FOLDER + os.path.sep + filename

def save_text_file(filename, content):
    filepath = path_to_file(filename)
    f = open(filepath, 'w')
    f.write(content)
    f.close()
    return filepath

@app.route("/")
def index():
    return render_template("index.html", content=app.config['DEFAULT_TEXT'])

@app.route("/edit/<string:content>")
def edit(content):
    return render_template("index.html", content=content)

@app.route("/convert/<string:from_format>/<string:to_format>/<string:content>")
def convert(from_format, to_format, content):
    content = urllib2.unquote(content).decode('utf8')
    content = content.replace("+"," ")
    print content
    infile = save_text_file("tmp." + from_format, content)
    outfile = docverter(infile, from_format, to_format)
    if outfile:
        return send_file(outfile)
    else:
        return "Conversion failed"

if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5005))
	app.run(host='0.0.0.0', port=port, debug=app.debug)
