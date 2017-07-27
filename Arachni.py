#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import yaml
import requests
try:
   import simplejson as json
except Exception as e:
   import json
from DB_config import *
from http_info import Http_Info


class ArachniClient(object):

   with open('./tscan_audit.json') as f:
      default_profile = json.load(f)

   headers = {'Content-Type':'application/json'}

   """docstring for ClassName"""
   def __init__(self, arachni_url='http://127.0.0.1:8888/scans'):
      super(ArachniClient, self).__init__()
      self.arachni_url = arachni_url
      self.default_profile = ArachniClient.default_profile
      self.headers = ArachniClient.headers

   def to_param_str(self,param_dict):
       """{'a':1,'b':2} to a=1&b=2"""
       try:
          param_dict = str(param_dict)
          param_dict = param_dict.replace('\\','\\\\')
          param_dict = ast.literal_eval(param_dict)
          params = '&'.join([k + '=' + v for k, v in param_dict.items()])
       except:
          params = param_dict
       
       return params

   def group_param(self,url,headers,parm,):
      values = yaml.safe_dump(parm, default_flow_style=False)
      self.default_profile['url'] = url
      self.default_profile['plugins']['vector_feed']['yaml_string'] = values.replace('-',' ')
      self.default_profile['http']['user_agent'] = headers['User-Agent']
      del headers['User-Agent']
      self.default_profile['http']['request_headers'] = headers

      options = json.dumps(self.default_profile)

      return options

   def get_token_result(self,token):
      token_url = ("{url}/{token}/report").format(url=self.arachni_url,token=token)
      try:
         resp = requests.get(token_url,headers=self.headers,timeout=60, verify=False)
         if resp.status_code == 200:
            results = json.loads(resp.content) 
            start_datetime = results['start_datetime']
            finish_datetime = results['finish_datetime']
            delta_time = results['delta_time']
            for issues in results['issues']:
               #print issues['name'],issues['severity'],issues['signature']
               #signature = issues['signature'] if 'signature' in issues else ''
               #print issues['request']['headers_string'],issues['request']['body']
               request_headers = issues['request']['headers']
               response_headers = issues['response']['headers']
               param = issues['vector']['affected_input_name']
               payload = issues['vector']['affected_input_value']
               param = param if param else ''
               payload = payload if payload else ''
               response_headers['code'] = issues['response']['code']
               response_content = issues['response']['body']
               param_dict = issues['request']['body']
               if param_dict:
                  request_info = issues['request']['headers_string']+self.to_param_str(param_dict)
               else:
                  request_info = issues['request']['headers_string']

               #name,severity,description,url,param,payload,requests_info,request_headers,response_headers,response_content
               args = token,issues['check']['name'],issues['severity'],issues['request']['url'],param,payload,request_info,request_headers,response_headers
               #insert
      except Exception as e:
         raise e
      finally:
         requests.delete(token_url.replace('/report',''),headers=self.headers,timeout=60, verify=False)


   def get_token_status(self,token):
      token_url = ("{url}/{token}").format(url=self.arachni_url,token=token)
      try:
         resp = requests.get(token_url,headers=self.headers,timeout=60, verify=False)
         if resp.status_code == 200:
            results = json.loads(resp.content) 
            if results['status'] == "done":
               self.get_token_result(token)
            return results['status']
      except Exception as e:
         raise e

   def get_all(self):
      try:
         resp = requests.get(self.arachni_url,headers=self.headers,timeout=60, verify=False)
         if resp.status_code == 200:
            results = json.loads(resp.content) 
            for token in results:
               status = self.get_token_status(token)
               #update 
            return results
      except:
         pass

   def start(self,url,headers,param):
      options = self.group_param(url,headers,param)
      #insert arachni_info
      try:
         res = requests.post(self.arachni_url,data = options,headers=self.headers,timeout=60, verify=False)
         print res.content
      except Exception as e:
         raise e
      


def get_ua(taskid):
   sql = "select user_agent from crawl_info where id = {taskid}"
   result = query_one(sql.format(taskid=taskid))

   return result['user_agent']

def update(type,uuid,taskid):
   upsql = "update `request` set `user_output`={type} where id ={id} and taskid = {taskid}"
   execute(upsql.format(type=type,id=uuid,taskid=taskid))
   if type == "1":
      insql = "insert `vuln_task_queen` (`urlid`,`taskid`,`sql_status`,`tscan_status`,`ischeck`,`add_time`) VALUES (%s, %s, 0,0,0,%s)"
      sqlarg = str(uuid),str(taskid),datetime.datetime.now()
      execute(insql,sqlarg)

def get_http():
   sql = "select * from `request` where id = '79' and `user_output`='0' order by id asc limit 0,1"
   result = query_one(sql)
   
   method = result['method'].upper()
   uuid = result['id']
   url = result['url']
   utype =  result['type']
   try:
      referer = result['referer']
   except:
      referer = result['url']

   header = {"User-Agent":get_ua(result['taskid'])}

   if len(result['cookies'])>2:
      header["Cookie"] = result['cookies']
   data = result['data']
   taskid = result['taskid']
   http_auth = result['http_auth']

   htpinfo = Http_Info(url,method,utype,data)
   if htpinfo.param_data():
      headers,param = htpinfo.param_data()
      headers = dict(headers,**header)
      arachni = ArachniClient()
      arachni.start(url,headers,param)

if __name__ == "__main__":
   arachni = ArachniClient()
   arachni.get_all()
   #print arachni.get_token_result('9c80b31f53a7d85a6c40a69e85950b08')
