import torch
import torch.nn as nn

class LSTM_CNN(nn.Module):
    def __init__(self  ,joints_num:int, coords:int, hidden_size:int):
        super().__init__()
        self.cnn= nn.Sequential(
            nn.Conv1d(in_channels=coords, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU()
        )
        self.lstm = nn.LSTM(input_size=64*joints_num, hidden_size=hidden_size)
        self.fc = nn.Linear(hidden_size, 2)
    def forward(self,x: torch.Tensor) -> torch.Tensor:
        B, T, J, C = x.shape
        x = x.view(B*T,J,C)
        x= x.permute(0,2,1)
        x = self.cnn(x)
        x = x.reshape(B,T,-1)
        out, _ = self.lstm(x)
        out = out[:, -1, :]


        return self.fc(out)