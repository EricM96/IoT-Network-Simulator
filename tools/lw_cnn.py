from __future__ import print_function, division
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils, models
from torchvision.datasets import ImageFolder
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
from pathlib import Path
import pickle
from set_types import *
from sklearn.metrics import confusion_matrix
from random import shuffle

from torch import cuda

cuda.set_device(0)
current_dev = cuda.current_device()
current_dev_name = cuda.get_device_name(current_dev)
current_dev_specs = cuda.get_device_properties(current_dev)

print(f'Current Device: {current_dev}')
print(f'Current Device Name: {current_dev_name}')
print(f'Current Device Specs: {current_dev_specs}')

def train_model(model, read_pth, write_pth, num_classes=2, s_net=True):
  if s_net:
    model.classifier[1] = nn.Conv2d(512, num_classes, kernel_size=(1,1), stride=(1,1))
  else:
    model.classifier[1] = nn.Linear(1280, num_classes)

  model.to('cuda')

  num_epochs = 30
  eta = 0.000075
  bs = 2

  if num_classes == 2:
    weights = torch.FloatTensor([1., 1])
  else:
    weights = torch.FloatTensor([1., 1., 1.])
  criterion = nn.CrossEntropyLoss()
  optimizer = optim.Adam(model.parameters(), lr=eta)

  preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
  ])

  train_set = ImageFolder(read_pth / 'train', transform=preprocess)
  valid_set = ImageFolder(read_pth / 'valid', transform=preprocess)
  test_set = ImageFolder(read_pth / 'test', transform=preprocess)

  ### Down sample training set ###
  down_sampled_set = []
  if num_classes == 2:
    target = sum([1 for data in train_set if data[1] == 0])
  else:
    target = sum([1 for data in train_set if data[1] == 1])
  
  if num_classes == 2:
    seen = 0
    for data in train_set.samples:
      if data[1] == 1 and seen < target:
        seen += 1
        down_sampled_set.append(data)
      elif data[1] != 1:
        down_sampled_set.append(data)
  else:
    seen = 0
    for data in train_set.samples:
      if data[1] == 2 and seen < target:
        seen += 1
        down_sampled_set.append(data)
      elif data[1] != 2:
        down_sampled_set.append(data)

  train_set.samples = down_sampled_set
  print('Target Size:', target)
  print('Set Size:', len(train_set))

  trainloader = DataLoader(train_set, batch_size=bs, num_workers=4, shuffle=True)
  validloader = DataLoader(valid_set, batch_size=bs, num_workers=4, shuffle=True)
  testloader = DataLoader(test_set, batch_size=len(test_set)//3, num_workers=4, shuffle=True)

  best_acc = -1
  for epoch in range(num_epochs):  # loop over the dataset multiple times
    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
      inputs, labels = data[0].to('cuda'), data[1].to('cuda')
      optimizer.zero_grad()

      outputs = model(inputs)
    
      loss = criterion(outputs, labels)

      loss.backward()
      optimizer.step()

      # print statistics
      running_loss += loss.item()

      if i % 10 == 9:    # print every 2000 mini-batches
        print('[%d, %5d] loss: %.3f' %
          (epoch + 1, i + 1, running_loss / 10))

        with torch.no_grad():
          correct, N = 0, len(valid_set)
          for i, valid_data in enumerate(validloader):
            x, y = valid_data[0].to('cuda'), valid_data[1].to('cuda')
            y_hat = model(x)

            for output, label in zip(y_hat, y):
              if output.max(0)[1].item() == label.item():
                correct += 1
          acc = correct / N
          if acc > best_acc:
            best_acc = acc
            print(f'New Best Accuracy: {best_acc:.3f}')
            torch.save(model.state_dict(), write_pth / 'best_model.pth')
          
        running_loss = 0.0
  best_model = model.eval()
  best_model.load_state_dict(torch.load(write_pth / 'best_model.pth'))
  best_model.to('cuda')

  correct = []
  predictions = []

  with torch.no_grad():
    for i, data in enumerate(testloader, 0):
      inputs, labels = data[0].to('cuda'), data[1].to('cuda')
      # inputs, labels = data
      outputs = best_model(inputs)
      for output, label in zip(outputs, labels):
        hypothesis = output.max(0)[1].item()
        predictions.append(hypothesis)
        correct.append(label.item())
  
    #  If 2 class data
  with open(write_pth / 'log.txt', 'w') as fout:
    if num_classes == 2:
      tp, fn, fp, tn = confusion_matrix(correct, predictions).ravel()
      print('True Positives:',tp, file=fout)
      print('True Negatives:',tn, file=fout)
      print('False Positives:',fp, file=fout)
      print('False Negatives:', fn, file=fout)
      tpr = tp / (tp + fp)
      tnr = tn / (tn + fn)
      fpr = fp / (fp + tn)
      fnr = fn / (fn + tp)

      acc = (tp + tn) / (tp + fp + tn + fn)
      print('Accuracy:',acc, file=fout)
      print('True Positive Rate:',tpr, file=fout)
      print('True Negative Rate:',tnr, file=fout)
      print('False Positive Rate:',fpr, file=fout)
      print('False Negative Rate:', fnr, file=fout)

    else:
      cm = confusion_matrix(correct, predictions)
      print(cm, file=fout)

  print(confusion_matrix(correct, predictions))

if __name__ == '__main__':
  model = torch.hub.load('pytorch/vision:v0.5.0', 'squeezenet1_1', pretrained=False)
  # model = torch.hub.load('pytorch/vision:v0.5.0', 'mobilenet_v2', pretrained=True)

  read_pth = Path.cwd() / '..' / 'datasets/archive/heatmap_datasets' / 'udp_binary'
  out_pth = Path.cwd() / 'models' / 's_net' / 'udp_binary'

  train_model(model, read_pth, out_pth, num_classes=2, s_net=True)
