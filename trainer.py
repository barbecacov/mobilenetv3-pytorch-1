# Inspired by https://github.com/victoresque/pytorch-template/
import logging


class Trainer:
    def __init__(self, model, criterion, optimizer, device, train_loader, valid_loader):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.train_loader = train_loader
        self.valid_loader = valid_loader

    def train(self, epochs: int):
        """Trains the model for epochs"""

        for epoch in range(epochs):
            logging.info('epoch %d', epoch)
            best_valid_loss = float('inf')

            # Training
            train_top1_acc, train_top5_acc, train_loss = self._train_epoch(
                epoch)
            logging.info('train_top1_acc {:.5f}, train_top5_acc {:.5f}, train_loss {:.5f}'.format(
                train_top1_acc, train_top5_acc, train_loss))

            # Validation
            valid_top1_acc, valid_top5_acc, valid_loss = self._valid_epoch(
                epoch)
            logging.info('valid_top1_acc {:.5f}, valid_top5_acc {:.5f}, valid_loss {:.5f}'.format(
                valid_top1_acc, valid_top5_acc, valid_loss))

            if valid_loss < best_valid_loss:
                best_valid_loss = valid_loss
                is_best = True
            else:
                is_best = False

            utils.save_checkpoint(model.state_dict(), is_best, savedir, epoch)

    def _train_epoch(self, epoch: int):
        """Trains the model for one epoch"""
        total_loss = utils.AveTracker()
        top1_acc = utils.AveTracker()
        top5_acc_acc = utils.AveTracker()
        self.model.train()

        for step, (x, y) in enumerate(self.train_loader):
            x, y = x.to(self.device), y.to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(x)
            loss = self.criterion(logits, y)
            loss.backward()
            self.optimizer.step()

            prec1, prec5 = utils.accuracy(logits, y, topk=(1, 5))
            n = x.size(0)
            total_loss.update(loss.data[0], n)
            top1_acc.update(prec1.data[0], n)
            top5_acc.update(prec5.data[0], n)

            if step % 100 == 0:
                logging.info('train %d %e %f %f', step,
                             total_loss.avg, top1_acc.avg, top5_acc.avg)

        return top1_acc.avg, top5_acc.avg, total_loss.avg

    def _valid_epoch(self, epoch):
        """Runs validation"""
        total_loss = utils.AveTracker()
        top1_acc = utils.AveTracker()
        top5_acc = utils.AveTracker()
        self.model.eval()

        with torch.no_grad():
            for step, (x, y) in enumerate(self.valid_loader):
                x, y = x.to(self.device), y.to(self.device)

                logits = self.model(x)
                loss = self.criterion(logits, y)

                prec1, prec5 = utils.accuracy(logits, y, topk=(1, 5))
                n = x.size(0)
                total_loss.update(loss.data[0], n)
                top1_acc.update(prec1.data[0], n)
                top5_acc.update(prec5.data[0], n)

                if step % 100 == 0:
                    logging.info('valid %d %e %f %f', step,
                                 total_loss.avg, top1_acc.avg, top5_acc.avg)

        return top1_acc.avg, top5_acc.avg, total_loss.avg