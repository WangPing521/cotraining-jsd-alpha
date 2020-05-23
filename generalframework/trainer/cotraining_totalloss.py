import random
from operator import itemgetter
from typing import Dict, List, Union
import pandas as pd
import yaml
from tensorboardX import SummaryWriter
import torch
from torch import Tensor, nn

from generalframework import ModelMode
from torch.utils.data import DataLoader
from .trainer import Trainer
from ..loss import CrossEntropyLoss2d, KL_Divergence_2D, KL_Divergence_2D_Logit
from ..models import Segmentator
from ..utils.AEGenerator import FSGMGenerator, VATGenerator
from ..utils import iterator_
from ..utils.utils import *
from ..metrics import DiceMeter, AverageValueMeter
from .. import scheduler
from ..scheduler import *


def fix_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


class CoTrainer(Trainer):

    def __init__(self, segmentators: List[Segmentator],
                 labeled_dataloaders: List[DataLoader],
                 unlabeled_dataloader: DataLoader,
                 val_dataloader: DataLoader,
                 criterions: Dict[str, nn.Module],
                 max_epoch: int = 100,
                 save_dir: str = 'tmp',
                 device: str = 'cpu',
                 axises: List[int] = [1, 2, 3],
                 checkpoint: Union[List[str], None] = None,
                 metricname: str = 'metrics.csv',
                 adv_scheduler_dict: dict = None,
                 cot_scheduler_dict: dict = None,
                 alpha_scheduler_dict: dict = None,
                 adv_training_dict: dict = {},
                 use_tqdm: bool = True,
                 whole_config=None) -> None:

        self.max_epoch = max_epoch
        self.segmentators = segmentators
        self.labeled_dataloaders = labeled_dataloaders
        self.unlabeled_dataloader = unlabeled_dataloader
        self.val_dataloader = val_dataloader

        # N segmentators should be consist with N+1 dataloders
        assert self.segmentators.__len__() == self.labeled_dataloaders.__len__()
        assert self.segmentators.__len__() >= 1
        # the sgementators and dataloaders must be different instance
        assert set(map_(id, self.segmentators)).__len__() == self.segmentators.__len__()
        assert set(map_(id, self.labeled_dataloaders)).__len__() == self.segmentators.__len__()
        # labeled_dataloaders should have the same batch number
        assert set(map_(lambda x: x.batch_size, self.labeled_dataloaders)).__len__() == 1
        # assert set(map_(lambda x: len(x), self.labeled_dataloaders)).__len__() == 1

        self.criterions = criterions
        assert set(self.criterions.keys()) == {'jsd', 'sup', 'adv'}

        self.save_dir = Path(save_dir)
        # assert not (self.save_dir.exists() and checkpoint is None), f'>> save_dir: {self.save_dir} exits.'
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.writer = SummaryWriter(save_dir)
        # save the whole new config to the save_dir
        if whole_config:
            with open(Path(self.save_dir, 'config.yml'), 'w') as outfile:
                yaml.dump(whole_config, outfile, default_flow_style=False)

        self.device = torch.device(device)
        self.C = self.segmentators[0].arch_params['num_classes']
        self.axises = axises
        self.best_scores = np.zeros(self.segmentators.__len__())
        self.last_scores = np.zeros(self.segmentators.__len__())
        self.start_epoch = 0
        self.metricname = metricname

        # scheduler
        self.cot_scheduler = getattr(scheduler, cot_scheduler_dict['name'])(
            **{k: v for k, v in cot_scheduler_dict.items() if k != 'name'})
        self.alpha_scheduler = getattr(scheduler, alpha_scheduler_dict['name'])(
            **{k: v for k, v in alpha_scheduler_dict.items() if k != 'name'})
        self.adv_scheduler = getattr(scheduler, adv_scheduler_dict['name'])(
            **{k: v for k, v in adv_scheduler_dict.items() if k != 'name'})
        self.adv_training_dict = adv_training_dict

        if checkpoint is not None:
            # todo
            self._load_checkpoint(checkpoint)

        self.to(self.device)
        self.use_tqdm = use_tqdm

    def to(self, device: torch.device):
        [segmentator.to(device) for segmentator in self.segmentators]
        [criterion.to(device) for _, criterion in self.criterions.items()]

    def tensorboard_loss(self, save_root):
        writer1 = SummaryWriter(save_root)
        return writer1

    def start_training(self,
                       entropy_min=False,
                       train_jsd=False,
                       train_adv=False,
                       save_train=False,
                       save_val=False,
                       augment_labeled_data=False,
                       augment_unlabeled_data=False):
        S = len(self.segmentators)
        metrics = {'train_dice': torch.zeros(self.max_epoch, S, self.C, 2, dtype=torch.float),
                   'train_unlab_dice': torch.zeros(self.max_epoch, S, self.C, 2, dtype=torch.float),
                   'val_dice': torch.zeros(self.max_epoch, S, self.C, 2, dtype=torch.float),
                   'val_batch_dice': torch.zeros(self.max_epoch, S, self.C, 2, dtype=torch.float)}
        writer1 = self.tensorboard_loss(self.save_dir)
        test = False
        if test:
            loss = self._test_unlab_loop(unlabeled_dataloader=self.unlabeled_dataloader, mode=ModelMode.EVAL)
        for epoch in range(self.start_epoch, self.max_epoch):

            train_dice, train_unlab_dice = self._train_loop(labeled_dataloaders=self.labeled_dataloaders,
                                                            unlabeled_dataloader=self.unlabeled_dataloader,
                                                            epoch=epoch,
                                                            mode=ModelMode.TRAIN,
                                                            save=save_train,
                                                            entropy_min=entropy_min,
                                                            train_jsd=train_jsd,
                                                            train_adv=train_adv,
                                                            augment_labeled_data=augment_labeled_data,
                                                            augment_unlabeled_data=augment_unlabeled_data,
                                                            writer1=writer1
                                                            )
            with torch.no_grad():
                val_dice, val_batch_dice = self._eval_loop(val_dataloader=self.val_dataloader,
                                                           epoch=epoch,
                                                           mode=ModelMode.EVAL,
                                                           save=save_val)

            self.schedulerStep()
            for k, v in metrics.items():
                assert v[epoch].shape == eval(k).shape
                v[epoch] = eval(k)
            for k, v in metrics.items():
                np.save(self.save_dir / f'{k}.npy', v.data.numpy())

            writer = pd.ExcelWriter(Path(self.save_dir, self.metricname.replace('csv', 'xlsx')), engine='openpyxl')
            for s in range(self.segmentators.__len__()):
                df = pd.DataFrame(
                    {
                        **{f"train_dice_{i}": metrics["train_dice"][:, s, i, 0] for i in self.axises},
                        **{f"train_unlab_dice_{i}": metrics["train_unlab_dice"][:, s, i, 0] for i in
                           self.axises},
                        **{f"val_dice_{i}": metrics["val_dice"][:, s, i, 0] for i in self.axises},
                        **{f"val_batch_dice_{i}": metrics["val_batch_dice"][:, s, i, 0] for i in self.axises}
                    })
                df.to_csv(Path(self.save_dir, self.metricname.replace('.csv', f'_{s}.csv')), float_format="%.4f",
                          index_label="epoch")
                df.to_excel(excel_writer=writer, sheet_name=f'Seg_{s}', encoding="utf-8", index_label='epoch',
                            float_format="%.4f")
            writer.save()
            writer.close()

            current_metric = val_batch_dice[:, self.axises, 0].mean(1)
            if epoch % 10 == 0:
                self.checkpoint(current_metric, epoch)

    def entropy(self, inputs):
        b, _, h, w = inputs.shape
        assert simplex(inputs)
        e = inputs * (inputs + 1e-16).log()
        e = -1.0 * e.sum(1)
        assert e.shape == torch.Size([b, h, w])
        return e

    def _test_unlab_loop(self, unlabeled_dataloader: DataLoader, mode: ModelMode = ModelMode.EVAL):
        [segmentator.set_mode(mode) for segmentator in self.segmentators]
        unlabeled_dataloader.dataset.set_mode(ModelMode.EVAL)
        assert not self.segmentators[0].training
        unlabeled_dataloader = tqdm_(unlabeled_dataloader) if self.use_tqdm else unlabeled_dataloader

        for batch_num, [(img, gt), _, path] in enumerate(unlabeled_dataloader):
            img, gt = img.to(self.device), gt.to(self.device)
            preds = map_(lambda x: x.predict(img, logit=True), self.segmentators)
            # preds[0].softmax(dim=1)[0]
            f1 = []
            f2 = []
            mean_pre = []
            for i in range(4):
                mean_prob = 0.5 * (preds[0][i].softmax(dim=0) + preds[1][i].softmax(dim=0))

                E_mean_pred = self.entropy(mean_prob.unsqueeze(0)).mean()
                E1 = self.entropy(preds[0][i].softmax(dim=0).unsqueeze(0)).mean()
                E2 = self.entropy(preds[1][i].softmax(dim=0).unsqueeze(0)).mean()

                Mean_E_pred = 0.5 * (E1 + E2)
                f1.append(E1.item())
                f2.append(E2.item())
                mean_pre.append(E_mean_pred.item())
            print('\n', f1,'\n', f2, '\n', mean_pre)
            loss = map_(lambda pred: self.criterions.get('sup')(pred, gt.squeeze(1)), preds)
        return E_mean_pred, Mean_E_pred, loss

    def _train_loop(self,
                    labeled_dataloaders: List[DataLoader],
                    unlabeled_dataloader: DataLoader,
                    epoch: int,
                    mode: ModelMode,
                    save: bool,
                    augment_labeled_data=False,
                    augment_unlabeled_data=False,
                    entropy_min=False,
                    train_jsd=False,
                    train_adv=False,
                    writer1=None):

        fix_seed(epoch)
        diceMeters = [DiceMeter(report_axises=self.axises, method='2d', C=self.C) for _ in
                      range(self.segmentators.__len__())]
        unlabdiceMeters = [DiceMeter(report_axises=self.axises, method='2d', C=self.C) for _ in
                           range(self.segmentators.__len__())]
        suplossMeters = [AverageValueMeter() for _ in range(self.segmentators.__len__())]
        jsdlossMeter = AverageValueMeter()
        advlossMeter = AverageValueMeter()

        [segmentator.set_mode(mode) for segmentator in self.segmentators]
        for l_dataloader in labeled_dataloaders:
            l_dataloader.dataset.set_mode(ModelMode.TRAIN if augment_labeled_data else ModelMode.EVAL)
        unlabeled_dataloader.dataset.training = ModelMode.TRAIN if augment_unlabeled_data else ModelMode.EVAL

        assert self.segmentators[0].training
        assert self.labeled_dataloaders[
                   0].dataset.training == ModelMode.TRAIN if augment_labeled_data else ModelMode.EVAL
        assert self.unlabeled_dataloader.dataset.training == ModelMode.TRAIN if augment_unlabeled_data else ModelMode.EVAL

        desc = f">>   Training   ({epoch})" if mode == ModelMode.TRAIN else f">> Validating   ({epoch})"
        # Here the concept of epoch is defined as the epoch
        # n_batch = max(map_(len, self.labeled_dataloaders))
        n_batch = 200
        S = len(self.segmentators)

        # build fake_iterator
        fake_labeled_iterators = [iterator_(x) for x in labeled_dataloaders]
        fake_unlabeled_iterator = iterator_(unlabeled_dataloader)

        report_iterator = iterator_(['label', 'unlab'])
        report_status = 'label'

        n_batch_iter = tqdm_(range(n_batch)) if self.use_tqdm else range(n_batch)

        for batch_num in n_batch_iter:
            if batch_num % 30 == 0 and train_jsd and self.cot_scheduler.value > 0:
                report_status = report_iterator.__next__()

            supervisedLoss, jsdLoss, advLoss, loss1, loss2, entLoss = 0, 0, 0, 0, 0, 0
            for enu_lab in range(len(fake_labeled_iterators)):
                [[img, gt], _, path] = fake_labeled_iterators[enu_lab].__next__()
                img, gt = img.to(self.device), gt.to(self.device)
                pred = self.segmentators[enu_lab].predict(img, logit=True)
                sup_loss = self.criterions.get('sup')(pred, gt.squeeze(1))
                diceMeters[enu_lab].add(pred, gt)
                suplossMeters[enu_lab].add(sup_loss.detach().data.cpu())
                if save:
                    save_images(pred2class(pred), names=path, root=self.save_dir, mode='train', iter=epoch,
                                seg_num=str(enu_lab))
                supervisedLoss += sup_loss
            if entropy_min:
                [[unlab_img, unlab_gt], _, path] = fake_unlabeled_iterator.__next__()
                unlab_img, unlab_gt = unlab_img.to(self.device), unlab_gt.to(self.device)
                unlab_preds: List[Tensor] = map_(lambda x: x.predict(unlab_img, logit=False), self.segmentators)
                list(map(lambda x, y: x.add(y, unlab_gt), unlabdiceMeters, unlab_preds))
                entropys_metric = self.entropy(unlab_preds[0])
                entLoss = entropys_metric.mean()

            if train_jsd:
                # for unlabeled data update
                [[unlab_img, unlab_gt], _, path] = fake_unlabeled_iterator.__next__()
                unlab_img, unlab_gt = unlab_img.to(self.device), unlab_gt.to(self.device)
                unlab_preds: List[Tensor] = map_(lambda x: x.predict(unlab_img, logit=False), self.segmentators)
                list(map(lambda x, y: x.add(y, unlab_gt), unlabdiceMeters, unlab_preds))
                f_term, mean_entropy = self.criterions.get('jsd')(unlab_preds)
                jsdloss_2D = f_term - self.alpha_scheduler.value * mean_entropy
                jsdLoss: Tensor = jsdloss_2D.mean()
                jsdlossMeter.add(jsdLoss.item())
                loss1 = f_term.mean().item()
                loss2 = (self.alpha_scheduler.value * mean_entropy).mean().item()
                #
                if save:
                    [save_images(probs2class(prob), names=path, root=self.save_dir, mode='unlab',
                                 iter=epoch, seg_num=str(i)) for i, prob in enumerate(unlab_preds)]

            if train_adv:
                try:
                    choice = sorted(np.random.choice(list(range(S)), 2, replace=False).tolist())
                except:
                    choice = sorted(np.random.choice(list(range(S)), 2, replace=True).tolist())

                advLoss = self._FSGM_adv_training(segmentators=itemgetter(*choice)(self.segmentators),
                                                  lab_data_iterators=itemgetter(*choice)(fake_labeled_iterators),
                                                  unlab_data_iterator=fake_unlabeled_iterator,
                                                  **self.adv_training_dict)

                advlossMeter.add(advLoss.item())
            map_(lambda x: x.optimizer.zero_grad(), self.segmentators)
            totalLoss = supervisedLoss + self.cot_scheduler.value * jsdLoss + self.adv_scheduler.value * advLoss + self.cot_scheduler.value * entLoss
            totalLoss.backward()
            map_(lambda x: x.optimizer.step(), self.segmentators)

            # for recording
            lab_dsc_dict = {f"S{i}": {f"DSC{n}": diceMeters[i].value()[1][0][n].cpu() for n in self.axises} \
                            for i in range(len(self.segmentators))}
            unlab_dsc_dict = {f"S{i}": {f"DSC{n}": unlabdiceMeters[i].value()[1][0][n].cpu() \
                                        for n in self.axises} for i in range(len(self.segmentators))}
            lab_mean_dict = {f"S{i}": {"DSC": diceMeters[i].value()[0][0].cpu()} for i in range(len(self.segmentators))}
            unlab_mean_dict = {f"S{i}": {"DSC": unlabdiceMeters[i].value()[0][0].cpu()} for i in
                               range(len(self.segmentators))}
            loss_dict = {f'L{i}': suplossMeters[i].value()[0] for i in range(len(self.segmentators))}
            nice_dict = dict_merge(lab_dsc_dict, lab_mean_dict, re=True) if report_status == 'label' else dict_merge(
                unlab_dsc_dict, unlab_mean_dict, re=True)
            if self.use_tqdm:
                n_batch_iter.set_postfix({f'{k}_{k_}': f'{v[k_]:.2f}' for k, v in nice_dict.items() for k_ in v.keys()})
                n_batch_iter.set_description(
                    report_status + ': ' + ','.join([f'{k}:{v:.3f}' for k, v in loss_dict.items()]))

        writer1.add_scalar('Loss/loss_sup', supervisedLoss.item() / 4, epoch)
        writer1.add_scalar('Loss/jsd_term1', loss1 / 4, epoch)
        writer1.add_scalar('Loss/jsd_term2',  loss2 / 4, epoch)
        writer1.add_scalar('Loss/entropy_value',  entLoss / 4, epoch)
        writer1.add_scalar('Loss/total_loss', totalLoss.item() / 4, epoch)

        self.upload_dicts('labeled dataset', lab_dsc_dict, epoch)
        self.upload_dicts('unlabeled dataset', unlab_dsc_dict, epoch)
        nice_dict = dict_merge(lab_dsc_dict, lab_mean_dict, re=True)
        print(f"{desc} " + ', '.join([f'{k}_{k_}:{v[k_]:.2f}' for k, v in nice_dict.items() for k_ in v.keys()]))
        return torch.stack([torch.stack(diceMeters[i].value()[1], dim=1) for i in range(S)]), torch.stack(
            [torch.stack(unlabdiceMeters[i].value()[1], dim=1) for i in range(S)])

    def _eval_loop(self,
                   val_dataloader: DataLoader,
                   epoch: int,
                   mode: ModelMode = ModelMode.EVAL,
                   save: bool = False
                   ):
        [segmentator.set_mode(mode) for segmentator in self.segmentators]
        val_dataloader.dataset.set_mode(ModelMode.EVAL)
        assert not self.segmentators[0].training
        desc = f">> Validating   ({epoch})"
        S = self.segmentators.__len__()

        coefdiceMeters = [DiceMeter(report_axises=self.axises, method='2d', C=4) for _ in range(S)]
        batchdiceMeters = [DiceMeter(report_axises=self.axises, method='3d', C=4) for _ in range(S)]
        vallossMeters = [AverageValueMeter() for _ in range(self.segmentators.__len__())]

        val_dataloader = tqdm_(val_dataloader) if self.use_tqdm else val_dataloader
        nice_dict: dict

        for batch_num, [(img, gt), _, path] in enumerate(val_dataloader):
            img, gt = img.to(self.device), gt.to(self.device)
            preds = map_(lambda x: x.predict(img, logit=True), self.segmentators)
            loss = map_(lambda pred: self.criterions.get('sup')(pred, gt.squeeze(1)), preds)
            list(map(lambda x, y: x.add(y, gt), coefdiceMeters, preds))
            list(map(lambda x, y: x.add(y, gt), batchdiceMeters, preds))
            list(map(lambda x, y: x.add(y.detach().data.cpu()), vallossMeters, loss))

            if save:
                [save_images(pred2class(pred), names=path, root=self.save_dir, mode='eval', seg_num=str(i), iter=epoch)
                 for i, pred in enumerate(preds)]

            dsc_dict = {f"S{i}": {f"DSC{n}": batchdiceMeters[i].value()[1][0][n] for n in self.axises} for i in range(S)}
            mean_dict = {f"S{i}": {"DSC": batchdiceMeters[i].value()[0][0]} for i in range(S)}
            nice_dict = dict_merge(dsc_dict, mean_dict, True)
            loss_dict = {f'L{i}': vallossMeters[i].value()[0] for i in range(S)}

            if self.use_tqdm:
                val_dataloader.set_description('val: ' + ','.join([f'{k}:{v:.3f}' for k, v in loss_dict.items()]))
                val_dataloader.set_postfix(
                    {f'{k}_{k_}': f'{v[k_]:.2f}' for k, v in nice_dict.items() for k_ in v.keys()})


        self.upload_dicts('val_data', dsc_dict, epoch)

        print(f"{desc} " + ', '.join([f'{k}_{k_}: {v[k_]:.2f}' for k, v in nice_dict.items() for k_ in v.keys()]))
        return torch.stack([torch.stack(coefdiceMeters[i].value()[1], dim=1) for i in range(S)]), torch.stack(
            [torch.stack(batchdiceMeters[i].value()[1], dim=1) for i in range(S)])

    def _adv_training(self, segmentators: List[Segmentator],
                      lab_data_iterators: List[iterator_],
                      unlab_data_iterator: iterator_,
                      eplision: float = 0.05,
                      label_data_ratio=0.5,
                      use_fsgm=True):
        assert segmentators.__len__() == 2, 'only implemented for 2 segmentators'
        adv_losses = []
        # draw first term from labeled1 or unlabeled
        if random.random() <= label_data_ratio:
            [[img, gt], _, _] = lab_data_iterators[0].__next__()
            img, gt = img.to(self.device), gt.to(self.device)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if use_fsgm:
                    img_adv, _ = FSGMGenerator(segmentators[0].torchnet, eplision=eplision) \
                        (dcopy(img), gt, criterion=self.criterions['sup'])
                else:
                    img_adv, _ = VATGenerator(segmentators[0].torchnet, eplision=eplision)(dcopy(img))
        else:
            [[img, _], _, _] = unlab_data_iterator.__next__()
            img = img.to(self.device)
            img_adv, _ = VATGenerator(segmentators[0].torchnet, eplision=eplision)(dcopy(img))
        assert img.shape == img_adv.shape
        adv_pred = segmentators[1].predict(img_adv, logit=False)
        real_pred = segmentators[0].predict(img, logit=False)
        # adv_losses.append(KL_Divergence_2D(reduce=True)(adv_pred, real_pred.detach()))
        adv_losses.append(KL_Divergence_2D(reduce=True)(adv_pred, real_pred))

        if random.random() <= label_data_ratio:
            [[img, gt], _, _] = lab_data_iterators[1].__next__()
            img, gt = img.to(self.device), gt.to(self.device)
            if use_fsgm:
                img_adv, _ = FSGMGenerator(segmentators[1].torchnet, eplision=eplision) \
                    (img, gt, criterion=CrossEntropyLoss2d())
            else:
                img_adv, _ = VATGenerator(segmentators[1].torchnet, eplision=eplision)(dcopy(img))
        else:
            [[img, _], _, _] = unlab_data_iterator.__next__()
            img = img.to(self.device)
            img_adv, _ = VATGenerator(segmentators[1].torchnet, eplision=eplision)(dcopy(img))

        adv_pred = segmentators[0].predict(img_adv, logit=False)
        real_pred = segmentators[1].predict(img, logit=False)
        # adv_losses.append(KL_Divergence_2D(reduce=True)(adv_pred, real_pred.detach()))
        adv_losses.append(KL_Divergence_2D(reduce=True)(adv_pred, real_pred))

        adv_loss = sum(adv_losses) / adv_losses.__len__()

        return adv_loss

    def _FSGM_adv_training(self, segmentators: List[Segmentator],
                           lab_data_iterators: List[iterator_],
                           unlab_data_iterator: iterator_,
                           eplision: float = 0.05):
        assert segmentators.__len__() == 2, 'only implemented for 2 segmentators'
        adv_losses = []

        '''
         to have two forward_backward path.
        '''
        [[img_1, gt_1], _, _] = lab_data_iterators[0].__cache__()
        img_1, gt_1 = img_1.to(self.device), gt_1.to(self.device)
        [[unl_img, unl_gt], _, _] = unlab_data_iterator.__cache__()
        unl_img = unl_img.to(self.device)

        [[img_2, gt_2], _, _] = lab_data_iterators[1].__cache__()
        img_2, gt_2 = img_2.to(self.device), gt_2.to(self.device)

        img_adv, noise, real_preds = FSGMGenerator(segmentators[1].torchnet, eplision=eplision) \
            (torch.cat((img_2, unl_img), dim=0), gt=gt_2, criterion=self.criterions['sup'])
        adv_preds = segmentators[0].predict(img_adv, logit=False)
        adv_losses.append(KL_Divergence_2D(reduce=True)(adv_preds, real_preds.detach()))

        #
        # draw first term from labeled1
        '''
        [[img_1, gt_1], _, _] = lab_data_iterators[0].__cache__()
        img_1, gt_1 = img_1.to(self.device), gt_1.to(self.device)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            img_1_adv, _,_ = FSGMGenerator(segmentators[0].torchnet, eplision=eplision) \
                (dcopy(img_1), gt_1, criterion=self.criterions['sup'])

        adv_pred = segmentators[1].predict(img_1_adv, logit=False)
        real_pred = segmentators[0].predict(img_1, logit=False)
        adv_losses.append(KL_Divergence_2D(reduce=True)(adv_pred, real_pred.detach()))

        # draw  term from labeled2
        [[img_2, gt_2], _, _] = lab_data_iterators[1].__cache__()
        img_2, gt_2 = img_2.to(self.device), gt_2.to(self.device)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            img_2_adv, _,_ = FSGMGenerator(segmentators[1].torchnet, eplision=eplision) \
                (dcopy(img_2), gt_2, criterion=self.criterions['sup'])

        adv_pred = segmentators[0].predict(img_2_adv, logit=False)
        real_pred = segmentators[1].predict(img_2, logit=False)
        adv_losses.append(KL_Divergence_2D(reduce=True)(adv_pred, real_pred.detach()))

        # draw from unlabeled dataset
        [[unl_img, _], _, _] = unlab_data_iterator.__cache__()
        unl_img = unl_img.to(self.device)
        with torch.no_grad():
            unl_pred1 = segmentators[0].predict(unl_img, logit=False)
            unl_mask1 = unl_pred1.max(1)[1]
            unl_pred2 = segmentators[1].predict(unl_img, logit=False)
            unl_mask2 = unl_pred2.max(1)[1]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            unl_adv1, _,_ = FSGMGenerator(segmentators[0].torchnet, eplision=eplision) \
                (dcopy(unl_img), unl_mask1, criterion=self.criterions['sup'])
            unl_adv2, _,_ = FSGMGenerator(segmentators[1].torchnet, eplision=eplision) \
                (dcopy(unl_img), unl_mask2, criterion=self.criterions['sup'])
        adv_pred = segmentators[1].predict(unl_adv1, logit=False)
        adv_losses.append(KL_Divergence_2D(reduce=True)(adv_pred, unl_pred1.detach()))

        adv_pred = segmentators[0].predict(unl_adv2, logit=False)
        adv_losses.append(KL_Divergence_2D(reduce=True)(adv_pred, unl_pred2.detach()))
        '''
        adv_loss = sum(adv_losses) / adv_losses.__len__()

        return adv_loss

    def upload_dicts(self, name, dicts, epoch):
        for k, v in dicts.items():
            name_ = name + '/' + k
            self.upload_dict(name_, v, epoch)

    def upload_dict(self, name, dict, epoch):
        self.writer.add_scalars(name, dict, epoch)

    def schedulerStep(self):
        for segmentator in self.segmentators:
            segmentator.schedulerStep()
        self.cot_scheduler.step()
        self.alpha_scheduler.step()
        self.adv_scheduler.step()

    def _load_checkpoint(self, checkpoint):
        # load checklit
        # if isinstance(checkpoint, str):
        #     checkpoint = eval(checkpoint)
        checkpoint = list(Path(checkpoint).glob('last*.pth'))
        assert isinstance(checkpoint, list), 'checkpoint should be provided as a list.'
        for i, cp in enumerate(checkpoint):
            cp = Path(cp)
            assert cp.exists(), cp
            state_dict = torch.load(cp, map_location=torch.device('cpu'))
            self.segmentators[i].load_state_dict(state_dict['segmentator'])
            self.last_scores[i] = state_dict['last_score']
            self.start_epoch = state_dict["start_epoch"]
            print(f'>>>  {cp} has been loaded successfully. \
                Last score {self.last_scores[i]:.3f} @ {state_dict["start_epoch"]}.')
            self.segmentators[i].train()

    def checkpoint(self, metric, epoch, filename_best=None, filename_last=None):
        assert isinstance(metric, Tensor)
        assert metric.__len__() == self.segmentators.__len__()
        for i, score in enumerate(metric):
            # slack variable:
            self.best_score = self.best_scores[i]
            self.last_score = self.last_scores[i]
            self.segmentator = self.segmentators[i]
            super().checkpoint(score, epoch, filename_best=f'best_{i}.pth', filename_last=f'last_{i}.pth')
            self.best_scores[i] = self.best_score
            self.last_scores[i] = self.last_score
