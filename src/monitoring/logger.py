import os
import csv

class TrainingLogger:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        self.filename = self._get_next_filename()
        self.filepath = os.path.join(self.log_dir, self.filename)
        self.file = open(self.filepath, mode='w', newline='')
        self.writer = csv.writer(self.file)
        self.headers = ['epoch', 'train_loss', 'val_loss', 'val_accuracy']
        self.writer.writerow(self.headers)
        self.file.flush() 

    def _get_next_filename(self):
        i = 1
        while True:
            filename = f"metrics{i:02d}.csv"
            if not os.path.exists(os.path.join(self.log_dir, filename)):
                return filename
            i += 1

    def log(self, epoch, train_loss, val_loss, val_accuracy):
        row = [epoch, train_loss, val_loss, val_accuracy]
        self.writer.writerow(row)
        self.file.flush() 

    def close(self):
        if self.file:
            self.file.close()