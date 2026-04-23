import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler
import pickle

print("1. 读取并清洗数据...")
df = pd.read_csv('traffic volume.csv')
df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['Time'], format='%d-%m-%Y %H:%M:%S')
df = df.sort_values('datetime').reset_index(drop=True)
df = df.drop_duplicates(subset=['datetime'])

# 提取关键路口的流量数据 (本数据集仅有一列交通流量)
data = df[['datetime', 'traffic_volume']].copy()

print("2. 构造时序特征 (用过去12个时间步预测未来3个时间步)...")
# 为了简单，我们将整个交通流量序列缩放至 0-1
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data[['traffic_volume']].values)

# 保存 scaler 供以后预测时使用
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

seq_length = 12  # 过去 12 小时
pred_length = 3  # 预测未来 3 小时

X, y = [], []
for i in range(len(scaled_data) - seq_length - pred_length + 1):
    X.append(scaled_data[i : i + seq_length])
    y.append(scaled_data[i + seq_length : i + seq_length + pred_length])

X = np.array(X)
y = np.array(y)

print(f"数据量 X: {X.shape}, y: {y.shape}")

# 划分训练集和验证集 (简单划分最后20%为验证集)
train_size = int(len(X) * 0.8)
X_train, y_train = X[:train_size], y[:train_size]

# 转换为 PyTorch 张量
X_train_t = torch.FloatTensor(X_train)
y_train_t = torch.FloatTensor(y_train).squeeze(-1) # (batch, pred_length)

print("3. 搭建并训练 LSTM 模型...")
class SimpleLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=1, output_size=3):
        super(SimpleLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # 初始化隐藏状态和细胞状态
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).requires_grad_()
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).requires_grad_()
        
        # 前向传播 LSTM
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))
        
        # 取最后一个时间步的输出经过全连接层
        out = self.fc(out[:, -1, :]) 
        return out

model = SimpleLSTM(input_size=1, hidden_size=32, num_layers=1, output_size=pred_length)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

num_epochs = 20 # 可以调节

print("开始训练...")
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()
    
    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)
    
    loss.backward()
    optimizer.step()
    
    if (epoch+1) % 5 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

print("4. 保存模型权重...")
torch.save(model.state_dict(), 'traffic_model.pth')

# 保存一份最后24小时的数据用于前端展示实线
last_24_data = data.iloc[-24:].copy()
last_24_data.to_csv('history_24h.csv', index=False)

print("训练与预处理完成！")
