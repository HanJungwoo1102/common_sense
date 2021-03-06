import torch
from transformers import BertTokenizerFast
from utils.trainer import Trainer
from utils.data_loader_maker import DataLoaderMaker
from utils import get_device
from model import Model

def train(args):
    batch_size = args.batch_size
    max_seq_length = args.max_seq_length
    drop_last = False
    append_answer_text = args.append_answer_text
    append_descr = args.append_descr
    append_tripple = False if args.append_tripple == 0 else True
    gpu_ids = None
    if gpu_ids is None:
        n_gpus = torch.cuda.device_count()
        gpu_ids=','.join([str(i) for i in range(n_gpus)])
    fp16 = True if args.fp16 == 1 else False
    model_path = args.model_path
    cache_dir = args.cache_dir
    no_att_merge = False
    print_step = args.print_step
    output_model_dir = args.output_model_dir
    num_train_epochs = args.num_train_epochs
    warmup_proportion = args.warmup_proportion
    weight_decay = args.weight_decay
    choice_num = args.choice_num
    scorer_hidden = args.scorer_hidden
    version = args.model_version
    lr = args.lr
    freeze_lm_epochs = 0
    gpu_ids = list(map(int, gpu_ids.split(',')))
    multi_gpu = (len(gpu_ids) > 1)
    device = get_device(gpu_ids)
    train_data_path = args.train_data_path
    dev_data_path = args.dev_data_path
    
    tokenizer = BertTokenizerFast.from_pretrained("kykim/albert-kor-base")

    data_loader_maker = DataLoaderMaker()
    train_dataloader = data_loader_maker.make(
        train_data_path,
        tokenizer,
        batch_size,
        drop_last,
        max_seq_length,
        append_answer_text,
        append_descr,
        append_tripple,
        shuffle = True
    )

    devlp_dataloader = data_loader_maker.make(
        dev_data_path,
        tokenizer,
        batch_size,
        drop_last,
        max_seq_length,
        append_answer_text,
        append_descr,
        append_tripple,
        shuffle = False
    )

    model = Model.from_pretrained(model_path, cache_dir=cache_dir, no_att_merge=no_att_merge, N_choices = choice_num, scorer_hidden = scorer_hidden, version = version ).cuda()

    trainer = Trainer(
        model, multi_gpu, device,
        print_step, output_model_dir, fp16
    )

    optimizer = trainer.make_optimizer(weight_decay, lr)
    scheduler = trainer.make_scheduler(optimizer, warmup_proportion, len(train_dataloader) * num_train_epochs)

    trainer.set_optimizer(optimizer)
    trainer.set_scheduler(scheduler)

    trainer.train(
        num_train_epochs, train_dataloader, devlp_dataloader, 
        save_last=False, freeze_lm_epochs=freeze_lm_epochs
    )