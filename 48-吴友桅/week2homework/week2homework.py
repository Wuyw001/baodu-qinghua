# -*-coding:GBK -*-
# coding:unicode_escape

import torch
import torch.nn as nn
import numpy as np
import random
import json
import matplotlib.pyplot as plt

"""

����pytorch��ܱ�дģ��ѵ��
ʵ��һ�����й�����ҹ���(����ѧϰ)����
���ɣ�x��һ��5ά�����������1����>��5��������Ϊ����������֮Ϊ������

"""


class TorchModel(nn.Module):
    def __init__(self, input_size):
        super(TorchModel, self).__init__()
        self.linear1 = nn.Linear(input_size, 6)  #5*6�����Բ�
        self.linear2 = nn.Linear(6, 3)  #6*3�����Բ�
        self.linear3 = nn.Linear(3, 1)  #3*1�����Բ�
        self.activation = torch.sigmoid  # sigmoid��һ������
        self.loss = nn.functional.mse_loss  # loss�������þ�������ʧ

    # ��������ʵ��ǩ������lossֵ������ʵ��ǩ������Ԥ��ֵ
    def forward(self, x, y=None):
        x = self.linear1(x)  # (batch_size, input_size) -> (batch_size, 1)
        x = self.linear2(x)
        x = self.linear3(x)
        y_pred = self.activation(x)  # (batch_size, 1) -> (batch_size, 1)
        if y is not None:
            return self.loss(y_pred, y)  # Ԥ��ֵ����ʵֵ������ʧ
        else:
            return y_pred  # ���Ԥ����


# ����һ������, ���������ɷ���������������Ҫѧϰ�Ĺ���
# �������һ��5ά�����������4��ֵС�ڵ�һ���͵ڶ���֮�ͣ���Ϊ������������֮Ϊ������
def build_sample():
    x = np.random.random(5)
    if (x[0]+x[1] )< x[3]:
        return x, 1
    else:
        return x, 0



# �������һ������
# ����������������(���ʵ��?)
def build_dataset(total_sample_num):
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append([y])
    return torch.FloatTensor(X), torch.FloatTensor(Y)


# ���Դ���
# ��������ÿ��ģ�͵�׼ȷ��
def evaluate(model):
    model.eval()
    test_sample_num = 100
    x, y = build_dataset(test_sample_num)
    #�������Լ�(�����������)
    print("����Ԥ�⼯�й���%d����������%d��������" % (sum(y), test_sample_num - sum(y)))
    #y=1�������������Զ�y��;����������ĸ���
    correct, wrong = 0, 0
    with torch.no_grad():
        y_pred = model(x)  # ģ��Ԥ��
        for y_p, y_t in zip(y_pred, y):  # ����ʵ��ǩ���жԱ�
            if float(y_p) < 0.5 and int(y_t) == 0:
                correct += 1  # �������ж���ȷ
            elif float(y_p) >= 0.5 and int(y_t) == 1:
                correct += 1  # �������ж���ȷ
            else:
                wrong += 1
    print("��ȷԤ�������%d, ��ȷ�ʣ�%f" % (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)


def main():
    # ���ò���
    epoch_num = 10  # ѵ������
    batch_size = 20  # ÿ��ѵ����������
    train_sample = 5000  # ÿ��ѵ���ܹ�ѵ������������
    input_size = 5  # ��������ά��
    learning_rate = 0.001  # ѧϰ��
    # ����ģ��
    model = TorchModel(input_size)#ģ�����ʼ��
    # ѡ���Ż���
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
                            #ģ�������еĲ���    ѧϰ��
    log = []
    # ����ѵ���������������Ƕ�ȡѵ����
    train_x, train_y = build_dataset(train_sample)
    # ѵ������
    for epoch in range(epoch_num):
        #ѵ��epoch_num�֣�ÿһ��ѵ�������ݣ�epoch��ʾѵ���˵ڼ���
        model.train()
        #ѵ��ģʽ
        watch_loss = []
        for batch_index in range(train_sample // batch_size):
            #ѡһ������
            x = train_x[batch_index * batch_size : (batch_index + 1) * batch_size]
            y = train_y[batch_index * batch_size : (batch_index + 1) * batch_size]
            optim.zero_grad()  # �����µ�һ�������ݶ�Ҫ�ȹ���
            loss = model(x, y)  # ����loss
            loss.backward()  # �����ݶ�
            optim.step()  # ����Ȩ��
            watch_loss.append(loss.item())
        print("=========\n��%d��ƽ��loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model)  # ���Ա���ģ�ͽ��
        log.append([acc, float(np.mean(watch_loss))])
    # ����ģ��
    torch.save(model.state_dict(), "model.pth")
    # ��ͼ
    print(log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # ��acc����
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # ��loss����
    plt.legend()
    plt.show()
    return


# ʹ��ѵ���õ�ģ����Ԥ��
def predict(model_path, input_vec):
    input_size = 5
    model = TorchModel(input_size)
    model.load_state_dict(torch.load(model_path))  # ����ѵ���õ�Ȩ��
    # print(model.state_dict())

    model.eval()  # ����ģʽ
    with torch.no_grad():  # �������ݶ�
        result = model.forward(torch.FloatTensor(input_vec))  # ģ��Ԥ��
    for vec, res in zip(input_vec, result):
        print("���룺%s, Ԥ�����%d, ����ֵ��%f" % (vec, round(float(res)), res))  # ��ӡ���
        #������������һ������ֵ��������������õ�����


if __name__ == "__main__":
    main()
    #main()����ʵ��ģ�͵�ѵ��
    test_vec = [[0.47889086,0.15229675,0.31082123,5,0.18920843],
                [0.94963533,0.5524256,0.95758807,0,0.84890681],
                [0.78797868,0.67482528,0.13625847,0.91,0.99871392],
                [0.1349776,0.59416669,0.92579291,0.41567412,0.7358894]]
    predict("model.pth", test_vec)
    #predict()����ѵ���õ�ģ��Ȩ�ؽ���Ԥ��
