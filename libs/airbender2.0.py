import pandas
from flask import Flask, jsonify, request
import xmltodict
import gspread
import gspread_dataframe as gd
#the format prescibesd in the fuction below presrcribes to the pandas Dataframe format which requires the values of all dictnary to be a list for
#more on this read the pandas documentation for more details
def split_data(air_data):
    data={}
    
    if str(type(air_data["GATEWAY_ID"]["DT"]))=="<class 'list'>":
        date_time=[]
        humidity=[]
        temp=[]
        dl_b=[]
        dl_p=[]
        dl_s=[]
        pm_a=[]
        pm_b=[]
        pm_c=[]
        pm_d=[]
        pm_e=[]
        pm_f=[]
        for i in air_data["GATEWAY_ID"]["DT"]:
            try:
                date_time.append(i["@V"])
            except:
                date_time("")    

            try:
                humidity.append(i["AT"]["@R"])
            except:
                humidity.append("")  
            try:
                temp.append(i["AT"]["@T"])
            except:
                temp.append("")
            try:
                dl_b.append(i["DL"]["@B"])
            except:
                dl_b.append("")   
            try:
                dl_p.append(i["DL"]["@P"])
            except:
                dl_p.append("")  
            try:
                dl_s.append(i["DL"]["@S"])
            except:
                dl_s.append("")
            try:
                pm_a.append(i["PM"]["@A"])
            except:
                pm_a.append("")   
            try:
                pm_b.append(i["PM"]["@B"])
            except:
                pm_b.append("")    
            try:
                pm_c.append(i["PM"]["@C"])
            except:
                pm_c.append("") 
            try:
                pm_d.append(i["PM"]["@D"])
            except:
                pm_d.append("") 
            try:
                pm_e.append(i["PM"]["@E"])
            except:
                pm_e.append("")
            try:
                pm_f.append(i["PM"]["@F"])
            except:
                pm_f.append("")
        data["id"]=[air_data["GATEWAY_ID"]["@V"] for i in date_time]
        data["datetime"]=date_time         
        data["humidity"]=humidity
        data["temp"]=temp
        data["dl_p"]=dl_p
        data["dl_s"]=dl_s
        data["dl_b"]=dl_b
        data["pm_a"]=pm_a
        data["pm_b"]=pm_b
        data["pm_c"]=pm_c
        data["pm_d"]=pm_d
        data["pm_f"]=pm_f

    else:
        try:
            data["date_time"]=[air_data["GATEWAY_ID"]["DT"]["@V"]]
        except:
            data["date_time"]=""    

        try:
            data["humidity"]=[air_data["GATEWAY_ID"]["DT"]["AT"]["@R"]]
        except:
            data["humidity"]=""  
        try:
            data["temp"]=[air_data["GATEWAY_ID"]["DT"]["AT"]["@T"]]
        except:
            data["temp"]=""
        try:
            data["dl_b"]=[air_data["GATEWAY_ID"]["DT"]["DL"]["@B"]]
        except:
            data["dl_b"]=""   
        try:
            data["dl_p"]=[air_data["GATEWAY_ID"]["DT"]["DL"]["@P"]]
        except:
            data["dl_p]"]=""  
        try:
            data["dl_s"]=[air_data["GATEWAY_ID"]["DT"]["DL"]["@S"]]
        except:
            data["dl_s"]=""
        try:
            data["pm_a"]=[air_data["GATEWAY_ID"]["DT"]["PM"]["@A"]]
        except:
            data["pm_a"]=""  
        try:
            data["pm_b"]=[air_data["GATEWAY_ID"]["DT"]["PM"]["@B"]]
        except:
            data["pm_b"]=""   
        try:
            data["pm_c"]=[air_data["GATEWAY_ID"]["DT"]["PM"]["@C"]]
        except:
            pm_c.append("") 
        try:
            data["pm_d"]=[air_data["GATEWAY_ID"]["DT"]["PM"]["@D"]]
        except:
            pm_d.append("") 
        try:
            data["pm_e"]=[air_data["GATEWAY_ID"]["DT"]["PM"]["@E"]]
        except:
            data["pm_e"]=""
        try:
            data["pm_f"]=[air_data["GATEWAY_ID"]["DT"]["PM"]["@F"]]
        except:
            data["pm_f"]=""
          
    return data


def write_to_gsheets(gd_key,df):
    gc = gspread.service_account(gd_key)
    ws=gc.open("airdata").worksheet("Sheet1")
    data_sheet_df=gd.get_as_dataframe(ws)
    data_sheet_df.dropna(how="all",inplace="True")
    data_sheet_df.dropna(how="all",axis=1,inplace="True")
    data_sheet_df=data_sheet_df.append(df)
    gd.set_with_dataframe(ws,data_sheet_df)




app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def parse_xml():
    xml_data = request.data
    content_dict = xmltodict.parse(xml_data)
    write_to_gsheets("gd_key.json",pandas.DataFrame(split_data(content_dict)))
    return jsonify(split_data(content_dict))
#x=parse_xml()
if __name__ == '__main__':
    print("Starting python app")
    app.run(host='0.0.0.0', port=8080)





