from flask import Flask, render_template
from flask_ask import Ask, request, statement, question, session, context
from intent import *
import datetime
from self_healing import *
import subprocess
import time

app = Flask(__name__)
ask = Ask(app, "/capstone")

# Homepage for GUI
@app.route("/")
def homepage():
   h= """
   <body>
    <a href="intents" class="button">Intents</a>    
    <a href="security" class="button">Security</a>    
    <a href="self_gui" class="button">Self-Healing</a>  <br/></div>
   </body>
  </html>
    """
   return render_template("home.html") + h 


# List of Intents on GUI
@app.route('/intents')
def intents():
    h = """
       <body>
        <a href="ospf_gui" class="button">Configure OSPF</a>  <br/> 
        <a href="hostname_gui" class="button">Configure Hostname</a>  <br/>  
        <a href="github_gui" class="button">Back NSOT to GITHUB</a>  
        <br/> <a href="pushflow_gui" class="button">Push Flow Entries</a> <br/>  
        <a href="dis_gui" class="button">Show disconnected switches</a> <br/> 
        <a href="down_gui" class="button">Show down interface</a> </div> 
       </body>
      </html>
        """
    return render_template("home.html")+h


# OSPF Intent for GUI
@app.route('/ospf_gui')
def ospf_gui():
   helper_ospf()
   return "Configured OSPF"


# Hostname Intent for GUI
@app.route('/hostname_gui')
def hostname_gui():
   helper_hostname()
   return "Configured Hostname"


# Backup to Github Intent for GUI
@app.route('/github_gui')
def github_gui():
   helper_github()
   return "Pushed Files to GitHub on GMT {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# Push Flow Entries Intent for GUI
@app.route('/pushflow_gui')
def pushflow_gui():
   helper_pushfe()
   return "Pushed flow entries"


# Show Disconnected Swtiches Intent for GUI
@app.route('/dis_gui')
def dis_gui():
   a = sdn_disconnected_sw()
   return a


# Show Down Interfaces Intent for GUI
@app.route('/down_gui')
def down_gui():
   a = helper_shut()
   return a


# Start Selfhealing for GUI
@app.route('/self_gui')
def self_gui():
   helper_sf()
   return "Done self healing"


# Start Security Module for GUI
@app.route('/security')
def security():
    helper_security()
    return "Security module started on the SDN Controller"


# To Check ROBOT Logs on GUI
@app.route('/robot')
def robot():
    f= open("templates/log.html", "r").read()
    return f


# Welcome Messege on Alexa
@ask.launch
def start_skill():
   welcome_message = 'Welcome to SNS, what would you like to configure?'
   return question(welcome_message)


# Hostname Intent for Alexa
@ask.intent("HostIntent")
def host_headlines():
   hi_text = 'Hostname configured successfully.'
   helper_hostname()
   return question(hi_text)


# Show Down Interfaces Intent for Alexa
@ask.intent("ShutdownINT")
def int_shutdown():
   hi_text = 'Displayed Diconnected interfaces'
   helper_shut()
   return question(hi_text)


# OSPF Intent for Alexa
@ask.intent("OSPFIntent")
def ospf_intent():
   bye_text = 'Configured OSPF'
   helper_ospf()
   return question(bye_text)


# Start Selfhealing for Alexa
@ask.intent("Selfhealing")
def self_healing():
   hi_text = 'Selfhealing has been started'
   helper_sf()
   return question(hi_text)


# Push Flow Entries Intent for Alexa
@ask.intent("sdn_intent")
def sdn_intent():
   hi_text = 'flow entries has been pushed'
   helper_pushfe()
   return question(hi_text)


# Backup to Github Intent for Alexa
@ask.intent("github")
def backup_github():
   hi_text = 'files have been backed up to github'
   helper_github()
   return question(hi_text)


# Show Disconnected Swtiches Intent for Alexa
@ask.intent("sdn_disconnected_sw")
def sdn_sw():
   bye_text = 'Disconnected switches in SDN network is diplayed'
   sdn_disconnected_sw()
   return question(bye_text)


if __name__ == '__main__':
   app.run(debug=True)

