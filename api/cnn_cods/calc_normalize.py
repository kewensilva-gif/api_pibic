import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

dataset_path = "dataset-train"
def compute_mean_std(dataset_path):
  transform = transforms.Compose([
      transforms.Resize((64,64)),
      transforms.ToTensor()
  ])

  dataset = datasets.ImageFolder(root=dataset_path, transform=transform)
  imgs = torch.stack([img_t for img_t, _ in dataset], dim=3)
  # imgs.shape
  
  mean = imgs.view(3,-1).mean(dim=1)
  std = imgs.view(3,-1).std(dim=1)

  print(f"Mean calculado: {mean}")
  print(f"Std calculado: {std}")

if __name__ == '__main__':
  compute_mean_std(dataset_path)
