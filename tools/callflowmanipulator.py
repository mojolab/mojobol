import json
from configparser import ConfigParser

with open("../conf/callbackcontext.skel", "r") as f:
    callbackcontextsection=f.read()
with open("../conf/fromsipcontext.skel", "r") as f:
    fromsipcontextsection=f.read()


# Generate a from-sip section by replacing <EXT_NAME> with the from-sip extension name in fromsipcontextsection

def generate_fromsip_section(ext_name, callback_ext_name):
    commentline=";ext_name={},callback_ext_name={}".format(ext_name,callback_ext_name)
    return commentline+"\n"+fromsipcontextsection.replace("<EXT_NAME>", ext_name).replace("<CALLBACK_EXT_NAME>", callback_ext_name)+"\n"

# Generate a callback section by replacing <CALLBACK_EXT_NAME> with the callback extension name in callbackcontextsection and <CALLFLOWFILE> with the path to callflow config file
def generate_callback_section(callback_ext_name, callflowfile):
    commentline=";callback_ext_name={},callflowfile={}".format(callback_ext_name,callflowfile)
    return commentline+"\n"+callbackcontextsection.replace("<CALLBACK_EXT_NAME>", callback_ext_name).replace("<CALLFLOWFILE>", callflowfile)+"\n"


# Get callflows from ../conf/callflows.json
def get_callflows():
    with open("../conf/local/callflows.json", "r") as f:
        callflows = json.load(f)
    return callflows['callflows']


# Generate a [from-sip] section for each extension in callflows
def generate_fromsip_sections(callflows):
    fromsip_sections = []
    for callflow in callflows:
        fromsip_sections.append(generate_fromsip_section(callflow['ext_name'], callflow['callback_ext_name']))
    from_sip_section="[from-sip]\n"
    for section in fromsip_sections:
        from_sip_section+=section+"\n"
    return from_sip_section

# Generate a [callback] section for each extension in callflows
def generate_callback_sections(callflows):
    callback_sections = []
    for callflow in callflows:
        callback_sections.append(generate_callback_section(callflow['callback_ext_name'], callflow['configfile']))
    callback_section="[callback]\n"
    for section in callback_sections:
        callback_section+=section+"\n"
    return callback_section

# Generate extensions.conf
def generate_extensions_conf():
    callflows=get_callflows()
    from_sip_section=generate_fromsip_sections(callflows)
    callback_section=generate_callback_sections(callflows)
    return from_sip_section+"\n"+callback_section

    
# Generate config file for callflow from ../conf/callflowconfigbase.conf with user input, leave existing entries as default, ask for user confirmation
def generate_config_file():
