
# pip install lorem-text

import requests
import json
from lorem_text import lorem

def generate_one( index, status, group, hashtags ):
  data = {}
  data["postId"]     = "NEW"
  data["mytextarea"] = lorem.paragraphs(10)
  data["title"]      = str(index) + "@" + lorem.sentence()[0:15]
  data["postStatus"]     = status
  data["postGroup"]      = group
  data["hashtags"]      = hashtags
  data["postStart"]    = "2010-11-01"
  data["postEnd"]      = "2010-11-02"
  
  answer = requests.post("http://localhost:5000/postData", json=data )
  print( json.dumps(data) )
  

index = 0
groups = [ "ходитъ", "думатъ", "готовитъца", "затаилъсо" ]
for group in groups:
  hashtags = lorem.sentence().split()
  for i in range(10):
    index += 1
    generate_one( index, status="виден", group=group, hashtags=hashtags )
    index += 1
    generate_one( index, status="скрыт", group=group, hashtags=hashtags )
