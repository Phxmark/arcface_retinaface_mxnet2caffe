import sys, argparse
import mxnet as mx
import sys
import os

import caffe


from find import *

import time
import os
#os.environ["CUDA_VISIBLE_DEVICES"] = '4'
parser = argparse.ArgumentParser(description='Convert MXNet model to Caffe model')
parser.add_argument('--mx-model',    type=str, default='./model_mxnet/mnet.25')
parser.add_argument('--mx-epoch',    type=int, default=0)
parser.add_argument('--cf-prototxt', type=str, default='./model_caffe/mnet.25.prototxt')
parser.add_argument('--cf-model',    type=str, default='./model_caffe/mnet.25.caffemodel')

args = parser.parse_args()

# Load
_, arg_params, aux_params = mx.model.load_checkpoint(args.mx_model, args.mx_epoch)
net = caffe.Net(args.cf_prototxt, caffe.TEST)

# Convert
all_keys = list(arg_params.keys()) + list(aux_params.keys())
all_keys.sort()

print('%d KEYS' %len(all_keys))
print('VALID KEYS:')

# backbone = "hstage1"
backbone = find_backbone(args.mx_model + '-symbol.json')
print('======>',backbone)


for i_key,key_i in enumerate(all_keys):

  # try:
    print("====% 3d | %s "%(i_key, key_i.ljust(40)))
    
    if 'data' is key_i:
      pass
    elif '_weight' in key_i:
      if key_i.find(backbone)!=-1 or key_i.find("dense") != -1:
        key_caffe = key_i.replace('_weight', '')
      else:
        key_caffe = key_i.replace('_weight','')
      print(key_i,key_caffe)
      print("{}: {}->{}".format(key_i, arg_params[key_i].shape, net.params[key_caffe][0].data.shape))
      net.params[key_caffe][0].data.flat = arg_params[key_i].asnumpy().flat
    elif '_bias' in key_i:
      if key_i.find(backbone)!=-1:
        key_caffe = key_i.replace('_bias', '_fwd')
      else:
        key_caffe = key_i.replace('_bias','')
      
      if key_i.find("dense") != -1:
        key_caffe = key_i.replace('_bias', '_fwd')
      else:
        key_caffe = key_i.replace('_bias', '')

      print("{}: {}->{}".format(key_i, arg_params[key_i].shape, net.params[key_caffe][0].data.shape))
      net.params[key_caffe][1].data.flat = arg_params[key_i].asnumpy().flat   
    elif '_gamma' in key_i and 'relu' not in key_i:
      if key_i.find(backbone)!=-1:
        key_caffe = key_i.replace('_gamma', '_scale')
      else:
        key_caffe = key_i.replace('_gamma','_scale')

      print("{}: {}->{}".format(key_i, arg_params[key_i].shape, net.params[key_caffe][0].data.shape))
      net.params[key_caffe][0].data.flat = arg_params[key_i].asnumpy().flat
    # TODO: support prelu
    elif '_gamma' in key_i and 'relu' in key_i:   # for prelu
      key_caffe = key_i.replace('_gamma','')
      print("key_i",key_i)
      print("{}: {}->{}".format(key_i, arg_params[key_i].shape, net.params[key_caffe][0].data.shape))
      assert (len(net.params[key_caffe]) == 1)
      net.params[key_caffe][0].data.flat = arg_params[key_i].asnumpy().flat
    elif '_beta' in key_i:

      if key_i.find(backbone)!=-1:
        key_caffe = key_i.replace('_beta', '_scale')
      else:
        key_caffe = key_i.replace('_beta','_scale')

      print("key in mxnet",key_i,key_i in arg_params.keys())
      print("key in caffe",key_caffe,key_caffe in net.params.keys())
      print("{}: {}->{}".format(key_i, arg_params[key_i].shape, net.params[key_caffe][0].data.shape))
      net.params[key_caffe][1].data.flat = arg_params[key_i].asnumpy().flat
    elif '_moving_mean' in key_i:
      key_caffe = key_i.replace('_moving_mean','')
      print("{}: {}->{}".format(key_i, aux_params[key_i].shape, net.params[key_caffe][0].data.shape))
      net.params[key_caffe][0].data.flat = aux_params[key_i].asnumpy().flat
      net.params[key_caffe][2].data[...] = 1
    elif '_moving_var' in key_i:
      key_caffe = key_i.replace('_moving_var','')
      print("{}: {}->{}".format(key_i, aux_params[key_i].shape, net.params[key_caffe][0].data.shape))
      net.params[key_caffe][1].data.flat = aux_params[key_i].asnumpy().flat
      net.params[key_caffe][2].data[...] = 1
    elif '_running_mean' in key_i: #gluoncv中bn的名字不一样，是running
      key_caffe = key_i.replace('_running_mean', '')
      print("{}: {}->{}".format(key_i, aux_params[key_i].shape, net.params[key_caffe][0].data.shape))
      net.params[key_caffe][0].data.flat = aux_params[key_i].asnumpy().flat
      net.params[key_caffe][2].data[...] = 1
    elif '_running_var' in key_i:
      key_caffe = key_i.replace('_running_var', '')
      print("{}: {}->{}".format(key_i, aux_params[key_i].shape, net.params[key_caffe][0].data.shape))
      net.params[key_caffe][1].data.flat = aux_params[key_i].asnumpy().flat
      net.params[key_caffe][2].data[...] = 1
    else:
      # pass
      sys.exit("Warning!  Unknown mxnet:{}".format(key_i))
  
    print("% 3d | %s -> %s, initialized." 
           %(i_key, key_i.ljust(40), key_caffe.ljust(30)))

net.save(args.cf_model)

print("\n*** PARAMS to CAFFEMODEL Finished. ***\n")

#print(aux_params.keys())

