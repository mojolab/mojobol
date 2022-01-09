from callflowmanipulator import *

if __name__=="__main__":
    callflows=get_callflows()
    from_sip_section=generate_fromsip_sections(callflows)
    callback_section=generate_callback_sections(callflows)
    print(from_sip_section+"\n"+callback_section)