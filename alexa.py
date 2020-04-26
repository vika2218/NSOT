from flask import Flask, render_template
from flask_ask import Ask, request, statement, question, session, context
from intent import *
from self_healing import *

app = Flask(__name__)
ask = Ask(app, "/capstone")

@app.route("/")
def homepage():
   h= """
   <body>
    <a href="intents" class="button">Intents</a>    
    <a href="security" class="button">Security</a>    
    <a href="healing" class="button">Self-Healing</a>  <br/></div>
   </body>
  </html>
    """
   return render_template("home.html") + h 
   #return "Welcome to Smart Network System....Would you like to configure hostname or OSPF?"

@app.route('/intents')
def intents():
    h = """
       <body>
        <a href="ospf_gui" class="button">Configure OSPF</a>  <br/> 
        <a href="hostname_gui" class="button">Configure Hostname</a>  <br/>  
        <a href="github_gui" class="button">Back NSOT to GITHUB</a>  
        <br/> <a href="topology" class="button">Push Flow Entries</a> <br/>  
        <a href="paths" class="button">Show disconnected switches</a> <br/> 
        <a href="topology" class="button">Show down interface</a> </div> 
       </body>
      </html>
        """
    return render_template("home.html")+h

@app.route('/ospf_gui')
def ospf_gui():
   helper_ospf()
   return "Configured OSPF"

@app.route('/hostname_gui')
def hostname_gui():
   helper_hostname()
   return "Configured Hostname"

@app.route('/github_gui')
def github_gui():
   helper_github()
   return "Pushed Files to GitHub"

@app.route('/ospf_gui1')
def ospf_gui1():
   helper_ospf()
   return "Configured OSPF"

@app.route('/ospf_g1ui')
def ospf_g1ui():
   helper_ospf()
   return "Configured OSPF"



@ask.launch
def start_skill():
   welcome_message = 'Welcome to SNS'
   return question(welcome_message)

@ask.intent("HostIntent")
def host_headlines():
   hi_text = 'Hostname configured successfully.'
   helper_hostname()
   return question(hi_text)

@ask.intent("ShutdownINT")
def int_shutdown():
   hi_text = 'Displayed Diconnected interfaces'
   helper_shut()
   return question(hi_text)

@ask.intent("OSPFIntent")
def ospf_intent():
   bye_text = 'Configured OSPF'
   helper_ospf()
   return question(bye_text)

@ask.intent("Selfhealing")
def self_healing():
   hi_text = 'Selfhealing has been started'
   helper_sf_sdn()
   return question(hi_text)

@ask.intent("sdn_intent")
def sdn_intent():
   hi_text = 'flow entries has been pushed'
   helper_pushfe()
   return question(hi_text)

@ask.intent("github")
def backup_github():
   hi_text = 'files has been backed up to github'
   #helper_pushfe()
   return question(hi_text)

@ask.intent("sdn_disconnected_sw")
def sdn_sw():
   bye_text = 'Disconnected switches in SDN network is diplayed'
   sdn_disconnected_sw()
   return question(bye_text)

if __name__ == '__main__':
   app.run(debug=True)

