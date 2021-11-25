# Common Sense

## Description

### Make Data Loader

```python

from utils.data_loader_maker import DataLoaderMaker

tokenizer = BertTokenizerFast.from_pretrained("kykim/albert-kor-base")
batch_size = 4
max_seq_length = 128
append_answer_text = 1
append_descr = 1
append_tripple = True

data_loader_maker = DataLoaderMaker()
dataloader = data_loader_maker.make(
    '../data/train_data.json',
    tokenizer,
    batch_size,
    drop_last,
    max_seq_length,
    append_answer_text,
    append_descr,
    append_tripple,
)

```