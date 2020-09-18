import sys
import argparse
import json
from prototxt_basic import *

parser = argparse.ArgumentParser(description='Convert MXNet jason to Caffe prototxt')
parser.add_argument('--mx-json',     type=str, default='./model_mxnet/model-r34-amf-slim/model-symbol.json')
parser.add_argument('--cf-prototxt', type=str, default='./model_caffe/model-r34-amf-slim/model.prototxt')
parser.add_argument('--input_shape', type=str, default='1,3,112,112')
args = parser.parse_args()

with open(args.mx_json) as json_file:
  jdata = json.load(json_file)

with open(args.cf_prototxt, "w") as prototxt_file:
  for i_node in range(0,len(jdata['nodes'])):
    node_i = jdata['nodes'][i_node]
    if str(node_i['op']) == 'null' and str(node_i['name']) != 'data':
      continue
    
    print('{}, \top:{}, name:{} -> {}'.format(i_node,node_i['op'].ljust(20),
                                        node_i['name'].ljust(30),
                                        node_i['name']).ljust(20))
    
    info = node_i
    #print(info)
    
    info['top'] = info['name']
    info['bottom'] = []
    info['params'] = []
    
    for input_idx_i in node_i['inputs']:
      
      input_i = jdata['nodes'][input_idx_i[0]]
      if str(input_i['op']) != 'null' or (str(input_i['name']) == 'data'):
        info['bottom'].append(str(input_i['name']))
      if str(input_i['op']) == 'null':
        info['params'].append(str(input_i['name']))
        if not str(input_i['name']).startswith(str(node_i['name'])):
          print('           use shared weight -> %s'% str(input_i['name']))
          info['share'] = True
    
    if str(node_i['op']) == 'data':
      for char in ['[', ']', '(', ')']:
        input_shape = args.input_shape.replace(char, '')
      input_shape = [int(item) for item in input_shape.split(',')]
      info["shape"] = input_shape
      
    write_node(prototxt_file, info)

print("*** JSON to PROTOTXT FINISH ***")

