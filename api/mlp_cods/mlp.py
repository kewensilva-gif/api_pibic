import torch
import torch.nn as nn

class MLP(nn.Module):
    def __init__(self, num_classes):
        super(MLP, self).__init__()
        self.model = nn.Sequential(
            nn.Flatten(),
            # Teste 01
            # nn.Linear(1 * 64 * 64, 64),
            # nn.ReLU(),
            # nn.Linear(64, num_classes)

            # Teste 02
            # nn.Linear(1 * 64 * 64, 128),
            # nn.ReLU(),
            # nn.Linear(128, num_classes)

            # Teste 03
            nn.Linear(1 * 64 * 64, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes)

            # Teste 04
            # nn.Linear(1 * 64 * 64, 64),
            # nn.ReLU(),
            # nn.Linear(64, 128),
            # nn.ReLU(),
            # nn.Linear(128, num_classes)

            # Teste 05
            # nn.Linear(1 * 64 * 64, 256),
            # nn.ReLU(),
            # nn.Linear(256, 128),
            # nn.ReLU(),
            # nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.model(x)
