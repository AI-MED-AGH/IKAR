import pandas as pd
import matplotlib.pyplot as plt
import os
#plots generated:
#1.Training vs Validation Loss
#2.Validation Accuracy
def plot_training_metrics(csv_path, output_dir=None):
    
    if not os.path.exists(csv_path):
        print(f"File {csv_path} does not exist.")
        return
    try:
        data = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return
    epochs = data['epoch']

    plt.style.use('ggplot') 
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
    #loss
    ax1.plot(epochs, data['train_loss'], label='Train Loss', color='blue', marker='.')
    ax1.plot(epochs, data['val_loss'], label='Val Loss', color='red', marker='.')
    ax1.set_title('Training and Validation Loss')
    ax1.set_ylabel('Loss')
    ax1.legend()
    ax1.grid(True)
    #accuracy
    ax2.plot(epochs, data['val_accuracy'], label='Val Accuracy', color='green', marker='o')
    ax2.set_title('Validation Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.legend()
    ax2.grid(True)
    plt.tight_layout()

    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        save_path = os.path.join(output_dir, f"{base_name}_plot.png")
        plt.savefig(save_path)
    else:
        plt.show()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        plot_training_metrics(sys.argv[1])
    else:
        print("Usage: python plots.py <path_to_csv_file>")