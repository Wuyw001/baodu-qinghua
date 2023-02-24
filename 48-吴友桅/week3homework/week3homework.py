#coding:GBK


import torch
import torch.nn as nn
import numpy as np
import random
import json
import matplotlib.pyplot as plt


"""
����pytorch�������д
ʵ��һ���������һ����nlp����
�ж��ı����Ƿ���ĳЩ�ض��ַ�����
"""


class TorchModel(nn.Module):
    def __init__(self, vector_dim, sentence_length, vocab):
        super(TorchModel, self).__init__()
        self.embedding = nn.Embedding(len(vocab), vector_dim)  #embedding��������������
        self.pool = nn.AvgPool1d(sentence_length)   #�ػ���
        self.classify = nn.Linear(vector_dim, 1)     #���Բ�
        self.activation = torch.sigmoid     #sigmoid��һ������
        self.loss = nn.functional.mse_loss  #loss�������þ�������ʧ

    #��������ʵ��ǩ������lossֵ������ʵ��ǩ������Ԥ��ֵ
    def forward(self, x, y=None):
        x = self.embedding(x)                      #(batch_size, sen_len) -> (batch_size, sen_len, vector_dim)
        x = self.pool(x.transpose(1, 2)).squeeze() #(batch_size, sen_len, vector_dim) -> (batch_size, vector_dim)
        x = self.classify(x)                       #(batch_size, vector_dim) -> (batch_size, 1)
        y_pred = self.activation(x)                #(batch_size, 1) -> (batch_size, 1)
        if y is not None:
            return self.loss(y_pred, y)   #Ԥ��ֵ����ʵֵ������ʧ
        else:
            return y_pred                 #���Ԥ����

#�ַ����������һЩ�֣�ʵ���ϻ���������
#Ϊÿ��������һ�����
#{"a":1, "b":2, "c":3...}
#abc -> [1,2,3]
def build_vocab():
    chars = "abcdefghijklmnopqrstuvwxyz1234567890����"  #�ַ���
    vocab = {}
    for index, char in enumerate(chars):
        vocab[char] = index   #ÿ���ֶ�Ӧһ�����
    vocab['unk'] = len(vocab)
    return vocab

#�������һ������
#����������ѡȡsentence_length����
#��֮Ϊ������
def build_sample(vocab, sentence_length):
    #������ֱ�ѡȡsentence_length���֣������ظ�
    x = [random.choice(list(vocab.keys())) for _ in range(sentence_length)]
    #ָ����Щ�ֳ���ʱΪ������
    if set("����") & set(x):
        y = 1
    #ָ���ֶ�δ���֣���Ϊ������
    else:
        y = 0
    x = [vocab.get(word, vocab['unk']) for word in x]   #����ת������ţ�Ϊ����embedding
    return x, y

#�������ݼ�
#������Ҫ��������������Ҫ�������ɶ���
def build_dataset(sample_length, vocab, sentence_length):
    dataset_x = []
    dataset_y = []
    for i in range(sample_length):
        x, y = build_sample(vocab, sentence_length)
        dataset_x.append(x)
        dataset_y.append([y])
    return torch.LongTensor(dataset_x), torch.FloatTensor(dataset_y)

#����ģ��
def build_model(vocab, char_dim, sentence_length):
    model = TorchModel(char_dim, sentence_length, vocab)
    return model

#���Դ���
#��������ÿ��ģ�͵�׼ȷ��
def evaluate(model, vocab, sample_length):
    model.eval()
    x, y = build_dataset(200, vocab, sample_length)   #����200�����ڲ��Ե�����
    print("����Ԥ�⼯�й���%d����������%d��������"%(sum(y), 200 - sum(y)))
    correct, wrong = 0, 0
    with torch.no_grad():
        y_pred = model(x)      #ģ��Ԥ��
        for y_p, y_t in zip(y_pred, y):  #����ʵ��ǩ���жԱ�
            if float(y_p) < 0.5 and int(y_t) == 0:
                correct += 1   #�������ж���ȷ
            elif float(y_p) >= 0.5 and int(y_t) == 1:
                correct += 1   #�������ж���ȷ
            else:
                wrong += 1
    print("��ȷԤ�������%d, ��ȷ�ʣ�%f"%(correct, correct/(correct+wrong)))
    return correct/(correct+wrong)


def main():
    #���ò���
    epoch_num = 20        #ѵ������
    batch_size = 20       #ÿ��ѵ����������
    train_sample = 500    #ÿ��ѵ���ܹ�ѵ������������
    char_dim = 20         #ÿ���ֵ�ά��
    sentence_length = 6   #�����ı�����
    learning_rate = 0.005 #ѧϰ��
    # �����ֱ�
    vocab = build_vocab()
    # ����ģ��
    model = build_model(vocab, char_dim, sentence_length)
    # ѡ���Ż���
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    # ѵ������
    for epoch in range(epoch_num):
        model.train()
        watch_loss = []
        for batch in range(int(train_sample / batch_size)):
            x, y = build_dataset(batch_size, vocab, sentence_length) #����һ��ѵ������
            optim.zero_grad()    #�ݶȹ���
            loss = model(x, y)   #����loss
            loss.backward()      #�����ݶ�
            optim.step()         #����Ȩ��
            watch_loss.append(loss.item())
        print("=========\n��%d��ƽ��loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model, vocab, sentence_length)   #���Ա���ģ�ͽ��
        log.append([acc, np.mean(watch_loss)])
    #��ͼ
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  #��acc����
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  #��loss����
    plt.legend()
    plt.show()
    #����ģ��
    torch.save(model.state_dict(), "model.pth")
    # ����ʱ�
    writer = open("vocab.json", "w", encoding="utf8")
    writer.write(json.dumps(vocab, ensure_ascii=False, indent=2))
    writer.close()
    return

#ʹ��ѵ���õ�ģ����Ԥ��
def predict(model_path, vocab_path, input_strings):
    char_dim = 20  # ÿ���ֵ�ά��
    sentence_length = 6  # �����ı�����
    vocab = json.load(open(vocab_path, "r", encoding="utf8")) #�����ַ���
    model = build_model(vocab, char_dim, sentence_length)     #����ģ��
    model.load_state_dict(torch.load(model_path))             #����ѵ���õ�Ȩ��
    x = []
    for input_string in input_strings:
        x.append([vocab[char] for char in input_string])  #���������л�
    model.eval()   #����ģʽ
    with torch.no_grad():  #�������ݶ�
        result = model.forward(torch.LongTensor(x))  #ģ��Ԥ��
    for i, input_string in enumerate(input_strings):
        print("���룺%s, Ԥ�����%d, ����ֵ��%f" % (input_string, round(float(result[i])), result[i])) #��ӡ���



if __name__ == "__main__":
   main()
   test_strings = ["��fvfe��", "w��sdf��", "rq����bg", "nak��ww","asdfgf","123456"]
   predict("model.pth", "vocab.json", test_strings)

