# Pinecone CLI
This is a tool to insert Pocket data into [Pinecone](https://pinecone.io).
To get started, you can create a Pinecone index for free in the
[Pinecone App](https://app.pinecone.io/).

## 1. Setup your environment
1. Create Conda environment:
```shell
conda env create -f pinecone_cli_environment.yml
```

2. Clone [recit-ralph](https://github.com/Pocket/recit-ralph), activate `$(maws)` with 
production read access, and run 
[get_latest.sh](https://github.com/Pocket/recit-ralph/blob/main/data/latest/get_latest.sh) to
download RecIt data files.

## 2. Run the tool
### Get help
Get a list of commands and shared arguments:
```shell
./pinecone_cli.py --help
```

Get help for a specific command, such as 'upsert':
```shell
./pinecone_cli.py upsert --help
```

### Shared arguments across all commands
- (required) `--pinecone-api-key="key-goes-here"` authenticates with the API key that you can find in the
[Pinecone App](https://app.pinecone.io/).
- (optional) `--pinecone-index="pocket-syndicated"` specifies the Pinecone index name that you can find in the
[Pinecone App](https://app.pinecone.io/). By default it's set to `pocket-syndicated`. 
- (optional) `--pinecone-region="us-west1-gcp"` override the Pinecone region. By default it's set to `us-west1-gcp`,
which is currently the only region that Pinecone is available in.

### Upsert command
Inserts and/or updates vectors into a Pinecone index.
The `docvecs` should be set to the RecIt-Ralph data file ending in 
`vectors_docs.npy`,  that was downloaded as part of the 'setup environment' step.

```shell
./pinecone_cli.py upsert \
  --pinecone-api-key="key-goes-here" \ 
  --pinecone-index="pocket-syndicated" \
  --docvecs="/path/to/recit/doc2vec.model.docvecs.vectors_docs.npy"
```
