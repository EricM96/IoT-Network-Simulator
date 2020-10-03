from __future__ import print_function, division
import argparse
import os
from collections import Counter
from functools import partial
from pathlib import Path

import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from torch import cuda
from torchvision import transforms
from torchvision.datasets import ImageFolder
from sklearn.metrics import confusion_matrix
from ray import tune
from ray.tune import CLIReporter
from ray.tune.schedulers import ASHAScheduler


def load_model(model_name, num_classes):
    if model_name == 'm_net':
        model = torch.hub.load('pytorch/vision:v0.5.0',
                               'mobilenet_v2', pretrained=False)
        model.classifier[1] = nn.Linear(1280, num_classes)
    else:
        model = torch.hub.load('pytorch/vision:v0.5.0',
                               'squeezenet1_1', pretrained=False)
        model.classifier[1] = nn.Conv2d(
            512, num_classes, kernel_size=(1, 1), stride=(1, 1))

    return model


def train_model(config, checkpoint_dir=None, model_name=None, device=None,
                max_epochs=None, num_workers=None, data_pth=None):
    train_set, valid_set, test_set = get_datasets(data_pth)
    model = load_model(model_name, len(train_set.classes))
    model.to(device)

    num_epochs = max_epochs
    bs = int(config['batch_size'])

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config['eta'])

    if checkpoint_dir:
        model_state, optimizer_state = torch.load(
            os.path.join(checkpoint_dir, 'checkpoint')
        )
        model.load_state_dict(model_state)
        optimizer.load_state_dict(optimizer_state)

    trainloader = DataLoader(
        train_set,
        batch_size=bs,
        shuffle=True,
        num_workers=num_workers
    )
    validloader = DataLoader(
        valid_set,
        batch_size=bs,
        shuffle=True,
        num_workers=num_workers
    )

    for epoch in range(num_epochs):
        running_loss = 0.0
        epoch_steps = 0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data[0].to(device), data[1].to(device)
            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            epoch_steps += 1

            if i % 2000 == 1999:    # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / epoch_steps))
                running_loss = 0.0

        val_loss = 0.0
        val_steps = 0
        total = 0
        correct = 0
        for i, data in enumerate(validloader, 0):
            with torch.no_grad():
                inputs, labels = data[0].to(device), data[1].to(device)

                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

                loss = criterion(outputs, labels)
                val_loss += loss.cpu().numpy()
                val_steps += 1

        with tune.checkpoint_dir(epoch) as checkpoint_dir:
            path = os.path.join(checkpoint_dir, 'checkpoint')
            torch.save((model.state_dict(), optimizer.state_dict()), path)

        tune.report(loss=(val_loss / val_steps), accuracy=correct / total)
    print('Finished training')


def test_model(model, device, test_data, write_pth, num_workers):
    model.eval()
    model.to(device)

    testloader = DataLoader(
        test_data,
        batch_size=4,
        shuffle=False,
        num_workers=num_workers
    )

    correct = []
    predictions = []

    with torch.no_grad():
        for data in testloader:
            inputs, labels = data[0].to(device), data[1].to(device)
            outputs = model(inputs)
            for output, label in zip(outputs, labels):
                hypothesis = output.max(0)[1].item()
                predictions.append(hypothesis)
                correct.append(label.item())

    with open(write_pth / 'log.txt', 'w') as fout:
        tp, fn, fp, tn = confusion_matrix(correct, predictions).ravel()
        print('True Positives:', tp, file=fout)
        print('True Negatives:', tn, file=fout)
        print('False Positives:', fp, file=fout)
        print('False Negatives:', fn, file=fout)

        tpr = tp / (tp + fp)
        tnr = tn / (tn + fn)
        fpr = fp / (fp + tn)
        fnr = fn / (fn + tp)
        acc = (tp + tn) / (tp + fp + tn + fn)
        dr = tp / (tp + fn)
        far = fp / (tn + fp)
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * tp / (2 * tn + fp + fn)

        print('Accuracy:', acc, file=fout)
        print('True Positive Rate:', tpr, file=fout)
        print('True Negative Rate:', tnr, file=fout)
        print('False Positive Rate:', fpr, file=fout)
        print('False Negative Rate:', fnr, file=fout)
        print('Detection Rate:', dr, file=fout)
        print('False Alarm Rate:', far, file=fout)
        print('Precision:', precision, file=fout)
        print('Recall:', recall, file=fout)
        print('F1 Score:', f1, file=fout)

    torch.save(model.state_dict(), write_pth / 'model.pt')

    return acc


def get_datasets(data_pth):
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])

    print(f'Retrieving datasets from {data_pth}')
    train_set = ImageFolder(data_pth / 'train', transform=preprocess)
    valid_set = ImageFolder(data_pth / 'valid', transform=preprocess)
    test_set = ImageFolder(data_pth / 'test', transform=preprocess)

    print(f'Retrieved {len(train_set)} training samples')
    print(f'Training targets: {train_set.class_to_idx}')
    print(f'Training distribution {dict(Counter(train_set.targets))}')
    print(f'Retrieved {len(valid_set)} validation samples')
    print(f'Validation targets: {valid_set.class_to_idx}')
    print(f'Validation distribution {dict(Counter(valid_set.targets))}')
    print(f'Retrieved {len(test_set)} testing samples')
    print(f'Testing targets: {test_set.class_to_idx}')
    print(f'Testing distribution {dict(Counter(test_set.targets))}')
    print()

    return train_set, valid_set, test_set


def config_cuda(use_cuda):
    if not use_cuda:
        print('Using cpu')
        torch.device('cpu')
        return 'cpu'
    elif not cuda.is_available():
        print('Cuda not found, using cpu')
        torch.device('cpu')
        return 'cpu'
    print('Configuring cuda...')
    torch.device('cuda')
    cuda.set_device(0)
    current_dev = cuda.current_device()
    current_dev_name = cuda.get_device_name(current_dev)
    current_dev_specs = cuda.get_device_properties(current_dev)

    print(f'Current Device: {current_dev}')
    print(f'Current Device Name: {current_dev_name}')
    print(f'Current Device Specs: {current_dev_specs}')
    print()

    return 'cuda'


def main(args):
    device = config_cuda(args.use_cuda)

    data_pth = Path(Path.cwd() / args.data_path)
    out_pth = Path(Path.cwd() / args.out_path)

    train_set, valid_set, test_set = get_datasets(data_pth)

    config = {
        'eta': tune.loguniform(1e-5, 1e-1),
        'batch_size': tune.choice([2, 4, 8, 16])
    }
    scheduler = ASHAScheduler(
        metric='loss',
        mode='min',
        max_t=args.max_epochs,
        grace_period=1,
        reduction_factor=2
    )
    reporter = CLIReporter(
        parameter_columns=['eta', 'batch_size'],
        metric_columns=['loss', 'accuracy', 'training_iteration']
    )
    num_gpus = 1 if device == 'cuda' else 0
    # result = tune.run(
    #     partial(train_model, model_name=args.model, device=device,
    #             max_epochs=args.max_epochs, num_workers=args.num_workers,
    #             data_pth=data_pth),
    #     resources_per_trial={'cpu': args.num_workers, 'gpu': num_gpus},
    #     config=config,
    #     num_samples=args.num_samples,
    #     scheduler=scheduler,
    #     progress_reporter=reporter
    # )
    train_model(config={'eta': 0.00001, 'batch_size': 4}, model_name=args.model, device=device, max_epochs=args.max_epochs, num_workers=args.num_workers, data_pth=data_pth)
    # best_trial = result.get_best_trial('loss', 'min', 'last')
    # print(f'Best trial config {best_trial.config}')
    # print(
    #       f'Best trial final validation loss: {best_trial.last_result["loss"]}'
    #      )
    # model = load_model(args.model, len(train_set.classes))

    # best_checkpoint_dir = best_trial.checkpoint.value
    # model_state, optimizer_state = torch.load(os.path.join(
    #     best_checkpoint_dir, 'checkpoint'))
    # model.load_state_dict(model_state)

    # test_acc = test_model(model, device, test_set, out_pth, args.num_workers)
    # print(f'Best trial test set accuracy: {test_acc}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Train a model on a dataset')
    parser.add_argument('model', choices=['m_net', 's_net'],
                        help='Model to train. m_net for mobilenet_v2, \
                                s_net for squeezenet1_1')
    parser.add_argument('data_path', help='Base path of the dataset')
    parser.add_argument('out_path', help='Path to save model and accuracy \
            statistics to')
    parser.add_argument('--use-cuda', '-c', type=bool, default=True,
                        help='If true, use GPU to accelerate model training. \
                                Defaults to true.')
    parser.add_argument('--max-epochs', '-e', type=int, default=30,
                        help='Maximum number of epochs per trial')
    parser.add_argument('--num-samples', '-n', type=int, default=10,
                        help='Number of samples for tune to run')
    parser.add_argument('--num-workers', '-w', type=int, default=4,
                        help='Number of cpus to use')
    args = parser.parse_args()
    main(args)
